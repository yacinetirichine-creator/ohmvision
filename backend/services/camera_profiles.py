"""
OhmVision - Camera Manufacturer Profiles
Templates et configurations pour tous les fabricants majeurs
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class StreamProfile:
    """Profil de stream pour un fabricant"""
    name: str
    path: str
    port: int
    description: str


class CameraProfile:
    """Profil de configuration pour un fabricant de caméra"""
    
    def __init__(
        self,
        manufacturer: str,
        default_port: int = 554,
        default_http_port: int = 80,
        default_onvif_port: int = 80,
        default_username: str = "admin",
        default_password: str = "",
        rtsp_templates: List[str] = None,
        http_templates: List[str] = None,
        snapshot_templates: List[str] = None,
        onvif_supported: bool = True,
        capabilities: List[str] = None
    ):
        self.manufacturer = manufacturer
        self.default_port = default_port
        self.default_http_port = default_http_port
        self.default_onvif_port = default_onvif_port
        self.default_username = default_username
        self.default_password = default_password
        self.rtsp_templates = rtsp_templates or []
        self.http_templates = http_templates or []
        self.snapshot_templates = snapshot_templates or []
        self.onvif_supported = onvif_supported
        self.capabilities = capabilities or []
    
    def get_rtsp_url(self, ip: str, username: str, password: str, 
                     channel: int = 1, stream: int = 1) -> List[str]:
        """Génère les URLs RTSP possibles"""
        urls = []
        auth = f"{username}:{password}@" if username else ""
        
        for template in self.rtsp_templates:
            url = template.format(
                auth=auth,
                ip=ip,
                port=self.default_port,
                channel=channel,
                stream=stream
            )
            urls.append(url)
        
        return urls
    
    def get_http_url(self, ip: str, username: str = "", password: str = "") -> List[str]:
        """Génère les URLs HTTP possibles"""
        urls = []
        
        for template in self.http_templates:
            url = template.format(
                ip=ip,
                port=self.default_http_port,
                username=username,
                password=password
            )
            urls.append(url)
        
        return urls
    
    def get_snapshot_url(self, ip: str, username: str = "", password: str = "") -> List[str]:
        """Génère les URLs de snapshot possibles"""
        urls = []
        
        for template in self.snapshot_templates:
            url = template.format(
                ip=ip,
                port=self.default_http_port,
                username=username,
                password=password
            )
            urls.append(url)
        
        return urls


# =============================================================================
# PROFILS PAR FABRICANT
# =============================================================================

CAMERA_PROFILES = {
    
    # HIKVISION - Leader mondial
    "hikvision": CameraProfile(
        manufacturer="Hikvision",
        default_port=554,
        default_http_port=80,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/Streaming/Channels/{channel}01",
            "rtsp://{auth}{ip}:{port}/Streaming/Channels/{channel}02",  # Sub stream
            "rtsp://{auth}{ip}:{port}/h264/ch{channel}/main/av_stream",
            "rtsp://{auth}{ip}:{port}/h264/ch{channel}/sub/av_stream",
        ],
        http_templates=[
            "http://{ip}:{port}/ISAPI/Streaming/channels/{channel}01/httpPreview",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/ISAPI/Streaming/channels/{channel}/picture",
            "http://{ip}:{port}/onvifsnapshot/media_service/snapshot?channel={channel}&subtype=0",
        ],
        onvif_supported=True,
        capabilities=["ptz", "audio", "alarm_io", "smart_events"]
    ),
    
    # DAHUA - 2ème fabricant mondial
    "dahua": CameraProfile(
        manufacturer="Dahua",
        default_port=554,
        default_http_port=80,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0",  # Main
            "rtsp://{auth}{ip}:{port}/cam/realmonitor?channel={channel}&subtype=1",  # Sub
            "rtsp://{auth}{ip}:{port}/live/ch{channel}",
        ],
        http_templates=[
            "http://{ip}:{port}/cgi-bin/mjpg/video.cgi?channel={channel}&subtype=0",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/cgi-bin/snapshot.cgi?channel={channel}",
        ],
        onvif_supported=True,
        capabilities=["ptz", "audio", "alarm_io", "smart_codec"]
    ),
    
    # AXIS - Haute qualité professionnelle
    "axis": CameraProfile(
        manufacturer="Axis",
        default_port=554,
        default_http_port=80,
        default_username="root",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/axis-media/media.amp",
            "rtsp://{auth}{ip}:{port}/axis-media/media.amp?videocodec=h264",
            "rtsp://{auth}{ip}:{port}/axis-media/media.amp?resolution=1920x1080",
        ],
        http_templates=[
            "http://{ip}:{port}/axis-cgi/mjpg/video.cgi",
            "http://{ip}:{port}/mjpg/video.mjpg",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/axis-cgi/jpg/image.cgi",
        ],
        onvif_supported=True,
        capabilities=["ptz", "audio", "analytics", "zipstream"]
    ),
    
    # FOSCAM - Grand public
    "foscam": CameraProfile(
        manufacturer="Foscam",
        default_port=554,
        default_http_port=88,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/videoMain",
            "rtsp://{auth}{ip}:{port}/videoSub",
        ],
        http_templates=[
            "http://{ip}:{port}/cgi-bin/CGIStream.cgi?cmd=GetMJStream&usr={username}&pwd={password}",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr={username}&pwd={password}",
        ],
        onvif_supported=True,
        capabilities=["ptz", "audio"]
    ),
    
    # VIVOTEK - Taiwan manufacturer
    "vivotek": CameraProfile(
        manufacturer="Vivotek",
        default_port=554,
        default_http_port=80,
        default_username="root",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/live.sdp",
            "rtsp://{auth}{ip}:{port}/live/ch00_0",
        ],
        http_templates=[
            "http://{ip}:{port}/video.mjpg",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/cgi-bin/viewer/snapshot.jpg",
        ],
        onvif_supported=True,
        capabilities=["analytics", "audio"]
    ),
    
    # BOSCH - Securite industrielle
    "bosch": CameraProfile(
        manufacturer="Bosch",
        default_port=554,
        default_http_port=80,
        default_username="service",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/rtsp_tunnel",
        ],
        http_templates=[
            "http://{ip}:{port}/snap.jpg",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/snap.jpg?JpegCam={channel}",
        ],
        onvif_supported=True,
        capabilities=["analytics", "intelligent_tracking"]
    ),
    
    # UNIVIEW (UNV) - Concurrent Hikvision
    "uniview": CameraProfile(
        manufacturer="Uniview",
        default_port=554,
        default_http_port=80,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/unicast/c{channel}/s0/live",
            "rtsp://{auth}{ip}:{port}/unicast/c{channel}/s1/live",  # Sub
        ],
        snapshot_templates=[
            "http://{ip}:{port}/cgi-bin/snapshot.cgi?channel={channel}",
        ],
        onvif_supported=True,
        capabilities=["ptz", "smart_ir"]
    ),
    
    # HANWHA (ex-Samsung Techwin)
    "hanwha": CameraProfile(
        manufacturer="Hanwha",
        default_port=554,
        default_http_port=80,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/profile{stream}/media.smp",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/cgi-bin/snapshot.cgi",
        ],
        onvif_supported=True,
        capabilities=["wisenet", "analytics"]
    ),
    
    # REOLINK - Populaire DIY
    "reolink": CameraProfile(
        manufacturer="Reolink",
        default_port=554,
        default_http_port=80,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/h264Preview_01_main",
            "rtsp://{auth}{ip}:{port}/h264Preview_01_sub",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user={username}&password={password}",
        ],
        onvif_supported=True,
        capabilities=["ptz", "audio", "person_vehicle_detection"]
    ),
    
    # TP-LINK
    "tplink": CameraProfile(
        manufacturer="TP-Link",
        default_port=554,
        default_http_port=80,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/stream1",
            "rtsp://{auth}{ip}:{port}/stream2",
        ],
        onvif_supported=True,
        capabilities=["motion_detection", "audio"]
    ),
    
    # XIAOMI
    "xiaomi": CameraProfile(
        manufacturer="Xiaomi",
        default_port=554,
        default_http_port=80,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/live/ch00_0",
        ],
        onvif_supported=False,  # Limité
        capabilities=["cloud", "ai_detection"]
    ),
    
    # GENERIC - Fallback pour caméras génériques
    "generic": CameraProfile(
        manufacturer="Generic",
        default_port=554,
        default_http_port=80,
        default_username="admin",
        rtsp_templates=[
            "rtsp://{auth}{ip}:{port}/stream1",
            "rtsp://{auth}{ip}:{port}/stream",
            "rtsp://{auth}{ip}:{port}/live",
            "rtsp://{auth}{ip}:{port}/",
            "rtsp://{auth}{ip}:{port}/h264",
            "rtsp://{auth}{ip}:{port}/video",
        ],
        http_templates=[
            "http://{ip}:{port}/video.mjpg",
            "http://{ip}:{port}/mjpg/video.mjpg",
        ],
        snapshot_templates=[
            "http://{ip}:{port}/snapshot.jpg",
            "http://{ip}:{port}/snap.jpg",
            "http://{ip}:{port}/image.jpg",
        ],
        onvif_supported=True,
        capabilities=[]
    ),
}


# =============================================================================
# CLOUD CAMERA PROFILES (Nest, Ring, Arlo, Wyze)
# =============================================================================

CLOUD_CAMERA_PROFILES = {
    "nest": {
        "name": "Google Nest",
        "auth_type": "oauth2",
        "api_base": "https://smartdevicemanagement.googleapis.com/v1",
        "requires_sdk": True,
        "capabilities": ["cloud_recording", "alerts", "person_detection"],
        "notes": "Nécessite Google Cloud Project + Device Access"
    },
    
    "ring": {
        "name": "Amazon Ring",
        "auth_type": "oauth2",
        "api_base": "https://api.ring.com/clients_api",
        "requires_sdk": False,
        "capabilities": ["cloud_recording", "motion_alerts", "doorbell"],
        "notes": "API non officielle, peut changer"
    },
    
    "arlo": {
        "name": "Arlo",
        "auth_type": "username_password",
        "api_base": "https://myapi.arlo.com/hmsweb",
        "requires_sdk": False,
        "capabilities": ["cloud_recording", "smart_alerts", "zones"],
        "notes": "API stable, bien documentée"
    },
    
    "wyze": {
        "name": "Wyze",
        "auth_type": "username_password",
        "api_base": "https://api.wyze.com",
        "requires_sdk": False,
        "rtsp_available": True,  # Via firmware RTSP
        "capabilities": ["cloud_recording", "motion_detection", "rtsp_firmware"],
        "notes": "RTSP disponible via firmware alternatif"
    },
}


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_profile(manufacturer: str) -> CameraProfile:
    """Récupère le profil d'un fabricant"""
    manufacturer_lower = manufacturer.lower()
    return CAMERA_PROFILES.get(manufacturer_lower, CAMERA_PROFILES["generic"])


