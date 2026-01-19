"""
OhmVision - Advanced Analytics API
Endpoints pour les analyses avancées, rapports et notifications
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import base64
from io import BytesIO

from ai.industry_analytics import IndustryType, industry_analytics
from ai.behavior_analytics import behavior_analyzer, BehaviorType
from services.notification_manager import (
    notification_manager, NotificationChannel, NotificationConfig, 
    Alert, AlertSeverity, send_alert_notification
)
from services.smart_recorder import smart_recorder, trigger_recording_on_alert
from services.report_generator import report_generator, ReportType, ReportData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advanced", tags=["Advanced Analytics"])


# ============================================================================
# Modèles
# ============================================================================

class IndustryAnalyticsRequest(BaseModel):
    """Requête d'analytics par secteur"""
    camera_id: int
    industry: IndustryType
    detections: List[Dict[str, Any]]
    zones: Optional[List[Dict[str, Any]]] = None


class NotificationChannelConfig(BaseModel):
    """Configuration d'un canal de notification"""
    name: str
    channel: NotificationChannel
    enabled: bool = True
    config: Dict[str, Any]
    min_severity: str = "info"
    alert_types: Optional[List[str]] = None
    cameras: Optional[List[int]] = None


class TestNotificationRequest(BaseModel):
    """Requête de test de notification"""
    channel_name: str
    message: str = "Test notification from OhmVision"


class ReportRequest(BaseModel):
    """Requête de génération de rapport"""
    report_type: ReportType
    start_date: datetime
    end_date: datetime
    camera_ids: Optional[List[int]] = None
    include_charts: bool = True
    include_snapshots: bool = False


class BehaviorZone(BaseModel):
    """Définition d'une zone de surveillance"""
    name: str
    x1: int
    y1: int
    x2: int
    y2: int
    zone_type: str = "normal"  # normal, restricted, counting, queue
    expected_direction: Optional[str] = None


class RecordingRequest(BaseModel):
    """Requête d'enregistrement"""
    camera_id: int
    camera_name: str
    alert_type: str
    alert_id: Optional[str] = None


# ============================================================================
# Analytics par Secteur
# ============================================================================

