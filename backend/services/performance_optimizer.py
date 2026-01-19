"""
OhmVision - Performance Optimizer
==================================
Optimisations pour traitement IA temps réel
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
from collections import deque
import psutil
import logging

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


logger = logging.getLogger(__name__)


class ProcessingMode(str, Enum):
    """Modes de traitement"""
    REALTIME = "realtime"  # Priorité latence faible
    BATCH = "batch"        # Priorité throughput
    BALANCED = "balanced"  # Équilibre latence/throughput


class HardwareAccelerator(str, Enum):
    """Accélérateurs matériels"""
    CPU = "cpu"
    CUDA = "cuda"  # NVIDIA GPU
    MPS = "mps"    # Apple Silicon
    OPENVINO = "openvino"  # Intel
    TENSORRT = "tensorrt"  # NVIDIA optimisé


@dataclass
class PerformanceMetrics:
    """Métriques de performance"""
    fps: float
    latency_ms: float
    cpu_percent: float
    gpu_percent: Optional[float]
    memory_mb: float
    frames_processed: int
    frames_dropped: int
    inference_time_ms: float
    preprocessing_time_ms: float
    postprocessing_time_ms: float


class FrameBuffer:
    """Buffer circulaire pour frames vidéo (thread-safe)"""
    
    def __init__(self, maxsize: int = 30):
        self.buffer = deque(maxlen=maxsize)
        self.lock = threading.Lock()
    
    def put(self, frame: np.ndarray, timestamp: float):
        """Ajouter une frame (drop oldest si plein)"""
        with self.lock:
            self.buffer.append((frame, timestamp))
    
    def get(self) -> Optional[Tuple[np.ndarray, float]]:
        """Récupérer une frame"""
        with self.lock:
            if self.buffer:
                return self.buffer.popleft()
            return None
    
    def size(self) -> int:
        with self.lock:
            return len(self.buffer)
    
    def clear(self):
        with self.lock:
            self.buffer.clear()


class GPUManager:
    """Gestion intelligente du GPU"""
    
    def __init__(self):
        self.device = self._detect_best_device()
        self.device_name = self._get_device_name()
        self.max_batch_size = self._calculate_optimal_batch_size()
    
    def _detect_best_device(self) -> str:
        """Détecter le meilleur accélérateur disponible"""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch non disponible, utilisation CPU")
            return "cpu"
        
        # 1. NVIDIA CUDA
        if torch.cuda.is_available():
            logger.info(f"CUDA disponible: {torch.cuda.get_device_name(0)}")
            return "cuda"
        
        # 2. Apple Silicon (M1/M2/M3)
        if torch.backends.mps.is_available():
            logger.info("Apple MPS disponible")
            return "mps"
        
        # 3. Fallback CPU
        logger.info("Utilisation CPU (considérez un GPU pour meilleures performances)")
        return "cpu"
    
    def _get_device_name(self) -> str:
        """Obtenir le nom du device"""
        if self.device == "cuda":
            return torch.cuda.get_device_name(0)
        elif self.device == "mps":
            return "Apple Silicon GPU"
        else:
            return f"CPU ({psutil.cpu_count()} cores)"
    
    def _calculate_optimal_batch_size(self) -> int:
        """Calculer la taille de batch optimale selon la mémoire GPU"""
        if self.device == "cuda":
            # Mémoire GPU en GB
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            
            # Estimation: 1 GB = ~8 frames 1080p
            if gpu_memory_gb >= 8:
                return 16
            elif gpu_memory_gb >= 4:
                return 8
            else:
                return 4
        
        elif self.device == "mps":
            # Apple Silicon: mémoire unifiée
            return 8
        
        else:
            # CPU: batch plus petits
            return 2
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Obtenir l'utilisation mémoire GPU"""
        if self.device == "cuda" and TORCH_AVAILABLE:
            allocated = torch.cuda.memory_allocated() / 1e9  # GB
            reserved = torch.cuda.memory_reserved() / 1e9
            total = torch.cuda.get_device_properties(0).total_memory / 1e9
            
            return {
                "allocated_gb": allocated,
                "reserved_gb": reserved,
                "total_gb": total,
                "percent": (allocated / total) * 100
            }
        
        return {"allocated_gb": 0, "reserved_gb": 0, "total_gb": 0, "percent": 0}


