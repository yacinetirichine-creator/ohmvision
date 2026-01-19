"""
OhmVision - Analytics API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timedelta

from core.database import get_db
from models.models import Alert, Camera, DailyStat, User, Contract, Client
from api.auth import get_current_active_user, require_admin

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    client_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Statistiques pour le dashboard"""
    # Détermine le client
    if current_user.role not in ["admin", "support"]:
        client_id = current_user.client_id
    
    stats = {
        "cameras": {"total": 0, "online": 0, "offline": 0},
        "alerts": {"today": 0, "week": 0, "critical": 0},
        "counting": {"entries_today": 0, "exits_today": 0},
        "ppe": {"compliance_rate": 100}
    }
    
    # Caméras
    cam_query = select(Camera)
    if client_id:
        cam_query = cam_query.where(Camera.client_id == client_id)
    
    result = await db.execute(cam_query)
    cameras = result.scalars().all()
    
    stats["cameras"]["total"] = len(cameras)
    stats["cameras"]["online"] = sum(1 for c in cameras if c.is_online)
    stats["cameras"]["offline"] = stats["cameras"]["total"] - stats["cameras"]["online"]
    
    # Alertes
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    
    alert_query = select(Alert).join(Camera)
    if client_id:
        alert_query = alert_query.where(Camera.client_id == client_id)
    
    today_alerts = await db.execute(
        alert_query.where(Alert.created_at >= today)
    )
    stats["alerts"]["today"] = len(today_alerts.scalars().all())
    
    week_alerts = await db.execute(
        alert_query.where(Alert.created_at >= week_ago)
    )
    stats["alerts"]["week"] = len(week_alerts.scalars().all())
    
    return stats

@router.get("/counting")
async def get_counting_stats(
    camera_id: Optional[int] = None,
    client_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Statistiques de comptage"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()
    
    query = select(DailyStat)
    
    if camera_id:
        query = query.where(DailyStat.camera_id == camera_id)
    
    query = query.where(
        (DailyStat.date >= start_date) &
        (DailyStat.date <= end_date)
    )
    
    result = await db.execute(query)
    stats = result.scalars().all()
    
    return {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_entries": sum(s.total_entries for s in stats),
        "total_exits": sum(s.total_exits for s in stats),
        "peak_count": max((s.peak_count for s in stats), default=0),
        "daily_data": [
            {
                "date": s.date.isoformat(),
                "entries": s.total_entries,
                "exits": s.total_exits,
                "peak": s.peak_count
            }
            for s in stats
        ]
    }

@router.get("/trends")
async def get_trends(
    client_id: Optional[int] = None,
    period: str = "week",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Analyse des tendances"""
    if period == "day":
        days = 1
    elif period == "week":
        days = 7
    else:
        days = 30
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Tendance des alertes
    alert_query = select(Alert).join(Camera).where(Alert.created_at >= start_date)
    if client_id:
        alert_query = alert_query.where(Camera.client_id == client_id)
    
    result = await db.execute(alert_query)
    alerts = result.scalars().all()
    
    # Grouper par jour
    by_day = {}
    for alert in alerts:
        day = alert.created_at.strftime("%Y-%m-%d")
        by_day[day] = by_day.get(day, 0) + 1
    
    return {
        "period": period,
        "alert_trend": by_day,
        "average_daily": len(alerts) / days if days > 0 else 0
    }
