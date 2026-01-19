"""
OhmVision - ONVIF Scanner
Discovers ONVIF-compliant cameras using WS-Discovery
"""

import socket
import uuid
import re
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass
from xml.etree import ElementTree as ET
import logging
import urllib.request
import urllib.parse
from datetime import datetime
import hashlib
import base64
import os

logger = logging.getLogger(__name__)


@dataclass
class ONVIFCamera:
    """Représente une caméra ONVIF découverte"""
    ip: str
    port: int = 80
    name: str = ""
    manufacturer: str = ""
    model: str = ""
    firmware: str = ""
    hardware_id: str = ""
    xaddr: str = ""  # Service address
    scopes: List[str] = None
    rtsp_port: int = 554
    profiles: List[Dict] = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = []
        if self.profiles is None:
            self.profiles = []
    
    @property
    def rtsp_url(self) -> str:
        """Génère une URL RTSP de base (sans auth)"""
        return f"rtsp://{self.ip}:{self.rtsp_port}/stream1"
    
    def get_rtsp_url(self, username: str = "", password: str = "", 
                     profile: str = "main") -> str:
        """Génère une URL RTSP avec authentification"""
        auth = ""
        if username:
            auth = f"{username}:{password}@" if password else f"{username}@"
        
        # URLs communes par fabricant
        paths = {
            "Hikvision": f"/Streaming/Channels/101",
            "Dahua": f"/cam/realmonitor?channel=1&subtype=0",
            "Axis": f"/axis-media/media.amp",
            "default": f"/stream1"
        }
        
        path = paths.get(self.manufacturer, paths["default"])
        return f"rtsp://{auth}{self.ip}:{self.rtsp_port}{path}"


