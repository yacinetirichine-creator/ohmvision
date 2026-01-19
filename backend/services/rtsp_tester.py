"""
OhmVision - RTSP Tester
Tests RTSP connections and extracts stream information
"""

import subprocess
import re
import socket
import asyncio
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, quote
import logging
import os

logger = logging.getLogger(__name__)


@dataclass
class RTSPStreamInfo:
    """Informations sur un flux RTSP"""
    url: str
    is_valid: bool = False
    width: int = 0
    height: int = 0
    fps: float = 0.0
    codec: str = ""
    bitrate: int = 0
    error_message: str = ""
    response_time_ms: float = 0.0
    
    @property
    def resolution(self) -> str:
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "unknown"


class RTSPTester:
    """Testeur de connexions RTSP"""
    
    # URLs RTSP communes par fabricant
    RTSP_PATHS = {
        "hikvision": [
            "/Streaming/Channels/101",  # Main stream
            "/Streaming/Channels/102",  # Sub stream
            "/Streaming/Channels/1",
            "/h264/ch1/main/av_stream",
        ],
        "dahua": [
            "/cam/realmonitor?channel=1&subtype=0",  # Main
            "/cam/realmonitor?channel=1&subtype=1",  # Sub
            "/live",
        ],
        "axis": [
            "/axis-media/media.amp",
            "/axis-media/media.amp?videocodec=h264",
            "/mpeg4/media.amp",
        ],
        "reolink": [
            "/h264Preview_01_main",
            "/h264Preview_01_sub",
        ],
        "generic": [
            "/stream1",
            "/stream",
            "/video1",
            "/live/ch00_0",
            "/live.sdp",
            "/media/video1",
            "/videoMain",
            "/cam/realmonitor?channel=1&subtype=0",
            "/Streaming/Channels/101",
            "/",
        ]
    }
    
    # Ports RTSP courants
    RTSP_PORTS = [554, 8554, 5554]
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
    
    def build_rtsp_url(self, ip: str, port: int = 554, path: str = "/stream1",
                       username: str = "", password: str = "") -> str:
        """Construit une URL RTSP complète"""
        auth = ""
        if username:
            # Encoder les caractères spéciaux dans le mot de passe
            safe_password = quote(password, safe='') if password else ""
            auth = f"{quote(username, safe='')}:{safe_password}@"
        
        # S'assurer que le path commence par /
        if not path.startswith('/'):
            path = '/' + path
        
        return f"rtsp://{auth}{ip}:{port}{path}"
    
    def test_rtsp_socket(self, ip: str, port: int = 554) -> Tuple[bool, float]:
        """
        Test rapide de connexion RTSP via socket
        
        Returns:
            (success, response_time_ms)
        """
        import time
        
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            elapsed = (time.time() - start) * 1000
            sock.close()
            
            return (result == 0, elapsed)
            
        except Exception as e:
            logger.debug(f"Socket test failed for {ip}:{port}: {e}")
            return (False, 0)
    
    def test_rtsp_url(self, url: str) -> RTSPStreamInfo:
        """
        Teste une URL RTSP et récupère les informations du flux
        
        Args:
            url: URL RTSP complète
        
        Returns:
            RTSPStreamInfo avec les détails du flux
        """
        info = RTSPStreamInfo(url=url)
        
        # Parser l'URL pour le test socket d'abord
        try:
            parsed = urlparse(url)
            ip = parsed.hostname
            port = parsed.port or 554
            
            # Test socket rapide
            socket_ok, response_time = self.test_rtsp_socket(ip, port)
            info.response_time_ms = response_time
            
            if not socket_ok:
                info.error_message = f"Cannot connect to {ip}:{port}"
                return info
                
        except Exception as e:
            info.error_message = f"Invalid URL: {e}"
            return info
        
        # Test avec ffprobe pour les détails du flux
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-rtsp_transport", "tcp",
                    "-i", url,
                    "-show_streams",
                    "-show_format",
                    "-print_format", "json",
                    "-timeout", str(int(self.timeout * 1000000))  # en microsecondes
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout + 2
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                # Extraire les infos du flux vidéo
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        info.is_valid = True
                        info.width = int(stream.get('width', 0))
                        info.height = int(stream.get('height', 0))
                        info.codec = stream.get('codec_name', '')
                        
                        # FPS
                        fps_str = stream.get('r_frame_rate', '0/1')
                        if '/' in fps_str:
                            num, den = fps_str.split('/')
                            info.fps = float(num) / float(den) if float(den) > 0 else 0
                        
                        # Bitrate
                        info.bitrate = int(stream.get('bit_rate', 0))
                        break
                
                if not info.is_valid:
                    info.error_message = "No video stream found"
            else:
                info.error_message = result.stderr[:200] if result.stderr else "ffprobe failed"
                
        except subprocess.TimeoutExpired:
            info.error_message = "Connection timeout"
        except FileNotFoundError:
            # ffprobe non disponible, faire un test basique
            info = self._test_rtsp_basic(url, info)
        except Exception as e:
            info.error_message = str(e)[:200]
        
        return info
    
    def _test_rtsp_basic(self, url: str, info: RTSPStreamInfo) -> RTSPStreamInfo:
        """Test RTSP basique sans ffprobe (via DESCRIBE)"""
        try:
            parsed = urlparse(url)
            ip = parsed.hostname
            port = parsed.port or 554
            
            # Construire la requête DESCRIBE
            path = parsed.path or "/"
            if parsed.query:
                path += f"?{parsed.query}"
            
            describe_request = (
                f"DESCRIBE rtsp://{ip}:{port}{path} RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"Accept: application/sdp\r\n"
            )
            
            # Ajouter l'auth si présente
            if parsed.username:
                import base64
                credentials = f"{parsed.username}:{parsed.password or ''}"
                auth_b64 = base64.b64encode(credentials.encode()).decode()
                describe_request += f"Authorization: Basic {auth_b64}\r\n"
            
            describe_request += "\r\n"
            
            # Envoyer la requête
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((ip, port))
            sock.send(describe_request.encode())
            
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            sock.close()
            
            # Analyser la réponse
            if "RTSP/1.0 200" in response:
                info.is_valid = True
                
                # Essayer d'extraire la résolution depuis SDP
                width_match = re.search(r'a=framesize:\d+\s+(\d+)-(\d+)', response)
                if width_match:
                    info.width = int(width_match.group(1))
                    info.height = int(width_match.group(2))
                
                # Codec
                if 'H264' in response.upper() or 'h264' in response:
                    info.codec = 'h264'
                elif 'H265' in response.upper() or 'HEVC' in response.upper():
                    info.codec = 'h265'
                    
            elif "401" in response:
                info.error_message = "Authentication required"
            elif "404" in response:
                info.error_message = "Stream not found"
            else:
                # Extraire le code d'erreur
                match = re.search(r'RTSP/1\.0 (\d+)', response)
                if match:
                    info.error_message = f"RTSP error {match.group(1)}"
                else:
                    info.error_message = "Invalid RTSP response"
                    
        except socket.timeout:
            info.error_message = "Connection timeout"
        except ConnectionRefusedError:
            info.error_message = "Connection refused"
        except Exception as e:
            info.error_message = str(e)[:100]
        
        return info
    
    def auto_discover_stream(self, ip: str, username: str = "", 
                             password: str = "", 
                             manufacturer: str = "") -> Optional[RTSPStreamInfo]:
        """
        Découvre automatiquement le flux RTSP d'une caméra
        
        Args:
            ip: Adresse IP de la caméra
            username: Nom d'utilisateur
            password: Mot de passe
            manufacturer: Fabricant (optionnel, pour optimiser la recherche)
        
        Returns:
            RTSPStreamInfo du premier flux valide trouvé
        """
        # Déterminer les paths à tester
        paths_to_try = []
        
        # Si le fabricant est connu, commencer par ses paths
        if manufacturer:
            manufacturer_lower = manufacturer.lower()
            if manufacturer_lower in self.RTSP_PATHS:
                paths_to_try.extend(self.RTSP_PATHS[manufacturer_lower])
        
        # Ajouter les paths génériques
        paths_to_try.extend(self.RTSP_PATHS["generic"])
        
        # Dédupliquer en gardant l'ordre
        seen = set()
        paths_to_try = [p for p in paths_to_try if not (p in seen or seen.add(p))]
        
        # Tester les ports
        for port in self.RTSP_PORTS:
            # Test socket rapide d'abord
            socket_ok, _ = self.test_rtsp_socket(ip, port)
            if not socket_ok:
                continue
            
            logger.info(f"Port {port} ouvert sur {ip}, test des streams...")
            
            # Tester chaque path
            for path in paths_to_try:
                url = self.build_rtsp_url(ip, port, path, username, password)
                logger.debug(f"Test: {url}")
                
                info = self.test_rtsp_url(url)
                if info.is_valid:
                    logger.info(f"Stream valide trouvé: {url}")
                    return info
        
        logger.warning(f"Aucun stream RTSP trouvé pour {ip}")
        return None
    
    def get_snapshot(self, url: str, output_path: str) -> bool:
        """
        Capture une image depuis un flux RTSP
        
        Args:
            url: URL RTSP
            output_path: Chemin du fichier image de sortie
        
        Returns:
            True si succès
        """
        try:
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-y",  # Overwrite
                    "-rtsp_transport", "tcp",
                    "-i", url,
                    "-frames:v", "1",
                    "-q:v", "2",
                    output_path
                ],
                capture_output=True,
                timeout=10
            )
            
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f"Erreur capture snapshot: {e}")
            return False
    
    async def test_rtsp_url_async(self, url: str) -> RTSPStreamInfo:
        """Version asynchrone du test RTSP"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.test_rtsp_url(url))
    
    async def auto_discover_stream_async(self, ip: str, username: str = "",
                                          password: str = "",
                                          manufacturer: str = "") -> Optional[RTSPStreamInfo]:
        """Version asynchrone de la découverte automatique"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.auto_discover_stream(ip, username, password, manufacturer)
        )


# Test rapide
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    tester = RTSPTester(timeout=5.0)
    
    # Test avec une IP fictive
    test_ip = "192.168.1.64"
    
    print(f"🔍 Test de connexion RTSP pour {test_ip}...")
    print()
    
    # Test socket
    socket_ok, response_time = tester.test_rtsp_socket(test_ip, 554)
    print(f"Socket test (port 554): {'✅ OK' if socket_ok else '❌ Failed'}")
    if socket_ok:
        print(f"  Response time: {response_time:.1f}ms")
    print()
    
    # Test auto-discover
    print("🔍 Auto-découverte du stream...")
    stream = tester.auto_discover_stream(test_ip, "admin", "password")
    
    if stream and stream.is_valid:
        print(f"\n✅ Stream trouvé!")
        print(f"  URL: {stream.url}")
        print(f"  Résolution: {stream.resolution}")
        print(f"  Codec: {stream.codec}")
        print(f"  FPS: {stream.fps}")
    else:
        print(f"\n❌ Aucun stream trouvé")
        if stream:
            print(f"  Erreur: {stream.error_message}")
