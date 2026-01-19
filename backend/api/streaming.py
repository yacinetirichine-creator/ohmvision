"""
OhmVision - API Streaming Vidéo
Endpoints pour le streaming MJPEG et la gestion des flux
"""

from fastapi import APIRouter, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

from services.stream_manager import stream_manager, draw_detection_overlay

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/streaming", tags=["Streaming"])


# ============================================================================
# Modèles
# ============================================================================

class StartStreamRequest(BaseModel):
    """Requête de démarrage de stream"""
    camera_id: int
    rtsp_url: str
    name: Optional[str] = ""


class StreamInfo(BaseModel):
    """Informations sur un stream"""
    camera_id: int
    name: str
    is_running: bool
    width: int
    height: int
    fps: float
    error: Optional[str] = None
    last_frame_age: Optional[float] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/start")
async def start_stream(request: StartStreamRequest):
    """
    Démarre le streaming pour une caméra
    
    Le stream sera accessible via /api/streaming/mjpeg/{camera_id}
    """
    try:
        success = stream_manager.start_stream(
            camera_id=request.camera_id,
            rtsp_url=request.rtsp_url,
            name=request.name
        )
        
        if success:
            return {
                "success": True,
                "message": f"Stream {request.camera_id} started",
                "stream_url": f"/api/streaming/mjpeg/{request.camera_id}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to start stream")
            
    except Exception as e:
        logger.error(f"Error starting stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop/{camera_id}")
async def stop_stream(camera_id: int):
    """Arrête le streaming pour une caméra"""
    try:
        stream_manager.stop_stream(camera_id)
        return {
            "success": True,
            "message": f"Stream {camera_id} stopped"
        }
    except Exception as e:
        logger.error(f"Error stopping stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{camera_id}", response_model=StreamInfo)
async def get_stream_info(camera_id: int):
    """Récupère les informations d'un stream"""
    info = stream_manager.get_stream_info(camera_id)
    
    if info is None:
        raise HTTPException(status_code=404, detail=f"Stream {camera_id} not found")
    
    return StreamInfo(**info)


@router.get("/list")
async def list_streams():
    """Liste tous les streams actifs"""
    streams = stream_manager.list_streams()
    return {
        "count": len(streams),
        "streams": streams
    }


@router.get("/mjpeg/{camera_id}")
async def mjpeg_stream(
    camera_id: int,
    fps: int = Query(default=15, ge=1, le=30, description="FPS limit"),
    quality: int = Query(default=70, ge=10, le=100, description="JPEG quality")
):
    """
    Stream MJPEG d'une caméra
    
    Usage dans le navigateur:
    <img src="/api/streaming/mjpeg/1?fps=15&quality=70">
    
    Args:
        camera_id: ID de la caméra
        fps: Limite de FPS (défaut: 15)
        quality: Qualité JPEG 10-100 (défaut: 70)
    """
    # Vérifier que le stream existe
    info = stream_manager.get_stream_info(camera_id)
    if info is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Stream {camera_id} not found. Start it first with POST /api/streaming/start"
        )
    
    return StreamingResponse(
        stream_manager.generate_mjpeg(camera_id, fps_limit=fps, quality=quality),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/snapshot/{camera_id}")
async def get_snapshot(
    camera_id: int,
    quality: int = Query(default=90, ge=10, le=100)
):
    """
    Capture une image instantanée d'une caméra
    
    Returns:
        Image JPEG
    """
    jpeg = stream_manager.get_jpeg_frame(camera_id, quality)
    
    if jpeg is None:
        raise HTTPException(
            status_code=404,
            detail=f"No frame available for camera {camera_id}"
        )
    
    return Response(
        content=jpeg,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@router.post("/stop-all")
async def stop_all_streams():
    """Arrête tous les streams"""
    stream_manager.stop_all()
    return {
        "success": True,
        "message": "All streams stopped"
    }


# ============================================================================
# Endpoint pour le streaming avec détection overlay (optionnel)
# ============================================================================

@router.get("/mjpeg-ai/{camera_id}")
async def mjpeg_stream_with_ai(
    camera_id: int,
    fps: int = Query(default=10, ge=1, le=30),
    quality: int = Query(default=60, ge=10, le=100),
    show_detections: bool = Query(default=True)
):
    """
    Stream MJPEG avec overlay des détections IA
    
    Note: Plus lent car inclut le traitement IA
    """
    info = stream_manager.get_stream_info(camera_id)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Stream {camera_id} not found")
    
    # TODO: Intégrer avec le moteur IA pour les détections en temps réel
    # Pour l'instant, retourne le stream normal
    return StreamingResponse(
        stream_manager.generate_mjpeg(camera_id, fps_limit=fps, quality=quality),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