class ONVIFScanner:
    """Scanner ONVIF utilisant WS-Discovery"""
    
    # WS-Discovery message template
    WS_DISCOVERY_PROBE = """<?xml version="1.0" encoding="UTF-8"?>
<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
    xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
    xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
    xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
    <e:Header>
        <w:MessageID>uuid:{message_id}</w:MessageID>
        <w:To e:mustUnderstand="true">urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
        <w:Action e:mustUnderstand="true">http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action>
    </e:Header>
    <e:Body>
        <d:Probe>
            <d:Types>dn:NetworkVideoTransmitter</d:Types>
        </d:Probe>
    </e:Body>
</e:Envelope>"""

    WS_DISCOVERY_MULTICAST_IP = "239.255.255.250"
    WS_DISCOVERY_PORT = 3702
    
    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
    
    def discover(self) -> List[ONVIFCamera]:
        """
        Découvre les caméras ONVIF sur le réseau via WS-Discovery
        
        Returns:
            Liste des caméras ONVIF trouvées
        """
        cameras = []
        
        # Générer un ID unique pour le message
        message_id = str(uuid.uuid4())
        probe_message = self.WS_DISCOVERY_PROBE.format(message_id=message_id)
        
        try:
            # Créer le socket multicast
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(self.timeout)
            
            # Bind sur toutes les interfaces
            sock.bind(('', 0))
            
            # Envoyer le probe
            sock.sendto(
                probe_message.encode('utf-8'),
                (self.WS_DISCOVERY_MULTICAST_IP, self.WS_DISCOVERY_PORT)
            )
            
            logger.info("WS-Discovery probe envoyé, attente des réponses...")
            
            # Collecter les réponses
            found_ips = set()
            while True:
                try:
                    data, addr = sock.recvfrom(65535)
                    ip = addr[0]
                    
                    # Éviter les doublons
                    if ip in found_ips:
                        continue
                    found_ips.add(ip)
                    
                    # Parser la réponse
                    camera = self._parse_probe_response(data.decode('utf-8'), ip)
                    if camera:
                        cameras.append(camera)
                        logger.info(f"Caméra ONVIF trouvée: {camera.ip} "
                                   f"({camera.manufacturer} {camera.model})")
                        
                except socket.timeout:
                    break
                except Exception as e:
                    logger.debug(f"Erreur parsing réponse: {e}")
                    continue
            
            sock.close()
            
        except Exception as e:
            logger.error(f"Erreur WS-Discovery: {e}")
        
        logger.info(f"Découverte ONVIF terminée: {len(cameras)} caméra(s)")
        return cameras
    
    def _parse_probe_response(self, xml_data: str, ip: str) -> Optional[ONVIFCamera]:
        """Parse la réponse WS-Discovery"""
        try:
            # Nettoyer les namespaces pour simplifier le parsing
            xml_data = re.sub(r'xmlns[^=]*="[^"]*"', '', xml_data)
            xml_data = re.sub(r'<[a-zA-Z]+:', '<', xml_data)
            xml_data = re.sub(r'</[a-zA-Z]+:', '</', xml_data)
            
            root = ET.fromstring(xml_data)
            
            # Extraire XAddrs (adresses de service)
            xaddr = ""
            xaddrs_elem = root.find('.//XAddrs')
            if xaddrs_elem is not None and xaddrs_elem.text:
                xaddr = xaddrs_elem.text.split()[0]  # Premier URL
            
            # Extraire les scopes
            scopes = []
            scopes_elem = root.find('.//Scopes')
            if scopes_elem is not None and scopes_elem.text:
                scopes = scopes_elem.text.split()
            
            # Parser les scopes pour extraire les infos
            manufacturer = ""
            model = ""
            name = ""
            hardware_id = ""
            
            for scope in scopes:
                scope_lower = scope.lower()
                if '/name/' in scope_lower:
                    name = urllib.parse.unquote(scope.split('/name/')[-1])
                elif '/hardware/' in scope_lower:
                    hardware_id = scope.split('/hardware/')[-1]
                elif '/location/' in scope_lower:
                    pass  # Location info
                elif 'onvif.org/type/' in scope_lower:
                    pass  # Type info
                else:
                    # Essayer d'extraire manufacturer/model des autres scopes
                    parts = scope.split('/')
                    for i, part in enumerate(parts):
                        if part.lower() in ['hikvision', 'dahua', 'axis', 'bosch', 
                                           'panasonic', 'samsung', 'sony', 'vivotek',
                                           'hanwha', 'uniview', 'reolink']:
                            manufacturer = part
                        elif 'model' in part.lower() and i + 1 < len(parts):
                            model = parts[i + 1]
            
            # Extraire le port depuis xaddr
            port = 80
            if xaddr:
                match = re.search(r':(\d+)/', xaddr)
                if match:
                    port = int(match.group(1))
            
            return ONVIFCamera(
                ip=ip,
                port=port,
                name=name or f"Camera-{ip}",
                manufacturer=manufacturer,
                model=model,
                hardware_id=hardware_id,
                xaddr=xaddr,
                scopes=scopes
            )
            
        except Exception as e:
            logger.debug(f"Erreur parsing XML pour {ip}: {e}")
            return ONVIFCamera(ip=ip, name=f"Camera-{ip}")
    
    def get_device_info(self, ip: str, port: int = 80,
                        username: str = "", password: str = "") -> Optional[ONVIFCamera]:
        """
        Récupère les informations détaillées d'une caméra ONVIF
        
        Args:
            ip: Adresse IP de la caméra
            port: Port ONVIF (généralement 80)
            username: Nom d'utilisateur
            password: Mot de passe
        
        Returns:
            ONVIFCamera avec les informations complètes
        """
        device_service_url = f"http://{ip}:{port}/onvif/device_service"
        
        # Message SOAP pour GetDeviceInformation
        soap_body = """<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
    {security_header}
    <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>
    </s:Body>
</s:Envelope>"""
        
        # Ajouter l'authentification si nécessaire
        security_header = ""
        if username and password:
            security_header = self._create_security_header(username, password)
        
        soap_message = soap_body.format(security_header=security_header)
        
        try:
            req = urllib.request.Request(
                device_service_url,
                data=soap_message.encode('utf-8'),
                headers={
                    'Content-Type': 'application/soap+xml; charset=utf-8',
                    'SOAPAction': '"http://www.onvif.org/ver10/device/wsdl/GetDeviceInformation"'
                }
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read().decode('utf-8')
                return self._parse_device_info(xml_data, ip, port)
                
        except urllib.error.HTTPError as e:
            if e.code == 401:
                logger.warning(f"Authentification requise pour {ip}")
            else:
                logger.error(f"Erreur HTTP {e.code} pour {ip}")
        except Exception as e:
            logger.error(f"Erreur GetDeviceInformation pour {ip}: {e}")
        
        return None
    
    def _create_security_header(self, username: str, password: str) -> str:
        """Crée le header WS-Security pour l'authentification ONVIF"""
        # Générer nonce et timestamp
        nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
        created = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        # Calculer le digest du password
        nonce_bytes = base64.b64decode(nonce)
        created_bytes = created.encode('utf-8')
        password_bytes = password.encode('utf-8')
        
        digest_input = nonce_bytes + created_bytes + password_bytes
        password_digest = base64.b64encode(
            hashlib.sha1(digest_input).digest()
        ).decode('utf-8')
        
        return f"""<s:Header>
    <Security xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <UsernameToken>
            <Username>{username}</Username>
            <Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">{password_digest}</Password>
            <Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">{nonce}</Nonce>
            <Created xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">{created}</Created>
        </UsernameToken>
    </Security>
</s:Header>"""
    
    def _parse_device_info(self, xml_data: str, ip: str, port: int) -> Optional[ONVIFCamera]:
        """Parse la réponse GetDeviceInformation"""
        try:
            # Nettoyer les namespaces
            xml_data = re.sub(r'xmlns[^=]*="[^"]*"', '', xml_data)
            xml_data = re.sub(r'<[a-zA-Z]+:', '<', xml_data)
            xml_data = re.sub(r'</[a-zA-Z]+:', '</', xml_data)
            
            root = ET.fromstring(xml_data)
            
            # Trouver GetDeviceInformationResponse
            response = root.find('.//GetDeviceInformationResponse')
            if response is None:
                return None
            
            def get_text(elem_name):
                elem = response.find(f'.//{elem_name}')
                return elem.text if elem is not None and elem.text else ""
            
            return ONVIFCamera(
                ip=ip,
                port=port,
                manufacturer=get_text('Manufacturer'),
                model=get_text('Model'),
                firmware=get_text('FirmwareVersion'),
                hardware_id=get_text('HardwareId'),
                name=f"{get_text('Manufacturer')} {get_text('Model')}"
            )
            
        except Exception as e:
            logger.error(f"Erreur parsing DeviceInfo: {e}")
            return None
    
    async def discover_async(self) -> List[ONVIFCamera]:
        """Version asynchrone de la découverte"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.discover)


# Test rapide
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scanner = ONVIFScanner(timeout=5.0)
    
    print("🔍 Recherche de caméras ONVIF...")
    print()
    
    cameras = scanner.discover()
    
    if cameras:
        print(f"\n✅ {len(cameras)} caméra(s) ONVIF trouvée(s):\n")
        for cam in cameras:
            print(f"  📹 {cam.ip}:{cam.port}")
            print(f"     Nom: {cam.name}")
            if cam.manufacturer:
                print(f"     Fabricant: {cam.manufacturer}")
            if cam.model:
                print(f"     Modèle: {cam.model}")
            print(f"     RTSP: {cam.rtsp_url}")
            print()
    else:
        print("\n❌ Aucune caméra ONVIF trouvée")
        print("   Vérifiez que vos caméras sont allumées et sur le même réseau")
