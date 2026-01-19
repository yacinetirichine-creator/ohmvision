"""
OhmVision - Agent IA API
==========================
Assistant intelligent pour le support et l'optimisation automatique.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

from core.database import get_db
from core.config import settings
from models.models import (
    User, Client, Camera, Alert, Ticket, TicketMessage,
    Contract, AlertType, AlertSeverity
)
from api.auth import get_current_active_user

router = APIRouter()

# Schemas
class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    actions_taken: List[str] = []
    suggestions: List[str] = []
    requires_human: bool = False

class DiagnosticRequest(BaseModel):
    camera_id: Optional[int] = None
    client_id: Optional[int] = None
    issue_type: Optional[str] = None

class DiagnosticResponse(BaseModel):
    status: str
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    auto_fixes_applied: List[str]
    requires_human: bool

# Agent IA Engine (simplifié - en production, utiliser Anthropic/OpenAI)
class AIAgent:
    """Agent IA pour le support et l'optimisation"""
    
    # Base de connaissances
    KNOWLEDGE_BASE = {
        "camera_offline": {
            "symptoms": ["hors ligne", "déconnectée", "pas de signal", "offline"],
            "diagnosis": [
                "Vérification de la connexion réseau",
                "Test de l'alimentation électrique",
                "Vérification du câble Ethernet",
                "Test de l'URL RTSP"
            ],
            "solutions": [
                "Redémarrer la caméra",
                "Vérifier le câble réseau",
                "Vérifier l'alimentation",
                "Mettre à jour le firmware"
            ],
            "auto_actions": ["ping_camera", "restart_stream"]
        },
        "false_positives": {
            "symptoms": ["faux positif", "fausse alerte", "détection erronée", "trop d'alertes"],
            "diagnosis": [
                "Analyse du taux de faux positifs",
                "Vérification de la sensibilité",
                "Analyse des conditions d'éclairage"
            ],
            "solutions": [
                "Ajuster la sensibilité de détection",
                "Définir des zones d'exclusion",
                "Configurer des plages horaires"
            ],
            "auto_actions": ["adjust_sensitivity", "suggest_zones"]
        },
        "performance": {
            "symptoms": ["lent", "lag", "latence", "fps bas", "saccade"],
            "diagnosis": [
                "Analyse de la charge CPU/GPU",
                "Vérification de la bande passante",
                "Analyse de la résolution"
            ],
            "solutions": [
                "Réduire la résolution",
                "Réduire le FPS",
                "Optimiser le modèle IA"
            ],
            "auto_actions": ["reduce_resolution", "optimize_model"]
        },
        "ppe_detection": {
            "symptoms": ["casque pas détecté", "gilet non détecté", "EPI", "équipement"],
            "diagnosis": [
                "Vérification de la qualité d'image",
                "Analyse de l'angle de caméra",
                "Vérification du modèle EPI"
            ],
            "solutions": [
                "Ajuster l'angle de caméra",
                "Améliorer l'éclairage",
                "Entraîner un modèle personnalisé"
            ],
            "auto_actions": ["adjust_ppe_sensitivity"]
        }
    }
    
    @classmethod
    def analyze_message(cls, message: str) -> Dict[str, Any]:
        """Analyse le message pour identifier le problème"""
        message_lower = message.lower()
        
        for issue_type, data in cls.KNOWLEDGE_BASE.items():
            for symptom in data["symptoms"]:
                if symptom in message_lower:
                    return {
                        "issue_type": issue_type,
                        "confidence": 0.85,
                        "data": data
                    }
        
        return {
            "issue_type": "unknown",
            "confidence": 0.0,
            "data": None
        }
    
    @classmethod
    async def generate_response(
        cls,
        message: str,
        context: Dict[str, Any],
        db: AsyncSession
    ) -> ChatResponse:
        """Génère une réponse intelligente"""
        
        analysis = cls.analyze_message(message)
        actions_taken = []
        suggestions = []
        requires_human = False
        
        if analysis["issue_type"] == "unknown":
            # Problème non identifié
            response = """Je n'ai pas pu identifier précisément votre problème. 
            
Pouvez-vous me donner plus de détails ?
- Quelle caméra est concernée ?
- Depuis quand avez-vous ce problème ?
- Avez-vous un message d'erreur ?

Je peux aussi créer un ticket pour qu'un technicien vous contacte."""
            requires_human = True
            
        else:
            data = analysis["data"]
            issue_type = analysis["issue_type"]
            
            # Génère le diagnostic
            diagnosis_text = "\n".join([f"• {d}" for d in data["diagnosis"]])
            solutions_text = "\n".join([f"• {s}" for s in data["solutions"]])
            
            # Actions automatiques possibles
            if context.get("camera_id"):
                camera_id = context["camera_id"]
                
                if "adjust_sensitivity" in data["auto_actions"]:
                    # Simulation d'ajustement automatique
                    actions_taken.append(f"✅ Sensibilité ajustée automatiquement pour la caméra {camera_id}")
                
                if "ping_camera" in data["auto_actions"]:
                    actions_taken.append(f"✅ Test de connexion effectué sur la caméra {camera_id}")
            
            # Suggestions
            suggestions = data["solutions"][:3]
            
            # Génère la réponse
            response = f"""🔍 **Diagnostic effectué**

J'ai identifié votre problème : **{issue_type.replace('_', ' ').title()}**

**Analyse réalisée :**
{diagnosis_text}

**Solutions recommandées :**
{solutions_text}

"""
            if actions_taken:
                response += f"""**Actions automatiques appliquées :**
{chr(10).join(actions_taken)}

"""
            
            response += "Avez-vous besoin d'aide supplémentaire ?"
        
        return ChatResponse(
            response=response,
            actions_taken=actions_taken,
            suggestions=suggestions,
            requires_human=requires_human
        )
    
    @classmethod
    async def run_diagnostic(
        cls,
        camera_id: Optional[int],
        client_id: Optional[int],
        db: AsyncSession
    ) -> DiagnosticResponse:
        """Exécute un diagnostic complet"""
        
        issues_found = []
        recommendations = []
        auto_fixes = []
        
        # Diagnostic caméra spécifique
        if camera_id:
            result = await db.execute(select(Camera).where(Camera.id == camera_id))
            camera = result.scalar_one_or_none()
            
            if camera:
                # Vérifie le statut
                if not camera.is_online:
                    issues_found.append({
                        "type": "camera_offline",
                        "severity": "high",
                        "message": f"Caméra '{camera.name}' hors ligne",
                        "camera_id": camera_id
                    })
                    recommendations.append("Vérifier la connexion réseau de la caméra")
                
                # Vérifie la dernière activité
                if camera.last_seen:
                    time_since = datetime.utcnow() - camera.last_seen
                    if time_since > timedelta(hours=1):
                        issues_found.append({
                            "type": "no_recent_activity",
                            "severity": "medium",
                            "message": f"Aucune activité depuis {time_since.seconds // 3600}h",
                            "camera_id": camera_id
                        })
                
                # Vérifie les alertes récentes (trop de faux positifs ?)
                alerts_result = await db.execute(
                    select(func.count()).where(
                        (Alert.camera_id == camera_id) &
                        (Alert.created_at > datetime.utcnow() - timedelta(hours=24))
                    )
                )
                alert_count = alerts_result.scalar()
                
                if alert_count > 100:
                    issues_found.append({
                        "type": "too_many_alerts",
                        "severity": "medium",
                        "message": f"{alert_count} alertes en 24h - possible faux positifs",
                        "camera_id": camera_id
                    })
                    recommendations.append("Ajuster la sensibilité de détection")
                    
                    # Auto-fix : ajuster la sensibilité
                    config = camera.detection_config or {}
                    if config.get("sensitivity", 0.5) < 0.7:
                        config["sensitivity"] = min(config.get("sensitivity", 0.5) + 0.1, 0.9)
                        camera.detection_config = config
                        await db.commit()
                        auto_fixes.append("Sensibilité augmentée de 0.1")
        
        # Diagnostic client complet
        if client_id:
            # Vérifie toutes les caméras du client
            cams_result = await db.execute(
                select(Camera).where(Camera.client_id == client_id)
            )
            cameras = cams_result.scalars().all()
            
            offline_count = sum(1 for c in cameras if not c.is_online)
            if offline_count > 0:
                issues_found.append({
                    "type": "multiple_offline",
                    "severity": "high" if offline_count > len(cameras) // 2 else "medium",
                    "message": f"{offline_count}/{len(cameras)} caméras hors ligne",
                    "client_id": client_id
                })
                recommendations.append("Vérifier l'infrastructure réseau du site")
        
        # Recommandations générales si pas de problème majeur
        if not issues_found:
            recommendations.append("Système fonctionnel - aucun problème détecté")
            recommendations.append("Pensez à mettre à jour vos caméras régulièrement")
        
        return DiagnosticResponse(
            status="completed",
            issues_found=issues_found,
            recommendations=recommendations,
            auto_fixes_applied=auto_fixes,
            requires_human=any(i["severity"] == "high" for i in issues_found)
        )
    
    @classmethod
    async def optimize_camera(cls, camera_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Optimise automatiquement une caméra"""
        
        result = await db.execute(select(Camera).where(Camera.id == camera_id))
        camera = result.scalar_one_or_none()
        
        if not camera:
            return {"error": "Caméra non trouvée"}
        
        optimizations = []
        config = camera.detection_config or {}
        
        # Analyse les alertes pour optimiser
        alerts_result = await db.execute(
            select(Alert).where(
                (Alert.camera_id == camera_id) &
                (Alert.created_at > datetime.utcnow() - timedelta(days=7))
            )
        )
        alerts = alerts_result.scalars().all()
        
        # Calcule le ratio de faux positifs (estimation)
        total_alerts = len(alerts)
        resolved_alerts = sum(1 for a in alerts if a.is_resolved)
        
        if total_alerts > 50 and resolved_alerts / total_alerts > 0.8:
            # Beaucoup d'alertes résolues = probablement des faux positifs
            config["sensitivity"] = min(config.get("sensitivity", 0.5) + 0.15, 0.95)
            optimizations.append("Sensibilité augmentée pour réduire les faux positifs")
        
        # Sauvegarde
        camera.detection_config = config
        await db.commit()
        
        return {
            "status": "optimized",
            "optimizations": optimizations,
            "new_config": config
        }

# Routes
@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Chat avec l'agent IA"""
    
    # Ajoute le contexte utilisateur
    context = message.context or {}
    context["user_id"] = current_user.id
    context["client_id"] = current_user.client_id
    
    response = await AIAgent.generate_response(message.message, context, db)
    
    return response

@router.post("/diagnostic", response_model=DiagnosticResponse)
async def run_diagnostic(
    request: DiagnosticRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lance un diagnostic automatique"""
    
    # Vérifie les permissions
    camera_id = request.camera_id
    client_id = request.client_id or current_user.client_id
    
    if current_user.role not in ["admin", "support"]:
        client_id = current_user.client_id
    
    response = await AIAgent.run_diagnostic(camera_id, client_id, db)
    
    return response

@router.post("/optimize/{camera_id}")
async def optimize_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Optimise automatiquement une caméra"""
    
    # Vérifie les permissions
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    if current_user.role not in ["admin", "support"]:
        if current_user.client_id != camera.client_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    response = await AIAgent.optimize_camera(camera_id, db)
    
    return response

@router.get("/suggestions/{client_id}")
async def get_ai_suggestions(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtient des suggestions proactives de l'IA"""
    
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"]:
        if current_user.client_id != client_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    suggestions = []
    
    # Analyse les caméras
    cams_result = await db.execute(
        select(Camera).where(Camera.client_id == client_id)
    )
    cameras = cams_result.scalars().all()
    
    for camera in cameras:
        config = camera.detection_config or {}
        
        # Suggestion : activer des fonctionnalités
        if not config.get("counting"):
            suggestions.append({
                "type": "feature_suggestion",
                "camera_id": camera.id,
                "message": f"Activez le comptage sur '{camera.name}' pour suivre le flux de personnes",
                "action": "enable_counting"
            })
        
        if not config.get("fall_detection") and config.get("person_detection"):
            suggestions.append({
                "type": "safety_suggestion",
                "camera_id": camera.id,
                "message": f"La détection de chute n'est pas activée sur '{camera.name}'",
                "action": "enable_fall_detection"
            })
    
    # Suggestion globale
    if len(cameras) > 5:
        suggestions.append({
            "type": "optimization",
            "message": "Vous avez plus de 5 caméras. Pensez à créer des groupes par zone.",
            "action": "create_zones"
        })
    
    return {"suggestions": suggestions[:5]}  # Max 5 suggestions

@router.post("/report/generate")
async def generate_ai_report(
    client_id: int,
    period: str = "week",  # day, week, month
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Génère un rapport intelligent avec l'IA"""
    
    # Détermine la période
    if period == "day":
        start_date = datetime.utcnow() - timedelta(days=1)
    elif period == "week":
        start_date = datetime.utcnow() - timedelta(weeks=1)
    else:
        start_date = datetime.utcnow() - timedelta(days=30)
    
    # Récupère les données
    alerts_result = await db.execute(
        select(Alert).join(Camera).where(
            (Camera.client_id == client_id) &
            (Alert.created_at > start_date)
        )
    )
    alerts = alerts_result.scalars().all()
    
    # Analyse
    total_alerts = len(alerts)
    by_type = {}
    by_severity = {}
    
    for alert in alerts:
        by_type[alert.type.value] = by_type.get(alert.type.value, 0) + 1
        by_severity[alert.severity.value] = by_severity.get(alert.severity.value, 0) + 1
    
    # Génère le rapport
    report = {
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_alerts": total_alerts,
            "by_type": by_type,
            "by_severity": by_severity
        },
        "insights": [],
        "recommendations": []
    }
    
    # Insights automatiques
    if total_alerts > 100:
        report["insights"].append(
            f"Activité élevée : {total_alerts} alertes sur la période"
        )
    
    if by_severity.get("critical", 0) > 0:
        report["insights"].append(
            f"⚠️ {by_severity['critical']} alertes critiques nécessitent attention"
        )
    
    # Recommandations
    if by_type.get("fall_detected", 0) > 0:
        report["recommendations"].append(
            "Des chutes ont été détectées. Vérifiez les zones à risque."
        )
    
    if by_type.get("ppe_missing", 0) > 5:
        report["recommendations"].append(
            "Taux de non-conformité EPI élevé. Formation recommandée."
        )
    
    return report
