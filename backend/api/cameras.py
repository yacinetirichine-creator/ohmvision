"""
OhmVision - Cameras API
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from core.database import get_db
from models.models import Camera, Client, Alert, User
from api.auth import get_current_active_user, require_admin

router = APIRouter()

# Schemas
class CameraCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    rtsp_url: Optional[str] = None
    ip_address: Optional[str] = None
    port: int = 554
    username: Optional[str] = None
    password: Optional[str] = None
    site_id: Optional[int] = None

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    rtsp_url: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    detection_config: Optional[Dict[str, Any]] = None
    zones: Optional[List[Dict]] = None

class CameraResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    location: Optional[str]
    ip_address: Optional[str]
    is_active: bool
    is_online: bool
    last_seen: Optional[datetime]
    detection_config: Dict[str, Any]
    zones: List[Dict]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DetectionConfigUpdate(BaseModel):
    person_detection: Optional[bool] = None
    counting: Optional[bool] = None
    fall_detection: Optional[bool] = None
    ppe_detection: Optional[bool] = None
    fire_detection: Optional[bool] = None
    vehicle_detection: Optional[bool] = None
    lpr_enabled: Optional[bool] = None
    sensitivity: Optional[float] = None

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, camera_id: int):
        await websocket.accept()
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = []
        self.active_connections[camera_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, camera_id: int):
        if camera_id in self.active_connections:
            self.active_connections[camera_id].remove(websocket)
    
    async def broadcast(self, camera_id: int, message: dict):
        if camera_id in self.active_connections:
            for connection in self.active_connections[camera_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# Routes
@router.get("/")
async def list_cameras(
    client_id: Optional[int] = None,
    site_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liste les caméras"""
    query = select(Camera)
    
    # Filtre par client pour les non-admin
    if current_user.role not in ["admin", "support"]:
        query = query.where(Camera.client_id == current_user.client_id)
    elif client_id:
        query = query.where(Camera.client_id == client_id)
    
    if site_id:
        query = query.where(Camera.site_id == site_id)
    
    if status == "online":
        query = query.where(Camera.is_online == True)
    elif status == "offline":
        query = query.where(Camera.is_online == False)
    
    query = query.order_by(Camera.name)
    
    result = await db.execute(query)
    cameras = result.scalars().all()
    
    return [CameraResponse(
        id=c.id,
        name=c.name,
        description=c.description,
        location=c.location,
        ip_address=c.ip_address,
        is_active=c.is_active,
        is_online=c.is_online,
        last_seen=c.last_seen,
        detection_config=c.detection_config or {},
        zones=c.zones or [],
        created_at=c.created_at
    ) for c in cameras]

@router.post("/", response_model=CameraResponse)
async def create_camera(
    camera_data: CameraCreate,
    client_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crée une nouvelle caméra"""
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"]:
        if current_user.client_id != client_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Vérifie la limite de caméras du contrat
    # TODO: Implémenter la vérification
    
    camera = Camera(
        client_id=client_id,
        **camera_data.model_dump()
    )
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    
    return CameraResponse(
        id=camera.id,
        name=camera.name,
        description=camera.description,
        location=camera.location,
        ip_address=camera.ip_address,
        is_active=camera.is_active,
        is_online=camera.is_online,
        last_seen=camera.last_seen,
        detection_config=camera.detection_config or {},
        zones=camera.zones or [],
        created_at=camera.created_at
    )

@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère une caméra"""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"]:
        if current_user.client_id != camera.client_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return CameraResponse(
        id=camera.id,
        name=camera.name,
        description=camera.description,
        location=camera.location,
        ip_address=camera.ip_address,
        is_active=camera.is_active,
        is_online=camera.is_online,
        last_seen=camera.last_seen,
        detection_config=camera.detection_config or {},
        zones=camera.zones or [],
        created_at=camera.created_at
    )

@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: int,
    camera_data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Met à jour une caméra"""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"]:
        if current_user.client_id != camera.client_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    update_data = camera_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)
    
    await db.commit()
    await db.refresh(camera)
    
    return CameraResponse(
        id=camera.id,
        name=camera.name,
        description=camera.description,
        location=camera.location,
        ip_address=camera.ip_address,
        is_active=camera.is_active,
        is_online=camera.is_online,
        last_seen=camera.last_seen,
        detection_config=camera.detection_config or {},
        zones=camera.zones or [],
        created_at=camera.created_at
    )

@router.delete("/{camera_id}")
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Supprime une caméra"""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"]:
        if current_user.client_id != camera.client_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    await db.delete(camera)
    await db.commit()
    
    return {"message": "Caméra supprimée"}

@router.put("/{camera_id}/detection-config")
async def update_detection_config(
    camera_id: int,
    config: DetectionConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Met à jour la configuration de détection"""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"]:
        if current_user.client_id != camera.client_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Met à jour la config
    current_config = camera.detection_config or {}
    update_data = config.model_dump(exclude_unset=True)
    current_config.update(update_data)
    camera.detection_config = current_config
    
    await db.commit()
    
    return {"message": "Configuration mise à jour", "config": current_config}

@router.put("/{camera_id}/zones")
async def update_zones(
    camera_id: int,
    zones: List[Dict],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Met à jour les zones de détection"""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"]:
        if current_user.client_id != camera.client_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    camera.zones = zones
    await db.commit()
    
    return {"message": "Zones mises à jour", "zones": zones}

@router.post("/{camera_id}/heartbeat")
async def camera_heartbeat(
    camera_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Heartbeat de la caméra (appelé par l'agent)"""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    camera.is_online = True
    camera.last_seen = datetime.utcnow()
    await db.commit()
    
    return {"status": "ok", "config": camera.detection_config}

# WebSocket pour le streaming temps réel
@router.websocket("/{camera_id}/stream")
async def camera_stream(
    websocket: WebSocket,
    camera_id: int,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket pour le streaming vidéo et les détections en temps réel"""
    await manager.connect(websocket, camera_id)
    try:
        while True:
            # Reçoit les données de l'agent (frames, détections)
            data = await websocket.receive_json()
            
            # Broadcast aux autres clients connectés
            await manager.broadcast(camera_id, data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, camera_id)
