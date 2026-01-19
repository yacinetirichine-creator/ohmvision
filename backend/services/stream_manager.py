"""
OhmVision - Video Streaming Service
Gère les flux vidéo RTSP et le streaming vers le navigateur
"""

import cv2
import asyncio
import threading
import time
from typing import Dict, Optional, Generator, Callable
from dataclasses import dataclass, field
from queue import Queue, Empty
import logging
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CameraStream:
    """Représente un flux caméra actif"""
    camera_id: int
    rtsp_url: str
    name: str = ""
    is_running: bool = False
    frame: Optional[np.ndarray] = None
    last_frame_time: float = 0
    fps: float = 0
    width: int = 0
    height: int = 0
    error: Optional[str] = None
    reconnect_attempts: int = 0
    _capture: Optional[cv2.VideoCapture] = field(default=None, repr=False)
    _thread: Optional[threading.Thread] = field(default=None, repr=False)
    _stop_event: threading.Event = field(default_factory=threading.Event, repr=False)
    _subscribers: Dict[str, Queue] = field(default_factory=dict, repr=False)


class StreamManager:
    """
    Gestionnaire central des flux vidéo
    Gère les connexions RTSP et le streaming vers les clients
    """
    
    MAX_RECONNECT_ATTEMPTS = 5
    RECONNECT_DELAY = 5  # secondes
    FRAME_TIMEOUT = 10  # secondes sans frame = déconnexion
    
    def __init__(self):
        self._streams: Dict[int, CameraStream] = {}
        self._lock = threading.Lock()
    
    def start_stream(self, camera_id: int, rtsp_url: str, name: str = "") -> bool:
        """
        Démarre le streaming pour une caméra
        
        Args:
            camera_id: ID unique de la caméra
            rtsp_url: URL RTSP complète
            name: Nom de la caméra (optionnel)
        
        Returns:
            True si démarré avec succès
        """
        with self._lock:
            # Si déjà en cours, retourner
            if camera_id in self._streams and self._streams[camera_id].is_running:
                logger.info(f"Stream {camera_id} already running")
                return True
            
            # Créer le stream
            stream = CameraStream(
                camera_id=camera_id,
                rtsp_url=rtsp_url,
                name=name
            )
            
            self._streams[camera_id] = stream
        
        # Démarrer le thread de capture
        self._start_capture_thread(stream)
        
        return True
    
    def stop_stream(self, camera_id: int):
        """Arrête le streaming pour une caméra"""
        with self._lock:
            if camera_id not in self._streams:
                return
            
            stream = self._streams[camera_id]
            stream._stop_event.set()
            
            if stream._thread and stream._thread.is_alive():
                stream._thread.join(timeout=5)
            
            if stream._capture:
                stream._capture.release()
            
            del self._streams[camera_id]
            logger.info(f"Stream {camera_id} stopped")
    
    def stop_all(self):
        """Arrête tous les streams"""
        camera_ids = list(self._streams.keys())
        for camera_id in camera_ids:
            self.stop_stream(camera_id)
    
    def get_frame(self, camera_id: int) -> Optional[np.ndarray]:
        """Récupère la dernière frame d'une caméra"""
        if camera_id not in self._streams:
            return None
        return self._streams[camera_id].frame
    
    def get_jpeg_frame(self, camera_id: int, quality: int = 80) -> Optional[bytes]:
        """Récupère la dernière frame en JPEG"""
        frame = self.get_frame(camera_id)
        if frame is None:
            return None
        
        # Encoder en JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, jpeg = cv2.imencode('.jpg', frame, encode_param)
        return jpeg.tobytes()
    
    def get_stream_info(self, camera_id: int) -> Optional[Dict]:
        """Récupère les infos d'un stream"""
        if camera_id not in self._streams:
            return None
        
        stream = self._streams[camera_id]
        return {
            "camera_id": stream.camera_id,
            "name": stream.name,
            "is_running": stream.is_running,
            "width": stream.width,
            "height": stream.height,
            "fps": stream.fps,
            "error": stream.error,
            "last_frame_age": time.time() - stream.last_frame_time if stream.last_frame_time else None
        }
    
    def list_streams(self) -> Dict[int, Dict]:
        """Liste tous les streams actifs"""
        return {
            camera_id: self.get_stream_info(camera_id)
            for camera_id in self._streams
        }
    
    def subscribe(self, camera_id: int, subscriber_id: str) -> Queue:
        """
        S'abonne aux frames d'une caméra
        
        Returns:
            Queue qui recevra les frames JPEG
        """
        if camera_id not in self._streams:
            raise ValueError(f"Stream {camera_id} not found")
        
        queue = Queue(maxsize=10)  # Buffer de 10 frames max
        self._streams[camera_id]._subscribers[subscriber_id] = queue
        return queue
    
    def unsubscribe(self, camera_id: int, subscriber_id: str):
        """Se désabonne des frames d'une caméra"""
        if camera_id in self._streams:
            self._streams[camera_id]._subscribers.pop(subscriber_id, None)
    
    def generate_mjpeg(self, camera_id: int, 
                       fps_limit: int = 15,
                       quality: int = 70) -> Generator[bytes, None, None]:
        """
        Générateur MJPEG pour streaming HTTP
        
        Args:
            camera_id: ID de la caméra
            fps_limit: Limite de FPS pour économiser la bande passante
            quality: Qualité JPEG (1-100)
        
        Yields:
            Frames JPEG formatées pour multipart/x-mixed-replace
        """
        if camera_id not in self._streams:
            yield b''
            return
        
        frame_interval = 1.0 / fps_limit
        last_frame_time = 0
        
        while camera_id in self._streams:
            current_time = time.time()
            
            # Limiter le FPS
            if current_time - last_frame_time < frame_interval:
                time.sleep(0.01)
                continue
            
            # Récupérer la frame
            jpeg = self.get_jpeg_frame(camera_id, quality)
            
            if jpeg:
                last_frame_time = current_time
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n'
                )
            else:
                # Pas de frame, attendre un peu
                time.sleep(0.1)
    
    def _start_capture_thread(self, stream: CameraStream):
        """Démarre le thread de capture pour un stream"""
        stream._stop_event.clear()
        stream._thread = threading.Thread(
            target=self._capture_loop,
            args=(stream,),
            daemon=True
        )
        stream._thread.start()
    
    def _capture_loop(self, stream: CameraStream):
        """Boucle de capture vidéo (tourne dans un thread séparé)"""
        logger.info(f"Starting capture for camera {stream.camera_id}: {stream.rtsp_url}")
        
        while not stream._stop_event.is_set():
            try:
                # Ouvrir la connexion RTSP
                stream._capture = cv2.VideoCapture(stream.rtsp_url)
                
                # Configurer pour le streaming
                stream._capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                if not stream._capture.isOpened():
                    raise Exception("Failed to open RTSP stream")
                
                # Récupérer les infos
                stream.width = int(stream._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                stream.height = int(stream._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                stream.fps = stream._capture.get(cv2.CAP_PROP_FPS) or 25
                
                stream.is_running = True
                stream.error = None
                stream.reconnect_attempts = 0
                
                logger.info(f"Camera {stream.camera_id} connected: "
                           f"{stream.width}x{stream.height} @ {stream.fps}fps")
                
                # Boucle de lecture des frames
                frame_count = 0
                start_time = time.time()
                
                while not stream._stop_event.is_set():
                    ret, frame = stream._capture.read()
                    
                    if not ret:
                        logger.warning(f"Camera {stream.camera_id}: Failed to read frame")
                        break
                    
                    # Stocker la frame
                    stream.frame = frame
                    stream.last_frame_time = time.time()
                    
                    # Calculer le FPS réel
                    frame_count += 1
                    elapsed = time.time() - start_time
                    if elapsed >= 1.0:
                        stream.fps = frame_count / elapsed
                        frame_count = 0
                        start_time = time.time()
                    
                    # Notifier les subscribers
                    self._notify_subscribers(stream, frame)
                    
                    # Petite pause pour ne pas surcharger le CPU
                    time.sleep(0.01)
                
            except Exception as e:
                stream.error = str(e)
                stream.is_running = False
                logger.error(f"Camera {stream.camera_id} error: {e}")
                
            finally:
                if stream._capture:
                    stream._capture.release()
                    stream._capture = None
            
            # Tentative de reconnexion
            if not stream._stop_event.is_set():
                stream.reconnect_attempts += 1
                
                if stream.reconnect_attempts >= self.MAX_RECONNECT_ATTEMPTS:
                    logger.error(f"Camera {stream.camera_id}: Max reconnect attempts reached")
                    stream.error = "Max reconnection attempts reached"
                    break
                
                logger.info(f"Camera {stream.camera_id}: Reconnecting in {self.RECONNECT_DELAY}s "
                           f"(attempt {stream.reconnect_attempts}/{self.MAX_RECONNECT_ATTEMPTS})")
                
                time.sleep(self.RECONNECT_DELAY)
        
        stream.is_running = False
        logger.info(f"Capture loop ended for camera {stream.camera_id}")
    
    def _notify_subscribers(self, stream: CameraStream, frame: np.ndarray):
        """Notifie tous les subscribers d'une nouvelle frame"""
        # Encoder en JPEG une seule fois
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        _, jpeg = cv2.imencode('.jpg', frame, encode_param)
        jpeg_bytes = jpeg.tobytes()
        
        # Envoyer à tous les subscribers
        dead_subscribers = []
        
        for subscriber_id, queue in stream._subscribers.items():
            try:
                # Non-blocking put, drop si la queue est pleine
                queue.put_nowait(jpeg_bytes)
            except:
                # Queue pleine ou erreur, marquer pour suppression
                dead_subscribers.append(subscriber_id)
        
        # Nettoyer les subscribers morts
        for subscriber_id in dead_subscribers:
            stream._subscribers.pop(subscriber_id, None)


# Instance globale
stream_manager = StreamManager()


# Fonctions utilitaires pour l'overlay
def draw_detection_overlay(frame: np.ndarray, 
                           detections: list,
                           show_labels: bool = True) -> np.ndarray:
    """
    Dessine les détections sur une frame
    
    Args:
        frame: Image OpenCV
        detections: Liste de détections [{"box": [x1,y1,x2,y2], "label": str, "confidence": float}]
        show_labels: Afficher les labels
    
    Returns:
        Frame avec overlay
    """
    frame_copy = frame.copy()
    
    colors = {
        "person": (0, 255, 0),      # Vert
        "fall": (0, 0, 255),         # Rouge
        "fire": (0, 128, 255),       # Orange
        "smoke": (128, 128, 128),    # Gris
        "helmet": (255, 255, 0),     # Cyan
        "vest": (255, 0, 255),       # Magenta
        "default": (255, 255, 255)   # Blanc
    }
    
    for det in detections:
        box = det.get("box", [])
        if len(box) != 4:
            continue
        
        x1, y1, x2, y2 = map(int, box)
        label = det.get("label", "object")
        confidence = det.get("confidence", 0)
        
        # Couleur selon le type
        color = colors.get(label.lower(), colors["default"])
        
        # Dessiner la boîte
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
        
        # Dessiner le label
        if show_labels:
            text = f"{label} {confidence:.0%}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            
            # Fond du texte
            cv2.rectangle(frame_copy, 
                         (x1, y1 - text_height - 10),
                         (x1 + text_width + 10, y1),
                         color, -1)
            
            # Texte
            cv2.putText(frame_copy, text,
                       (x1 + 5, y1 - 5),
                       font, font_scale, (0, 0, 0), thickness)
    
    return frame_copy


def draw_counting_line(frame: np.ndarray,
                       line: dict,
                       count_in: int = 0,
                       count_out: int = 0) -> np.ndarray:
    """
    Dessine une ligne de comptage sur une frame
    
    Args:
        frame: Image OpenCV
        line: {"x1": int, "y1": int, "x2": int, "y2": int}
        count_in: Nombre d'entrées
        count_out: Nombre de sorties
    
    Returns:
        Frame avec la ligne
    """
    frame_copy = frame.copy()
    
    x1 = int(line.get("x1", 0))
    y1 = int(line.get("y1", 0))
    x2 = int(line.get("x2", frame.shape[1]))
    y2 = int(line.get("y2", 0))
    
    # Dessiner la ligne
    cv2.line(frame_copy, (x1, y1), (x2, y2), (0, 255, 255), 2)
    
    # Afficher les compteurs
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2
    
    cv2.putText(frame_copy, f"IN: {count_in}",
               (mid_x - 50, mid_y - 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.putText(frame_copy, f"OUT: {count_out}",
               (mid_x - 50, mid_y + 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return frame_copy


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = StreamManager()
    
    # Test avec une URL RTSP (remplacer par une vraie URL)
    test_url = "rtsp://admin:password@192.168.1.64:554/stream1"
    
    print("Starting stream...")
    manager.start_stream(1, test_url, "Test Camera")
    
    print("Waiting for frames...")
    time.sleep(5)
    
    info = manager.get_stream_info(1)
    print(f"Stream info: {info}")
    
    frame = manager.get_frame(1)
    if frame is not None:
        print(f"Got frame: {frame.shape}")
        cv2.imwrite("test_frame.jpg", frame)
        print("Saved to test_frame.jpg")
    
    print("Stopping stream...")
    manager.stop_stream(1)
    print("Done")
