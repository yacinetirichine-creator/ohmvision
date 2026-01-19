"""
OhmVision - API RGPD/GDPR
=========================
Endpoints pour conformité RGPD
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from core.database import get_db
from services.gdpr_compliance import (
    GDPRComplianceService,
    get_gdpr_service,
    ConsentType,
    DataRetentionPolicy,
    GDPRRequest
)
from api.auth import get_current_user
from models.models import User

router = APIRouter(prefix="/api/gdpr", tags=["RGPD/GDPR"])


# =============================================================================
# SCHEMAS
# =============================================================================

class ConsentRequestSchema(BaseModel):
    consent_types: List[ConsentType]
    purpose: str
    duration_days: int = 365


class GrantConsentSchema(BaseModel):
    consent_id: str
    granted_consents: dict  # {consent_type: bool}


class DataExportRequest(BaseModel):
    email: EmailStr
    format: str = "json"  # json, csv, xml


class DataDeletionRequest(BaseModel):
    email: EmailStr
    reason: Optional[str] = "user_request"
    confirmation_code: str  # Code envoyé par email pour confirmer


class BreachReportSchema(BaseModel):
    breach_type: str
    description: str
    severity: str = "high"


# =============================================================================
# ENDPOINTS - CONSENTEMENT
# =============================================================================

@router.post("/consent/request")
async def request_user_consent(
    data: ConsentRequestSchema,
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """
    Demander le consentement utilisateur pour traitement de données
    
    Conforme Art. 6 & 7 RGPD
    """
    result = await gdpr_service.request_consent(
        user_id=current_user.id,
        consent_types=data.consent_types,
        purpose=data.purpose,
        duration_days=data.duration_days
    )
    
    return {
        "status": "success",
        "message": "Demande de consentement créée",
        "data": result
    }


@router.post("/consent/grant")
async def grant_consent(
    data: GrantConsentSchema,
    request: Request,
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """
    Enregistrer le consentement donné par l'utilisateur
    
    Peut être appelé sans authentification (lien email)
    """
    # Convertir dict en ConsentType
    granted_consents = {
        ConsentType(k): v for k, v in data.granted_consents.items()
    }
    
    success = await gdpr_service.grant_consent(
        consent_id=data.consent_id,
        granted_consents=granted_consents,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "status": "success",
        "message": "Consentement enregistré",
        "granted": success
    }


@router.post("/consent/withdraw/{consent_type}")
async def withdraw_consent(
    consent_type: ConsentType,
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """
    Retirer un consentement (Art. 7.3 RGPD)
    
    L'utilisateur peut retirer son consentement à tout moment
    """
    success = await gdpr_service.withdraw_consent(
        user_id=current_user.id,
        consent_type=consent_type
    )
    
    return {
        "status": "success",
        "message": f"Consentement {consent_type.value} retiré. Le traitement associé sera arrêté.",
        "withdrawn": success
    }


@router.get("/consent/status")
async def get_consent_status(
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """Obtenir le statut de tous les consentements de l'utilisateur"""
    consents = {}
    
    for consent_type in ConsentType:
        consents[consent_type.value] = await gdpr_service.check_consent(
            user_id=current_user.id,
            consent_type=consent_type
        )
    
    return {
        "user_id": current_user.id,
        "consents": consents,
        "last_updated": "2026-01-19"  # TODO: Récupérer de la DB
    }


# =============================================================================
# ENDPOINTS - DROIT D'ACCÈS (Art. 15 RGPD)
# =============================================================================