class ModelOptimizer:
    """Optimisation des modèles IA"""
    
    def __init__(self, device: str = "cpu"):
        self.device = device
    
    def optimize_yolo(self, model_path: str, precision: str = "fp16") -> Any:
        """
        Optimiser un modèle YOLO
        
        Args:
            model_path: Chemin vers le modèle
            precision: "fp32" (précision), "fp16" (rapide), "int8" (très rapide)
        
        Returns:
            Modèle optimisé
        """
        if not YOLO_AVAILABLE:
            raise ImportError("Ultralytics YOLO non disponible")
        
        logger.info(f"Chargement modèle YOLO: {model_path}")
        model = YOLO(model_path)
        
        # Export vers format optimisé selon device
        if self.device == "cuda":
            # TensorRT pour NVIDIA (3-5x plus rapide)
            logger.info("Export TensorRT (NVIDIA)...")
            try:
                model.export(format="engine", half=(precision == "fp16"))
                return YOLO(model_path.replace(".pt", ".engine"))
            except Exception as e:
                logger.warning(f"TensorRT export failed: {e}, using ONNX")
                model.export(format="onnx", half=(precision == "fp16"))
                return model
        
        elif self.device == "cpu":
            # OpenVINO pour Intel CPU (2x plus rapide)
            logger.info("Export OpenVINO (Intel)...")
            try:
                model.export(format="openvino", half=False)  # FP16 non supporté CPU
                return model
            except Exception as e:
                logger.warning(f"OpenVINO export failed: {e}, using standard")
                return model
        
        else:
            # Format standard
            return model
    
    def enable_half_precision(self, model: Any) -> Any:
        """Activer FP16 (2x plus rapide, même précision pour détection)"""
        if TORCH_AVAILABLE and self.device in ["cuda", "mps"]:
            try:
                model.half()
                logger.info("FP16 activé (2x speedup)")
            except Exception as e:
                logger.warning(f"FP16 non supporté: {e}")
        
        return model
    
    def quantize_model(self, model: Any) -> Any:
        """
        Quantification INT8 (4x plus rapide, -2% précision)
        
        Recommandé pour CPU ou edge devices
        """
        if TORCH_AVAILABLE:
            try:
                quantized_model = torch.quantization.quantize_dynamic(
                    model, {torch.nn.Linear}, dtype=torch.qint8
                )
                logger.info("Quantification INT8 appliquée (4x speedup)")
                return quantized_model
            except Exception as e:
                logger.warning(f"Quantification failed: {e}")
        
        return model


