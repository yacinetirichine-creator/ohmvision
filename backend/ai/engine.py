"""
OhmVision - Moteur IA Complet
==============================
Toutes les fonctionnalités de détection par package.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import time

# Import YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️ YOLO non disponible - mode simulation")


class DetectionType(Enum):
    PERSON = "person"
    VEHICLE = "vehicle"
    FALL = "fall"
    PPE_HELMET = "ppe_helmet"
    PPE_VEST = "ppe_vest"
    PPE_GLOVES = "ppe_gloves"
    FIRE = "fire"
    SMOKE = "smoke"
    LICENSE_PLATE = "license_plate"
    INTRUSION = "intrusion"
    CROWD = "crowd"
    LOITERING = "loitering"


@dataclass
class Detection:
    """Représente une détection"""
    type: DetectionType
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "center": self.center,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }


@dataclass
class Alert:
    """Représente une alerte"""
    type: str
    severity: str  # low, medium, high, critical
    message: str
    detections: List[Detection]
    timestamp: datetime
    camera_id: int
    snapshot: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "severity": self.severity,
            "message": self.message,
            "detections": [d.to_dict() for d in self.detections],
            "timestamp": self.timestamp.isoformat(),
            "camera_id": self.camera_id
        }


class PackageFeatures:
    """Définit les fonctionnalités par package"""
    
    STARTER = {
        "person_detection": True,
        "counting_basic": True,
        "alerts_email": True,
        "fall_detection": False,
        "ppe_detection": False,
        "vehicle_detection": False,
        "fire_detection": False,
        "lpr": False,
        "behavior_analysis": False,
        "heatmaps": False,
        "ai_agent": False,
        "api_access": False,
        "max_cameras": 4,
        "history_days": 7
    }
    
    BUSINESS = {
        "person_detection": True,
        "counting_basic": True,
        "counting_advanced": True,
        "alerts_email": True,
        "alerts_sms": True,
        "alerts_push": True,
        "fall_detection": True,
        "man_down": True,
        "ppe_detection": True,
        "ppe_helmet": True,
        "ppe_vest": True,
        "vehicle_detection": True,
        "fire_detection": False,
        "lpr": False,
        "behavior_analysis": False,
        "heatmaps": True,
        "zones": True,
        "reports": True,
        "ai_agent": True,
        "api_access": False,
        "max_cameras": 20,
        "history_days": 30
    }
    
    ENTERPRISE = {
        "person_detection": True,
        "counting_basic": True,
        "counting_advanced": True,
        "counting_queues": True,
        "alerts_email": True,
        "alerts_sms": True,
        "alerts_push": True,
        "alerts_webhook": True,
        "fall_detection": True,
        "man_down": True,
        "ppe_detection": True,
        "ppe_helmet": True,
        "ppe_vest": True,
        "ppe_gloves": True,
        "ppe_glasses": True,
        "vehicle_detection": True,
        "fire_detection": True,
        "smoke_detection": True,
        "lpr": True,
        "behavior_analysis": True,
        "loitering": True,
        "intrusion": True,
        "heatmaps": True,
        "zones": True,
        "reports": True,
        "ai_agent": True,
        "api_access": True,
        "on_premise": True,
        "multi_site": True,
        "max_cameras": -1,
        "history_days": 365
    }
    
    PLATINUM = {
        **ENTERPRISE,
        "custom_models": True,
        "predictive_ai": True,
        "sla_247": True,
        "dedicated_support": True,
        "custom_integrations": True,
        "white_label": True,
        "history_days": -1
    }
    
    @classmethod
    def get_features(cls, package: str) -> Dict:
        return getattr(cls, package.upper(), cls.STARTER)


class BaseDetector:
    """Classe de base pour les détecteurs"""
    
    def __init__(self):
        self.enabled = True
        self.sensitivity = 0.5
        self.min_confidence = 0.5
    
    def configure(self, config: Dict):
        """Configure le détecteur"""
        self.sensitivity = config.get("sensitivity", 0.5)
        self.min_confidence = config.get("min_confidence", 0.5)
        self.enabled = config.get("enabled", True)
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """À implémenter dans les sous-classes"""
        raise NotImplementedError


class PersonDetector(BaseDetector):
    """Détection de personnes avec YOLO"""
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        super().__init__()
        self.model = None
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(self.model_path)
                print("✅ Modèle PersonDetector chargé")
            except Exception as e:
                print(f"⚠️ Erreur chargement modèle: {e}")
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled or self.model is None:
            return []
        
        detections = []
        results = self.model(frame, conf=self.min_confidence, verbose=False)
        
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == 0:  # Classe personne
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    
                    detections.append(Detection(
                        type=DetectionType.PERSON,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=((x1 + x2) // 2, (y1 + y2) // 2),
                        timestamp=datetime.now(),
                        metadata={"width": x2 - x1, "height": y2 - y1}
                    ))
        
        return detections


class VehicleDetector(BaseDetector):
    """Détection de véhicules"""
    
    VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        super().__init__()
        self.model = None
        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(model_path)
            except:
                pass
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled or self.model is None:
            return []
        
        detections = []
        results = self.model(frame, conf=self.min_confidence, verbose=False)
        
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                if class_id in self.VEHICLE_CLASSES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    
                    vehicle_type = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}.get(class_id, "vehicle")
                    
                    detections.append(Detection(
                        type=DetectionType.VEHICLE,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=((x1 + x2) // 2, (y1 + y2) // 2),
                        timestamp=datetime.now(),
                        metadata={"vehicle_type": vehicle_type}
                    ))
        
        return detections


class FallDetector(BaseDetector):
    """Détection de chute basée sur le ratio et le mouvement"""
    
    def __init__(self):
        super().__init__()
        self.tracked_persons = defaultdict(lambda: {
            "positions": [],
            "ratios": [],
            "fall_start": None,
            "confirmed": False
        })
        self.ratio_threshold = 1.2
        self.time_threshold = 1.5
        self.next_id = 0
    
    def detect(self, frame: np.ndarray, person_detections: List[Detection]) -> List[Detection]:
        if not self.enabled:
            return []
        
        fall_detections = []
        current_time = time.time()
        
        for det in person_detections:
            # Suivi simplifié par position
            person_id = self._get_person_id(det.center)
            person = self.tracked_persons[person_id]
            
            width = det.metadata.get("width", 0)
            height = det.metadata.get("height", 1)
            ratio = width / height if height > 0 else 0
            
            person["ratios"].append(ratio)
            if len(person["ratios"]) > 10:
                person["ratios"].pop(0)
            
            avg_ratio = np.mean(person["ratios"])
            
            if avg_ratio > self.ratio_threshold:
                if person["fall_start"] is None:
                    person["fall_start"] = current_time
                elif current_time - person["fall_start"] >= self.time_threshold:
                    if not person["confirmed"]:
                        person["confirmed"] = True
                        fall_detections.append(Detection(
                            type=DetectionType.FALL,
                            confidence=0.85,
                            bbox=det.bbox,
                            center=det.center,
                            timestamp=datetime.now(),
                            metadata={"ratio": avg_ratio, "person_id": person_id}
                        ))
            else:
                person["fall_start"] = None
                person["confirmed"] = False
        
        return fall_detections
    
    def _get_person_id(self, center: Tuple[int, int]) -> int:
        # Suivi simplifié - en production utiliser un vrai tracker
        self.next_id += 1
        return self.next_id


class PPEDetector(BaseDetector):
    """Détection d'équipements de protection"""
    
    def __init__(self):
        super().__init__()
        # Couleurs HSV pour les gilets
        self.vest_colors = [
            (np.array([20, 100, 100]), np.array([35, 255, 255])),   # Jaune
            (np.array([10, 100, 100]), np.array([25, 255, 255])),   # Orange
            (np.array([35, 100, 100]), np.array([85, 255, 255])),   # Vert
        ]
        # Couleurs pour les casques
        self.helmet_colors = [
            (np.array([0, 0, 180]), np.array([180, 30, 255])),      # Blanc
            (np.array([20, 100, 100]), np.array([35, 255, 255])),   # Jaune
            (np.array([100, 100, 100]), np.array([130, 255, 255])), # Bleu
        ]
        self.vest_threshold = 0.15
        self.helmet_threshold = 0.20
    
    def detect(self, frame: np.ndarray, person_detections: List[Detection]) -> List[Detection]:
        if not self.enabled:
            return []
        
        ppe_detections = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for person in person_detections:
            x1, y1, x2, y2 = person.bbox
            height = y2 - y1
            
            # Zone tête (casque)
            head_y2 = y1 + int(height * 0.25)
            head_region = hsv[max(0, y1-20):head_y2, x1:x2]
            has_helmet = self._detect_helmet(head_region)
            
            # Zone torse (gilet)
            torso_y1 = y1 + int(height * 0.2)
            torso_y2 = y1 + int(height * 0.7)
            torso_region = hsv[torso_y1:torso_y2, x1:x2]
            has_vest = self._detect_vest(torso_region)
            
            if not has_helmet:
                ppe_detections.append(Detection(
                    type=DetectionType.PPE_HELMET,
                    confidence=0.8,
                    bbox=person.bbox,
                    center=person.center,
                    timestamp=datetime.now(),
                    metadata={"missing": True, "item": "helmet"}
                ))
            
            if not has_vest:
                ppe_detections.append(Detection(
                    type=DetectionType.PPE_VEST,
                    confidence=0.8,
                    bbox=person.bbox,
                    center=person.center,
                    timestamp=datetime.now(),
                    metadata={"missing": True, "item": "vest"}
                ))
        
        return ppe_detections
    
    def _detect_helmet(self, region: np.ndarray) -> bool:
        if region.size == 0:
            return False
        
        total_pixels = region.shape[0] * region.shape[1]
        
        for lower, upper in self.helmet_colors:
            mask = cv2.inRange(region, lower, upper)
            if np.sum(mask > 0) / total_pixels > self.helmet_threshold:
                return True
        return False
    
    def _detect_vest(self, region: np.ndarray) -> bool:
        if region.size == 0:
            return False
        
        total_pixels = region.shape[0] * region.shape[1]
        
        for lower, upper in self.vest_colors:
            mask = cv2.inRange(region, lower, upper)
            if np.sum(mask > 0) / total_pixels > self.vest_threshold:
                return True
        return False


