"""
OhmVision - API de découverte de caméras
Endpoints pour scanner le réseau et découvrir les caméras
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import asyncio
import logging

from services.network_scanner import NetworkScanner, NetworkDevice
from services.onvif_scanner import ONVIFScanner, ONVIFCamera
from services.rtsp_tester import RTSPTester, RTSPStreamInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/discovery", tags=["Discovery"])


# ============================================================================
# Modèles Pydantic
# ============================================================================

class ScanStatus(str, Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    COMPLETED = "completed"
    ERROR = "error"


class DiscoveredDevice(BaseModel):
    """Appareil découvert sur le réseau"""
    ip: str
    hostname: Optional[str] = None
    mac: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    device_type: str = "unknown"
    open_ports: List[int] = []
    is_onvif: bool = False
    rtsp_url: Optional[str] = None
    rtsp_valid: bool = False
    resolution: Optional[str] = None
    
    class Config:
        from_attributes = True


class ScanResult(BaseModel):
    """Résultat d'un scan réseau"""
    status: ScanStatus
    progress: int = 0  # 0-100
    total_ips: int = 0
    scanned_ips: int = 0
    devices: List[DiscoveredDevice] = []
    error_message: Optional[str] = None


class RTSPTestRequest(BaseModel):
    """Requête de test RTSP"""
    ip: str
    port: int = 554
    path: str = "/stream1"
    username: str = ""
    password: str = ""


class RTSPTestResponse(BaseModel):
    """Réponse de test RTSP"""
    url: str
    is_valid: bool
    width: int = 0
    height: int = 0
    fps: float = 0.0
    codec: str = ""
    error_message: str = ""
    response_time_ms: float = 0.0


class CameraCredentials(BaseModel):
    """Identifiants pour tester une caméra"""
    ip: str
    username: str = "admin"
    password: str = ""
    manufacturer: Optional[str] = None


class NetworkInfo(BaseModel):
    """Informations sur le réseau local"""
    local_ip: str
    network: str
    gateway: Optional[str] = None


# ============================================================================
# État global du scan (en production, utiliser Redis)
# ============================================================================

_scan_state: Dict[str, Any] = {
    "status": ScanStatus.IDLE,
    "progress": 0,
    "total_ips": 0,
    "scanned_ips": 0,
    "devices": [],
    "error_message": None
}


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/network-info", response_model=NetworkInfo)
async def get_network_info():
    """Récupère les informations du réseau local"""
    scanner = NetworkScanner()
    
    local_ip = scanner.get_local_ip()
    network = scanner.get_local_network()
    
    if not local_ip or not network:
        raise HTTPException(status_code=500, detail="Cannot detect local network")
    
    return NetworkInfo(
        local_ip=local_ip,
        network=network
    )


@router.post("/scan/start")
async def start_network_scan(background_tasks: BackgroundTasks):
    """
    Démarre un scan complet du réseau
    Combine: scan réseau + découverte ONVIF + test RTSP
    """
    global _scan_state
    
    if _scan_state["status"] == ScanStatus.SCANNING:
        raise HTTPException(status_code=400, detail="Scan already in progress")
    
    # Reset state
    _scan_state = {
        "status": ScanStatus.SCANNING,
        "progress": 0,
        "total_ips": 254,
        "scanned_ips": 0,
        "devices": [],
        "error_message": None
    }
    
    # Lancer le scan en arrière-plan
    background_tasks.add_task(run_full_scan)
    
    return {"message": "Scan started", "status": ScanStatus.SCANNING}


@router.get("/scan/status", response_model=ScanResult)
async def get_scan_status():
    """Récupère l'état actuel du scan"""
    return ScanResult(**_scan_state)


@router.post("/scan/stop")
async def stop_scan():
    """Arrête le scan en cours"""
    global _scan_state
    
    if _scan_state["status"] == ScanStatus.SCANNING:
        _scan_state["status"] = ScanStatus.IDLE
        return {"message": "Scan stopped"}
    
    return {"message": "No scan in progress"}


@router.post("/onvif/discover", response_model=List[DiscoveredDevice])
async def discover_onvif_cameras():
    """Découvre les caméras ONVIF via WS-Discovery"""
    scanner = ONVIFScanner(timeout=5.0)
    
    try:
        cameras = await scanner.discover_async()
        
        devices = []
        for cam in cameras:
            devices.append(DiscoveredDevice(
                ip=cam.ip,
                manufacturer=cam.manufacturer,
                model=cam.model,
                device_type="camera",
                is_onvif=True,
                rtsp_url=cam.rtsp_url,
                open_ports=[cam.port, 554]
            ))
        
        return devices
        
    except Exception as e:
        logger.error(f"ONVIF discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rtsp/test", response_model=RTSPTestResponse)
async def test_rtsp_connection(request: RTSPTestRequest):
    """Teste une connexion RTSP"""
    tester = RTSPTester(timeout=5.0)
    
    url = tester.build_rtsp_url(
        ip=request.ip,
        port=request.port,
        path=request.path,
        username=request.username,
        password=request.password
    )
    
    try:
        info = await tester.test_rtsp_url_async(url)
        
        return RTSPTestResponse(
            url=url,
            is_valid=info.is_valid,
            width=info.width,
            height=info.height,
            fps=info.fps,
            codec=info.codec,
            error_message=info.error_message,
            response_time_ms=info.response_time_ms
        )
        
    except Exception as e:
        logger.error(f"RTSP test error: {e}")
        return RTSPTestResponse(
            url=url,
            is_valid=False,
            error_message=str(e)
        )


