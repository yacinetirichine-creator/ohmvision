"""
OhmVision - API Setup & Onboarding
Gère la première configuration de l'application
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging
import os
import json
from datetime import datetime

from core.database import get_db
from models.models import User, Camera, SystemSettings
from api.auth import get_password_hash, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/setup", tags=["Setup"])


# ============================================================================
# Modèles
# ============================================================================

class SetupStatus(BaseModel):
    """État de la configuration"""
    is_first_run: bool
    has_admin: bool
    has_cameras: bool
    setup_completed: bool
    current_step: int  # 0=not started, 1=admin, 2=cameras, 3=detections, 4=done
    version: str = "1.0.0"


class AdminSetupRequest(BaseModel):
    """Création du compte admin initial"""
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2)
    company_name: Optional[str] = None


class CameraSetupRequest(BaseModel):
    """Ajout d'une caméra pendant le setup"""
    name: str
    ip: str
    rtsp_url: str
    username: Optional[str] = ""
    password: Optional[str] = ""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    enabled_detections: List[str] = []  # ["person", "fall", "fire", "ppe", "counting"]


class DetectionConfig(BaseModel):
    """Configuration des détections pour une caméra"""
    camera_id: int
    person_detection: bool = True
    fall_detection: bool = False
    fire_detection: bool = False
    ppe_detection: bool = False
    counting_enabled: bool = False
    counting_line: Optional[dict] = None  # {"x1": 0, "y1": 0, "x2": 100, "y2": 100}
    zones: List[dict] = []  # Zones de détection


class SetupCompleteRequest(BaseModel):
    """Finalisation du setup"""
    enable_notifications: bool = True
    notification_email: Optional[EmailStr] = None


class SetupCompleteResponse(BaseModel):
    """Réponse de finalisation"""
    success: bool
    message: str
    access_token: str
    dashboard_url: str = "/dashboard"


# ============================================================================
# Fichier de configuration local
# ============================================================================

SETUP_FILE = "/app/data/setup_status.json"


