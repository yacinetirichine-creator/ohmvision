"""
OhmVision - Camera Health Check Service
Surveille la santé des connexions caméra et gère la reconnexion automatique
"""

import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models.models import Camera
from services.multi_channel_connector import MultiChannelConnector, ReconnectionManager

logger = logging.getLogger(__name__)


@dataclass
class CameraHealthStatus:
    """Statut de santé d'une caméra"""
    camera_id: int
    is_online: bool
    health: str  # excellent, good, fair, poor, offline
    last_check: datetime
    response_time_ms: float
    uptime_percentage: float
    failed_attempts: int
    last_error: Optional[str] = None
    next_check_in: int = 60  # secondes


class HealthCheckService:
    """
    Service de surveillance de santé des caméras
    - Vérifie périodiquement toutes les caméras actives
    - Détecte les caméras offline
    - Tente la reconnexion automatique
    - Calcule les statistiques de uptime
    """
    
    def __init__(
        self,
        check_interval: int = 60,  # Vérifier toutes les 60 secondes
        batch_size: int = 10  # Nombre de caméras à vérifier en parallèle
    ):
        self.check_interval = check_interval
        self.batch_size = batch_size
        self.reconnection_manager = ReconnectionManager(
            max_attempts=5,
            initial_delay=10.0,
            max_delay=300.0
        )
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._connector: Optional[MultiChannelConnector] = None
        
        # Statistiques de uptime (30 derniers jours)
        self._uptime_stats: Dict[int, List[bool]] = {}  # camera_id -> [True/False checks]
        self._max_stats_entries = 43200  # 30 jours * 24h * 60min (checks par minute)
    
    async def start(self):
        """Démarre le service de health check"""
        if self._running:
            logger.warning("Health check service already running")
            return
        
        self._running = True
        self._connector = MultiChannelConnector()
        await self._connector.__aenter__()
        
        logger.info("🏥 Starting camera health check service...")
        self._task = asyncio.create_task(self._health_check_loop())
    
    async def stop(self):
        """Arrête le service de health check"""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self._connector:
            await self._connector.__aexit__(None, None, None)
        
        logger.info("🏥 Health check service stopped")
    
    async def _health_check_loop(self):
        """Boucle principale de vérification"""
        while self._running:
            try:
                await self._perform_health_checks()
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
            
            # Attendre avant le prochain cycle
            await asyncio.sleep(self.check_interval)
    
    async def _perform_health_checks(self):
        """Effectue les vérifications de santé"""
        from core.database import get_async_session
        
        async for db in get_async_session():
            try:
                # Récupérer toutes les caméras actives
                result = await db.execute(
                    select(Camera).where(Camera.is_active == True)
                )
                cameras = result.scalars().all()
                
                if not cameras:
                    return
                
                logger.info(f"🏥 Checking health of {len(cameras)} cameras...")
                
                # Traiter par batch pour ne pas surcharger
                for i in range(0, len(cameras), self.batch_size):
                    batch = cameras[i:i + self.batch_size]
                    await self._check_camera_batch(batch, db)
                    
                    # Petit délai entre les batches
                    await asyncio.sleep(1)
                
                await db.commit()
                
            except Exception as e:
                logger.error(f"Error in health checks: {e}")
                await db.rollback()
            finally:
                await db.close()
    
    async def _check_camera_batch(self, cameras: List[Camera], db: AsyncSession):
        """Vérifie un batch de caméras en parallèle"""
        tasks = [
            self._check_single_camera(camera, db)
            for camera in cameras
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_single_camera(self, camera: Camera, db: AsyncSession):
        """Vérifie une caméra individuelle"""
        try:
            # Déterminer l'URL à tester
            url = camera.primary_stream_url or camera.rtsp_url
            connection_type = camera.connection_type.value if camera.connection_type else "rtsp"
            
            if not url:
                logger.warning(f"Camera {camera.id} has no stream URL")
                await self._update_camera_status(camera, db, False, "No stream URL configured")
                return
            
            # Vérifier la santé
            health_result = await self._connector.check_health(url, connection_type)
            
            is_online = health_result["status"] == "online"
            
            if is_online:
                # Caméra online
                health = health_result.get("health", "good")
                response_time = health_result.get("response_time_ms", 0)
                
                await self._update_camera_status(
                    camera, db, True, None,
                    health=health,
                    response_time=response_time
                )
                
                # Enregistrer le succès
                self.reconnection_manager.record_attempt(camera.id, success=True)
                self._record_uptime_check(camera.id, True)
                
                logger.debug(f"✓ Camera {camera.id} ({camera.name}): {health} ({response_time:.0f}ms)")
                
            else:
                # Caméra offline
                error = health_result.get("error", "Unknown error")
                
                await self._update_camera_status(camera, db, False, error)
                
                # Enregistrer l'échec
                self.reconnection_manager.record_attempt(camera.id, success=False)
                self._record_uptime_check(camera.id, False)
                
                logger.warning(f"✗ Camera {camera.id} ({camera.name}): offline - {error}")
                
                # Tenter la reconnexion si nécessaire
                if self.reconnection_manager.should_retry(camera.id):
                    await self._attempt_reconnection(camera, db)
        
        except Exception as e:
            logger.error(f"Error checking camera {camera.id}: {e}")
            await self._update_camera_status(camera, db, False, str(e))
            self._record_uptime_check(camera.id, False)
    
    async def _attempt_reconnection(self, camera: Camera, db: AsyncSession):
        """Tente de reconnecter une caméra offline"""
        logger.info(f"🔄 Attempting reconnection for camera {camera.id}...")
        
        try:
            # Essayer l'auto-détection si on a les credentials
            if camera.ip_address and camera.username:
                from services.multi_channel_connector import test_camera_connectivity
                
                result = await test_camera_connectivity(
                    ip=camera.ip_address,
                    username=camera.username,
                    password=camera.password or "",
                    manufacturer=camera.manufacturer.value if camera.manufacturer else None
                )
                
                if result["success"] and result["recommended_url"]:
                    # Mise à jour avec la nouvelle URL
                    camera.primary_stream_url = result["recommended_url"]
                    camera.connection_type = result["recommended_type"]
                    camera.is_online = True
                    camera.last_seen = datetime.now()
                    camera.failed_connection_attempts = 0
                    camera.last_error_message = None
                    
                    await db.commit()
                    
                    logger.info(f"✓ Camera {camera.id} reconnected successfully!")
                    self.reconnection_manager.reset(camera.id)
                else:
                    logger.warning(f"✗ Reconnection failed for camera {camera.id}")
        
        except Exception as e:
            logger.error(f"Reconnection attempt error for camera {camera.id}: {e}")
    
    async def _update_camera_status(
        self,
        camera: Camera,
        db: AsyncSession,
        is_online: bool,
        error_message: Optional[str],
        health: str = "offline",
        response_time: float = 0
    ):
        """Met à jour le statut d'une caméra dans la DB"""
        camera.is_online = is_online
        camera.last_health_check = datetime.now()
        camera.connection_health = health
        
        if is_online:
            camera.last_seen = datetime.now()
            camera.failed_connection_attempts = 0
            camera.last_error_message = None
        else:
            camera.failed_connection_attempts += 1
            camera.last_error_message = error_message
        
        # Calculer le uptime
        camera.uptime_percentage = self._calculate_uptime(camera.id)
        
        # La session sera committée par le caller
    
    def _record_uptime_check(self, camera_id: int, success: bool):
        """Enregistre un check de uptime"""
        if camera_id not in self._uptime_stats:
            self._uptime_stats[camera_id] = []
        
        stats = self._uptime_stats[camera_id]
        stats.append(success)
        
        # Limiter la taille
        if len(stats) > self._max_stats_entries:
            stats.pop(0)
    
    def _calculate_uptime(self, camera_id: int) -> float:
        """Calcule le pourcentage de uptime"""
        if camera_id not in self._uptime_stats:
            return 0.0
        
        stats = self._uptime_stats[camera_id]
        
        if not stats:
            return 0.0
        
        successful = sum(1 for s in stats if s)
        return (successful / len(stats)) * 100.0
    
    async def get_camera_health(self, camera_id: int) -> Optional[CameraHealthStatus]:
        """Récupère le statut de santé d'une caméra"""
        from core.database import get_async_session
        
        async for db in get_async_session():
            try:
                result = await db.execute(
                    select(Camera).where(Camera.id == camera_id)
                )
                camera = result.scalar_one_or_none()
                
                if not camera:
                    return None
                
                # Calculer le temps avant le prochain check
                if camera.last_health_check:
                    elapsed = (datetime.now() - camera.last_health_check).total_seconds()
                    next_check = max(0, self.check_interval - int(elapsed))
                else:
                    next_check = 0
                
                return CameraHealthStatus(
                    camera_id=camera.id,
                    is_online=camera.is_online,
                    health=camera.connection_health or "unknown",
                    last_check=camera.last_health_check or datetime.now(),
                    response_time_ms=0,  # TODO: stocker ça
                    uptime_percentage=camera.uptime_percentage or 0.0,
                    failed_attempts=camera.failed_connection_attempts or 0,
                    last_error=camera.last_error_message,
                    next_check_in=next_check
                )
            finally:
                await db.close()
    
    async def get_all_health_status(self) -> List[CameraHealthStatus]:
        """Récupère le statut de santé de toutes les caméras"""
        from core.database import get_async_session
        
        async for db in get_async_session():
            try:
                result = await db.execute(
                    select(Camera).where(Camera.is_active == True)
                )
                cameras = result.scalars().all()
                
                statuses = []
                for camera in cameras:
                    status = await self.get_camera_health(camera.id)
                    if status:
                        statuses.append(status)
                
                return statuses
            finally:
                await db.close()
    
    def get_reconnection_status(self, camera_id: int) -> Dict:
        """Récupère le statut de reconnexion"""
        return self.reconnection_manager.get_status(camera_id)


# =============================================================================
# INSTANCE GLOBALE
# =============================================================================

# Instance globale du service (à initialiser au démarrage de l'app)
health_check_service: Optional[HealthCheckService] = None


async def start_health_check_service():
    """Démarre le service global de health check"""
    global health_check_service
    
    if health_check_service is None:
        health_check_service = HealthCheckService(
            check_interval=60,  # Vérifier toutes les minutes
            batch_size=10
        )
    
    await health_check_service.start()


async def stop_health_check_service():
    """Arrête le service global de health check"""
    global health_check_service
    
    if health_check_service:
        await health_check_service.stop()