@router.get("/data/export")
async def export_my_data(
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """
    Exporter toutes mes données (droit à la portabilité - Art. 20 RGPD)
    
    Retourne les données dans un format structuré et machine-readable
    """
    export_data = await gdpr_service.export_user_data(user_id=current_user.id)
    
    return {
        "status": "success",
        "message": "Export de données effectué",
        "data": export_data
    }


# =============================================================================
# ENDPOINTS - DROIT À L'OUBLI (Art. 17 RGPD)
# =============================================================================

@router.post("/data/delete")
async def request_data_deletion(
    data: DataDeletionRequest,
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """
    Demander la suppression de toutes mes données (droit à l'oubli)
    
    ATTENTION: Action irréversible
    Conformité Art. 17 RGPD
    """
    # Vérifier que l'email correspond
    if data.email != current_user.email:
        raise HTTPException(
            status_code=400,
            detail="L'email ne correspond pas à votre compte"
        )
    
    # TODO: Vérifier le code de confirmation (envoyé par email)
    # if not verify_confirmation_code(data.confirmation_code):
    #     raise HTTPException(status_code=400, detail="Code de confirmation invalide")
    
    deletion_report = await gdpr_service.delete_user_data(
        user_id=current_user.id,
        reason=data.reason
    )
    
    return {
        "status": "success",
        "message": "Vos données ont été supprimées conformément au RGPD",
        "report": deletion_report,
        "warning": "Votre compte a été anonymisé. Vous ne pourrez plus vous connecter."
    }


# =============================================================================
# ENDPOINTS - ADMINISTRATION (Réservé admin/DPO)
# =============================================================================

@router.get("/registry/processing-activities")
async def get_processing_registry(
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """
    Registre des activités de traitement (Art. 30 RGPD)
    
    Obligatoire pour toute entreprise
    Réservé: Admin ou DPO
    """
    # TODO: Vérifier rôle admin
    if current_user.role not in ["admin", "support"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    registry = gdpr_service.get_processing_registry()
    
    return {
        "company": gdpr_service.COMPANY_INFO,
        "processing_activities": registry,
        "generated_at": "2026-01-19"
    }


@router.post("/breach/report")
async def report_data_breach(
    data: BreachReportSchema,
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Signaler une violation de données (Art. 33 RGPD)
    
    Notification CNIL obligatoire sous 72h si violation grave
    Réservé: Admin uniquement
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    # TODO: Récupérer la liste des utilisateurs affectés
    affected_users = []  # À implémenter
    
    breach_report = await gdpr_service.report_data_breach(
        breach_type=data.breach_type,
        affected_users=affected_users,
        description=data.description,
        severity=data.severity
    )
    
    return {
        "status": "success",
        "message": "Violation signalée. Procédure RGPD déclenchée.",
        "report": breach_report,
        "next_steps": [
            "Notifier la CNIL sous 72h si gravité élevée",
            "Notifier les utilisateurs affectés si risque critique",
            "Documenter les mesures correctives",
            "Mettre à jour le registre des violations"
        ]
    }


@router.get("/audit/log")
async def get_gdpr_audit_log(
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """
    Journal d'audit RGPD (traçabilité)
    
    Réservé: Admin ou utilisateur pour ses propres données
    """
    # Si user_id fourni, vérifier droits
    if user_id and user_id != current_user.id:
        if current_user.role not in ["admin", "support"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    target_user_id = user_id or current_user.id
    
    audit_log = gdpr_service.get_audit_log(user_id=target_user_id)
    
    return {
        "user_id": target_user_id,
        "audit_entries": audit_log,
        "count": len(audit_log)
    }


@router.post("/retention/apply")
async def apply_retention_policy(
    policy: DataRetentionPolicy,
    camera_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    gdpr_service: GDPRComplianceService = Depends(get_gdpr_service)
):
    """
    Appliquer une politique de rétention des données
    
    Supprime automatiquement les données expirées
    Réservé: Admin
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    result = await gdpr_service.apply_retention_policy(
        policy=policy,
        camera_id=camera_id
    )
    
    return {
        "status": "success",
        "message": f"Politique de rétention {policy.value} appliquée",
        "deleted_items": result
    }


# =============================================================================
# ENDPOINTS - INFORMATIONS PUBLIQUES
# =============================================================================

@router.get("/privacy-policy")
async def get_privacy_policy():
    """
    Politique de confidentialité (Art. 13 & 14 RGPD)
    
    Accessible sans authentification
    """
    return {
        "company": GDPRComplianceService.COMPANY_INFO,
        "last_updated": "2026-01-19",
        "policy": {
            "data_controller": {
                "name": "OHM TRONIC",
                "address": "64 Avenue Marinville, 94100 Saint-Maur-des-Fossés, France",
                "contact": "dpo@ohmtronic.com"
            },
            "purpose": "Fourniture de services de vidéosurveillance intelligente",
            "legal_basis": [
                "Consentement (Art. 6.1.a RGPD)",
                "Exécution du contrat (Art. 6.1.b RGPD)",
                "Intérêt légitime (Art. 6.1.f RGPD)"
            ],
            "data_collected": [
                "Identité (nom, prénom, email)",
                "Données de connexion (IP, logs)",
                "Images vidéo et détections IA",
                "Données audio (si activé)"
            ],
            "retention_periods": {
                "videos": "7 à 365 jours selon package",
                "user_account": "Durée du contrat + 10 ans (obligations comptables)",
                "logs": "1 an"
            },
            "your_rights": [
                "Droit d'accès (Art. 15)",
                "Droit de rectification (Art. 16)",
                "Droit à l'effacement (Art. 17)",
                "Droit à la portabilité (Art. 20)",
                "Droit d'opposition (Art. 21)",
                "Droit de retirer le consentement (Art. 7.3)"
            ],
            "how_to_exercise_rights": "Contactez dpo@ohmtronic.com ou utilisez les endpoints /api/gdpr/*",
            "cnil": {
                "name": "Commission Nationale de l'Informatique et des Libertés",
                "website": "https://www.cnil.fr",
                "complaint": "Vous pouvez déposer une réclamation auprès de la CNIL"
            }
        }
    }


@router.get("/data-protection-officer")
async def get_dpo_info():
    """Informations sur le Délégué à la Protection des Données (DPO)"""
    return {
        "dpo": {
            "company": "OHM TRONIC",
            "email": "dpo@ohmtronic.com",
            "address": "64 Avenue Marinville, 94100 Saint-Maur-des-Fossés, France",
            "role": "Délégué à la Protection des Données (DPO)",
            "responsibilities": [
                "Veiller à la conformité RGPD",
                "Conseiller sur les obligations légales",
                "Point de contact avec la CNIL",
                "Traiter les demandes des personnes concernées"
            ]
        }
    }