@router.post("/industry-analytics")
async def get_industry_analytics(request: IndustryAnalyticsRequest):
    """
    Récupère les analytics spécifiques à un secteur d'activité
    
    Secteurs supportés:
    - retail: Commerce (comptage, files d'attente, zones chaudes)
    - industrial: Industrie (EPI, zones dangereuses, productivité)
    - healthcare: Santé (patients, hygiène, urgences)
    - logistics: Logistique (véhicules, quais, flux)
    - construction: Chantiers (EPI, zones d'exclusion)
    - parking: Parkings (occupation, flux, LPR)
    - smart_city: Villes (trafic, foule, incidents)
    """
    try:
        analytics = industry_analytics.get_analytics(
            camera_id=request.camera_id,
            industry=request.industry,
            detections=request.detections,
            zones=request.zones
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Industry analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry-types")
async def list_industry_types():
    """Liste tous les types d'industries supportés"""
    return {
        "industries": [
            {"id": "retail", "name": "Commerce", "icon": "🛒", 
             "features": ["Comptage", "Files d'attente", "Zones chaudes", "Dwell time"]},
            {"id": "industrial", "name": "Industrie", "icon": "🏭",
             "features": ["Conformité EPI", "Zones restreintes", "Productivité", "Sécurité"]},
            {"id": "healthcare", "name": "Santé", "icon": "🏥",
             "features": ["Chutes patients", "Hygiène", "Temps d'attente", "Urgences"]},
            {"id": "logistics", "name": "Logistique", "icon": "📦",
             "features": ["Flux véhicules", "Occupation quais", "Comptage palettes"]},
            {"id": "construction", "name": "Chantiers", "icon": "🏗️",
             "features": ["EPI obligatoire", "Zones d'exclusion", "Incidents"]},
            {"id": "parking", "name": "Parkings", "icon": "🅿️",
             "features": ["Occupation", "Reconnaissance plaques", "Flux"]},
            {"id": "smart_city", "name": "Villes", "icon": "🌆",
             "features": ["Trafic", "Foule", "Incidents", "Sécurité publique"]}
        ]
    }


# ============================================================================
# Analyse Comportementale
# ============================================================================

@router.post("/behavior/analyze")
async def analyze_behavior(
    camera_id: int,
    detections: List[Dict[str, Any]]
):
    """
    Analyse les comportements en temps réel
    
    Détecte:
    - Flânerie (loitering)
    - Course (running)
    - Formation de foule
    - Bagarres
    - Intrusions
    - Mouvements erratiques
    """
    behaviors = behavior_analyzer.update(detections)
    
    return {
        "behaviors": behaviors,
        "statistics": behavior_analyzer.get_statistics()
    }


@router.post("/behavior/zones")
async def configure_behavior_zones(zones: List[BehaviorZone]):
    """Configure les zones de surveillance comportementale"""
    for zone in zones:
        behavior_analyzer.add_zone(
            name=zone.name,
            x1=zone.x1, y1=zone.y1,
            x2=zone.x2, y2=zone.y2,
            zone_type=zone.zone_type,
            expected_direction=zone.expected_direction
        )
    
    return {"message": f"{len(zones)} zones configured"}


@router.get("/behavior/heatmap")
async def get_heatmap():
    """Récupère la heatmap des mouvements"""
    heatmap = behavior_analyzer.get_heatmap()
    hot_zones = behavior_analyzer.get_hot_zones()
    
    return {
        "heatmap": heatmap.tolist(),
        "hot_zones": hot_zones,
        "dimensions": {
            "width": behavior_analyzer.frame_width,
            "height": behavior_analyzer.frame_height,
            "grid_size": behavior_analyzer.heatmap.grid_size
        }
    }


@router.get("/behavior/statistics")
async def get_behavior_statistics():
    """Récupère les statistiques comportementales"""
    return behavior_analyzer.get_statistics()


# ============================================================================
# Notifications Multi-Canal
# ============================================================================

@router.post("/notifications/channels")
async def add_notification_channel(config: NotificationChannelConfig):
    """Ajoute ou met à jour un canal de notification"""
    notification_config = NotificationConfig(
        channel=config.channel,
        enabled=config.enabled,
        config=config.config,
        min_severity=AlertSeverity(config.min_severity),
        alert_types=config.alert_types,
        cameras=config.cameras
    )
    
    notification_manager.add_channel(config.name, notification_config)
    
    return {"message": f"Channel '{config.name}' configured"}


@router.delete("/notifications/channels/{name}")
async def remove_notification_channel(name: str):
    """Supprime un canal de notification"""
    notification_manager.remove_channel(name)
    return {"message": f"Channel '{name}' removed"}


@router.get("/notifications/channels")
async def list_notification_channels():
    """Liste tous les canaux de notification configurés"""
    channels = []
    for name, config in notification_manager.channels.items():
        channels.append({
            "name": name,
            "channel": config.channel.value,
            "enabled": config.enabled,
            "min_severity": config.min_severity.value
        })
    return {"channels": channels}


@router.post("/notifications/test")
async def test_notification(request: TestNotificationRequest):
    """Envoie une notification de test"""
    results = await send_alert_notification(
        camera_id=0,
        camera_name="Test Camera",
        alert_type="test",
        severity="info",
        message=request.message
    )
    
    return {"results": results}


@router.post("/notifications/send")
async def send_notification(
    camera_id: int,
    camera_name: str,
    alert_type: str,
    severity: str,
    message: str,
    snapshot_base64: Optional[str] = None
):
    """Envoie une notification sur tous les canaux configurés"""
    results = await send_alert_notification(
        camera_id=camera_id,
        camera_name=camera_name,
        alert_type=alert_type,
        severity=severity,
        message=message,
        snapshot_base64=snapshot_base64
    )
    
    return {"success": any(results.values()), "results": results}


# ============================================================================
# Enregistrement Intelligent
# ============================================================================

@router.post("/recording/start")
async def start_smart_recording(request: RecordingRequest):
    """Démarre un enregistrement intelligent suite à une alerte"""
    session_id = await trigger_recording_on_alert(
        camera_id=request.camera_id,
        camera_name=request.camera_name,
        alert_type=request.alert_type,
        alert_id=request.alert_id
    )
    
    return {
        "session_id": session_id,
        "message": "Recording started"
    }


@router.post("/recording/stop/{session_id}")
async def stop_recording(session_id: str):
    """Arrête un enregistrement"""
    filepath = smart_recorder.stop_recording(session_id)
    
    if filepath:
        return {
            "success": True,
            "filepath": filepath
        }
    else:
        raise HTTPException(status_code=404, detail="Recording not found")


@router.get("/recording/status/{session_id}")
async def get_recording_status(session_id: str):
    """Récupère le statut d'un enregistrement"""
    status = smart_recorder.get_recording_status(session_id)
    
    if status:
        return status
    else:
        raise HTTPException(status_code=404, detail="Recording not found")


@router.get("/recordings")
async def list_recordings(
    camera_id: Optional[int] = None,
    days: int = Query(default=7, ge=1, le=90)
):
    """Liste les enregistrements"""
    recordings = smart_recorder.list_recordings(camera_id=camera_id, days=days)
    return {"recordings": recordings}


@router.get("/recordings/storage")
async def get_storage_status():
    """Récupère l'état du stockage"""
    return smart_recorder.check_storage()


@router.post("/recordings/cleanup")
async def cleanup_recordings():
    """Nettoie les anciens enregistrements"""
    deleted = smart_recorder.cleanup_old_recordings()
    return {"deleted_count": deleted}


# ============================================================================
# Rapports PDF
# ============================================================================

@router.post("/reports/generate")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """
    Génère un rapport PDF
    
    Types de rapports:
    - daily: Rapport journalier
    - weekly: Rapport hebdomadaire
    - monthly: Rapport mensuel
    - incident: Rapport d'incident
    - compliance: Rapport de conformité
    - executive: Rapport exécutif
    """
    try:
        # Récupérer les données (simulées pour l'exemple)
        data = ReportData(
            report_type=request.report_type,
            title=f"Rapport {request.report_type.value.capitalize()}",
            period_start=request.start_date,
            period_end=request.end_date,
            total_alerts=42,
            critical_alerts=5,
            cameras_online=8,
            cameras_total=10,
            alerts_by_type={"fall": 5, "fire": 2, "intrusion": 15, "ppe": 20},
            alerts_by_hour={h: int(10 * abs(12 - h) / 12) for h in range(24)},
            total_entries=1250,
            total_exits=1180,
            peak_occupancy=85,
            avg_occupancy=42.5,
            ppe_compliance_rate=92.5,
            safety_incidents=3,
            ai_insights=[
                "Pic d'alertes détecté entre 14h et 16h",
                "Zone d'entrée principale sous-surveillée",
                "Amélioration de 15% de la conformité EPI ce mois"
            ],
            recommendations=[
                "Ajouter une caméra zone d'entrée",
                "Renforcer les contrôles aux heures de pointe",
                "Former l'équipe sur les nouveaux protocoles"
            ]
        )
        
        # Générer le PDF
        pdf_content = report_generator.generate_report(data)
        
        # Retourner le PDF
        filename = f"ohmvision_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/daily/{date}")
