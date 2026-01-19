"""
OhmVision - Advanced Behavior Analytics
Analyse comportementale avancée et détection d'anomalies
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class BehaviorType(str, Enum):
    """Types de comportements détectables"""
    NORMAL = "normal"
    LOITERING = "loitering"           # Flânerie prolongée
    RUNNING = "running"               # Course
    FIGHTING = "fighting"             # Bagarre
    CROWD_FORMING = "crowd_forming"   # Formation de foule
    CROWD_DISPERSING = "crowd_dispersing"
    WRONG_DIRECTION = "wrong_direction"  # Sens interdit
    TAILGATING = "tailgating"         # Suivre de trop près
    ABANDONED_OBJECT = "abandoned_object"
    INTRUSION = "intrusion"
    FALL = "fall"
    ERRATIC_MOVEMENT = "erratic_movement"  # Mouvement erratique


@dataclass
class TrackedPerson:
    """Personne suivie dans le temps"""
    track_id: int
    positions: deque = field(default_factory=lambda: deque(maxlen=300))  # ~10 sec à 30fps
    timestamps: deque = field(default_factory=lambda: deque(maxlen=300))
    first_seen: datetime = None
    last_seen: datetime = None
    zone_history: List[str] = field(default_factory=list)
    
    # Métriques calculées
    avg_speed: float = 0.0
    max_speed: float = 0.0
    total_distance: float = 0.0
    dwell_time: float = 0.0
    
    # État
    is_stationary: bool = False
    current_behavior: BehaviorType = BehaviorType.NORMAL
    behavior_confidence: float = 0.0


@dataclass
class HeatmapData:
    """Données de heatmap"""
    width: int
    height: int
    grid_size: int = 20  # Cellules de 20x20 pixels
    data: np.ndarray = None
    
    def __post_init__(self):
        if self.data is None:
            grid_w = self.width // self.grid_size
            grid_h = self.height // self.grid_size
            self.data = np.zeros((grid_h, grid_w), dtype=np.float32)
    
    def add_point(self, x: int, y: int, weight: float = 1.0):
        """Ajoute un point à la heatmap"""
        grid_x = min(x // self.grid_size, self.data.shape[1] - 1)
        grid_y = min(y // self.grid_size, self.data.shape[0] - 1)
        self.data[grid_y, grid_x] += weight
    
    def normalize(self) -> np.ndarray:
        """Normalise la heatmap entre 0 et 1"""
        if self.data.max() > 0:
            return self.data / self.data.max()
        return self.data
    
    def get_hot_zones(self, threshold: float = 0.7) -> List[Tuple[int, int]]:
        """Retourne les zones chaudes"""
        normalized = self.normalize()
        hot = np.where(normalized > threshold)
        return list(zip(hot[1].tolist(), hot[0].tolist()))
    
    def decay(self, factor: float = 0.99):
        """Applique un decay temporel"""
        self.data *= factor


class BehaviorAnalyzer:
    """
    Analyseur de comportements
    Détecte les comportements anormaux en temps réel
    """
    
    # Seuils de détection
    LOITERING_TIME_THRESHOLD = 120  # 2 minutes
    RUNNING_SPEED_THRESHOLD = 3.0   # m/s
    STATIONARY_SPEED_THRESHOLD = 0.1
    CROWD_THRESHOLD = 5  # Personnes dans une zone
    CROWD_DENSITY_THRESHOLD = 0.5  # personnes/m²
    
    def __init__(self, frame_width: int = 1920, frame_height: int = 1080):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        self.tracked_persons: Dict[int, TrackedPerson] = {}
        self.heatmap = HeatmapData(frame_width, frame_height)
        
        # Historique des comportements détectés
        self.behavior_history: deque = deque(maxlen=1000)
        
        # Zones définies
        self.zones: Dict[str, Dict] = {}  # zone_name -> coordinates
        self.restricted_zones: List[str] = []
        self.direction_zones: Dict[str, str] = {}  # zone_name -> expected_direction
    
    def update(self, detections: List[Dict], timestamp: datetime = None) -> List[Dict]:
        """
        Met à jour l'analyse avec les nouvelles détections
        
        Args:
            detections: Liste des détections [{"track_id": int, "box": [x1,y1,x2,y2], ...}]
            timestamp: Horodatage actuel
        
        Returns:
            Liste des comportements détectés
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        behaviors = []
        current_track_ids = set()
        
        for det in detections:
            if det.get("label") != "person":
                continue
            
            track_id = det.get("track_id")
            if track_id is None:
                continue
            
            current_track_ids.add(track_id)
            box = det.get("box", [0, 0, 0, 0])
            
            # Centre de la personne
            cx = (box[0] + box[2]) / 2
            cy = (box[1] + box[3]) / 2
            
            # Mettre à jour le tracking
            if track_id not in self.tracked_persons:
                self.tracked_persons[track_id] = TrackedPerson(
                    track_id=track_id,
                    first_seen=timestamp
                )
            
            person = self.tracked_persons[track_id]
            person.positions.append((cx, cy))
            person.timestamps.append(timestamp)
            person.last_seen = timestamp
            
            # Mettre à jour la heatmap
            self.heatmap.add_point(int(cx), int(cy))
            
            # Calculer les métriques
            self._calculate_metrics(person)
            
            # Analyser le comportement
            behavior = self._analyze_person_behavior(person)
            if behavior:
                behaviors.append(behavior)
        
        # Nettoyer les personnes parties
        self._cleanup_old_tracks(current_track_ids, timestamp)
        
        # Analyser les comportements de groupe
        group_behaviors = self._analyze_group_behavior(detections, timestamp)
        behaviors.extend(group_behaviors)
        
        # Decay de la heatmap
        self.heatmap.decay()
        
        return behaviors
    
    def _calculate_metrics(self, person: TrackedPerson):
        """Calcule les métriques de mouvement"""
        if len(person.positions) < 2:
            return
        
        # Calculer la vitesse
        positions = list(person.positions)
        timestamps = list(person.timestamps)
        
        speeds = []
        total_distance = 0
        
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            distance = math.sqrt(dx**2 + dy**2)
            
            dt = (timestamps[i] - timestamps[i-1]).total_seconds()
            if dt > 0:
                # Convertir pixels en mètres (approximatif)
                distance_m = distance * 0.01  # 1 pixel ≈ 1cm
                speed = distance_m / dt
                speeds.append(speed)
            
            total_distance += distance
        
        if speeds:
            person.avg_speed = np.mean(speeds)
            person.max_speed = max(speeds)
        
        person.total_distance = total_distance * 0.01  # en mètres
        
        # Temps de présence
        if person.first_seen and person.last_seen:
            person.dwell_time = (person.last_seen - person.first_seen).total_seconds()
        
        # Déterminer si stationnaire
        person.is_stationary = person.avg_speed < self.STATIONARY_SPEED_THRESHOLD
    
    def _analyze_person_behavior(self, person: TrackedPerson) -> Optional[Dict]:
        """Analyse le comportement d'une personne"""
        behaviors_detected = []
        
        # Détection de flânerie (loitering)
        if person.is_stationary and person.dwell_time > self.LOITERING_TIME_THRESHOLD:
            behaviors_detected.append({
                "type": BehaviorType.LOITERING,
                "confidence": min(person.dwell_time / (self.LOITERING_TIME_THRESHOLD * 2), 1.0),
                "details": f"Stationnaire depuis {person.dwell_time:.0f}s"
            })
        
        # Détection de course
        if person.avg_speed > self.RUNNING_SPEED_THRESHOLD:
            behaviors_detected.append({
                "type": BehaviorType.RUNNING,
                "confidence": min(person.avg_speed / (self.RUNNING_SPEED_THRESHOLD * 2), 1.0),
                "details": f"Vitesse: {person.avg_speed:.1f} m/s"
            })
        
        # Détection de mouvement erratique
        if self._is_erratic_movement(person):
            behaviors_detected.append({
                "type": BehaviorType.ERRATIC_MOVEMENT,
                "confidence": 0.7,
                "details": "Changements de direction fréquents"
            })
        
        # Vérifier les zones restreintes
        if person.positions:
            current_pos = person.positions[-1]
            for zone_name in self.restricted_zones:
                if self._is_in_zone(current_pos, zone_name):
                    behaviors_detected.append({
                        "type": BehaviorType.INTRUSION,
                        "confidence": 1.0,
                        "details": f"Intrusion dans zone: {zone_name}"
                    })
        
        if behaviors_detected:
            # Retourner le comportement le plus significatif
            best = max(behaviors_detected, key=lambda x: x["confidence"])
            person.current_behavior = best["type"]
            person.behavior_confidence = best["confidence"]
            
            return {
                "track_id": person.track_id,
                "behavior": best["type"].value,
                "confidence": best["confidence"],
                "details": best["details"],
                "position": person.positions[-1] if person.positions else (0, 0),
                "dwell_time": person.dwell_time,
                "speed": person.avg_speed
            }
        
        person.current_behavior = BehaviorType.NORMAL
        return None
    
    def _is_erratic_movement(self, person: TrackedPerson) -> bool:
        """Détecte les mouvements erratiques (changements de direction fréquents)"""
        if len(person.positions) < 10:
            return False
        
        positions = list(person.positions)[-20:]
        
        # Calculer les angles de direction
        angles = []
        for i in range(2, len(positions)):
            dx1 = positions[i-1][0] - positions[i-2][0]
            dy1 = positions[i-1][1] - positions[i-2][1]
            dx2 = positions[i][0] - positions[i-1][0]
            dy2 = positions[i][1] - positions[i-1][1]
            
            if abs(dx1) > 1 and abs(dx2) > 1:  # Éviter division par zéro
                angle1 = math.atan2(dy1, dx1)
                angle2 = math.atan2(dy2, dx2)
                angle_diff = abs(angle2 - angle1)
                angles.append(angle_diff)
        
        if angles:
            # Si beaucoup de changements de direction
            sudden_changes = sum(1 for a in angles if a > math.pi / 4)
            return sudden_changes > len(angles) * 0.4
        
        return False
    
    def _analyze_group_behavior(self, detections: List[Dict], 
                                 timestamp: datetime) -> List[Dict]:
        """Analyse les comportements de groupe"""
        behaviors = []
        persons = [d for d in detections if d.get("label") == "person"]
        
        if len(persons) < 2:
            return behaviors
        
        # Détecter la formation de foule
        clusters = self._find_clusters(persons)
        
        for cluster in clusters:
            if len(cluster) >= self.CROWD_THRESHOLD:
                # Calculer le centre du cluster
                cx = np.mean([p["box"][0] + p["box"][2] for p in cluster]) / 2
                cy = np.mean([p["box"][1] + p["box"][3] for p in cluster]) / 2
                
                behaviors.append({
                    "behavior": BehaviorType.CROWD_FORMING.value,
                    "confidence": min(len(cluster) / 10, 1.0),
                    "details": f"{len(cluster)} personnes regroupées",
                    "position": (cx, cy),
                    "count": len(cluster)
                })
        
        # Détecter les bagarres (proximité + mouvement rapide)
        for i, p1 in enumerate(persons):
            for p2 in persons[i+1:]:
                if self._are_fighting(p1, p2):
                    cx = (p1["box"][0] + p2["box"][0]) / 2
                    cy = (p1["box"][1] + p2["box"][1]) / 2
                    
                    behaviors.append({
                        "behavior": BehaviorType.FIGHTING.value,
                        "confidence": 0.8,
                        "details": "Altercation possible détectée",
                        "position": (cx, cy)
                    })
        
        return behaviors
    
    def _find_clusters(self, persons: List[Dict], 
                       distance_threshold: float = 100) -> List[List[Dict]]:
        """Trouve les clusters de personnes proches"""
        if not persons:
            return []
        
        # Simple clustering basé sur la distance
        clusters = []
        used = set()
        
        for i, p1 in enumerate(persons):
            if i in used:
                continue
            
            cluster = [p1]
            used.add(i)
            
            cx1 = (p1["box"][0] + p1["box"][2]) / 2
            cy1 = (p1["box"][1] + p1["box"][3]) / 2
            
            for j, p2 in enumerate(persons):
                if j in used:
                    continue
                
                cx2 = (p2["box"][0] + p2["box"][2]) / 2
                cy2 = (p2["box"][1] + p2["box"][3]) / 2
                
                distance = math.sqrt((cx2 - cx1)**2 + (cy2 - cy1)**2)
                
                if distance < distance_threshold:
                    cluster.append(p2)
                    used.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    def _are_fighting(self, p1: Dict, p2: Dict) -> bool:
        """Détecte si deux personnes sont en altercation"""
        # Vérifier la proximité
        cx1 = (p1["box"][0] + p1["box"][2]) / 2
        cy1 = (p1["box"][1] + p1["box"][3]) / 2
        cx2 = (p2["box"][0] + p2["box"][2]) / 2
        cy2 = (p2["box"][1] + p2["box"][3]) / 2
        
        distance = math.sqrt((cx2 - cx1)**2 + (cy2 - cy1)**2)
        
        if distance > 50:  # Trop loin
            return False
        
        # Vérifier si les deux ont un mouvement rapide
        t1 = self.tracked_persons.get(p1.get("track_id"))
        t2 = self.tracked_persons.get(p2.get("track_id"))
        
        if t1 and t2:
            if t1.avg_speed > 1.0 and t2.avg_speed > 1.0:
                return True
        
        return False
    
    def _is_in_zone(self, position: Tuple[float, float], zone_name: str) -> bool:
        """Vérifie si une position est dans une zone"""
        if zone_name not in self.zones:
            return False
        
        zone = self.zones[zone_name]
        x, y = position
        
        return (zone.get("x1", 0) <= x <= zone.get("x2", 9999) and
                zone.get("y1", 0) <= y <= zone.get("y2", 9999))
    
    def _cleanup_old_tracks(self, current_ids: set, timestamp: datetime):
        """Nettoie les tracks qui ne sont plus actifs"""
        timeout = timedelta(seconds=5)
        to_remove = []
        
        for track_id, person in self.tracked_persons.items():
            if track_id not in current_ids:
                if person.last_seen and (timestamp - person.last_seen) > timeout:
                    to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracked_persons[track_id]
    
    def add_zone(self, name: str, x1: int, y1: int, x2: int, y2: int,
                 zone_type: str = "normal", expected_direction: str = None):
        """Ajoute une zone de surveillance"""
        self.zones[name] = {
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "type": zone_type
        }
        
        if zone_type == "restricted":
            self.restricted_zones.append(name)
        
        if expected_direction:
            self.direction_zones[name] = expected_direction
    
    def get_heatmap(self) -> np.ndarray:
        """Retourne la heatmap normalisée"""
        return self.heatmap.normalize()
    
    def get_hot_zones(self) -> List[Dict]:
        """Retourne les zones chaudes"""
        hot = self.heatmap.get_hot_zones(threshold=0.6)
        return [{"x": x * self.heatmap.grid_size, 
                 "y": y * self.heatmap.grid_size,
                 "intensity": float(self.heatmap.data[y, x])} 
                for x, y in hot]
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques globales"""
        return {
            "active_tracks": len(self.tracked_persons),
            "avg_dwell_time": np.mean([p.dwell_time for p in self.tracked_persons.values()]) if self.tracked_persons else 0,
            "stationary_count": sum(1 for p in self.tracked_persons.values() if p.is_stationary),
            "running_count": sum(1 for p in self.tracked_persons.values() if p.current_behavior == BehaviorType.RUNNING),
            "loitering_count": sum(1 for p in self.tracked_persons.values() if p.current_behavior == BehaviorType.LOITERING)
        }


# Instance globale
behavior_analyzer = BehaviorAnalyzer()
