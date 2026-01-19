"""
OhmVision - Storage Manager
============================
Gestion intelligente du stockage vidéo avec compression et rétention
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import aiofiles
import cv2
import numpy as np
import hashlib
import json
import shutil
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.models import Camera, Alert, DataRetentionPolicy


logger = logging.getLogger(__name__)


class StorageTier(str, Enum):
    """Niveaux de stockage (tiering)"""
    HOT = "hot"        # SSD - Accès rapide (24-48h)
    WARM = "warm"      # HDD - Accès moyen (7-30j)
    COLD = "cold"      # Archive - Accès lent (90j+)
    GLACIER = "glacier"  # Glacier/S3 - Très lent (1 an+)


class CompressionProfile(str, Enum):
    """Profils de compression vidéo"""
    LOSSLESS = "lossless"      # Aucune perte (énorme)
    HIGH_QUALITY = "high"       # H.264 CRF 18 (excellent)
    BALANCED = "balanced"       # H.264 CRF 23 (bon)
    EFFICIENT = "efficient"     # H.265 CRF 28 (compact)
    ULTRA_COMPRESSED = "ultra"  # H.265 CRF 32 (très compact)


@dataclass
class StorageStats:
    """Statistiques de stockage"""
    total_gb: float
    used_gb: float
    available_gb: float
    percent_used: float
    
    hot_tier_gb: float
    warm_tier_gb: float
    cold_tier_gb: float
    
    video_count: int
    total_video_size_gb: float
    avg_video_size_mb: float


@dataclass
class VideoMetadata:
    """Métadonnées vidéo"""
    video_id: str
    camera_id: int
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    
    file_path: str
    file_size_mb: float
    
    resolution: Tuple[int, int]
    fps: int
    codec: str
    
    tier: StorageTier
    compression_profile: CompressionProfile
    
    has_detections: bool
    detection_count: int
    
    created_at: datetime
    last_accessed: datetime


class VideoCompressor:
    """Compression intelligente de vidéo"""
    
    COMPRESSION_SETTINGS = {
        CompressionProfile.LOSSLESS: {
            "codec": "ffv1",  # FFmpeg lossless
            "params": {},
            "compression_ratio": 1.0,
            "quality": "Lossless"
        },
        CompressionProfile.HIGH_QUALITY: {
            "codec": "libx264",
            "params": {
                "crf": 18,
                "preset": "slow"
            },
            "compression_ratio": 0.15,  # 85% réduction
            "quality": "Excellent (quasi imperceptible)"
        },
        CompressionProfile.BALANCED: {
            "codec": "libx264",
            "params": {
                "crf": 23,
                "preset": "medium"
            },
            "compression_ratio": 0.08,  # 92% réduction
            "quality": "Bon (usage général)"
        },
        CompressionProfile.EFFICIENT: {
            "codec": "libx265",  # H.265/HEVC
            "params": {
                "crf": 28,
                "preset": "medium"
            },
            "compression_ratio": 0.04,  # 96% réduction
            "quality": "Correct (archivage)"
        },
        CompressionProfile.ULTRA_COMPRESSED: {
            "codec": "libx265",
            "params": {
                "crf": 32,
                "preset": "fast"
            },
            "compression_ratio": 0.02,  # 98% réduction
            "quality": "Acceptable (archivage long terme)"
        }
    }
    
    @staticmethod
    def compress_video(
        input_path: str,
        output_path: str,
        profile: CompressionProfile = CompressionProfile.BALANCED
    ) -> Dict[str, Any]:
        """
        Compresser une vidéo avec FFmpeg
        
        Args:
            input_path: Chemin vidéo source
            output_path: Chemin vidéo compressée
            profile: Profil de compression
        
        Returns:
            Statistiques de compression
        """
        settings = VideoCompressor.COMPRESSION_SETTINGS[profile]
        
        # Construire commande FFmpeg
        import subprocess
        
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", settings["codec"],
            "-y",  # Overwrite
        ]
        
        # Ajouter paramètres spécifiques
        for param, value in settings["params"].items():
            cmd.extend([f"-{param}", str(value)])
        
        # Audio: copie ou suppression
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])  # Audio compressé
        
        cmd.append(output_path)
        
        # Exécuter
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1h max
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise RuntimeError(f"Compression failed: {result.stderr}")
            
            # Calculer stats
            input_size = Path(input_path).stat().st_size
            output_size = Path(output_path).stat().st_size
            
            compression_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "input_size_mb": input_size / 1024 / 1024,
                "output_size_mb": output_size / 1024 / 1024,
                "compression_ratio": output_size / input_size,
                "space_saved_mb": (input_size - output_size) / 1024 / 1024,
                "compression_time_seconds": compression_time,
                "profile": profile.value,
                "quality": settings["quality"]
            }
        
        except subprocess.TimeoutExpired:
            logger.error("Compression timeout (>1h)")
            return {"success": False, "error": "timeout"}
        
        except Exception as e:
            logger.error(f"Compression error: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def estimate_compressed_size(
        original_size_mb: float,
        profile: CompressionProfile
    ) -> float:
        """Estimer la taille après compression"""
        settings = VideoCompressor.COMPRESSION_SETTINGS[profile]
        return original_size_mb * settings["compression_ratio"]


class StorageManager:
    """
    Gestionnaire de stockage intelligent
    
    Fonctionnalités:
    - Tiering automatique (hot -> warm -> cold)
    - Compression adaptative
    - Rétention selon policies
    - Déduplication
    - Archivage cloud (S3, etc.)
    """
    
    def __init__(
        self,
        base_path: str = "/var/lib/ohmvision/storage",
        db: Optional[AsyncSession] = None
    ):
        self.base_path = Path(base_path)
        self.db = db
        
        # Créer structure de dossiers
        self.tiers = {
            StorageTier.HOT: self.base_path / "hot",
            StorageTier.WARM: self.base_path / "warm",
            StorageTier.COLD: self.base_path / "cold",
            StorageTier.GLACIER: self.base_path / "glacier"
        }
        
        for tier_path in self.tiers.values():
            tier_path.mkdir(parents=True, exist_ok=True)
        
        self.compressor = VideoCompressor()
    
    async def store_video(
        self,
        camera_id: int,
        video_data: bytes,
        start_time: datetime,
        end_time: datetime,
        has_detections: bool = False,
        tier: StorageTier = StorageTier.HOT
    ) -> VideoMetadata:
        """
        Stocker une vidéo
        
        Args:
            camera_id: ID caméra
            video_data: Données vidéo (bytes)
            start_time: Début enregistrement
            end_time: Fin enregistrement
            has_detections: Contient des détections IA ?
            tier: Niveau de stockage initial
        
        Returns:
            Métadonnées vidéo
        """
        # Générer ID unique
        video_id = self._generate_video_id(camera_id, start_time)
        
        # Déterminer profil de compression selon tier
        compression_profile = self._get_compression_for_tier(tier, has_detections)
        
        # Chemin de stockage
        tier_path = self.tiers[tier]
        camera_path = tier_path / f"camera_{camera_id}"
        camera_path.mkdir(exist_ok=True)
        
        date_folder = camera_path / start_time.strftime("%Y-%m-%d")
        date_folder.mkdir(exist_ok=True)
        
        video_filename = f"{video_id}.mp4"
        video_path = date_folder / video_filename
        
        # Écrire fichier temporaire
        temp_path = video_path.with_suffix(".tmp")
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(video_data)
        
        # Compresser si nécessaire
        if compression_profile != CompressionProfile.LOSSLESS:
            compressed_path = video_path
            
            compression_stats = self.compressor.compress_video(
                str(temp_path),
                str(compressed_path),
                compression_profile
            )
            
            if compression_stats["success"]:
                # Supprimer temporaire
                temp_path.unlink()
                file_size_mb = compression_stats["output_size_mb"]
                logger.info(
                    f"Vidéo compressée: {compression_stats['space_saved_mb']:.1f} MB économisés "
                    f"({compression_stats['compression_ratio']*100:.1f}% de la taille originale)"
                )
            else:
                # Échec compression: garder l'original
                temp_path.rename(compressed_path)
                file_size_mb = len(video_data) / 1024 / 1024
                logger.warning("Compression failed, using original")
        else:
            # Pas de compression
            temp_path.rename(video_path)
            file_size_mb = len(video_data) / 1024 / 1024
        
        # Créer métadonnées
        metadata = VideoMetadata(
            video_id=video_id,
            camera_id=camera_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=int((end_time - start_time).total_seconds()),
            file_path=str(video_path),
            file_size_mb=file_size_mb,
            resolution=(1920, 1080),  # TODO: Extraire de la vidéo
            fps=25,  # TODO: Extraire
            codec=compression_profile.value,
            tier=tier,
            compression_profile=compression_profile,
            has_detections=has_detections,
            detection_count=0,  # TODO: Compter
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        
        # Sauvegarder métadonnées
        await self._save_metadata(metadata)
        
        logger.info(
            f"Vidéo stockée: {video_id} ({file_size_mb:.1f} MB, tier={tier.value})"
        )
        
        return metadata
    
    async def apply_retention_policy(
        self,
        policy: DataRetentionPolicy,
        camera_id: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Appliquer une politique de rétention
        
        Args:
            policy: Politique de rétention
            camera_id: ID caméra (None = toutes)
            dry_run: Simulation sans suppression réelle
        
        Returns:
            Rapport de suppression
        """
        retention_days = {
            DataRetentionPolicy.DAYS_7: 7,
            DataRetentionPolicy.DAYS_30: 30,
            DataRetentionPolicy.DAYS_90: 90,
            DataRetentionPolicy.YEAR_1: 365
        }
        
        days = retention_days.get(policy, 30)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        logger.info(f"Application politique {policy.value}: suppression avant {cutoff_date}")
        
        deleted_count = 0
        space_freed_mb = 0
        videos_to_delete = []
        
        # Parcourir tous les tiers
        for tier, tier_path in self.tiers.items():
            if not tier_path.exists():
                continue
            
            # Parcourir les caméras
            for camera_path in tier_path.iterdir():
                if not camera_path.is_dir():
                    continue
                
                # Extraire camera_id
                cam_id = int(camera_path.name.replace("camera_", ""))
                
                # Filtrer par camera_id si spécifié
                if camera_id and cam_id != camera_id:
                    continue
                
                # Parcourir les dates
                for date_folder in camera_path.iterdir():
                    if not date_folder.is_dir():
                        continue
                    
                    # Parser date du dossier
                    try:
                        folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d")
                    except ValueError:
                        continue
                    
                    # Vérifier si expiré
                    if folder_date < cutoff_date:
                        # Compter fichiers et taille
                        for video_file in date_folder.glob("*.mp4"):
                            size_mb = video_file.stat().st_size / 1024 / 1024
                            videos_to_delete.append({
                                "path": video_file,
                                "size_mb": size_mb,
                                "date": folder_date
                            })
                            space_freed_mb += size_mb
                            deleted_count += 1
        
        # Supprimer si pas dry_run
        if not dry_run:
            for video in videos_to_delete:
                video["path"].unlink()
                logger.info(f"Supprimé: {video['path']} ({video['size_mb']:.1f} MB)")
            
            # Supprimer dossiers vides
            for tier_path in self.tiers.values():
                for camera_path in tier_path.iterdir():
                    for date_folder in camera_path.iterdir():
                        if date_folder.is_dir() and not any(date_folder.iterdir()):
                            date_folder.rmdir()
        
        return {
            "policy": policy.value,
            "cutoff_date": cutoff_date.isoformat(),
            "videos_deleted": deleted_count,
            "space_freed_mb": space_freed_mb,
            "space_freed_gb": space_freed_mb / 1024,
            "dry_run": dry_run
        }
    
    async def tier_migration(self, age_thresholds: Dict[StorageTier, int]):
        """
        Migration automatique entre tiers selon l'âge
        
        Args:
            age_thresholds: {tier: jours} ex: {HOT: 2, WARM: 30, COLD: 90}
        
        Exemple:
            - HOT: 0-2 jours (accès fréquent, SSD, qualité haute)
            - WARM: 2-30 jours (accès moyen, HDD, compression balanced)
            - COLD: 30-90 jours (accès rare, HDD, compression ultra)
            - GLACIER: 90+ jours (archivage, compression maximale)
        """
        now = datetime.now()
        
        migrations = []
        
        # HOT -> WARM (>2 jours)
        if StorageTier.HOT in age_thresholds:
            hot_path = self.tiers[StorageTier.HOT]
            threshold_date = now - timedelta(days=age_thresholds[StorageTier.HOT])
            
            for video_path in hot_path.rglob("*.mp4"):
                created = datetime.fromtimestamp(video_path.stat().st_ctime)
                
                if created < threshold_date:
                    # Migrer vers WARM avec re-compression
                    await self._migrate_video(
                        video_path,
                        StorageTier.HOT,
                        StorageTier.WARM,
                        CompressionProfile.EFFICIENT
                    )
                    migrations.append({
                        "video": video_path.name,
                        "from": "HOT",
                        "to": "WARM"
                    })
        
        # WARM -> COLD (>30 jours)
        # COLD -> GLACIER (>90 jours)
        # Implémentation similaire...
        
        logger.info(f"{len(migrations)} vidéos migrées entre tiers")
        
        return migrations
    
    async def _migrate_video(
        self,
        source_path: Path,
        from_tier: StorageTier,
        to_tier: StorageTier,
        compression_profile: CompressionProfile
    ):
        """Migrer une vidéo d'un tier à un autre"""
        # Construire chemin destination
        relative_path = source_path.relative_to(self.tiers[from_tier])
        dest_path = self.tiers[to_tier] / relative_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Compresser vers destination
        compression_stats = self.compressor.compress_video(
            str(source_path),
            str(dest_path),
            compression_profile
        )
        
        if compression_stats["success"]:
            # Supprimer source
            source_path.unlink()
            logger.info(
                f"Migré: {source_path.name} {from_tier.value} -> {to_tier.value} "
                f"(-{compression_stats['space_saved_mb']:.1f} MB)"
            )
        else:
            # Échec: copier sans re-compression
            shutil.move(str(source_path), str(dest_path))
    
    def get_storage_stats(self) -> StorageStats:
        """Obtenir statistiques de stockage"""
        # Espace disque total
        usage = shutil.disk_usage(self.base_path)
        
        total_gb = usage.total / 1024 / 1024 / 1024
        used_gb = usage.used / 1024 / 1024 / 1024
        available_gb = usage.free / 1024 / 1024 / 1024
        percent_used = (used_gb / total_gb) * 100
        
        # Taille par tier
        tier_sizes = {}
        for tier, tier_path in self.tiers.items():
            if tier_path.exists():
                tier_size = sum(
                    f.stat().st_size for f in tier_path.rglob("*") if f.is_file()
                )
                tier_sizes[tier] = tier_size / 1024 / 1024 / 1024  # GB
            else:
                tier_sizes[tier] = 0
        
        # Compter vidéos
        video_count = sum(
            1 for tier_path in self.tiers.values()
            if tier_path.exists()
            for _ in tier_path.rglob("*.mp4")
        )
        
        total_video_size_gb = sum(tier_sizes.values())
        avg_video_size_mb = (total_video_size_gb * 1024 / video_count) if video_count > 0 else 0
        
        return StorageStats(
            total_gb=total_gb,
            used_gb=used_gb,
            available_gb=available_gb,
            percent_used=percent_used,
            hot_tier_gb=tier_sizes.get(StorageTier.HOT, 0),
            warm_tier_gb=tier_sizes.get(StorageTier.WARM, 0),
            cold_tier_gb=tier_sizes.get(StorageTier.COLD, 0),
            video_count=video_count,
            total_video_size_gb=total_video_size_gb,
            avg_video_size_mb=avg_video_size_mb
        )
    
    def _generate_video_id(self, camera_id: int, timestamp: datetime) -> str:
        """Générer ID unique pour vidéo"""
        data = f"{camera_id}_{timestamp.isoformat()}".encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _get_compression_for_tier(
        self,
        tier: StorageTier,
        has_detections: bool
    ) -> CompressionProfile:
        """Déterminer profil de compression selon tier"""
        # Si détections importantes: meilleure qualité
        if has_detections:
            compression_map = {
                StorageTier.HOT: CompressionProfile.HIGH_QUALITY,
                StorageTier.WARM: CompressionProfile.BALANCED,
                StorageTier.COLD: CompressionProfile.EFFICIENT,
                StorageTier.GLACIER: CompressionProfile.EFFICIENT
            }
        else:
            # Pas de détections: compression plus agressive
            compression_map = {
                StorageTier.HOT: CompressionProfile.BALANCED,
                StorageTier.WARM: CompressionProfile.EFFICIENT,
                StorageTier.COLD: CompressionProfile.ULTRA_COMPRESSED,
                StorageTier.GLACIER: CompressionProfile.ULTRA_COMPRESSED
            }
        
        return compression_map.get(tier, CompressionProfile.BALANCED)
    
    async def _save_metadata(self, metadata: VideoMetadata):
        """Sauvegarder métadonnées vidéo"""
        # En production: INSERT dans table `video_metadata`
        metadata_file = Path(metadata.file_path).with_suffix(".json")
        
        async with aiofiles.open(metadata_file, 'w') as f:
            await f.write(json.dumps({
                "video_id": metadata.video_id,
                "camera_id": metadata.camera_id,
                "start_time": metadata.start_time.isoformat(),
                "end_time": metadata.end_time.isoformat(),
                "duration_seconds": metadata.duration_seconds,
                "file_size_mb": metadata.file_size_mb,
                "tier": metadata.tier.value,
                "compression_profile": metadata.compression_profile.value,
                "has_detections": metadata.has_detections
            }, indent=2))
