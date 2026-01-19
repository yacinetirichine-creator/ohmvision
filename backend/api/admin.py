"""
OhmVision - Admin API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from core.database import get_db
from core.config import settings
from models.models import User, Client, Contract, Camera, Alert, Invoice, ContractStatus
from api.auth import require_admin

router = APIRouter()

@router.get("/overview")
async def admin_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Vue d'ensemble admin"""
    
    # Clients
    clients_result = await db.execute(select(func.count(Client.id)))
    total_clients = clients_result.scalar()
    
    active_clients_result = await db.execute(
        select(func.count(Client.id)).where(Client.is_active == True)
    )
    active_clients = active_clients_result.scalar()
    
    # Contrats actifs
    contracts_result = await db.execute(
        select(func.count(Contract.id)).where(Contract.status == ContractStatus.ACTIVE)
    )
    active_contracts = contracts_result.scalar()
    
    # En essai
    trial_result = await db.execute(
        select(func.count(Contract.id)).where(Contract.status == ContractStatus.TRIAL)
    )
    trial_contracts = trial_result.scalar()
    
    # MRR
    mrr_result = await db.execute(
        select(func.sum(Contract.price_monthly)).where(Contract.status == ContractStatus.ACTIVE)
    )
    mrr = mrr_result.scalar() or 0
    
    # Caméras
    cameras_result = await db.execute(select(func.count(Camera.id)))
    total_cameras = cameras_result.scalar()
    
    online_cameras_result = await db.execute(
        select(func.count(Camera.id)).where(Camera.is_online == True)
    )
    online_cameras = online_cameras_result.scalar()
    
    # Alertes aujourd'hui
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    alerts_result = await db.execute(
        select(func.count(Alert.id)).where(Alert.created_at >= today)
    )
    today_alerts = alerts_result.scalar()
    
    return {
        "clients": {
            "total": total_clients,
            "active": active_clients
        },
        "contracts": {
            "active": active_contracts,
            "trial": trial_contracts
        },
        "revenue": {
            "mrr": round(mrr, 2),
            "arr": round(mrr * 12, 2)
        },
        "cameras": {
            "total": total_cameras,
            "online": online_cameras,
            "offline": total_cameras - online_cameras
        },
        "alerts": {
            "today": today_alerts
        }
    }

@router.get("/packages")
async def get_packages(
    current_user: User = Depends(require_admin)
):
    """Liste des packages disponibles"""
    return settings.PACKAGES

@router.get("/recent-activity")
async def recent_activity(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Activité récente"""
    
    # Nouveaux clients
    new_clients = await db.execute(
        select(Client)
        .order_by(Client.created_at.desc())
        .limit(5)
    )
    
    # Alertes critiques
    critical_alerts = await db.execute(
        select(Alert)
        .where(Alert.severity == "critical")
        .order_by(Alert.created_at.desc())
        .limit(5)
    )
    
    # Contrats récents
    recent_contracts = await db.execute(
        select(Contract)
        .order_by(Contract.created_at.desc())
        .limit(5)
    )
    
    return {
        "new_clients": [c for c in new_clients.scalars().all()],
        "critical_alerts": [a for a in critical_alerts.scalars().all()],
        "recent_contracts": [c for c in recent_contracts.scalars().all()]
    }

@router.get("/churn-analysis")
async def churn_analysis(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Analyse du churn"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Contrats annulés
    cancelled = await db.execute(
        select(func.count(Contract.id)).where(
            (Contract.status == ContractStatus.CANCELLED) &
            (Contract.end_date >= start_date)
        )
    )
    cancelled_count = cancelled.scalar()
    
    # Contrats actifs au début de période (approximation)
    active_start = await db.execute(
        select(func.count(Contract.id)).where(
            (Contract.status == ContractStatus.ACTIVE) |
            ((Contract.status == ContractStatus.CANCELLED) & (Contract.end_date >= start_date))
        )
    )
    active_count = active_start.scalar()
    
    churn_rate = (cancelled_count / active_count * 100) if active_count > 0 else 0
    
    return {
        "period_days": days,
        "cancelled_contracts": cancelled_count,
        "churn_rate": round(churn_rate, 2),
        "retention_rate": round(100 - churn_rate, 2)
    }

@router.get("/system-health")
async def system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Santé du système"""
    
    # Caméras hors ligne depuis longtemps
    offline_threshold = datetime.utcnow() - timedelta(hours=24)
    long_offline = await db.execute(
        select(func.count(Camera.id)).where(
            (Camera.is_online == False) &
            (Camera.last_seen < offline_threshold)
        )
    )
    long_offline_count = long_offline.scalar()
    
    # Alertes non lues
    unread_alerts = await db.execute(
        select(func.count(Alert.id)).where(Alert.is_read == False)
    )
    unread_count = unread_alerts.scalar()
    
    # Uptime global
    total_cams = await db.execute(select(func.count(Camera.id)))
    total = total_cams.scalar()
    
    online_cams = await db.execute(
        select(func.count(Camera.id)).where(Camera.is_online == True)
    )
    online = online_cams.scalar()
    
    uptime = (online / total * 100) if total > 0 else 100
    
    return {
        "status": "healthy" if uptime > 90 else "degraded" if uptime > 70 else "critical",
        "uptime_percent": round(uptime, 2),
        "issues": {
            "cameras_long_offline": long_offline_count,
            "unread_alerts": unread_count
        }
    }
