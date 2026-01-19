"""
OhmVision - Tests Suite
========================
Suite de tests complète pour assurer la qualité du code
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List
import numpy as np
import cv2

# Tests imports
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

# App imports
from main import app
from core.database import Base
from models.models import User, Client, Camera, Alert
from services.gdpr_compliance import GDPRComplianceService, ConsentType
from services.performance_optimizer import (
    GPUManager, ModelOptimizer, PerformanceMonitor, BatchProcessor
)
from services.storage_manager import StorageManager, StorageTier, CompressionProfile
from ai.engine import AIEngine, DetectionType


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
async def db_session():
    """Fixture pour session base de données de test"""
    # Base de données en mémoire pour tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def test_client():
    """Client HTTP pour tests API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_user():
    """Utilisateur de test"""
    return User(
        id=1,
        email="test@ohmvision.com",
        hashed_password="$2b$12$test",
        first_name="Test",
        last_name="User",
        role="client_user",
        is_active=True
    )


@pytest.fixture
def sample_camera():
    """Caméra de test"""
    return Camera(
        id=1,
        client_id=1,
        name="Test Camera",
        rtsp_url="rtsp://192.168.1.100:554/stream",
        location="Entrance",
        is_active=True
    )


@pytest.fixture
def sample_frame():
    """Frame vidéo de test (640x480 RGB)"""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


# =============================================================================
# TESTS - API ENDPOINTS
# =============================================================================

@pytest.mark.asyncio
class TestAPIEndpoints:
    """Tests des endpoints API"""
    
    async def test_health_check(self, test_client: AsyncClient):
        """Test endpoint /health"""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    async def test_root_endpoint(self, test_client: AsyncClient):
        """Test endpoint /"""
        response = await test_client.get("/")
        
        assert response.status_code == 200
        assert "OhmVision" in response.json()["message"]
    
    async def test_login_invalid_credentials(self, test_client: AsyncClient):
        """Test login avec credentials invalides"""
        response = await test_client.post(
            "/api/auth/login",
            json={"email": "wrong@test.com", "password": "wrong"}
        )
        
        assert response.status_code in [401, 422]
    
    async def test_cameras_list_unauthorized(self, test_client: AsyncClient):
        """Test liste caméras sans authentification"""
        response = await test_client.get("/api/cameras/")
        
        assert response.status_code == 401


# =============================================================================
# TESTS - RGPD COMPLIANCE
# =============================================================================

@pytest.mark.asyncio
class TestGDPRCompliance:
    """Tests conformité RGPD"""
    
    async def test_consent_request(self, db_session: AsyncSession, sample_user: User):
        """Test demande de consentement"""
        gdpr_service = GDPRComplianceService(db_session)
        
        result = await gdpr_service.request_consent(
            user_id=sample_user.id,
            consent_types=[ConsentType.VIDEO_RECORDING, ConsentType.DATA_PROCESSING],
            purpose="Vidéosurveillance intelligente",
            duration_days=365
        )
        
        assert "consent_id" in result
        assert "consent_url" in result
        assert result["required_consents"] == [
            "video_recording", "data_processing"
        ]
    
    async def test_grant_consent(self, db_session: AsyncSession):
        """Test enregistrement du consentement"""
        gdpr_service = GDPRComplianceService(db_session)
        
        # Demander consentement
        consent_request = await gdpr_service.request_consent(
            user_id=1,
            consent_types=[ConsentType.VIDEO_RECORDING],
            purpose="Test",
            duration_days=30
        )
        
        # Accorder consentement
        success = await gdpr_service.grant_consent(
            consent_id=consent_request["consent_id"],
            granted_consents={ConsentType.VIDEO_RECORDING: True},
            ip_address="127.0.0.1",
            user_agent="pytest"
        )
        
        assert success is True
    
    async def test_anonymize_face(self, sample_frame: np.ndarray):
        """Test anonymisation de visage"""
        gdpr_service = GDPRComplianceService(None)
        
        # Bbox d'un visage fictif
        bbox = (100, 100, 200, 200)
        
        # Anonymiser
        anonymized = gdpr_service.anonymize_face(sample_frame.copy(), bbox)
        
        # Vérifier que la zone est modifiée
        original_region = sample_frame[100:200, 100:200]
        anonymized_region = anonymized[100:200, 100:200]
        
        assert not np.array_equal(original_region, anonymized_region)
    
    async def test_data_export(self, db_session: AsyncSession, sample_user: User):
        """Test export de données utilisateur"""
        db_session.add(sample_user)
        await db_session.commit()
        
        gdpr_service = GDPRComplianceService(db_session)
        
        export_data = await gdpr_service.export_user_data(user_id=sample_user.id)
        
        assert "export_date" in export_data
        assert "data" in export_data
        assert "user" in export_data["data"]
        assert export_data["data"]["user"]["email"] == sample_user.email
    
    async def test_data_deletion(self, db_session: AsyncSession, sample_user: User):
        """Test suppression de données (droit à l'oubli)"""
        db_session.add(sample_user)
        await db_session.commit()
        
        gdpr_service = GDPRComplianceService(db_session)
        
        deletion_report = await gdpr_service.delete_user_data(
            user_id=sample_user.id,
            reason="user_request"
        )
        
        assert deletion_report["status"] == "completed"
        assert "deleted_items" in deletion_report