@router.post("/rtsp/auto-discover", response_model=RTSPTestResponse)
async def auto_discover_rtsp(credentials: CameraCredentials):
    """
    Découvre automatiquement le flux RTSP d'une caméra
    Teste plusieurs URLs communes jusqu'à trouver un flux valide
    """
    tester = RTSPTester(timeout=5.0)
    
    try:
        info = await tester.auto_discover_stream_async(
            ip=credentials.ip,
            username=credentials.username,
            password=credentials.password,
            manufacturer=credentials.manufacturer
        )
        
        if info:
            return RTSPTestResponse(
                url=info.url,
                is_valid=info.is_valid,
                width=info.width,
                height=info.height,
                fps=info.fps,
                codec=info.codec,
                error_message=info.error_message,
                response_time_ms=info.response_time_ms
            )
        else:
            return RTSPTestResponse(
                url="",
                is_valid=False,
                error_message="No valid RTSP stream found"
            )
            
    except Exception as e:
        logger.error(f"RTSP auto-discover error: {e}")
        return RTSPTestResponse(
            url="",
            is_valid=False,
            error_message=str(e)
        )


@router.get("/common-rtsp-paths")
async def get_common_rtsp_paths():
    """Retourne les chemins RTSP communs par fabricant"""
    return RTSPTester.RTSP_PATHS


# ============================================================================
# Fonction de scan en arrière-plan
# ============================================================================

async def run_full_scan():
    """Exécute un scan complet du réseau"""
    global _scan_state
    
    try:
        # Phase 1: Scan réseau (50%)
        logger.info("Phase 1: Network scan...")
        network_scanner = NetworkScanner(timeout=0.3, max_workers=100)
        
        def progress_callback(current, total, ip):
            _scan_state["scanned_ips"] = current
            _scan_state["total_ips"] = total
            _scan_state["progress"] = int((current / total) * 50)
        
        # Exécuter le scan réseau
        loop = asyncio.get_event_loop()
        network_devices = await loop.run_in_executor(
            None,
            lambda: network_scanner.scan_network(progress_callback=progress_callback)
        )
        
        # Convertir en DiscoveredDevice
        devices = []
        for dev in network_devices:
            devices.append({
                "ip": dev.ip,
                "hostname": dev.hostname,
                "mac": dev.mac,
                "manufacturer": dev.manufacturer,
                "device_type": dev.device_type,
                "open_ports": dev.open_ports,
                "is_onvif": False,
                "rtsp_url": None,
                "rtsp_valid": False
            })
        
        _scan_state["devices"] = devices
        _scan_state["progress"] = 50
        
        # Phase 2: Découverte ONVIF (70%)
        logger.info("Phase 2: ONVIF discovery...")
        onvif_scanner = ONVIFScanner(timeout=3.0)
        onvif_cameras = await onvif_scanner.discover_async()
        
        # Fusionner avec les appareils trouvés
        onvif_ips = {cam.ip for cam in onvif_cameras}
        
        for cam in onvif_cameras:
            # Chercher si déjà dans la liste
            found = False
            for dev in _scan_state["devices"]:
                if dev["ip"] == cam.ip:
                    dev["is_onvif"] = True
                    dev["manufacturer"] = cam.manufacturer or dev.get("manufacturer")
                    dev["model"] = cam.model
                    dev["device_type"] = "camera"
                    dev["rtsp_url"] = cam.rtsp_url
                    found = True
                    break
            
            if not found:
                _scan_state["devices"].append({
                    "ip": cam.ip,
                    "hostname": None,
                    "mac": None,
                    "manufacturer": cam.manufacturer,
                    "model": cam.model,
                    "device_type": "camera",
                    "open_ports": [cam.port, 554],
                    "is_onvif": True,
                    "rtsp_url": cam.rtsp_url,
                    "rtsp_valid": False
                })
        
        _scan_state["progress"] = 70
        
        # Phase 3: Test RTSP pour les caméras potentielles (100%)
        logger.info("Phase 3: RTSP validation...")
        rtsp_tester = RTSPTester(timeout=3.0)
        
        camera_devices = [d for d in _scan_state["devices"] 
                         if d["device_type"] == "camera" or 554 in d.get("open_ports", [])]
        
        total_cameras = len(camera_devices)
        for i, dev in enumerate(camera_devices):
            # Calculer le progress (70-100%)
            _scan_state["progress"] = 70 + int((i / max(total_cameras, 1)) * 30)
            
            # Si pas d'URL RTSP, essayer d'en trouver une
            if not dev.get("rtsp_url"):
                info = await rtsp_tester.auto_discover_stream_async(
                    ip=dev["ip"],
                    manufacturer=dev.get("manufacturer", "")
                )
                if info and info.is_valid:
                    dev["rtsp_url"] = info.url
                    dev["rtsp_valid"] = True
                    dev["resolution"] = info.resolution
            else:
                # Tester l'URL existante
                info = await rtsp_tester.test_rtsp_url_async(dev["rtsp_url"])
                dev["rtsp_valid"] = info.is_valid
                if info.is_valid:
                    dev["resolution"] = info.resolution
        
        # Terminé
        _scan_state["status"] = ScanStatus.COMPLETED
        _scan_state["progress"] = 100
        
        logger.info(f"Scan completed: {len(_scan_state['devices'])} devices found")
        
    except Exception as e:
        logger.error(f"Scan error: {e}")
        _scan_state["status"] = ScanStatus.ERROR
        _scan_state["error_message"] = str(e)
