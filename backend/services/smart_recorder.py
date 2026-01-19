"""
OhmVision - Smart Recording System
Enregistrement vidéo intelligent déclenché par les alertes
"""

import cv2
import os
import asyncio
import threading
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Queue
from collections import deque
import logging
import subprocess
import shutil

logger = logging.getLogger(__name__)


@dataclass
class RecordingConfig:
    """Configuration d'enregistrement"""
    # Durées
    pre_event_seconds: int = 10      # Secondes avant l'événement
    post_event_seconds: int = 30     # Secondes après l'événement
    max_duration_seconds: int = 300  # Durée max d'un enregistrement
    
    # Qualité
    fps: int = 15
    resolution: tuple = (1280, 720)
    codec: str = "mp4v"
    
    # Stockage
    output_dir: str = os.getenv("RECORDINGS_DIR", "./recordings")
    max_storage_gb: float = 50.0
    retention_days: int = 30
    
    # Format
    filename_format: str = "{camera_name}_{date}_{time}_{alert_type}"


@dataclass
class RecordingSession:
    """Session d'enregistrement active"""
    session_id: str
    camera_id: int
    camera_name: str
    alert_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    filepath: str = ""
    status: str = "recording"  # recording, completed, error
    frame_count: int = 0
    file_size_mb: float = 0.0
    
    # Buffer pre-event
    pre_buffer: deque = field(default_factory=lambda: deque(maxlen=300))