class FireSmokeDetector(BaseDetector):
    """Détection de feu et fumée basée sur la couleur et le mouvement"""
    
    def __init__(self):
        super().__init__()
        # Couleurs du feu (HSV)
        self.fire_lower = np.array([0, 100, 200])
        self.fire_upper = np.array([25, 255, 255])
        # Gris pour la fumée
        self.smoke_lower = np.array([0, 0, 100])
        self.smoke_upper = np.array([180, 50, 200])
        self.min_area = 500
        self.prev_frame = None
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        if not self.enabled:
            return []
        
        detections = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Détection feu
        fire_mask = cv2.inRange(hsv, self.fire_lower, self.fire_upper)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, np.ones((5, 5)))
        
        contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > self.min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append(Detection(
                    type=DetectionType.FIRE,
                    confidence=min(0.5 + area / 10000, 0.95),
                    bbox=(x, y, x + w, y + h),
                    center=(x + w // 2, y + h // 2),
                    timestamp=datetime.now(),
                    metadata={"area": area}
                ))
        
        # Détection fumée (avec mouvement)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.prev_frame is not None:
            diff = cv2.absdiff(gray, self.prev_frame)
            smoke_mask = cv2.inRange(hsv, self.smoke_lower, self.smoke_upper)
            combined = cv2.bitwise_and(smoke_mask, diff)
            
            contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > self.min_area * 2:
                    x, y, w, h = cv2.boundingRect(cnt)
                    detections.append(Detection(
                        type=DetectionType.SMOKE,
                        confidence=min(0.4 + area / 20000, 0.85),
                        bbox=(x, y, x + w, y + h),
                        center=(x + w // 2, y + h // 2),
                        timestamp=datetime.now(),
                        metadata={"area": area}
                    ))
        
        self.prev_frame = gray
        return detections


class PeopleCounter:
    """Comptage de personnes avec ligne virtuelle"""
    
    def __init__(self, line_position: float = 0.5, direction: str = "horizontal"):
        self.line_position = line_position
        self.direction = direction
        self.count_in = 0
        self.count_out = 0
        self.tracked = defaultdict(lambda: {"positions": [], "counted": False})
        self.next_id = 0
    
    def update(self, detections: List[Detection], frame_shape: Tuple) -> Dict:
        """Met à jour le comptage"""
        height, width = frame_shape[:2]
        
        if self.direction == "horizontal":
            line_coord = int(height * self.line_position)
        else:
            line_coord = int(width * self.line_position)
        
        events = []
        
        for det in detections:
            if det.type != DetectionType.PERSON:
                continue
            
            person_id = self._match_person(det.center)
            person = self.tracked[person_id]
            person["positions"].append(det.center)
            
            if len(person["positions"]) > 30:
                person["positions"].pop(0)
            
            if len(person["positions"]) >= 3 and not person["counted"]:
                old_pos = person["positions"][-3]
                new_pos = person["positions"][-1]
                
                if self.direction == "horizontal":
                    old_coord, new_coord = old_pos[1], new_pos[1]
                else:
                    old_coord, new_coord = old_pos[0], new_pos[0]
                
                if (old_coord < line_coord <= new_coord):
                    self.count_out += 1
                    person["counted"] = True
                    events.append({"type": "exit", "id": person_id})
                elif (old_coord > line_coord >= new_coord):
                    self.count_in += 1
                    person["counted"] = True
                    events.append({"type": "entry", "id": person_id})
        
        return {
            "entries": self.count_in,
            "exits": self.count_out,
            "inside": self.count_in - self.count_out,
            "events": events
        }
    
    def _match_person(self, center: Tuple[int, int]) -> int:
        # Matching simplifié par distance
        for pid, data in self.tracked.items():
            if data["positions"]:
                last_pos = data["positions"][-1]
                dist = np.sqrt((center[0] - last_pos[0])**2 + (center[1] - last_pos[1])**2)
                if dist < 100:
                    return pid
        
        self.next_id += 1
        return self.next_id
    
    def reset(self):
        self.count_in = 0
        self.count_out = 0
        self.tracked.clear()


class ZoneManager:
    """Gestion des zones de détection"""
    
    def __init__(self):
        self.zones = []
    
    def add_zone(self, zone_id: str, points: List[Tuple[int, int]], 
                 zone_type: str = "forbidden", name: str = ""):
        """Ajoute une zone"""
        self.zones.append({
            "id": zone_id,
            "points": np.array(points, dtype=np.int32),
            "type": zone_type,  # forbidden, counting, monitoring
            "name": name
        })
    
    def check_intrusion(self, detections: List[Detection]) -> List[Detection]:
        """Vérifie les intrusions dans les zones interdites"""
        intrusions = []
        
        for zone in self.zones:
            if zone["type"] != "forbidden":
                continue
            
            for det in detections:
                if det.type == DetectionType.PERSON:
                    if cv2.pointPolygonTest(zone["points"], det.center, False) >= 0:
                        intrusions.append(Detection(
                            type=DetectionType.INTRUSION,
                            confidence=0.95,
                            bbox=det.bbox,
                            center=det.center,
                            timestamp=datetime.now(),
                            metadata={"zone_id": zone["id"], "zone_name": zone["name"]}
                        ))
        
        return intrusions
    
    def draw_zones(self, frame: np.ndarray) -> np.ndarray:
        """Dessine les zones sur l'image"""
        overlay = frame.copy()
        
        for zone in self.zones:
            color = (0, 0, 255) if zone["type"] == "forbidden" else (0, 255, 255)
            cv2.fillPoly(overlay, [zone["points"]], color)
            cv2.polylines(frame, [zone["points"]], True, color, 2)
        
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        return frame


class HeatmapGenerator:
    """Génère des heatmaps de mouvement"""
    
    def __init__(self, width: int = 640, height: int = 480):
        self.heatmap = np.zeros((height, width), dtype=np.float32)
        self.decay_rate = 0.995
    
    def update(self, detections: List[Detection]):
        """Met à jour la heatmap"""
        # Decay
        self.heatmap *= self.decay_rate
        
        # Ajoute les nouvelles détections
        for det in detections:
            if det.type == DetectionType.PERSON:
                cx, cy = det.center
                cv2.circle(self.heatmap, (cx, cy), 30, 1.0, -1)
    
    def get_heatmap(self) -> np.ndarray:
        """Retourne la heatmap colorée"""
        normalized = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
        colored = cv2.applyColorMap(normalized.astype(np.uint8), cv2.COLORMAP_JET)
        return colored
    
    def reset(self):
        self.heatmap.fill(0)


class AIEngine:
    """Moteur IA principal - Orchestre toutes les détections"""
    
    def __init__(self, package: str = "starter"):
        self.package = package
        self.features = PackageFeatures.get_features(package)
        
        # Initialise les détecteurs selon le package
        self.person_detector = PersonDetector() if self.features.get("person_detection") else None
        self.vehicle_detector = VehicleDetector() if self.features.get("vehicle_detection") else None
        self.fall_detector = FallDetector() if self.features.get("fall_detection") else None
        self.ppe_detector = PPEDetector() if self.features.get("ppe_detection") else None
        self.fire_detector = FireSmokeDetector() if self.features.get("fire_detection") else None
        
        # Compteur
        self.counter = PeopleCounter() if self.features.get("counting_basic") else None
        
        # Zones
        self.zone_manager = ZoneManager() if self.features.get("zones") else None
        
        # Heatmap
        self.heatmap = HeatmapGenerator() if self.features.get("heatmaps") else None
        
        # Alertes
        self.alert_callbacks = []
        self.alert_cooldowns = {}
        self.cooldown_seconds = 10
        
        print(f"✅ AIEngine initialisé - Package: {package}")
        print(f"   Fonctionnalités: {[k for k, v in self.features.items() if v is True]}")
    
    def process_frame(self, frame: np.ndarray, camera_id: int = 0) -> Dict[str, Any]:
        """Traite une frame et retourne les résultats"""
        results = {
            "detections": [],
            "alerts": [],
            "counting": None,
            "timestamp": datetime.now().isoformat()
        }
        
        all_detections = []
        
        # 1. Détection de personnes
        if self.person_detector:
            persons = self.person_detector.detect(frame)
            all_detections.extend(persons)
            
            # 2. Détection de chute (nécessite les personnes)
            if self.fall_detector and persons:
                falls = self.fall_detector.detect(frame, persons)
                all_detections.extend(falls)
                for fall in falls:
                    self._trigger_alert("fall", "critical", 
                                       "Chute détectée", [fall], camera_id)
            
            # 3. Détection EPI
            if self.ppe_detector and persons:
                ppe_issues = self.ppe_detector.detect(frame, persons)
                all_detections.extend(ppe_issues)
                if ppe_issues:
                    self._trigger_alert("ppe_missing", "medium",
                                       f"EPI manquant détecté ({len(ppe_issues)} problèmes)",
                                       ppe_issues, camera_id)
            
            # 4. Comptage
            if self.counter:
                results["counting"] = self.counter.update(persons, frame.shape)
            
            # 5. Zones
            if self.zone_manager:
                intrusions = self.zone_manager.check_intrusion(persons)
                all_detections.extend(intrusions)
                for intrusion in intrusions:
                    self._trigger_alert("intrusion", "high",
                                       f"Intrusion zone {intrusion.metadata.get('zone_name', '')}",
                                       [intrusion], camera_id)
            
            # 6. Heatmap
            if self.heatmap:
                self.heatmap.update(persons)
        
        # 7. Détection véhicules
        if self.vehicle_detector:
            vehicles = self.vehicle_detector.detect(frame)
            all_detections.extend(vehicles)
        
        # 8. Détection feu/fumée
        if self.fire_detector:
            fire_smoke = self.fire_detector.detect(frame)
            all_detections.extend(fire_smoke)
            for det in fire_smoke:
                severity = "critical" if det.type == DetectionType.FIRE else "high"
                self._trigger_alert(det.type.value, severity,
                                   f"{det.type.value.replace('_', ' ').title()} détecté!",
                                   [det], camera_id)
        
        results["detections"] = [d.to_dict() for d in all_detections]
        
        return results
    
    def _trigger_alert(self, alert_type: str, severity: str, 
                       message: str, detections: List[Detection], camera_id: int):
        """Déclenche une alerte avec cooldown"""
        cooldown_key = f"{camera_id}_{alert_type}"
        now = time.time()
        
        if cooldown_key in self.alert_cooldowns:
            if now - self.alert_cooldowns[cooldown_key] < self.cooldown_seconds:
                return
        
        self.alert_cooldowns[cooldown_key] = now
        
        alert = Alert(
            type=alert_type,
            severity=severity,
            message=message,
            detections=detections,
            timestamp=datetime.now(),
            camera_id=camera_id
        )
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Erreur callback alerte: {e}")
    
    def on_alert(self, callback):
        """Enregistre un callback pour les alertes"""
        self.alert_callbacks.append(callback)
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Dessine les détections sur l'image"""
        annotated = frame.copy()
        
        colors = {
            "person": (0, 255, 0),
            "vehicle": (255, 255, 0),
            "fall": (0, 0, 255),
            "ppe_helmet": (0, 165, 255),
            "ppe_vest": (0, 165, 255),
            "fire": (0, 0, 255),
            "smoke": (128, 128, 128),
            "intrusion": (0, 0, 255)
        }
        
        for det in detections:
            color = colors.get(det["type"], (255, 255, 255))
            x1, y1, x2, y2 = det["bbox"]
            
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            label = f"{det['type']} {det['confidence']:.0%}"
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Dessine les zones si activé
        if self.zone_manager:
            annotated = self.zone_manager.draw_zones(annotated)
        
        return annotated
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques"""
        stats = {
            "package": self.package,
            "features_enabled": [k for k, v in self.features.items() if v is True]
        }
        
        if self.counter:
            stats["counting"] = {
                "entries": self.counter.count_in,
                "exits": self.counter.count_out,
                "inside": self.counter.count_in - self.counter.count_out
            }
        
        return stats
    
    def configure_camera(self, config: Dict):
        """Configure les détecteurs pour une caméra"""
        if self.person_detector:
            self.person_detector.configure(config.get("person_detection", {}))
        if self.fall_detector:
            self.fall_detector.configure(config.get("fall_detection", {}))
        if self.ppe_detector:
            self.ppe_detector.configure(config.get("ppe_detection", {}))
        if self.fire_detector:
            self.fire_detector.configure(config.get("fire_detection", {}))
        
        # Configure les zones
        if self.zone_manager and "zones" in config:
            for zone in config["zones"]:
                self.zone_manager.add_zone(
                    zone["id"],
                    zone["points"],
                    zone.get("type", "forbidden"),
                    zone.get("name", "")
                )


# Instance globale par défaut
ai_engine = AIEngine(package="enterprise")

# Test
if __name__ == "__main__":
    print("Test du moteur IA OhmVision")
    
    # Test avec différents packages
    for package in ["starter", "business", "enterprise", "platinum"]:
        print(f"\n--- Package {package.upper()} ---")
        engine = AIEngine(package)
        print(engine.get_stats())