class FramePreprocessor:
    """Prétraitement optimisé des frames"""
    
    @staticmethod
    def resize_fast(frame: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """
        Resize rapide avec interpolation optimale
        
        INTER_LINEAR = bon compromis vitesse/qualité
        INTER_AREA = meilleur pour downscaling
        """
        return cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def normalize_fast(frame: np.ndarray) -> np.ndarray:
        """Normalisation rapide (vectorisée)"""
        # Conversion uint8 -> float32 et normalisation [0, 1]
        return frame.astype(np.float32) / 255.0
    
    @staticmethod
    def apply_clahe(frame: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
        """
        CLAHE pour améliorer contraste (utile basse lumière)
        
        Seulement si nécessaire (coûteux en CPU)
        """
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    @staticmethod
    def denoise_fast(frame: np.ndarray) -> np.ndarray:
        """Débruitage rapide"""
        return cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)


class BatchProcessor:
    """Traitement par lots pour améliorer throughput"""
    
    def __init__(
        self,
        batch_size: int = 4,
        max_wait_ms: int = 50,
        device: str = "cpu"
    ):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.device = device
        
        self.frame_queue = queue.Queue(maxsize=batch_size * 2)
        self.result_queue = queue.Queue()
        
        self.running = False
        self.worker_thread = None
    
    def start(self, model: Any):
        """Démarrer le worker de batch processing"""
        self.running = True
        self.worker_thread = threading.Thread(
            target=self._batch_worker,
            args=(model,),
            daemon=True
        )
        self.worker_thread.start()
        logger.info(f"Batch processor démarré (batch_size={self.batch_size})")
    
    def stop(self):
        """Arrêter le worker"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        logger.info("Batch processor arrêté")
    
    def submit_frame(
        self,
        frame: np.ndarray,
        camera_id: int,
        timestamp: float
    ) -> str:
        """Soumettre une frame pour traitement"""
        frame_id = f"{camera_id}_{timestamp}"
        
        try:
            self.frame_queue.put((frame_id, frame, camera_id, timestamp), timeout=0.1)
            return frame_id
        except queue.Full:
            logger.warning("Batch queue pleine, frame dropped")
            return None
    
    def get_result(self, timeout: float = 0.1) -> Optional[Dict]:
        """Récupérer un résultat de traitement"""
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def _batch_worker(self, model: Any):
        """Worker thread pour batch processing"""
        batch_frames = []
        batch_metadata = []
        last_process_time = time.time()
        
        while self.running:
            try:
                # Collecter frames pour le batch
                while len(batch_frames) < self.batch_size:
                    # Timeout pour ne pas attendre trop longtemps
                    wait_time = (self.max_wait_ms / 1000.0)
                    
                    try:
                        frame_id, frame, camera_id, timestamp = self.frame_queue.get(
                            timeout=wait_time
                        )
                        
                        batch_frames.append(frame)
                        batch_metadata.append({
                            "frame_id": frame_id,
                            "camera_id": camera_id,
                            "timestamp": timestamp
                        })
                    
                    except queue.Empty:
                        # Timeout atteint, traiter ce qu'on a
                        break
                
                # Traiter le batch si non vide
                if batch_frames:
                    start_time = time.time()
                    
                    # Inférence batch
                    results = model(batch_frames, verbose=False)
                    
                    inference_time = (time.time() - start_time) * 1000  # ms
                    
                    # Dispatcher les résultats
                    for i, result in enumerate(results):
                        self.result_queue.put({
                            "frame_id": batch_metadata[i]["frame_id"],
                            "camera_id": batch_metadata[i]["camera_id"],
                            "timestamp": batch_metadata[i]["timestamp"],
                            "detections": result,
                            "inference_time_ms": inference_time / len(results)
                        })
                    
                    # Reset batch
                    batch_frames = []
                    batch_metadata = []
                    last_process_time = time.time()
            
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                batch_frames = []
                batch_metadata = []


class PerformanceMonitor:
    """Monitoring temps réel des performances"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        
        self.frame_times = deque(maxlen=window_size)
        self.inference_times = deque(maxlen=window_size)
        self.total_frames = 0
        self.dropped_frames = 0
        
        self.start_time = time.time()
    
    def record_frame(
        self,
        processing_time_ms: float,
        inference_time_ms: float,
        dropped: bool = False
    ):
        """Enregistrer une frame traitée"""
        self.frame_times.append(processing_time_ms)
        self.inference_times.append(inference_time_ms)
        self.total_frames += 1
        
        if dropped:
            self.dropped_frames += 1
    
    def get_metrics(self) -> PerformanceMetrics:
        """Obtenir les métriques actuelles"""
        if not self.frame_times:
            return PerformanceMetrics(
                fps=0, latency_ms=0, cpu_percent=0, gpu_percent=None,
                memory_mb=0, frames_processed=0, frames_dropped=0,
                inference_time_ms=0, preprocessing_time_ms=0, postprocessing_time_ms=0
            )
        
        # FPS moyen
        avg_frame_time = np.mean(self.frame_times)
        fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        # Latence
        latency_ms = np.mean(self.frame_times)
        
        # CPU/Mémoire
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        
        # GPU (si CUDA)
        gpu_percent = None
        if TORCH_AVAILABLE and torch.cuda.is_available():
            gpu_percent = torch.cuda.utilization()
        
        # Inférence
        avg_inference_time = np.mean(self.inference_times) if self.inference_times else 0
        
        return PerformanceMetrics(
            fps=fps,
            latency_ms=latency_ms,
            cpu_percent=cpu_percent,
            gpu_percent=gpu_percent,
            memory_mb=memory_mb,
            frames_processed=self.total_frames,
            frames_dropped=self.dropped_frames,
            inference_time_ms=avg_inference_time,
            preprocessing_time_ms=0,  # TODO
            postprocessing_time_ms=0  # TODO
        )
    
    def print_stats(self):
        """Afficher les stats"""
        metrics = self.get_metrics()
        
        print("\n" + "="*60)
        print("📊 PERFORMANCE METRICS")
        print("="*60)
        print(f"FPS:              {metrics.fps:.1f}")
        print(f"Latency:          {metrics.latency_ms:.1f} ms")
        print(f"Inference Time:   {metrics.inference_time_ms:.1f} ms")
        print(f"CPU Usage:        {metrics.cpu_percent:.1f}%")
        if metrics.gpu_percent:
            print(f"GPU Usage:        {metrics.gpu_percent:.1f}%")
        print(f"Memory:           {metrics.memory_mb:.0f} MB")
        print(f"Frames Processed: {metrics.frames_processed}")
        print(f"Frames Dropped:   {metrics.dropped_frames}")
        
        if metrics.frames_processed > 0:
            drop_rate = (metrics.dropped_frames / metrics.frames_processed) * 100
            print(f"Drop Rate:        {drop_rate:.2f}%")
        
        print("="*60 + "\n")


class AdaptiveFrameSkipper:
    """
    Skip intelligent de frames selon la charge CPU/GPU
    
    Si système surchargé: traiter 1 frame / 2 ou 1 / 3
    """
    
    def __init__(self, target_fps: int = 30, cpu_threshold: float = 80.0):
        self.target_fps = target_fps
        self.cpu_threshold = cpu_threshold
        
        self.frame_counter = 0
        self.skip_ratio = 1  # 1 = pas de skip, 2 = skip 1/2, 3 = skip 1/3
    
    def should_process_frame(self) -> bool:
        """Déterminer si on doit traiter cette frame"""
        self.frame_counter += 1
        
        # Vérifier CPU toutes les 10 frames
        if self.frame_counter % 10 == 0:
            cpu = psutil.cpu_percent(interval=0.01)
            
            if cpu > self.cpu_threshold:
                # Augmenter skip
                self.skip_ratio = min(self.skip_ratio + 1, 3)
                logger.warning(f"CPU élevé ({cpu:.1f}%), skip_ratio={self.skip_ratio}")
            elif cpu < self.cpu_threshold - 20:
                # Réduire skip
                self.skip_ratio = max(self.skip_ratio - 1, 1)
        
        # Décision de traitement
        return (self.frame_counter % self.skip_ratio) == 0


# =============================================================================
# EXEMPLE D'UTILISATION
# =============================================================================

if __name__ == "__main__":
    # 1. Détecter le meilleur hardware
    gpu_manager = GPUManager()
    print(f"Device: {gpu_manager.device_name}")
    print(f"Batch size optimal: {gpu_manager.max_batch_size}")
    
    # 2. Optimiser un modèle YOLO
    optimizer = ModelOptimizer(device=gpu_manager.device)
    # model = optimizer.optimize_yolo("yolov8n.pt", precision="fp16")
    
    # 3. Monitoring
    monitor = PerformanceMonitor()
    
    # 4. Adaptive frame skipping
    skipper = AdaptiveFrameSkipper(target_fps=30)
    
    print("\n✅ Performance Optimizer initialisé")