async def get_daily_report(date: str):
    """Génère un rapport journalier pour une date spécifique"""
    try:
        report_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Générer le rapport (avec données simulées)
    pdf_content = report_generator.generate_daily_report(
        date=report_date,
        alerts=[],  # À remplacer par vraies données
        cameras=[],
        counting_data={}
    )
    
    filename = f"ohmvision_daily_{date}.pdf"
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ============================================================================
# Dashboard Exécutif
# ============================================================================

@router.get("/executive/kpis")
async def get_executive_kpis(
    period: str = Query(default="today", enum=["today", "week", "month"])
):
    """
    Récupère les KPIs pour le dashboard exécutif
    """
    # Simuler des données (en production, requêter la BDD)
    return {
        "period": period,
        "kpis": {
            "total_alerts": {"value": 42, "trend": -5, "trend_pct": -10.6},
            "critical_alerts": {"value": 3, "trend": -2, "trend_pct": -40.0},
            "uptime": {"value": 99.2, "unit": "%", "trend": 0.1},
            "avg_response_time": {"value": 2.3, "unit": "sec", "trend": -0.5},
            "ppe_compliance": {"value": 94.5, "unit": "%", "trend": 2.1},
            "visitor_count": {"value": 1250, "trend": 150, "trend_pct": 13.6},
            "incidents_prevented": {"value": 8, "trend": 3},
            "cost_savings": {"value": 15000, "unit": "€", "trend": 2000}
        },
        "alerts_by_severity": {
            "critical": 3,
            "high": 12,
            "warning": 27
        },
        "top_cameras": [
            {"name": "Entrée principale", "alerts": 15},
            {"name": "Parking", "alerts": 10},
            {"name": "Zone stockage", "alerts": 8}
        ],
        "recent_incidents": [
            {"time": "14:32", "type": "fall", "camera": "Hall", "status": "resolved"},
            {"time": "11:15", "type": "ppe", "camera": "Atelier", "status": "resolved"},
            {"time": "09:45", "type": "intrusion", "camera": "Réserve", "status": "investigating"}
        ]
    }


@router.get("/executive/trends")
async def get_executive_trends(days: int = Query(default=30, ge=7, le=90)):
    """Récupère les tendances pour le dashboard exécutif"""
    # Générer des données de tendance
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") 
             for i in range(days, 0, -1)]
    
    import random
    return {
        "dates": dates,
        "series": {
            "alerts": [random.randint(20, 60) for _ in dates],
            "visitors": [random.randint(800, 1500) for _ in dates],
            "ppe_compliance": [random.uniform(88, 98) for _ in dates],
            "incidents": [random.randint(0, 5) for _ in dates]
        }
    }