def detect_manufacturer_from_mac(mac: str) -> Optional[str]:
    """Détecte le fabricant depuis l'adresse MAC"""
    # Premiers 6 caractères (OUI - Organizationally Unique Identifier)
    mac_prefix = mac.replace(":", "").replace("-", "")[:6].upper()
    
    # Base de données OUI (simplifié)
    oui_database = {
        "001D7E": "hikvision",
        "448544": "hikvision",
        "A4146B": "dahua",
        "C03D46": "dahua",
        "00408C": "axis",
        "ACCC8C": "axis",
        "C4BE84": "foscam",
        "98D6F7": "foscam",
        "000D42": "vivotek",
        "00501E": "vivotek",
        "0004F2": "bosch",
        "001921": "bosch",
        "001FC6": "tp_link",
        "341863": "xiaomi",
    }
    
    return oui_database.get(mac_prefix)


def auto_detect_stream_urls(ip: str, username: str, password: str, 
                            manufacturer: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Auto-détecte les URLs de stream possibles
    """
    if manufacturer:
        profile = get_profile(manufacturer)
        return {
            "rtsp": profile.get_rtsp_url(ip, username, password),
            "http": profile.get_http_url(ip, username, password),
            "snapshot": profile.get_snapshot_url(ip, username, password),
        }
    
    # Si pas de fabricant, essayer les URLs génériques
    generic_profile = CAMERA_PROFILES["generic"]
    return {
        "rtsp": generic_profile.get_rtsp_url(ip, username, password),
        "http": generic_profile.get_http_url(ip, username, password),
        "snapshot": generic_profile.get_snapshot_url(ip, username, password),
    }


def get_all_manufacturers() -> List[Dict[str, any]]:
    """Retourne la liste de tous les fabricants supportés"""
    return [
        {
            "id": key,
            "name": profile.manufacturer,
            "default_port": profile.default_port,
            "onvif_supported": profile.onvif_supported,
            "capabilities": profile.capabilities
        }
        for key, profile in CAMERA_PROFILES.items()
    ]


def test_connection_priority(manufacturer: str) -> List[str]:
    """
    Retourne l'ordre de priorité des méthodes de connexion
    selon le fabricant
    """
    priority_map = {
        "hikvision": ["onvif", "rtsp", "http"],
        "dahua": ["onvif", "rtsp", "http"],
        "axis": ["onvif", "rtsp", "http"],
        "foscam": ["rtsp", "onvif", "http"],
        "generic": ["rtsp", "onvif", "http"],
    }
    
    return priority_map.get(manufacturer.lower(), ["rtsp", "onvif", "http"])
