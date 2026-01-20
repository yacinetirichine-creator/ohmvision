"""
OhmVision - Multi-Channel Connection Manager
Gère tous les types de connexion : RTSP, HTTP, WebRTC, Cloud APIs, etc.
"""

import asyncio
import logging
from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
import cv2
import numpy as np

from services.camera_profiles import get_profile, auto_detect_stream_urls

logger = logging.getLogger(__name__)


@dataclass
class ConnectionTest:
    """Résultat d'un test de connexion"""
    success: bool
    connection_type: str
    url: str
    response_time_ms: float
    resolution: Optional[Tuple[int, int]] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class MultiChannelConnector:
    """
    Gestionnaire de connexions multi-canal
    Supporte : RTSP, RTMP, HTTP/MJPEG, HTTPS, WebRTC, HLS, Cloud APIs
    """
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    # =========================================================================
    # TEST RTSP
    # =========================================================================
    
    async def test_rtsp_connection(self, url: str) -> ConnectionTest:
        """
        Teste une connexion RTSP
        """
        start_time = datetime.now()
        
        try:
            # Utiliser OpenCV pour tester RTSP
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
            
            if not cap.isOpened():
                return ConnectionTest(
                    success=False,
                    connection_type="rtsp",
                    url=url,
                    response_time_ms=0,
                    error_message="Cannot open RTSP stream"
                )
            
            # Lire une frame pour vérifier
            ret, frame = cap.read()
            
            if not ret or frame is None:
                cap.release()
                return ConnectionTest(
                    success=False,
                    connection_type="rtsp",
                    url=url,
                    response_time_ms=0,
                    error_message="Cannot read frame from stream"
                )
            
            # Récupérer les propriétés
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            cap.release()
            
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            return ConnectionTest(
                success=True,
                connection_type="rtsp",
                url=url,
                response_time_ms=elapsed,
                resolution=(width, height),
                fps=fps if fps > 0 else None,
                codec="h264"  # Most common
            )
            
        except Exception as e:
            logger.error(f"RTSP test error for {url}: {e}")
            return ConnectionTest(
                success=False,
                connection_type="rtsp",
                url=url,
                response_time_ms=0,
                error_message=str(e)
            )
    
    # =========================================================================
    # TEST HTTP/MJPEG
    # =========================================================================
    
    async def test_http_mjpeg(self, url: str, username: str = "", 
                             password: str = "") -> ConnectionTest:
        """
        Teste une connexion HTTP MJPEG
        """
        start_time = datetime.now()
        
        try:
            auth = None
            if username:
                auth = aiohttp.BasicAuth(username, password)
            
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            async with self._session.get(
                url, 
                auth=auth, 
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                
                if response.status != 200:
                    return ConnectionTest(
                        success=False,
                        connection_type="http_mjpeg",
                        url=url,
                        response_time_ms=0,
                        error_message=f"HTTP {response.status}"
                    )
                
                # Lire quelques bytes pour vérifier le format MJPEG
                chunk = await response.content.read(512)
                
                if b'--' not in chunk or b'Content-Type' not in chunk:
                    return ConnectionTest(
                        success=False,
                        connection_type="http_mjpeg",
                        url=url,
                        response_time_ms=0,
                        error_message="Not a valid MJPEG stream"
                    )
                
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                
                return ConnectionTest(
                    success=True,
                    connection_type="http_mjpeg",
                    url=url,
                    response_time_ms=elapsed,
                    codec="mjpeg"
                )
        
        except Exception as e:
            logger.error(f"HTTP MJPEG test error for {url}: {e}")
            return ConnectionTest(
                success=False,
                connection_type="http_mjpeg",
                url=url,
                response_time_ms=0,
                error_message=str(e)
            )
    
    # =========================================================================
    # TEST SNAPSHOT
    # =========================================================================
    
    async def test_snapshot(self, url: str, username: str = "", 
                           password: str = "") -> ConnectionTest:
        """
        Teste une URL de snapshot
        """
        start_time = datetime.now()
        
        try:
            auth = None
            if username:
                auth = aiohttp.BasicAuth(username, password)
            
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            async with self._session.get(
                url,
                auth=auth,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                
                if response.status != 200:
                    return ConnectionTest(
                        success=False,
                        connection_type="snapshot",
                        url=url,
                        response_time_ms=0,
                        error_message=f"HTTP {response.status}"
                    )
                
                # Vérifier que c'est une image
                content_type = response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    return ConnectionTest(
                        success=False,
                        connection_type="snapshot",
                        url=url,
                        response_time_ms=0,
                        error_message=f"Not an image: {content_type}"
                    )
                
                # Lire l'image pour vérifier la résolution
                image_data = await response.read()
                
                # Décoder avec OpenCV
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    return ConnectionTest(
                        success=False,
                        connection_type="snapshot",
                        url=url,
                        response_time_ms=0,
                        error_message="Cannot decode image"
                    )
                
                height, width = img.shape[:2]
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                
                return ConnectionTest(
                    success=True,
                    connection_type="snapshot",
                    url=url,
                    response_time_ms=elapsed,
                    resolution=(width, height)
                )
        
        except Exception as e:
            logger.error(f"Snapshot test error for {url}: {e}")
            return ConnectionTest(
                success=False,
                connection_type="snapshot",
                url=url,
                response_time_ms=0,
                error_message=str(e)
            )
    
    # =========================================================================
    # AUTO-DETECTION INTELLIGENTE
    # =========================================================================
    
    async def auto_detect_best_connection(
        self,
        ip: str,
        username: str,
        password: str,
        manufacturer: Optional[str] = None
    ) -> Tuple[Optional[ConnectionTest], List[ConnectionTest]]:
        """
        Détecte automatiquement la meilleure méthode de connexion
        
        Returns:
            (meilleure_connexion, tous_les_tests)
        """
        # Récupérer les URLs possibles
        urls = auto_detect_stream_urls(ip, username, password, manufacturer)
        
        all_tests = []
        
        # Tester RTSP en priorité
        for rtsp_url in urls.get("rtsp", []):
            result = await self.test_rtsp_connection(rtsp_url)
            all_tests.append(result)
            
            if result.success:
                logger.info(f"✓ RTSP connection successful: {rtsp_url}")
                return result, all_tests
            
            # Petit délai entre les tests
            await asyncio.sleep(0.5)
        
        # Si RTSP échoue, tester HTTP MJPEG
        for http_url in urls.get("http", []):
            result = await self.test_http_mjpeg(http_url, username, password)
            all_tests.append(result)
            
            if result.success:
                logger.info(f"✓ HTTP MJPEG connection successful: {http_url}")
                return result, all_tests
            
            await asyncio.sleep(0.5)
        
        # Tester au moins le snapshot
        for snap_url in urls.get("snapshot", []):
            result = await self.test_snapshot(snap_url, username, password)
            all_tests.append(result)
            
            if result.success:
                logger.info(f"✓ Snapshot URL successful: {snap_url}")
                # On continue car snapshot seul n'est pas idéal
            
            await asyncio.sleep(0.5)
        
        # Aucune connexion réussie
        logger.warning(f"No successful connection found for {ip}")
        return None, all_tests
    
    # =========================================================================
    # CONNECTION HEALTH CHECK
    # =========================================================================
    
    async def check_health(self, url: str, connection_type: str) -> Dict[str, Any]:
        """
        Vérifie la santé d'une connexion existante
        """
        if connection_type == "rtsp":
            result = await self.test_rtsp_connection(url)
        elif connection_type == "http_mjpeg":
            result = await self.test_http_mjpeg(url)
        else:
            return {"status": "unknown", "error": "Unknown connection type"}
        
        if result.success:
            # Déterminer le niveau de santé basé sur le temps de réponse
            if result.response_time_ms < 500:
                health = "excellent"
            elif result.response_time_ms < 1500:
                health = "good"
            elif result.response_time_ms < 3000:
                health = "fair"
            else:
                health = "poor"
            
            return {
                "status": "online",
                "health": health,
                "response_time_ms": result.response_time_ms,
                "resolution": result.resolution,
                "fps": result.fps
            }
        else:
            return {
                "status": "offline",
                "health": "offline",
                "error": result.error_message
            }


class ReconnectionManager:
    """
    Gère la reconnexion automatique avec backoff exponentiel
    """
    
    def __init__(
        self,
        max_attempts: int = 5,
        initial_delay: float = 5.0,
        max_delay: float = 300.0,
        backoff_factor: float = 2.0
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self._attempts: Dict[int, int] = {}  # camera_id -> attempt_count
        self._last_attempt: Dict[int, datetime] = {}  # camera_id -> last_attempt_time
    
    def get_delay(self, camera_id: int) -> float:
        """Calcule le délai avant la prochaine tentative"""
        attempts = self._attempts.get(camera_id, 0)
        delay = min(
            self.initial_delay * (self.backoff_factor ** attempts),
            self.max_delay
        )
        return delay
    
    def should_retry(self, camera_id: int) -> bool:
        """Détermine si une reconnexion doit être tentée"""
        attempts = self._attempts.get(camera_id, 0)
        
        if attempts >= self.max_attempts:
            return False
        
        last_attempt = self._last_attempt.get(camera_id)
        if last_attempt:
            delay = self.get_delay(camera_id)
            if (datetime.now() - last_attempt).total_seconds() < delay:
                return False
        
        return True
    
    def record_attempt(self, camera_id: int, success: bool):
        """Enregistre une tentative de connexion"""
        if success:
            # Réinitialiser les compteurs
            self._attempts[camera_id] = 0
            self._last_attempt.pop(camera_id, None)
        else:
            # Incrémenter le compteur
            self._attempts[camera_id] = self._attempts.get(camera_id, 0) + 1
            self._last_attempt[camera_id] = datetime.now()
    
    def reset(self, camera_id: int):
        """Réinitialise les compteurs pour une caméra"""
        self._attempts.pop(camera_id, None)
        self._last_attempt.pop(camera_id, None)
    
    def get_status(self, camera_id: int) -> Dict[str, Any]:
        """Récupère le statut de reconnexion"""
        return {
            "attempts": self._attempts.get(camera_id, 0),
            "max_attempts": self.max_attempts,
            "last_attempt": self._last_attempt.get(camera_id),
            "next_retry_in_seconds": self.get_delay(camera_id) if camera_id in self._last_attempt else 0
        }


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

async def test_camera_connectivity(
    ip: str,
    username: str = "admin",
    password: str = "",
    manufacturer: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fonction wrapper pour tester la connectivité d'une caméra
    """
    async with MultiChannelConnector() as connector:
        best_connection, all_tests = await connector.auto_detect_best_connection(
            ip, username, password, manufacturer
        )
        
        return {
            "success": best_connection is not None,
            "best_connection": best_connection.__dict__ if best_connection else None,
            "all_tests": [test.__dict__ for test in all_tests],
            "recommended_type": best_connection.connection_type if best_connection else None,
            "recommended_url": best_connection.url if best_connection else None
        }


async def batch_test_cameras(cameras: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Teste plusieurs caméras en parallèle
    
    Args:
        cameras: Liste de dicts avec keys: ip, username, password, manufacturer
    """
    async with MultiChannelConnector() as connector:
        tasks = [
            connector.auto_detect_best_connection(
                cam["ip"],
                cam.get("username", "admin"),
                cam.get("password", ""),
                cam.get("manufacturer")
            )
            for cam in cameras
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            {
                "camera": cameras[i],
                "success": not isinstance(results[i], Exception) and results[i][0] is not None,
                "best_connection": results[i][0].__dict__ if not isinstance(results[i], Exception) and results[i][0] else None,
                "error": str(results[i]) if isinstance(results[i], Exception) else None
            }
            for i in range(len(cameras))
        ]