class SmartRecorder:
    """
    Enregistreur vidéo intelligent
    - Buffer circulaire pour capturer les secondes avant l'événement
    - Enregistrement automatique sur alerte
    - Gestion du stockage et de la rétention
    """
    
    def __init__(self, config: RecordingConfig = None):
        self.config = config or RecordingConfig()
        self._sessions: Dict[str, RecordingSession] = {}
        self._buffers: Dict[int, deque] = {}  # camera_id -> frame buffer
        self._writers: Dict[str, cv2.VideoWriter] = {}
        self._lock = threading.Lock()
        
        # Créer le dossier de sortie
        os.makedirs(self.config.output_dir, exist_ok=True)
    
    def add_frame(self, camera_id: int, frame, timestamp: datetime = None):
        """
        Ajoute une frame au buffer circulaire
        Doit être appelé pour chaque frame du flux vidéo
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Stocker dans le buffer circulaire
        if camera_id not in self._buffers:
            # Buffer de N secondes à 15 fps
            buffer_size = self.config.pre_event_seconds * self.config.fps
            self._buffers[camera_id] = deque(maxlen=buffer_size)
        
        self._buffers[camera_id].append((frame.copy(), timestamp))
        
        # Écrire dans les sessions actives
        with self._lock:
            for session_id, session in self._sessions.items():
                if session.camera_id == camera_id and session.status == "recording":
                    self._write_frame(session_id, frame)
    
    def start_recording(self, camera_id: int, camera_name: str, 
                        alert_type: str, alert_id: str = None) -> str:
        """
        Démarre un enregistrement suite à une alerte
        
        Args:
            camera_id: ID de la caméra
            camera_name: Nom de la caméra
            alert_type: Type d'alerte (fall, fire, intrusion, etc.)
            alert_id: ID unique de l'alerte
        
        Returns:
            session_id de l'enregistrement
        """
        session_id = alert_id or f"rec_{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Générer le nom de fichier
        now = datetime.now()
        filename = self.config.filename_format.format(
            camera_name=self._sanitize_filename(camera_name),
            date=now.strftime('%Y%m%d'),
            time=now.strftime('%H%M%S'),
            alert_type=alert_type
        ) + ".mp4"
        
        filepath = os.path.join(self.config.output_dir, filename)
        
        # Créer la session
        session = RecordingSession(
            session_id=session_id,
            camera_id=camera_id,
            camera_name=camera_name,
            alert_type=alert_type,
            start_time=now,
            filepath=filepath
        )
        
        # Copier le buffer pre-event
        if camera_id in self._buffers:
            session.pre_buffer = deque(self._buffers[camera_id])
        
        # Initialiser le writer
        fourcc = cv2.VideoWriter_fourcc(*self.config.codec)
        writer = cv2.VideoWriter(
            filepath,
            fourcc,
            self.config.fps,
            self.config.resolution
        )
        
        if not writer.isOpened():
            logger.error(f"Failed to create video writer for {filepath}")
            session.status = "error"
            return session_id
        
        with self._lock:
            self._sessions[session_id] = session
            self._writers[session_id] = writer
        
        # Écrire le buffer pre-event
        self._write_pre_buffer(session_id)
        
        logger.info(f"Started recording: {session_id} -> {filepath}")
        
        # Programmer l'arrêt automatique
        asyncio.create_task(self._schedule_stop(session_id))
        
        return session_id
    
    async def _schedule_stop(self, session_id: str):
        """Programme l'arrêt automatique après la durée configurée"""
        await asyncio.sleep(self.config.post_event_seconds)
        self.stop_recording(session_id)
    
    def stop_recording(self, session_id: str) -> Optional[str]:
        """
        Arrête un enregistrement
        
        Returns:
            Chemin du fichier enregistré ou None
        """
        with self._lock:
            if session_id not in self._sessions:
                return None
            
            session = self._sessions[session_id]
            
            if session_id in self._writers:
                self._writers[session_id].release()
                del self._writers[session_id]
            
            session.end_time = datetime.now()
            session.status = "completed"
            
            # Calculer la taille du fichier
            if os.path.exists(session.filepath):
                session.file_size_mb = os.path.getsize(session.filepath) / (1024 * 1024)
            
            filepath = session.filepath
            del self._sessions[session_id]
        
        logger.info(f"Recording completed: {session_id} ({session.frame_count} frames, "
                   f"{session.file_size_mb:.1f} MB)")
        
        # Convertir en H.264 pour compatibilité web (async)
        asyncio.create_task(self._convert_to_h264(filepath))
        
        return filepath
    
    def _write_frame(self, session_id: str, frame):
        """Écrit une frame dans l'enregistrement"""
        if session_id not in self._writers:
            return
        
        # Redimensionner si nécessaire
        if frame.shape[:2] != self.config.resolution[::-1]:
            frame = cv2.resize(frame, self.config.resolution)
        
        self._writers[session_id].write(frame)
        self._sessions[session_id].frame_count += 1
    
    def _write_pre_buffer(self, session_id: str):
        """Écrit le buffer pre-event dans l'enregistrement"""
        session = self._sessions.get(session_id)
        if not session:
            return
        
        for frame, timestamp in session.pre_buffer:
            self._write_frame(session_id, frame)
    
    async def _convert_to_h264(self, filepath: str):
        """Convertit la vidéo en H.264 pour compatibilité navigateur"""
        if not os.path.exists(filepath):
            return
        
        output_path = filepath.replace('.mp4', '_web.mp4')
        
        try:
            # Utiliser FFmpeg pour la conversion
            cmd = [
                'ffmpeg', '-y',
                '-i', filepath,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-movflags', '+faststart',
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                # Remplacer l'original par la version web
                os.replace(output_path, filepath)
                logger.info(f"Video converted to H.264: {filepath}")
            else:
                logger.warning(f"FFmpeg conversion failed for {filepath}")
                
        except Exception as e:
            logger.error(f"Conversion error: {e}")
    
    def _sanitize_filename(self, name: str) -> str:
        """Nettoie un nom pour l'utiliser dans un fichier"""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    
    def get_recording_status(self, session_id: str) -> Optional[Dict]:
        """Récupère le statut d'un enregistrement"""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "camera_id": session.camera_id,
            "camera_name": session.camera_name,
            "alert_type": session.alert_type,
            "status": session.status,
            "start_time": session.start_time.isoformat(),
            "frame_count": session.frame_count,
            "filepath": session.filepath
        }
    
    def list_recordings(self, camera_id: int = None, 
                        days: int = 7) -> List[Dict]:
        """Liste les enregistrements"""
        recordings = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(self.config.output_dir):
            if not filename.endswith('.mp4'):
                continue
            
            filepath = os.path.join(self.config.output_dir, filename)
            stat = os.stat(filepath)
            created = datetime.fromtimestamp(stat.st_ctime)
            
            if created < cutoff:
                continue
            
            # Parser le nom de fichier
            parts = filename.replace('.mp4', '').split('_')
            cam_name = parts[0] if parts else "Unknown"
            
            recordings.append({
                "filename": filename,
                "filepath": filepath,
                "camera_name": cam_name,
                "created": created.isoformat(),
                "size_mb": stat.st_size / (1024 * 1024),
                "duration_estimate": stat.st_size / (1024 * 1024 * 0.5)  # ~0.5 MB/sec
            })
        
        # Filtrer par caméra si spécifié
        if camera_id:
            # Note: nécessite une correspondance camera_id -> camera_name
            pass
        
        return sorted(recordings, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_recordings(self) -> int:
        """
        Supprime les anciens enregistrements selon la politique de rétention
        
        Returns:
            Nombre de fichiers supprimés
        """
        deleted = 0
        cutoff = datetime.now() - timedelta(days=self.config.retention_days)
        
        for filename in os.listdir(self.config.output_dir):
            if not filename.endswith('.mp4'):
                continue
            
            filepath = os.path.join(self.config.output_dir, filename)
            stat = os.stat(filepath)
            created = datetime.fromtimestamp(stat.st_ctime)
            
            if created < cutoff:
                try:
                    os.remove(filepath)
                    deleted += 1
                    logger.info(f"Deleted old recording: {filename}")
                except Exception as e:
                    logger.error(f"Failed to delete {filename}: {e}")
        
        return deleted
    
    def check_storage(self) -> Dict:
        """Vérifie l'état du stockage"""
        total_size = 0
        file_count = 0
        
        for filename in os.listdir(self.config.output_dir):
            filepath = os.path.join(self.config.output_dir, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
                file_count += 1
        
        total_gb = total_size / (1024 ** 3)
        max_gb = self.config.max_storage_gb
        
        return {
            "used_gb": total_gb,
            "max_gb": max_gb,
            "usage_percent": (total_gb / max_gb) * 100 if max_gb > 0 else 0,
            "file_count": file_count,
            "needs_cleanup": total_gb > max_gb * 0.9  # > 90%
        }


# Instance globale
smart_recorder = SmartRecorder()


# ============================================================================
# Event-Triggered Recording
# ============================================================================

async def trigger_recording_on_alert(
    camera_id: int,
    camera_name: str,
    alert_type: str,
    alert_id: str,
    frame = None
) -> str:
    """
    Déclenche un enregistrement suite à une alerte
    
    Args:
        camera_id: ID de la caméra
        camera_name: Nom de la caméra
        alert_type: Type d'alerte
        alert_id: ID de l'alerte
        frame: Frame courante (optionnel, pour snapshot)
    
    Returns:
        session_id de l'enregistrement
    """
    session_id = smart_recorder.start_recording(
        camera_id=camera_id,
        camera_name=camera_name,
        alert_type=alert_type,
        alert_id=alert_id
    )
    
    return session_id
