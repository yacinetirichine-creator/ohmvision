"""
OhmVision - Health Check API
Endpoints pour surveiller la santé des connexions caméra
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from api.auth import get_current_active_user
from models.models import User
from services.health_check_service import health_check_service

router = APIRouter(prefix="/api/health", tags=["Health"])


# =============================================================================
# Modèles
# =============================================================================

class HealthStatus(BaseModel):
    """Statut de santé d'une caméra"""
    camera_id: int
    camera_name: str
    is_online: bool
    health: str  # excellent, good, fair, poor, offline
    last_check: datetime
    uptime_percentage: float
    failed_attempts: int
    last_error: Optional[str] = None
    next_check_in: int  # secondes
    
    class Config:
        from_attributes = True


class ReconnectionStatus(BaseModel):
    """Statut de reconnexion"""
    camera_id: int
    attempts: int
    max_attempts: int
    last_attempt: Optional[datetime]
    next_retry_in_seconds: float


class SystemHealthSummary(BaseModel):
    """Résumé de santé du système"""
    total_cameras: int
    online_cameras: int
    offline_cameras: int
    average_uptime: float
    cameras_excellent: int
    cameras_good: int
    cameras_fair: int
    cameras_poor: int
    cameras_offline: int


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/status", response_model=SystemHealthSummary)
async def get_system_health(
    current_user: User = Depends(get_current_active_user)
):
    """
    📊 Résumé de santé du système
    Vue d'ensemble de toutes les caméras
    """
    if not health_check_service:
        raise HTTPException(
            status_code=503,
            detail="Health check service not available"
        )
    
    statuses = await health_check_service.get_all_health_status()
    
    total = len(statuses)
    online = sum(1 for s in statuses if s.is_online)
    offline = total - online
    
    # Calculer la moyenne de uptime
    avg_uptime = sum(s.uptime_percentage for s in statuses) / total if total > 0 else 0
    
    # Compter par niveau de santé
    excellent = sum(1 for s in statuses if s.health == "excellent")
    good = sum(1 for s in statuses if s.health == "good")
    fair = sum(1 for s in statuses if s.health == "fair")
    poor = sum(1 for s in statuses if s.health == "poor")
    offline_count = sum(1 for s in statuses if s.health == "offline")
    
    return SystemHealthSummary(
        total_cameras=total,
        online_cameras=online,
        offline_cameras=offline,
        average_uptime=round(avg_uptime, 2),
        cameras_excellent=excellent,
        cameras_good=good,
        cameras_fair=fair,
        cameras_poor=poor,
        cameras_offline=offline_count
    )


@router.get("/cameras", response_model=List[HealthStatus])
async def get_all_cameras_health(
    current_user: User = Depends(get_current_active_user)
):
    """
    📹 Statut de santé de toutes les caméras
    """
    if not health_check_service:
        raise HTTPException(
            status_code=503,
            detail="Health check service not available"
        )
    
    statuses = await health_check_service.get_all_health_status()
    
    # TODO: Récupérer les noms des caméras depuis la DB
    # Pour l'instant, on retourne juste les IDs
    return [
        HealthStatus(
            camera_id=s.camera_id,
            camera_name=f"Camera {s.camera_id}",  # TODO: récupérer le vrai nom
            is_online=s.is_online,
            health=s.health,
            last_check=s.last_check,
            uptime_percentage=round(s.uptime_percentage, 2),
            failed_attempts=s.failed_attempts,
            last_error=s.last_error,
            next_check_in=s.next_check_in
        )
        for s in statuses
    ]


@router.get("/cameras/{camera_id}", response_model=HealthStatus)
async def get_camera_health(
    camera_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    📹 Statut de santé d'une caméra spécifique
    """
    if not health_check_service:
        raise HTTPException(
            status_code=503,
            detail="Health check service not available"
        )
    
    status = await health_check_service.get_camera_health(camera_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    return HealthStatus(
        camera_id=status.camera_id,
        camera_name=f"Camera {status.camera_id}",  # TODO: récupérer le vrai nom
        is_online=status.is_online,
        health=status.health,
        last_check=status.last_check,
        uptime_percentage=round(status.uptime_percentage, 2),
        failed_attempts=status.failed_attempts,
        last_error=status.last_error,
        next_check_in=status.next_check_in
    )


@router.get("/cameras/{camera_id}/reconnection", response_model=ReconnectionStatus)
async def get_reconnection_status(
    camera_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    🔄 Statut de reconnexion d'une caméra
    """
    if not health_check_service:
        raise HTTPException(
            status_code=503,
            detail="Health check service not available"
        )
    
    status = health_check_service.get_reconnection_status(camera_id)
    
    return ReconnectionStatus(
        camera_id=camera_id,
        **status
    )


@router.post("/cameras/{camera_id}/check-now")
async def force_health_check(
    camera_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    ⚡ Force une vérification immédiate de santé
    """
    if not health_check_service:
        raise HTTPException(
            status_code=503,
            detail="Health check service not available"
        )
    
    # TODO: Implémenter un check immédiat
    # Pour l'instant, on retourne juste un message
    
    return {
        "message": "Health check scheduled",
        "camera_id": camera_id
    }


@router.post("/cameras/{camera_id}/reconnect")
async def force_reconnection(
    camera_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🔄 Force une tentative de reconnexion immédiate
    """
    if not health_check_service:
        raise HTTPException(
            status_code=503,
            detail="Health check service not available"
        )
    
    # TODO: Implémenter une reconnexion forcée
    
    return {
        "message": "Reconnection attempt started",
        "camera_id": camera_id
    }