# =============================================================================
# TESTS - PERFORMANCE OPTIMIZER
# =============================================================================

class TestPerformanceOptimizer:
    """Tests optimisations de performance"""
    
    def test_gpu_detection(self):
        """Test détection GPU"""
        gpu_manager = GPUManager()
        
        assert gpu_manager.device in ["cpu", "cuda", "mps"]
        assert gpu_manager.device_name is not None
        assert gpu_manager.max_batch_size > 0
    
    def test_performance_monitor(self):
        """Test monitoring performance"""
        monitor = PerformanceMonitor(window_size=10)
        
        # Enregistrer frames
        for i in range(5):
            monitor.record_frame(
                processing_time_ms=20.0,
                inference_time_ms=15.0,
                dropped=False
            )
        
        metrics = monitor.get_metrics()
        
        assert metrics.fps > 0
        assert metrics.latency_ms > 0
        assert metrics.frames_processed == 5
        assert metrics.frames_dropped == 0
    
    def test_frame_buffer(self):
        """Test buffer de frames"""
        from services.performance_optimizer import FrameBuffer
        
        buffer = FrameBuffer(maxsize=5)
        
        # Ajouter frames
        for i in range(3):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            buffer.put(frame, timestamp=float(i))
        
        assert buffer.size() == 3
        
        # Récupérer
        frame, timestamp = buffer.get()
        assert timestamp == 0.0
        assert buffer.size() == 2


# =============================================================================
# TESTS - STORAGE MANAGER
# =============================================================================

@pytest.mark.asyncio
class TestStorageManager:
    """Tests gestion du stockage"""
    
    async def test_video_compression_estimation(self):
        """Test estimation taille compressée"""
        from services.storage_manager import VideoCompressor
        
        original_size_mb = 1000.0  # 1 GB
        
        # Balanced profile
        compressed_size = VideoCompressor.estimate_compressed_size(
            original_size_mb,
            CompressionProfile.BALANCED
        )
        
        # Doit être ~8% de l'original
        assert compressed_size < original_size_mb * 0.1
        assert compressed_size > original_size_mb * 0.05
    
    async def test_storage_tiers(self, tmp_path):
        """Test niveaux de stockage"""
        storage = StorageManager(base_path=str(tmp_path))
        
        # Vérifier création des tiers
        for tier in StorageTier:
            tier_path = storage.tiers[tier]
            assert tier_path.exists()
            assert tier_path.is_dir()
    
    async def test_storage_stats(self, tmp_path):
        """Test statistiques de stockage"""
        storage = StorageManager(base_path=str(tmp_path))
        
        stats = storage.get_storage_stats()
        
        assert stats.total_gb > 0
        assert stats.percent_used >= 0
        assert stats.video_count == 0  # Pas de vidéos


