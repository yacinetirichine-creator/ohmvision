"""
OhmVision - Network Scanner
Scans the local network to find potential IP cameras
"""

import socket
import asyncio
import ipaddress
import subprocess
import platform
from typing import List, Dict, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


@dataclass
class NetworkDevice:
    """Représente un appareil trouvé sur le réseau"""
    ip: str
    hostname: Optional[str] = None
    mac: Optional[str] = None
    open_ports: List[int] = None
    device_type: str = "unknown"  # camera, nvr, unknown
    manufacturer: Optional[str] = None
    
    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []


class NetworkScanner:
    """Scanner réseau pour découvrir les caméras IP"""
    
    # Ports communs pour les caméras IP
    CAMERA_PORTS = [
        80,    # HTTP
        443,   # HTTPS
        554,   # RTSP
        8080,  # HTTP alt
        8554,  # RTSP alt
        8000,  # Hikvision
        8899,  # Dahua
        37777, # Dahua
        34567, # Generic Chinese cams
    ]
    
    # Préfixes MAC des fabricants de caméras connus
    MAC_PREFIXES = {
        "00:40:8c": "Axis",
        "00:1a:07": "Arecont Vision",
        "00:80:f0": "Panasonic",
        "28:57:be": "Hikvision",
        "c0:56:e3": "Hikvision",
        "54:c4:15": "Hikvision",
        "44:19:b6": "Hikvision",
        "c4:2f:90": "Dahua",
        "3c:ef:8c": "Dahua",
        "a0:bd:1d": "Dahua",
        "e0:50:8b": "Dahua",
        "90:02:a9": "Dahua",
        "00:18:ae": "TVT",
        "00:12:17": "Cisco/Linksys",
        "00:62:6e": "Vivotek",
        "00:0f:7c": "ACTi",
        "00:30:53": "Basler",
        "00:04:7d": "Pelco",
        "00:19:c7": "Cambridge Industries",
        "00:11:22": "FLIR",
        "a4:5e:60": "Apple (iPhone pour test)",
    }
    
    def __init__(self, timeout: float = 0.5, max_workers: int = 100):
        self.timeout = timeout
        self.max_workers = max_workers
    
    def get_local_network(self) -> Optional[str]:
        """Détecte le réseau local (ex: 192.168.1.0/24)"""
        try:
            # Créer un socket pour trouver l'IP locale
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Construire le réseau /24
            ip_parts = local_ip.split('.')
            network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            
            logger.info(f"Réseau local détecté: {network} (IP locale: {local_ip})")
            return network
            
        except Exception as e:
            logger.error(f"Erreur détection réseau: {e}")
            return None
    
    def get_local_ip(self) -> Optional[str]:
        """Retourne l'IP locale"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return None
    
    def _check_port(self, ip: str, port: int) -> bool:
        """Vérifie si un port est ouvert sur une IP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _scan_ip(self, ip: str) -> Optional[NetworkDevice]:
        """Scanne une IP pour trouver les ports ouverts"""
        open_ports = []
        
        # Vérifier d'abord si l'hôte répond
        # Quick check sur le port 554 (RTSP) ou 80 (HTTP)
        quick_ports = [554, 80, 8080]
        has_response = False
        
        for port in quick_ports:
            if self._check_port(ip, port):
                has_response = True
                open_ports.append(port)
                break
        
        if not has_response:
            return None
        
        # Scanner tous les ports caméra
        for port in self.CAMERA_PORTS:
            if port not in open_ports and self._check_port(ip, port):
                open_ports.append(port)
        
        if not open_ports:
            return None
        
        # Déterminer le type d'appareil
        device_type = "unknown"
        if 554 in open_ports or 8554 in open_ports:
            device_type = "camera"
        elif 37777 in open_ports or 8000 in open_ports:
            device_type = "nvr"
        
        # Essayer de récupérer le hostname
        hostname = None
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            pass
        
        # Essayer de récupérer l'adresse MAC et identifier le fabricant
        mac = self._get_mac_address(ip)
        manufacturer = self._identify_manufacturer(mac) if mac else None
        
        return NetworkDevice(
            ip=ip,
            hostname=hostname,
            mac=mac,
            open_ports=sorted(open_ports),
            device_type=device_type,
            manufacturer=manufacturer
        )
    
    def _get_mac_address(self, ip: str) -> Optional[str]:
        """Récupère l'adresse MAC d'une IP via ARP"""
        try:
            if platform.system() == "Windows":
                # Windows: arp -a
                output = subprocess.check_output(["arp", "-a", ip], 
                                                  stderr=subprocess.DEVNULL,
                                                  timeout=2).decode()
                # Parser la sortie Windows
                for line in output.split('\n'):
                    if ip in line:
                        parts = line.split()
                        for part in parts:
                            if '-' in part and len(part) == 17:
                                return part.replace('-', ':').lower()
            else:
                # Linux/Mac: arp -n ou ip neigh
                try:
                    output = subprocess.check_output(["arp", "-n", ip],
                                                      stderr=subprocess.DEVNULL,
                                                      timeout=2).decode()
                    for line in output.split('\n'):
                        if ip in line:
                            parts = line.split()
                            for part in parts:
                                if ':' in part and len(part) == 17:
                                    return part.lower()
                except:
                    # Essayer ip neigh sur Linux
                    output = subprocess.check_output(["ip", "neigh", "show", ip],
                                                      stderr=subprocess.DEVNULL,
                                                      timeout=2).decode()
                    parts = output.split()
                    for i, part in enumerate(parts):
                        if part == "lladdr" and i + 1 < len(parts):
                            return parts[i + 1].lower()
        except:
            pass
        return None
    
    def _identify_manufacturer(self, mac: str) -> Optional[str]:
        """Identifie le fabricant à partir de l'adresse MAC"""
        if not mac:
            return None
        
        mac_prefix = mac[:8].lower()
        return self.MAC_PREFIXES.get(mac_prefix)
    
    def scan_network(self, network: str = None, 
                     progress_callback=None) -> List[NetworkDevice]:
        """
        Scanne le réseau pour trouver les caméras
        
        Args:
            network: Réseau à scanner (ex: "192.168.1.0/24")
            progress_callback: Fonction appelée avec (current, total, ip)
        
        Returns:
            Liste des appareils trouvés
        """
        if network is None:
            network = self.get_local_network()
            if network is None:
                logger.error("Impossible de détecter le réseau local")
                return []
        
        try:
            net = ipaddress.ip_network(network, strict=False)
            hosts = list(net.hosts())
        except ValueError as e:
            logger.error(f"Réseau invalide: {e}")
            return []
        
        total = len(hosts)
        devices = []
        
        logger.info(f"Scan de {total} adresses IP sur {network}...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._scan_ip, str(ip)): str(ip) 
                for ip in hosts
            }
            
            for i, future in enumerate(futures):
                ip = futures[future]
                
                if progress_callback:
                    progress_callback(i + 1, total, ip)
                
                try:
                    result = future.result(timeout=self.timeout * 2)
                    if result:
                        devices.append(result)
                        logger.info(f"Appareil trouvé: {result.ip} "
                                   f"(ports: {result.open_ports}, "
                                   f"type: {result.device_type})")
                except:
                    pass
        
        # Trier par IP
        devices.sort(key=lambda d: [int(p) for p in d.ip.split('.')])
        
        logger.info(f"Scan terminé: {len(devices)} appareils trouvés")
        return devices
    
    async def scan_network_async(self, network: str = None,
                                  progress_callback=None) -> List[NetworkDevice]:
        """Version asynchrone du scan réseau"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.scan_network(network, progress_callback)
        )


# Test rapide
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scanner = NetworkScanner(timeout=0.3, max_workers=50)
    
    print("🔍 Scan du réseau local...")
    print(f"IP locale: {scanner.get_local_ip()}")
    print(f"Réseau: {scanner.get_local_network()}")
    print()
    
    def progress(current, total, ip):
        percent = (current / total) * 100
        print(f"\r[{'=' * int(percent/5)}{' ' * (20-int(percent/5))}] "
              f"{percent:.1f}% - {ip}", end='', flush=True)
    
    devices = scanner.scan_network(progress_callback=progress)
    print("\n")
    
    if devices:
        print(f"✅ {len(devices)} appareil(s) trouvé(s):\n")
        for device in devices:
            print(f"  📹 {device.ip}")
            print(f"     Ports: {device.open_ports}")
            print(f"     Type: {device.device_type}")
            if device.manufacturer:
                print(f"     Fabricant: {device.manufacturer}")
            if device.hostname:
                print(f"     Hostname: {device.hostname}")
            print()
    else:
        print("❌ Aucun appareil trouvé")
