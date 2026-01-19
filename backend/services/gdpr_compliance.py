"""
OhmVision - RGPD/GDPR Compliance Service
=========================================
Service de conformité RGPD pour Ohm Tronic
Entreprise: OHM TRONIC
Adresse: 64 Avenue Marinville, 94100 Saint-Maur-des-Fossés
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import hashlib
import cv2
import numpy as np
from pydantic import BaseModel, EmailStr

from models.models import User, Client, Camera, Alert, Contract
from core.database import get_db


class ConsentType(str, Enum):
    """Types de consentement RGPD"""
    VIDEO_RECORDING = "video_recording"
    FACE_DETECTION = "face_detection"
    AUDIO_RECORDING = "audio_recording"
    DATA_PROCESSING = "data_processing"
    MARKETING = "marketing"
    ANALYTICS = "analytics"


class DataRetentionPolicy(str, Enum):
    """Politiques de rétention des données"""
    DAYS_7 = "7_days"
    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    YEAR_1 = "1_year"
    CUSTOM = "custom"


class GDPRRequest(BaseModel):
    """Modèle pour requête RGPD"""
    user_id: int
    request_type: str  # access, rectification, erasure, portability
    email: EmailStr
    reason: Optional[str] = None


class ConsentRecord(BaseModel):
    """Enregistrement de consentement"""
    user_id: int
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class GDPRComplianceService:
    """
    Service de conformité RGPD
    
    Fonctionnalités:
    - Gestion des consentements
    - Anonymisation des données
    - Droit à l'oubli
    - Portabilité des données
    - Registre des traitements
    - Notification de violation
    """
    
    COMPANY_INFO = {
        "name": "OHM TRONIC",
        "address": "64 Avenue Marinville",
        "postal_code": "94100",
        "city": "Saint-Maur-des-Fossés",
        "country": "France",
        "dpo_email": "dpo@ohmtronic.com",  # À configurer
        "privacy_policy_url": "https://ohmvision.com/privacy",  # À configurer
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.consent_storage = {}  # En production: base de données dédiée
        self.audit_log = []
    
    # =========================================================================
    # CONSENTEMENT (Art. 6 & 7 RGPD)
    # =========================================================================
    
    async def request_consent(
        self,
        user_id: int,
        consent_types: List[ConsentType],
        purpose: str,
        duration_days: int = 365
    ) -> Dict[str, Any]:
        """
        Demander le consentement utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            consent_types: Types de consentement requis
            purpose: Finalité du traitement
            duration_days: Durée de validité du consentement
        
        Returns:
            Lien vers formulaire de consentement
        """
        consent_id = hashlib.sha256(
            f"{user_id}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        consent_request = {
            "consent_id": consent_id,
            "user_id": user_id,
            "consent_types": [ct.value for ct in consent_types],
            "purpose": purpose,
            "duration_days": duration_days,
            "requested_at": datetime.now().isoformat(),
            "status": "pending",
            "company": self.COMPANY_INFO
        }
        
        self.consent_storage[consent_id] = consent_request
        
        self._log_audit(
            action="consent_requested",
            user_id=user_id,
            details={"consent_id": consent_id, "types": [ct.value for ct in consent_types]}
        )
        
        return {
            "consent_id": consent_id,
            "consent_url": f"/gdpr/consent/{consent_id}",
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
            "required_consents": [ct.value for ct in consent_types]
        }
    
    async def grant_consent(
        self,
        consent_id: str,
        granted_consents: Dict[ConsentType, bool],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Enregistrer le consentement donné"""
        if consent_id not in self.consent_storage:
            raise ValueError("Consent ID invalide")
        
        consent_request = self.consent_storage[consent_id]
        
        # Enregistrer chaque consentement
        for consent_type, granted in granted_consents.items():
            record = ConsentRecord(
                user_id=consent_request["user_id"],
                consent_type=consent_type,
                granted=granted,
                timestamp=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Stocker dans la base (simplifié ici)
            self._store_consent(record)
        
        consent_request["status"] = "completed"
        consent_request["completed_at"] = datetime.now().isoformat()
        
        self._log_audit(
            action="consent_granted",
            user_id=consent_request["user_id"],
            details={"consent_id": consent_id, "granted": granted_consents}
        )
        
        return True
    
    async def check_consent(self, user_id: int, consent_type: ConsentType) -> bool:
        """Vérifier si le consentement est accordé"""
        # En production: requête base de données
        for consent in self.consent_storage.values():
            if consent.get("user_id") == user_id and consent.get("status") == "completed":
                return True
        return False
    
    async def withdraw_consent(self, user_id: int, consent_type: ConsentType) -> bool:
        """Retirer le consentement (Art. 7.3 RGPD)"""
        self._log_audit(
            action="consent_withdrawn",
            user_id=user_id,
            details={"consent_type": consent_type.value}
        )
        
        # Arrêter le traitement associé
        await self._stop_processing_for_consent_type(user_id, consent_type)
        
        return True
    
    # =========================================================================
    # ANONYMISATION & PSEUDONYMISATION (Art. 25 RGPD)
    # =========================================================================
    
    def anonymize_face(self, frame: np.ndarray, bbox: tuple) -> np.ndarray:
        """
        Anonymiser un visage dans une image
        
        Args:
            frame: Image OpenCV
            bbox: (x1, y1, x2, y2) coordonnées du visage
        
        Returns:
            Image avec visage flouté
        """
        x1, y1, x2, y2 = bbox
        
        # Extraire la région du visage
        face_region = frame[y1:y2, x1:x2]
        
        # Flouter fortement (kernel 99x99 pour vraie anonymisation)
        blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
        
        # Remplacer dans l'image
        frame[y1:y2, x1:x2] = blurred_face
        
        return frame
    
    def anonymize_license_plate(self, frame: np.ndarray, bbox: tuple) -> np.ndarray:
        """Anonymiser une plaque d'immatriculation"""
        x1, y1, x2, y2 = bbox
        
        # Pixeliser la zone
        plate_region = frame[y1:y2, x1:x2]
        
        # Réduire puis agrandir pour effet pixelisé
        small = cv2.resize(plate_region, (8, 4), interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(small, (x2-x1, y2-y1), interpolation=cv2.INTER_NEAREST)
        
        frame[y1:y2, x1:x2] = pixelated
        
        return frame
    
    def pseudonymize_user_data(self, user_data: Dict) -> Dict:
        """
        Pseudonymiser les données utilisateur
        
        Remplace les données identifiantes par des pseudonymes
        """
        sensitive_fields = ["email", "first_name", "last_name", "phone", "address"]
        
        pseudonymized = user_data.copy()
        
        for field in sensitive_fields:
            if field in pseudonymized and pseudonymized[field]:
                # Hash SHA-256 + salt
                salt = "ohmvision_gdpr_salt"  # À configurer de manière sécurisée
                hashed = hashlib.sha256(
                    f"{pseudonymized[field]}{salt}".encode()
                ).hexdigest()[:16]
                
                pseudonymized[field] = f"ANON_{hashed}"
        
        return pseudonymized
    
    # =========================================================================
    # DROIT À L'OUBLI (Art. 17 RGPD)
    # =========================================================================
    
    async def delete_user_data(self, user_id: int, reason: str = "user_request") -> Dict[str, Any]:
        """
        Effacer toutes les données d'un utilisateur (droit à l'oubli)
        
        Args:
            user_id: ID utilisateur
            reason: Raison de la suppression
        
        Returns:
            Rapport de suppression
        """
        deletion_report = {
            "user_id": user_id,
            "requested_at": datetime.now().isoformat(),
            "reason": reason,
            "deleted_items": {}
        }
        
        # 1. Anonymiser les alertes (conservation légale possible)
        alerts_result = await self.db.execute(
            select(Alert).where(Alert.camera_id.in_(
                select(Camera.id).where(Camera.client_id == user_id)
            ))
        )
        alerts = alerts_result.scalars().all()
        
        for alert in alerts:
            # Anonymiser plutôt que supprimer (traçabilité)
            alert.metadata = {"anonymized": True, "date": datetime.now().isoformat()}
        
        deletion_report["deleted_items"]["alerts_anonymized"] = len(alerts)
        
        # 2. Supprimer les vidéos enregistrées
        # TODO: Implémenter suppression fichiers vidéo
        deletion_report["deleted_items"]["videos_deleted"] = 0
        
        # 3. Supprimer les caméras
        await self.db.execute(
            delete(Camera).where(Camera.client_id == user_id)
        )
        deletion_report["deleted_items"]["cameras_deleted"] = True
        
        # 4. Anonymiser l'utilisateur (conservation compte pour facturation)
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            user.email = f"deleted_{user_id}@anonymized.local"
            user.first_name = "DELETED"
            user.last_name = "USER"
            user.is_active = False
            deletion_report["deleted_items"]["user_anonymized"] = True
        
        await self.db.commit()
        
        # Log audit
        self._log_audit(
            action="user_data_deleted",
            user_id=user_id,
            details=deletion_report
        )
        
        deletion_report["completed_at"] = datetime.now().isoformat()
        deletion_report["status"] = "completed"
        
        return deletion_report
    
    # =========================================================================
    # PORTABILITÉ DES DONNÉES (Art. 20 RGPD)
    # =========================================================================
    
    async def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Exporter toutes les données d'un utilisateur (format JSON)
        
        Returns:
            Données structurées au format machine-readable
        """
        export_data = {
            "export_date": datetime.now().isoformat(),
            "user_id": user_id,
            "company": self.COMPANY_INFO,
            "data": {}
        }
        
        # 1. Données utilisateur
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if user:
            export_data["data"]["user"] = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        
        # 2. Caméras
        cameras_result = await self.db.execute(
            select(Camera).where(Camera.client_id == user_id)
        )
        cameras = cameras_result.scalars().all()
        
        export_data["data"]["cameras"] = [
            {
                "name": cam.name,
                "location": cam.location,
                "created_at": cam.created_at.isoformat() if cam.created_at else None
            }
            for cam in cameras
        ]
        
        # 3. Alertes (30 derniers jours)
        # TODO: Implémenter export alertes
        
        # 4. Consentements
        export_data["data"]["consents"] = [
            consent for consent in self.consent_storage.values()
            if consent.get("user_id") == user_id
        ]
        
        self._log_audit(
            action="data_exported",
            user_id=user_id,
            details={"items_count": len(export_data["data"])}
        )
        
        return export_data
    
    # =========================================================================
    # REGISTRE DES TRAITEMENTS (Art. 30 RGPD)
    # =========================================================================
    
    def get_processing_registry(self) -> List[Dict[str, Any]]:
        """
        Registre des activités de traitement (obligatoire RGPD)
        
        Returns:
            Liste des traitements effectués
        """
        return [
            {
                "name": "Vidéosurveillance intelligente",
                "controller": self.COMPANY_INFO,
                "purpose": "Sécurité des biens et des personnes",
                "legal_basis": "Consentement (Art. 6.1.a) + Intérêt légitime (Art. 6.1.f)",
                "categories_of_data": [
                    "Images vidéo",
                    "Données de détection (personnes, véhicules)",
                    "Métadonnées (date, heure, localisation caméra)"
                ],
                "categories_of_recipients": [
                    "Personnel autorisé du client",
                    "Sous-traitants techniques (hébergement cloud si applicable)"
                ],
                "retention_period": "Selon package: 7 à 365 jours",
                "security_measures": [
                    "Chiffrement des données en transit (TLS)",
                    "Authentification forte (JWT)",
                    "Journalisation des accès",
                    "Anonymisation automatique possible"
                ]
            },
            {
                "name": "Analyse comportementale par IA",
                "controller": self.COMPANY_INFO,
                "purpose": "Détection d'incidents et prévention des risques",
                "legal_basis": "Consentement explicite (Art. 6.1.a)",
                "categories_of_data": [
                    "Données biométriques (détection de chute)",
                    "Patterns comportementaux",
                    "Données audio (si activé)"
                ],
                "retention_period": "30-90 jours selon package",
                "security_measures": [
                    "Pseudonymisation des détections",
                    "Suppression automatique après rétention",
                    "Accès restreint par rôle"
                ]
            },
            {
                "name": "Gestion des utilisateurs et facturation",
                "controller": self.COMPANY_INFO,
                "purpose": "Gestion commerciale et comptable",
                "legal_basis": "Exécution du contrat (Art. 6.1.b)",
                "categories_of_data": [
                    "Identité (nom, prénom, email)",
                    "Données de facturation (SIRET, adresse)",
                    "Historique des paiements"
                ],
                "retention_period": "10 ans (obligations légales comptables)",
                "security_measures": [
                    "Chiffrement base de données",
                    "Accès administrateur uniquement",
                    "Sauvegarde chiffrée"
                ]
            }
        ]
    
    # =========================================================================
    # NOTIFICATION DE VIOLATION (Art. 33 & 34 RGPD)
    # =========================================================================
    
    async def report_data_breach(
        self,
        breach_type: str,
        affected_users: List[int],
        description: str,
        severity: str = "high"
    ) -> Dict[str, Any]:
        """
        Signaler une violation de données
        
        RGPD exige notification sous 72h à la CNIL
        
        Args:
            breach_type: Type de violation
            affected_users: Liste des utilisateurs impactés
            description: Description de la violation
            severity: Gravité (low, medium, high, critical)
        
        Returns:
            Rapport de violation
        """
        breach_report = {
            "breach_id": hashlib.sha256(
                f"breach_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16],
            "timestamp": datetime.now().isoformat(),
            "type": breach_type,
            "severity": severity,
            "description": description,
            "affected_users_count": len(affected_users),
            "affected_users": affected_users,
            "notification_status": {
                "cnil": "pending",  # Autorité de contrôle
                "users": "pending"
            },
            "remediation_actions": []
        }
        
        # Si gravité élevée: notification CNIL obligatoire
        if severity in ["high", "critical"]:
            breach_report["cnil_notification_required"] = True
            breach_report["cnil_deadline"] = (
                datetime.now() + timedelta(hours=72)
            ).isoformat()
            
            # TODO: Envoyer email automatique au DPO
            # await self._notify_dpo(breach_report)
        
        # Notification utilisateurs si risque élevé pour leurs droits
        if severity == "critical":
            breach_report["user_notification_required"] = True
            # TODO: Envoyer emails aux utilisateurs affectés
        
        self._log_audit(
            action="data_breach_reported",
            user_id=None,
            details=breach_report
        )
        
        return breach_report
    
    # =========================================================================
    # RÉTENTION DES DONNÉES
    # =========================================================================
    
    async def apply_retention_policy(
        self,
        policy: DataRetentionPolicy,
        camera_id: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Appliquer une politique de rétention
        
        Supprime automatiquement les données expirées
        """
        retention_days = {
            DataRetentionPolicy.DAYS_7: 7,
            DataRetentionPolicy.DAYS_30: 30,
            DataRetentionPolicy.DAYS_90: 90,
            DataRetentionPolicy.YEAR_1: 365
        }
        
        days = retention_days.get(policy, 30)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Supprimer les alertes expirées
        result = await self.db.execute(
            delete(Alert).where(Alert.created_at < cutoff_date)
        )
        
        deleted_count = result.rowcount
        
        await self.db.commit()
        
        self._log_audit(
            action="retention_policy_applied",
            user_id=None,
            details={
                "policy": policy.value,
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_alerts": deleted_count
            }
        )
        
        return {"deleted_alerts": deleted_count}
    
    # =========================================================================
    # UTILITAIRES
    # =========================================================================
    
    def _store_consent(self, record: ConsentRecord):
        """Stocker un consentement (à implémenter en DB)"""
        # En production: INSERT dans table `consents`
        pass
    
    async def _stop_processing_for_consent_type(
        self,
        user_id: int,
        consent_type: ConsentType
    ):
        """Arrêter le traitement lié à un type de consentement retiré"""
        # Exemple: désactiver la détection de visages si consent retiré
        if consent_type == ConsentType.FACE_DETECTION:
            # Mettre à jour config caméras
            await self.db.execute(
                update(Camera)
                .where(Camera.client_id == user_id)
                .values(face_detection_enabled=False)
            )
            await self.db.commit()
    
    def _log_audit(self, action: str, user_id: Optional[int], details: Dict):
        """Journaliser une action RGPD (traçabilité)"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details
        }
        self.audit_log.append(audit_entry)
        
        # En production: INSERT dans table `gdpr_audit_log`
        print(f"[GDPR AUDIT] {action}: {json.dumps(details, indent=2)}")
    
    def get_audit_log(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Récupérer le journal d'audit RGPD"""
        logs = self.audit_log
        
        if user_id:
            logs = [log for log in logs if log.get("user_id") == user_id]
        
        if start_date:
            logs = [
                log for log in logs
                if datetime.fromisoformat(log["timestamp"]) >= start_date
            ]
        
        return logs


# =============================================================================
# HELPERS
# =============================================================================

async def get_gdpr_service(db: AsyncSession = Depends(get_db)) -> GDPRComplianceService:
    """Dependency pour obtenir le service RGPD"""
    return GDPRComplianceService(db)
