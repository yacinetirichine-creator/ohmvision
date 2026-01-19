"""
OhmVision - Advanced Fire & Smoke Detection with Thermal Analysis
Détection feu/fumée avancée avec analyse thermique et multi-capteurs
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Niveaux d'alerte incendie"""
    NORMAL = "normal"
    WATCH = "watch"          # Surveillance accrue
    WARNING = "warning"      # Pré-alerte
    ALARM = "alarm"          # Alerte confirmée
    CRITICAL = "critical"    # Urgence - évacuation


class DetectionMethod(str, Enum):
    """Méthodes de détection"""
    VISUAL = "visual"              # Caméra standard (couleur)
    THERMAL = "thermal"            # Caméra thermique
    THERMAL_RATE = "thermal_rate"  # Variation température
    SMOKE_PATTERN = "smoke_pattern"  # Pattern fumée
    MULTI_SENSOR = "multi_sensor"  # Combinaison


@dataclass
class ThermalZone:
    """Zone de surveillance thermique"""
    zone_id: str
    name: str
    x1: int
    y1: int
    x2: int
    y2: int
    
    # Seuils de température (°C)
    temp_normal_max: float = 40.0      # Température normale max
    temp_warning: float = 60.0          # Seuil pré-alerte
    temp_alarm: float = 80.0            # Seuil alerte
    temp_critical: float = 150.0        # Seuil critique
    
    # Seuils de variation (°C/min)
    rate_warning: float = 5.0           # +5°C/min = pré-alerte
    rate_alarm: float = 15.0            # +15°C/min = alerte
    rate_critical: float = 30.0         # +30°C/min = critique
    
    # État actuel
    current_temp: float = 20.0
    max_temp: float = 20.0
    temp_history: deque = field(default_factory=lambda: deque(maxlen=60))  # 1 min
    alert_level: AlertLevel = AlertLevel.NORMAL


@dataclass
class FireSmokeDetection:
    """Résultat de détection feu/fumée"""
    detection_id: str
    timestamp: datetime
    camera_id: int
    
    # Type de détection
    detection_type: str  # fire, smoke, heat, spark
    detection_method: DetectionMethod
    confidence: float
    
    # Localisation
    box: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    
    # Données thermiques (si disponible)
    temperature: Optional[float] = None
    temp_rate: Optional[float] = None  # °C/min
    
    # Niveau d'alerte
    alert_level: AlertLevel = AlertLevel.WARNING
    
    # Métadonnées
    zone_name: Optional[str] = None
    is_confirmed: bool = False
    confirmation_count: int = 1