# =============================================================================
# TESTS - AI ENGINE
# =============================================================================

@pytest.mark.skipif(
    not pytest.importorskip("ultralytics", minversion="8.0"),
    reason="YOLO non disponible"
)
class TestAIEngine:
    """Tests moteur IA"""
    
    def test_detection_types(self):
        """Test types de détection"""
        assert DetectionType.PERSON.value == "person"
        assert DetectionType.FIRE.value == "fire"
        assert DetectionType.PPE_HELMET.value == "ppe_helmet"
    
    @pytest.mark.slow
    def test_yolo_inference(self, sample_frame: np.ndarray):
        """Test inférence YOLO (lent, skip par défaut)"""
        # Ce test est marqué "slow" et ne s'exécute que si pytest -m slow
        from ultralytics import YOLO
        
        model = YOLO("yolov8n.pt")  # Nano model
        results = model(sample_frame)
        
        assert results is not None
        assert len(results) == 1


# =============================================================================
# TESTS - DATABASE MODELS
# =============================================================================

@pytest.mark.asyncio
class TestDatabaseModels:
    """Tests modèles de base de données"""
    
    async def test_create_user(self, db_session: AsyncSession):
        """Test création utilisateur"""
        user = User(
            email="newuser@test.com",
            hashed_password="hashed",
            first_name="New",
            last_name="User",
            role="client_user"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "newuser@test.com"
    
    async def test_create_camera(self, db_session: AsyncSession, sample_user: User):
        """Test création caméra"""
        db_session.add(sample_user)
        await db_session.commit()
        
        camera = Camera(
            client_id=sample_user.id,
            name="Test Cam",
            rtsp_url="rtsp://test",
            location="Test Location"
        )
        
        db_session.add(camera)
        await db_session.commit()
        await db_session.refresh(camera)
        
        assert camera.id is not None
        assert camera.client_id == sample_user.id


# =============================================================================
# TESTS - INTEGRATION
# =============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestIntegration:
    """Tests d'intégration (plusieurs composants)"""
    
    async def test_full_detection_pipeline(
        self,
        db_session: AsyncSession,
        sample_user: User,
        sample_camera: Camera,
        sample_frame: np.ndarray
    ):
        """Test pipeline complet: frame -> détection -> alerte -> stockage"""
        # 1. Setup database
        db_session.add(sample_user)
        db_session.add(sample_camera)
        await db_session.commit()
        
        # 2. Process frame (simulation)
        # TODO: Implémenter avec vrai AI Engine
        
        # 3. Créer alerte
        alert = Alert(
            camera_id=sample_camera.id,
            type="person_detected",
            severity="medium",
            message="Personne détectée",
            metadata={"count": 1}
        )
        
        db_session.add(alert)
        await db_session.commit()
        
        # 4. Vérifier
        assert alert.id is not None
        assert alert.camera_id == sample_camera.id


# =============================================================================
# CONFIGURATION PYTEST
# =============================================================================

# pytest.ini
"""
[pytest]
markers =
    slow: Tests lents (désactivés par défaut)
    integration: Tests d'intégration
    asyncio: Tests asynchrones

asyncio_mode = auto

testpaths = tests

python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v
    --tb=short
    --strict-markers
    -m "not slow"
    --cov=backend
    --cov-report=html
    --cov-report=term-missing
"""


# =============================================================================
# COMMANDES UTILES
# =============================================================================

"""
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=backend --cov-report=html

# Tests lents inclus
pytest -m slow

# Tests d'intégration uniquement
pytest -m integration

# Tests parallèles (plus rapide)
pytest -n auto

# Tests avec verbose
pytest -vv

# Re-run tests qui ont échoué
pytest --lf

# Stop au premier échec
pytest -x

# Afficher print statements
pytest -s
"""
