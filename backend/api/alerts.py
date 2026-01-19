"""
OhmVision - Alerts API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from core.database import get_db
from models.models import Alert, Camera, User, AlertType, AlertSeverity
from api.auth import get_current_active_user

router = APIRouter()

class AlertCreate(BaseModel):
    camera_id: int
    type: AlertType
    severity: AlertSeverity = AlertSeverity.MEDIUM
    message: str
    data: Optional[Dict[str, Any]] = None
    snapshot_url: Optional[str] = None

@router.get("/")
async def list_alerts(
    camera_id: Optional[int] = None,
    client_id: Optional[int] = None,
    type: Optional[AlertType] = None,
    severity: Optional[AlertSeverity] = None,
    is_read: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liste les alertes"""
    query = select(Alert).join(Camera)
    
    # Filtre par client pour les non-admin
    if current_user.role not in ["admin", "support"]:
        query = query.where(Camera.client_id == current_user.client_id)
    elif client_id:
        query = query.where(Camera.client_id == client_id)
    
    if camera_id:
        query = query.where(Alert.camera_id == camera_id)
    if type:
        query = query.where(Alert.type == type)
    if severity:
        query = query.where(Alert.severity == severity)
    if is_read is not None:
        query = query.where(Alert.is_read == is_read)
    if start_date:
        query = query.where(Alert.created_at >= start_date)
    if end_date:
        query = query.where(Alert.created_at <= end_date)
    
    # Count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Alert.created_at.desc())
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return {
        "items": alerts,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.post("/")
async def create_alert(
    data: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crée une nouvelle alerte (appelé par le moteur IA)"""
    alert = Alert(**data.model_dump())
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    # TODO: Envoyer notifications (email, SMS, push)
    
    return alert

@router.get("/stats")
async def get_alert_stats(
    client_id: Optional[int] = None,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Statistiques des alertes"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(Alert).join(Camera).where(Alert.created_at >= start_date)
    
    if current_user.role not in ["admin", "support"]:
        query = query.where(Camera.client_id == current_user.client_id)
    elif client_id:
        query = query.where(Camera.client_id == client_id)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    # Stats
    by_type = {}
    by_severity = {}
    by_day = {}
    
    for alert in alerts:
        # Par type
        type_key = alert.type.value
        by_type[type_key] = by_type.get(type_key, 0) + 1
        
        # Par sévérité
        sev_key = alert.severity.value
        by_severity[sev_key] = by_severity.get(sev_key, 0) + 1
        
        # Par jour
        day_key = alert.created_at.strftime("%Y-%m-%d")
        by_day[day_key] = by_day.get(day_key, 0) + 1
    
    return {
        "total": len(alerts),
        "by_type": by_type,
        "by_severity": by_severity,
        "by_day": by_day,
        "unread": sum(1 for a in alerts if not a.is_read),
        "critical": sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL)
    }

@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère une alerte"""
    result = await db.execute(
        select(Alert).join(Camera).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    return alert

@router.put("/{alert_id}/read")
async def mark_as_read(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marque une alerte comme lue"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    alert.is_read = True
    await db.commit()
    
    return {"message": "Alerte marquée comme lue"}

@router.put("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Résout une alerte"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    
    await db.commit()
    
    return {"message": "Alerte résolue"}

@router.post("/mark-all-read")
async def mark_all_as_read(
    camera_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marque toutes les alertes comme lues"""
    query = select(Alert).join(Camera).where(Alert.is_read == False)
    
    if current_user.role not in ["admin", "support"]:
        query = query.where(Camera.client_id == current_user.client_id)
    
    if camera_id:
        query = query.where(Alert.camera_id == camera_id)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    for alert in alerts:
        alert.is_read = True
    
    await db.commit()
    
    return {"message": f"{len(alerts)} alertes marquées comme lues"}