class ThermalFireDetector:
    """
    Détecteur de feu/fumée multi-méthodes
    Combine analyse visuelle, thermique et variation de température
    """
    
    # Constantes de détection visuelle
    FIRE_HSV_LOWER = np.array([0, 50, 200])      # Orange/Rouge
    FIRE_HSV_UPPER = np.array([35, 255, 255])
    SMOKE_HSV_LOWER = np.array([0, 0, 100])      # Gris
    SMOKE_HSV_UPPER = np.array([180, 50, 200])
    
    # Seuils de confirmation
    CONFIRMATION_FRAMES = 3  # Confirmer sur 3 frames
    FALSE_POSITIVE_TIMEOUT = 30  # Secondes avant reset
    
    def __init__(self):
        self.thermal_zones: Dict[str, ThermalZone] = {}
        self.detection_history: deque = deque(maxlen=1000)
        self.pending_detections: Dict[str, List[FireSmokeDetection]] = {}
        self.confirmed_alerts: List[FireSmokeDetection] = []
        
        # Calibration thermique
        self.thermal_calibration = {
            "min_temp": 0.0,      # Température min de la caméra
            "max_temp": 150.0,    # Température max de la caméra
            "emissivity": 0.95    # Émissivité par défaut
        }
        
        # Statistiques
        self.stats = {
            "total_detections": 0,
            "confirmed_fires": 0,
            "confirmed_smoke": 0,
            "false_positives": 0
        }
    
    def add_thermal_zone(self, zone: ThermalZone):
        """Ajoute une zone de surveillance thermique"""
        self.thermal_zones[zone.zone_id] = zone
        logger.info(f"Thermal zone added: {zone.name} (warning: {zone.temp_warning}°C)")
    
    def process_frame(self, 
                      frame: np.ndarray, 
                      camera_id: int,
                      thermal_frame: np.ndarray = None) -> List[FireSmokeDetection]:
        """
        Traite une frame pour détecter feu/fumée
        
        Args:
            frame: Image RGB standard
            camera_id: ID de la caméra
            thermal_frame: Image thermique (optionnel) - valeurs = températures
        
        Returns:
            Liste des détections
        """
        detections = []
        timestamp = datetime.now()
        
        # 1. Détection visuelle (toujours)
        visual_detections = self._detect_visual(frame, camera_id, timestamp)
        detections.extend(visual_detections)
        
        # 2. Détection thermique (si caméra thermique disponible)
        if thermal_frame is not None:
            thermal_detections = self._detect_thermal(thermal_frame, camera_id, timestamp)
            detections.extend(thermal_detections)
            
            # 3. Détection par variation de température
            rate_detections = self._detect_thermal_rate(thermal_frame, camera_id, timestamp)
            detections.extend(rate_detections)
        
        # 4. Fusion multi-capteurs
        if thermal_frame is not None and visual_detections:
            detections = self._fuse_detections(detections, frame, thermal_frame)
        
        # 5. Confirmation des détections
        confirmed = self._confirm_detections(detections)
        
        # 6. Mettre à jour les statistiques
        self._update_stats(confirmed)
        
        return confirmed
    
    def _detect_visual(self, frame: np.ndarray, camera_id: int, 
                       timestamp: datetime) -> List[FireSmokeDetection]:
        """Détection visuelle par analyse colorimétrique"""
        detections = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Détection feu (orange/rouge)
        fire_mask = cv2.inRange(hsv, self.FIRE_HSV_LOWER, self.FIRE_HSV_UPPER)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, np.ones((5, 5)))
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_CLOSE, np.ones((10, 10)))
        
        fire_contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in fire_contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Filtrer les petites zones
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculer la confiance basée sur la taille et la forme
                confidence = self._calculate_fire_confidence(contour, area, frame[y:y+h, x:x+w])
                
                if confidence > 0.5:
                    detections.append(FireSmokeDetection(
                        detection_id=f"fire_{timestamp.timestamp()}_{len(detections)}",
                        timestamp=timestamp,
                        camera_id=camera_id,
                        detection_type="fire",
                        detection_method=DetectionMethod.VISUAL,
                        confidence=confidence,
                        box=(x, y, x+w, y+h),
                        center=(x + w//2, y + h//2),
                        alert_level=self._get_alert_level_from_confidence(confidence)
                    ))
        
        # Détection fumée (gris)
        smoke_mask = cv2.inRange(hsv, self.SMOKE_HSV_LOWER, self.SMOKE_HSV_UPPER)
        smoke_mask = cv2.morphologyEx(smoke_mask, cv2.MORPH_OPEN, np.ones((3, 3)))
        
        # Analyse du mouvement ascendant pour la fumée
        smoke_detections = self._analyze_smoke_pattern(smoke_mask, frame, camera_id, timestamp)
        detections.extend(smoke_detections)
        
        return detections
    
    def _detect_thermal(self, thermal_frame: np.ndarray, camera_id: int,
                        timestamp: datetime) -> List[FireSmokeDetection]:
        """Détection par analyse thermique directe"""
        detections = []
        
        # Convertir l'image thermique en températures
        # Note: Le format dépend de la caméra thermique utilisée
        # Ici on suppose une image 16-bit où chaque pixel = température en °C * 100
        if thermal_frame.dtype == np.uint16:
            temp_map = thermal_frame.astype(np.float32) / 100.0
        else:
            # Si 8-bit, mapper sur la plage de température
            temp_map = self._convert_8bit_to_temp(thermal_frame)
        
        # Analyser chaque zone thermique définie
        for zone_id, zone in self.thermal_zones.items():
            zone_temp = temp_map[zone.y1:zone.y2, zone.x1:zone.x2]
            
            if zone_temp.size == 0:
                continue
            
            # Calculer les statistiques de température
            max_temp = float(np.max(zone_temp))
            avg_temp = float(np.mean(zone_temp))
            
            # Mettre à jour la zone
            zone.current_temp = avg_temp
            zone.max_temp = max(zone.max_temp, max_temp)
            zone.temp_history.append((timestamp, max_temp))
            
            # Vérifier les seuils
            if max_temp >= zone.temp_critical:
                alert_level = AlertLevel.CRITICAL
            elif max_temp >= zone.temp_alarm:
                alert_level = AlertLevel.ALARM
            elif max_temp >= zone.temp_warning:
                alert_level = AlertLevel.WARNING
            else:
                alert_level = AlertLevel.NORMAL
                zone.alert_level = alert_level
                continue
            
            zone.alert_level = alert_level
            
            # Trouver le point chaud
            hot_point = np.unravel_index(np.argmax(zone_temp), zone_temp.shape)
            hot_x = zone.x1 + hot_point[1]
            hot_y = zone.y1 + hot_point[0]
            
            # Créer une détection autour du point chaud
            box_size = 50
            detections.append(FireSmokeDetection(
                detection_id=f"thermal_{zone_id}_{timestamp.timestamp()}",
                timestamp=timestamp,
                camera_id=camera_id,
                detection_type="heat",
                detection_method=DetectionMethod.THERMAL,
                confidence=min(max_temp / zone.temp_critical, 1.0),
                box=(
                    max(0, hot_x - box_size),
                    max(0, hot_y - box_size),
                    hot_x + box_size,
                    hot_y + box_size
                ),
                center=(hot_x, hot_y),
                temperature=max_temp,
                alert_level=alert_level,
                zone_name=zone.name
            ))
        
        # Détecter les points chauds globaux (hors zones définies)
        global_detections = self._detect_global_hotspots(temp_map, camera_id, timestamp)
        detections.extend(global_detections)
        
        return detections
    
    def _detect_thermal_rate(self, thermal_frame: np.ndarray, camera_id: int,
                             timestamp: datetime) -> List[FireSmokeDetection]:
        """
        Détection par VARIATION de température (élévation rapide)
        C'est la méthode la plus fiable pour la détection précoce
        """
        detections = []
        
        for zone_id, zone in self.thermal_zones.items():
            if len(zone.temp_history) < 10:  # Besoin d'historique
                continue
            
            # Calculer le taux de variation (°C/minute)
            history = list(zone.temp_history)
            
            if len(history) >= 2:
                # Variation sur les 30 dernières secondes
                recent = [h for h in history if (timestamp - h[0]).total_seconds() <= 30]
                
                if len(recent) >= 2:
                    time_diff = (recent[-1][0] - recent[0][0]).total_seconds() / 60  # minutes
                    temp_diff = recent[-1][1] - recent[0][1]
                    
                    if time_diff > 0:
                        rate = temp_diff / time_diff  # °C/min
                        
                        # Vérifier les seuils de variation
                        if rate >= zone.rate_critical:
                            alert_level = AlertLevel.CRITICAL
                        elif rate >= zone.rate_alarm:
                            alert_level = AlertLevel.ALARM
                        elif rate >= zone.rate_warning:
                            alert_level = AlertLevel.WARNING
                        else:
                            continue
                        
                        detections.append(FireSmokeDetection(
                            detection_id=f"rate_{zone_id}_{timestamp.timestamp()}",
                            timestamp=timestamp,
                            camera_id=camera_id,
                            detection_type="heat_rise",
                            detection_method=DetectionMethod.THERMAL_RATE,
                            confidence=min(rate / zone.rate_critical, 1.0),
                            box=(zone.x1, zone.y1, zone.x2, zone.y2),
                            center=((zone.x1 + zone.x2) // 2, (zone.y1 + zone.y2) // 2),
                            temperature=zone.current_temp,
                            temp_rate=rate,
                            alert_level=alert_level,
                            zone_name=zone.name
                        ))
                        
                        logger.warning(
                            f"🔥 THERMAL RATE ALERT: {zone.name} - "
                            f"+{rate:.1f}°C/min (current: {zone.current_temp:.1f}°C)"
                        )
        
        return detections
    
    def _analyze_smoke_pattern(self, smoke_mask: np.ndarray, frame: np.ndarray,
                                camera_id: int, timestamp: datetime) -> List[FireSmokeDetection]:
        """Analyse avancée des patterns de fumée"""
        detections = []
        
        contours, _ = cv2.findContours(smoke_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1000:  # Filtrer les petites zones
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # La fumée a des caractéristiques spécifiques:
            # 1. Forme irrégulière (non rectangulaire)
            # 2. Mouvement ascendant
            # 3. Expansion progressive
            # 4. Transparence partielle
            
            # Calculer l'irrégularité de la forme
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            # Calculer le ratio hauteur/largeur (fumée = plutôt vertical)
            aspect_ratio = h / w if w > 0 else 0
            
            # Score de fumée basé sur les caractéristiques
            smoke_score = 0.0
            
            # Forme irrégulière (solidity < 0.8)
            if solidity < 0.8:
                smoke_score += 0.3
            
            # Forme verticale (aspect_ratio > 1)
            if aspect_ratio > 1.0:
                smoke_score += 0.2
            
            # Position haute dans l'image (fumée monte)
            if y < frame.shape[0] * 0.5:
                smoke_score += 0.2
            
            # Vérifier la transparence (variance des couleurs)
            roi = frame[y:y+h, x:x+w]
            if roi.size > 0:
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                variance = np.var(gray_roi)
                if 500 < variance < 3000:  # Variance modérée = fumée
                    smoke_score += 0.3
            
            if smoke_score > 0.5:
                detections.append(FireSmokeDetection(
                    detection_id=f"smoke_{timestamp.timestamp()}_{len(detections)}",
                    timestamp=timestamp,
                    camera_id=camera_id,
                    detection_type="smoke",
                    detection_method=DetectionMethod.SMOKE_PATTERN,
                    confidence=smoke_score,
                    box=(x, y, x+w, y+h),
                    center=(x + w//2, y + h//2),
                    alert_level=AlertLevel.WARNING if smoke_score > 0.7 else AlertLevel.WATCH
                ))
        
        return detections
    
    def _detect_global_hotspots(self, temp_map: np.ndarray, camera_id: int,
                                 timestamp: datetime) -> List[FireSmokeDetection]:
        """Détecte les points chauds globaux"""
        detections = []
        
        # Seuil global par défaut
        threshold = 70.0  # °C
        
        # Trouver les zones au-dessus du seuil
        hot_mask = (temp_map > threshold).astype(np.uint8) * 255
        
        contours, _ = cv2.findContours(hot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            zone_temp = temp_map[y:y+h, x:x+w]
            max_temp = float(np.max(zone_temp))
            
            # Vérifier si ce n'est pas déjà dans une zone définie
            in_defined_zone = False
            for zone in self.thermal_zones.values():
                if (zone.x1 <= x and x+w <= zone.x2 and 
                    zone.y1 <= y and y+h <= zone.y2):
                    in_defined_zone = True
                    break
            
            if not in_defined_zone:
                alert_level = AlertLevel.ALARM if max_temp > 100 else AlertLevel.WARNING
                
                detections.append(FireSmokeDetection(
                    detection_id=f"hotspot_{timestamp.timestamp()}_{len(detections)}",
                    timestamp=timestamp,
                    camera_id=camera_id,
                    detection_type="hotspot",
                    detection_method=DetectionMethod.THERMAL,
                    confidence=min(max_temp / 150.0, 1.0),
                    box=(x, y, x+w, y+h),
                    center=(x + w//2, y + h//2),
                    temperature=max_temp,
                    alert_level=alert_level,
                    zone_name="Zone non définie"
                ))
        
        return detections
    
    def _fuse_detections(self, detections: List[FireSmokeDetection],
                         visual_frame: np.ndarray,
                         thermal_frame: np.ndarray) -> List[FireSmokeDetection]:
        """
        Fusion multi-capteurs pour réduire les faux positifs
        Si une détection visuelle correspond à un point chaud thermique = haute confiance
        """
        fused = []
        visual_dets = [d for d in detections if d.detection_method == DetectionMethod.VISUAL]
        thermal_dets = [d for d in detections if d.detection_method in 
                       [DetectionMethod.THERMAL, DetectionMethod.THERMAL_RATE]]
        
        for v_det in visual_dets:
            matched = False
            for t_det in thermal_dets:
                # Vérifier le chevauchement
                if self._boxes_overlap(v_det.box, t_det.box):
                    # Créer une détection fusionnée avec haute confiance
                    fused_det = FireSmokeDetection(
                        detection_id=f"fused_{v_det.detection_id}",
                        timestamp=v_det.timestamp,
                        camera_id=v_det.camera_id,
                        detection_type=v_det.detection_type,
                        detection_method=DetectionMethod.MULTI_SENSOR,
                        confidence=min((v_det.confidence + t_det.confidence) / 1.5, 1.0),
                        box=v_det.box,
                        center=v_det.center,
                        temperature=t_det.temperature,
                        temp_rate=t_det.temp_rate,
                        alert_level=max(v_det.alert_level, t_det.alert_level, 
                                       key=lambda x: list(AlertLevel).index(x)),
                        zone_name=t_det.zone_name,
                        is_confirmed=True
                    )
                    fused.append(fused_det)
                    matched = True
                    break
            
            if not matched:
                # Détection visuelle seule = confiance réduite
                v_det.confidence *= 0.7
                fused.append(v_det)
        
        # Ajouter les détections thermiques sans correspondance visuelle
        for t_det in thermal_dets:
            has_match = any(self._boxes_overlap(t_det.box, f.box) for f in fused)
            if not has_match:
                fused.append(t_det)
        
        return fused
    
    def _confirm_detections(self, detections: List[FireSmokeDetection]) -> List[FireSmokeDetection]:
        """Confirme les détections sur plusieurs frames"""
        confirmed = []
        
        for det in detections:
            key = f"{det.camera_id}_{det.detection_type}"
            
            if key not in self.pending_detections:
                self.pending_detections[key] = []
            
            # Ajouter à la liste de détections en attente
            self.pending_detections[key].append(det)
            
            # Nettoyer les anciennes détections
            cutoff = datetime.now() - timedelta(seconds=self.FALSE_POSITIVE_TIMEOUT)
            self.pending_detections[key] = [
                d for d in self.pending_detections[key] 
                if d.timestamp > cutoff
            ]
            
            # Vérifier si on a assez de confirmations
            recent = [d for d in self.pending_detections[key] 
                     if (datetime.now() - d.timestamp).total_seconds() < 5]
            
            if len(recent) >= self.CONFIRMATION_FRAMES:
                # Détection confirmée!
                det.is_confirmed = True
                det.confirmation_count = len(recent)
                
                # Augmenter le niveau d'alerte si multi-confirmé
                if len(recent) >= 5:
                    det.alert_level = AlertLevel.ALARM
                if len(recent) >= 10:
                    det.alert_level = AlertLevel.CRITICAL
                
                confirmed.append(det)
                self.confirmed_alerts.append(det)
            else:
                # Pas encore confirmé mais à surveiller
                if det.alert_level in [AlertLevel.ALARM, AlertLevel.CRITICAL]:
                    # Les alertes graves sont transmises même non confirmées
                    confirmed.append(det)
        
        return confirmed
    
    def _calculate_fire_confidence(self, contour, area: float, roi: np.ndarray) -> float:
        """Calcule la confiance pour une détection de feu"""
        confidence = 0.0
        
        # Taille significative
        if area > 1000:
            confidence += 0.3
        elif area > 500:
            confidence += 0.2
        
        # Forme irrégulière (feu a des bords irréguliers)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * math.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        if circularity < 0.5:  # Forme irrégulière
            confidence += 0.2
        
        # Intensité des couleurs de feu
        if roi.size > 0:
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            # Vérifier la saturation et la luminosité
            avg_sat = np.mean(hsv_roi[:, :, 1])
            avg_val = np.mean(hsv_roi[:, :, 2])
            
            if avg_sat > 100 and avg_val > 200:
                confidence += 0.3
            elif avg_sat > 50 and avg_val > 150:
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _get_alert_level_from_confidence(self, confidence: float) -> AlertLevel:
        """Détermine le niveau d'alerte selon la confiance"""
        if confidence >= 0.9:
            return AlertLevel.CRITICAL
        elif confidence >= 0.7:
            return AlertLevel.ALARM
        elif confidence >= 0.5:
            return AlertLevel.WARNING
        else:
            return AlertLevel.WATCH
    
    def _convert_8bit_to_temp(self, thermal_8bit: np.ndarray) -> np.ndarray:
        """Convertit une image thermique 8-bit en températures"""
        min_temp = self.thermal_calibration["min_temp"]
        max_temp = self.thermal_calibration["max_temp"]
        
        temp_map = thermal_8bit.astype(np.float32) / 255.0
        temp_map = temp_map * (max_temp - min_temp) + min_temp
        
        return temp_map
    
    def _boxes_overlap(self, box1: Tuple, box2: Tuple) -> bool:
        """Vérifie si deux boîtes se chevauchent"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        return not (x2_1 < x1_2 or x2_2 < x1_1 or y2_1 < y1_2 or y2_2 < y1_1)
    
    def _update_stats(self, confirmed: List[FireSmokeDetection]):
        """Met à jour les statistiques"""
        self.stats["total_detections"] += len(confirmed)
        
        for det in confirmed:
            if det.detection_type == "fire":
                self.stats["confirmed_fires"] += 1
            elif det.detection_type == "smoke":
                self.stats["confirmed_smoke"] += 1
    
    def get_zone_status(self) -> Dict[str, Dict]:
        """Récupère le statut de toutes les zones thermiques"""
        return {
            zone_id: {
                "name": zone.name,
                "current_temp": zone.current_temp,
                "max_temp": zone.max_temp,
                "alert_level": zone.alert_level.value,
                "thresholds": {
                    "warning": zone.temp_warning,
                    "alarm": zone.temp_alarm,
                    "critical": zone.temp_critical
                }
            }
            for zone_id, zone in self.thermal_zones.items()
        }
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques globales"""
        return {
            **self.stats,
            "active_zones": len(self.thermal_zones),
            "zones_in_alert": sum(1 for z in self.thermal_zones.values() 
                                  if z.alert_level != AlertLevel.NORMAL)
        }
    
    def calibrate_thermal(self, min_temp: float, max_temp: float, emissivity: float = 0.95):
        """Calibre les paramètres de la caméra thermique"""
        self.thermal_calibration = {
            "min_temp": min_temp,
            "max_temp": max_temp,
            "emissivity": emissivity
        }
        logger.info(f"Thermal calibration: {min_temp}°C - {max_temp}°C (ε={emissivity})")


# Instance globale
thermal_fire_detector = ThermalFireDetector()


# ============================================================================
# Fonctions utilitaires pour l'API
# ============================================================================

def setup_thermal_zones_for_site(site_type: str, frame_width: int, frame_height: int):
    """
    Configure les zones thermiques selon le type de site
    """
    zones = []
    
    if site_type == "warehouse":
        # Entrepôt: zones de stockage, quais, zones électriques
        zones = [
            ThermalZone("storage_1", "Zone Stockage A", 0, 0, frame_width//2, frame_height//2,
                       temp_warning=50, temp_alarm=70, temp_critical=100),
            ThermalZone("storage_2", "Zone Stockage B", frame_width//2, 0, frame_width, frame_height//2,
                       temp_warning=50, temp_alarm=70, temp_critical=100),
            ThermalZone("electrical", "Armoire Électrique", 0, frame_height//2, 200, frame_height,
                       temp_warning=40, temp_alarm=60, temp_critical=80,
                       rate_warning=3, rate_alarm=10, rate_critical=20),
        ]
    
    elif site_type == "industrial":
        # Usine: machines, fours, zones de process
        zones = [
            ThermalZone("machine_area", "Zone Machines", 0, 0, frame_width, frame_height//2,
                       temp_warning=80, temp_alarm=120, temp_critical=200),
            ThermalZone("process", "Zone Process", 0, frame_height//2, frame_width//2, frame_height,
                       temp_warning=60, temp_alarm=100, temp_critical=150),
        ]
    
    elif site_type == "datacenter":
        # Datacenter: serveurs, climatisation
        zones = [
            ThermalZone("servers", "Baies Serveurs", 0, 0, frame_width, frame_height,
                       temp_warning=35, temp_alarm=45, temp_critical=60,
                       rate_warning=2, rate_alarm=5, rate_critical=10),
        ]
    
    elif site_type == "kitchen":
        # Cuisine: zones de cuisson, hottes
        zones = [
            ThermalZone("cooking", "Zone Cuisson", 0, 0, frame_width//2, frame_height,
                       temp_warning=150, temp_alarm=250, temp_critical=350),
            ThermalZone("hood", "Hotte", frame_width//2, 0, frame_width, frame_height//3,
                       temp_warning=80, temp_alarm=120, temp_critical=180),
        ]
    
    for zone in zones:
        thermal_fire_detector.add_thermal_zone(zone)
    
    return len(zones)