def load_setup_status() -> dict:
    """Charge l'état du setup depuis le fichier"""
    default = {
        "setup_completed": False,
        "current_step": 0,
        "completed_at": None
    }
    
    try:
        if os.path.exists(SETUP_FILE):
            with open(SETUP_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    
    return default


def save_setup_status(status: dict):
    """Sauvegarde l'état du setup"""
    try:
        os.makedirs(os.path.dirname(SETUP_FILE), exist_ok=True)
        with open(SETUP_FILE, 'w') as f:
            json.dump(status, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving setup status: {e}")


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/status", response_model=SetupStatus)
async def get_setup_status(db: AsyncSession = Depends(get_db)):
    """
    Vérifie l'état de la configuration initiale
    Appelé au démarrage de l'app pour savoir si le wizard doit s'afficher
    """
    # Vérifier si un admin existe
    result = await db.execute(
        select(func.count(User.id)).where(User.role == "admin")
    )
    admin_count = result.scalar()
    has_admin = admin_count > 0
    
    # Vérifier si des caméras existent
    result = await db.execute(select(func.count(Camera.id)))
    camera_count = result.scalar()
    has_cameras = camera_count > 0
    
    # Charger le statut du fichier
    file_status = load_setup_status()
    setup_completed = file_status.get("setup_completed", False)
    
    # Déterminer l'étape courante
    if setup_completed:
        current_step = 4
    elif has_cameras:
        current_step = 3
    elif has_admin:
        current_step = 2
    else:
        current_step = 0
    
    return SetupStatus(
        is_first_run=not has_admin,
        has_admin=has_admin,
        has_cameras=has_cameras,
        setup_completed=setup_completed,
        current_step=current_step
    )


@router.post("/admin")
async def setup_admin(
    request: AdminSetupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Étape 1: Créer le compte administrateur initial
    Ne fonctionne que si aucun admin n'existe
    """
    # Vérifier qu'aucun admin n'existe
    result = await db.execute(
        select(func.count(User.id)).where(User.role == "admin")
    )
    if result.scalar() > 0:
        raise HTTPException(
            status_code=400,
            detail="Un administrateur existe déjà"
        )
    
    # Créer l'admin
    admin = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role="admin",
        is_active=True
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    # Mettre à jour le statut
    status = load_setup_status()
    status["current_step"] = 2
    status["admin_created_at"] = datetime.now().isoformat()
    save_setup_status(status)
    
    logger.info(f"Admin account created: {request.email}")
    
    return {
        "success": True,
        "message": "Compte administrateur créé",
        "user_id": admin.id,
        "next_step": "cameras"
    }


@router.post("/cameras")
async def setup_cameras(
    cameras: List[CameraSetupRequest],
    db: AsyncSession = Depends(get_db)
):
    """
    Étape 2: Ajouter les caméras découvertes/configurées
    """
    added_cameras = []
    
    for cam_data in cameras:
        camera = Camera(
            name=cam_data.name,
            ip_address=cam_data.ip,
            rtsp_url=cam_data.rtsp_url,
            username=cam_data.username,
            password=cam_data.password,
            manufacturer=cam_data.manufacturer,
            model=cam_data.model,
            location=cam_data.location,
            is_active=True,
            # Détections
            person_detection=("person" in cam_data.enabled_detections),
            fall_detection=("fall" in cam_data.enabled_detections),
            fire_detection=("fire" in cam_data.enabled_detections),
            ppe_detection=("ppe" in cam_data.enabled_detections),
            counting_enabled=("counting" in cam_data.enabled_detections),
        )
        
        db.add(camera)
        added_cameras.append(cam_data.name)
    
    await db.commit()
    
    # Mettre à jour le statut
    status = load_setup_status()
    status["current_step"] = 3
    status["cameras_added"] = len(added_cameras)
    save_setup_status(status)
    
    logger.info(f"Setup: {len(added_cameras)} cameras added")
    
    return {
        "success": True,
        "message": f"{len(added_cameras)} caméra(s) ajoutée(s)",
        "cameras": added_cameras,
        "next_step": "detections"
    }


@router.put("/cameras/{camera_id}/detections")
async def setup_camera_detections(
    camera_id: int,
    config: DetectionConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Étape 3: Configurer les détections pour une caméra
    """
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    # Mettre à jour les détections
    camera.person_detection = config.person_detection
    camera.fall_detection = config.fall_detection
    camera.fire_detection = config.fire_detection
    camera.ppe_detection = config.ppe_detection
    camera.counting_enabled = config.counting_enabled
    
    if config.counting_line:
        camera.counting_line = json.dumps(config.counting_line)
    
    if config.zones:
        camera.detection_zones = json.dumps(config.zones)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Configuration mise à jour",
        "camera_id": camera_id
    }


@router.post("/complete", response_model=SetupCompleteResponse)
async def complete_setup(
    request: SetupCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Étape 4: Finaliser le setup
    """
    # Récupérer l'admin
    result = await db.execute(
        select(User).where(User.role == "admin").limit(1)
    )
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise HTTPException(
            status_code=400,
            detail="Aucun administrateur trouvé. Complétez d'abord l'étape 1."
        )
    
    # Mettre à jour les préférences de notification si spécifié
    if request.notification_email:
        admin.notification_email = request.notification_email
        admin.notifications_enabled = request.enable_notifications
        await db.commit()
    
    # Marquer le setup comme terminé
    status = load_setup_status()
    status["setup_completed"] = True
    status["current_step"] = 4
    status["completed_at"] = datetime.now().isoformat()
    save_setup_status(status)
    
    # Générer un token d'accès
    access_token = create_access_token(data={"sub": admin.email})
    
    logger.info("Setup completed successfully")
    
    return SetupCompleteResponse(
        success=True,
        message="Configuration terminée ! Bienvenue sur OhmVision.",
        access_token=access_token,
        dashboard_url="/dashboard"
    )


@router.post("/reset")
async def reset_setup(db: AsyncSession = Depends(get_db)):
    """
    Réinitialise le setup (pour développement/test uniquement)
    En production, cette route devrait être désactivée ou protégée
    """
    # Reset le fichier de status
    save_setup_status({
        "setup_completed": False,
        "current_step": 0,
        "reset_at": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "message": "Setup reset. Le wizard s'affichera au prochain chargement."
    }


@router.get("/skip-to-dashboard")
async def skip_setup(db: AsyncSession = Depends(get_db)):
    """
    Permet de sauter le setup (si admin existe déjà)
    Utile pour les mises à jour où le setup a déjà été fait
    """
    # Vérifier si un admin existe
    result = await db.execute(
        select(User).where(User.role == "admin").limit(1)
    )
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise HTTPException(
            status_code=400,
            detail="Impossible de sauter: aucun administrateur configuré"
        )
    
    # Marquer comme terminé
    status = load_setup_status()
    status["setup_completed"] = True
    status["current_step"] = 4
    status["skipped_at"] = datetime.now().isoformat()
    save_setup_status(status)
    
    return {
        "success": True,
        "message": "Setup skipped",
        "redirect": "/dashboard"
    }
