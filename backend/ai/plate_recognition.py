"""
OhmVision - License Plate Recognition (LPR/ANPR)
Reconnaissance automatique des plaques d'immatriculation
"""

import cv2
import numpy as np
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class PlateDetection:
    """Détection d'une plaque d'immatriculation"""
    plate_text: str
    confidence: float
    box: Tuple[int, int, int, int]  # x1, y1, x2, y2
    timestamp: datetime
    camera_id: int
    image_crop: Optional[np.ndarray] = None
    
    # Infos véhicule
    vehicle_type: str = "unknown"  # car, truck, motorcycle, bus
    vehicle_color: str = "unknown"
    direction: str = "unknown"  # in, out, unknown
    
    # Statut
    is_vip: bool = False
    is_blacklisted: bool = False
    is_authorized: bool = True


@dataclass
class VehicleRecord:
    """Enregistrement d'un véhicule"""
    plate: str
    first_seen: datetime
    last_seen: datetime
    visit_count: int = 1
    cameras_seen: List[int] = field(default_factory=list)
    
    # Classification
    category: str = "visitor"  # visitor, employee, vip, blacklist, delivery
    notes: str = ""
    
    # Statistiques
    avg_duration: float = 0.0  # minutes
    total_duration: float = 0.0


class PlateRecognizer:
    """
    Système de reconnaissance de plaques d'immatriculation
    Utilise OCR et patterns pour détecter les plaques
    """
    
    # Patterns de plaques par pays
    PLATE_PATTERNS = {
        "FR": r"^[A-Z]{2}[-\s]?\d{3}[-\s]?[A-Z]{2}$",  # AA-123-BB (France)
        "FR_OLD": r"^\d{1,4}[-\s]?[A-Z]{2,3}[-\s]?\d{2}$",  # 1234 AB 75
        "DE": r"^[A-Z]{1,3}[-\s]?[A-Z]{1,2}[-\s]?\d{1,4}$",  # M-AB-1234 (Allemagne)
        "UK": r"^[A-Z]{2}\d{2}[-\s]?[A-Z]{3}$",  # AB12 CDE (UK)
        "ES": r"^\d{4}[-\s]?[A-Z]{3}$",  # 1234 ABC (Espagne)
        "IT": r"^[A-Z]{2}[-\s]?\d{3}[-\s]?[A-Z]{2}$",  # AB 123 CD (Italie)
        "BE": r"^\d[-\s]?[A-Z]{3}[-\s]?\d{3}$",  # 1-ABC-123 (Belgique)
        "GENERIC": r"^[A-Z0-9]{4,10}$"
    }
    
    def __init__(self):
        self.vehicle_database: Dict[str, VehicleRecord] = {}
        self.vip_list: set = set()
        self.blacklist: set = set()
        self.authorized_list: set = set()  # Employés, résidents
        
        # Historique des détections
        self.detection_history: List[PlateDetection] = []
        self.daily_stats: Dict[str, Dict] = defaultdict(lambda: {
            "entries": 0, "exits": 0, "unique_plates": set()
        })
        
        # Configuration
        self.min_confidence = 0.7
        self.duplicate_timeout = 60  # Ignorer les doublons pendant 60s
        self._last_detections: Dict[str, datetime] = {}
    
    def detect_plates(self, frame: np.ndarray, camera_id: int) -> List[PlateDetection]:
        """
        Détecte les plaques dans une frame
        
        Args:
            frame: Image OpenCV
            camera_id: ID de la caméra
        
        Returns:
            Liste des plaques détectées
        """
        detections = []
        
        # Prétraitement
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Détection des contours potentiels de plaques
        plate_candidates = self._find_plate_candidates(gray)
        
        for candidate in plate_candidates:
            x, y, w, h = candidate
            
            # Extraire la région
            plate_region = gray[y:y+h, x:x+w]
            
            # OCR sur la région
            plate_text, confidence = self._ocr_plate(plate_region)
            
            if plate_text and confidence >= self.min_confidence:
                # Vérifier si c'est un doublon récent
                if self._is_duplicate(plate_text):
                    continue
                
                # Créer la détection
                detection = PlateDetection(
                    plate_text=plate_text,
                    confidence=confidence,
                    box=(x, y, x+w, y+h),
                    timestamp=datetime.now(),
                    camera_id=camera_id,
                    image_crop=frame[y:y+h, x:x+w].copy()
                )
                
                # Enrichir avec les infos de la base
                self._enrich_detection(detection)
                
                # Enregistrer
                self._record_detection(detection)
                
                detections.append(detection)
                self._last_detections[plate_text] = datetime.now()
        
        return detections
    
    def _find_plate_candidates(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Trouve les régions candidates pour les plaques"""
        candidates = []
        
        # Méthode 1: Détection de contours
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 100, 200)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filtrer par ratio (plaques sont rectangulaires)
            aspect_ratio = w / h if h > 0 else 0
            
            # Plaques européennes: ratio ~4.5:1 à 5:1
            # Plaques US: ratio ~2:1
            if 1.5 < aspect_ratio < 6 and w > 60 and h > 15:
                candidates.append((x, y, w, h))
        
        # Méthode 2: Cascade classifier (si disponible)
        # cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')
        # plates = cascade.detectMultiScale(gray, 1.1, 5)
        
        return candidates
    
    def _ocr_plate(self, plate_region: np.ndarray) -> Tuple[str, float]:
        """
        Effectue l'OCR sur une région de plaque
        
        Note: En production, utiliser Tesseract ou un service cloud
        """
        try:
            # Prétraitement pour OCR
            plate_region = cv2.resize(plate_region, (200, 50))
            _, thresh = cv2.threshold(plate_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR avec Tesseract (si disponible)
            try:
                import pytesseract
                text = pytesseract.image_to_string(
                    thresh,
                    config='--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                )
                text = self._clean_plate_text(text)
                confidence = self._validate_plate(text)
                return text, confidence
            except ImportError:
                # Fallback: simulation pour démo
                return self._simulate_ocr()
                
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return "", 0.0
    
    def _simulate_ocr(self) -> Tuple[str, float]:
        """Simule l'OCR pour les démos (quand Tesseract n'est pas disponible)"""
        import random
        
        # Générer une plaque française aléatoire
        letters1 = ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ', k=2))
        numbers = ''.join(random.choices('0123456789', k=3))
        letters2 = ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ', k=2))
        
        plate = f"{letters1}-{numbers}-{letters2}"
        confidence = random.uniform(0.75, 0.98)
        
        return plate, confidence
    
    def _clean_plate_text(self, text: str) -> str:
        """Nettoie le texte OCR"""
        # Supprimer les caractères non alphanumériques (sauf tirets)
        text = re.sub(r'[^A-Z0-9\-\s]', '', text.upper())
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        # Corrections communes OCR
        text = text.replace('O', '0').replace('I', '1').replace('S', '5')
        return text
    
    def _validate_plate(self, text: str) -> float:
        """Valide le format de la plaque et retourne un score de confiance"""
        if not text or len(text) < 4:
            return 0.0
        
        for country, pattern in self.PLATE_PATTERNS.items():
            if re.match(pattern, text.replace('-', '').replace(' ', '')):
                return 0.9  # Format reconnu
        
        # Format générique
        if re.match(r'^[A-Z0-9\-\s]{4,12}$', text):
            return 0.7
        
        return 0.0
    
    def _is_duplicate(self, plate_text: str) -> bool:
        """Vérifie si c'est une détection en double"""
        if plate_text in self._last_detections:
            elapsed = (datetime.now() - self._last_detections[plate_text]).total_seconds()
            return elapsed < self.duplicate_timeout
        return False
    
    def _enrich_detection(self, detection: PlateDetection):
        """Enrichit la détection avec les infos de la base"""
        plate = detection.plate_text
        
        detection.is_vip = plate in self.vip_list
        detection.is_blacklisted = plate in self.blacklist
        detection.is_authorized = plate in self.authorized_list or detection.is_vip
    
    def _record_detection(self, detection: PlateDetection):
        """Enregistre la détection dans l'historique"""
        self.detection_history.append(detection)
        
        # Mettre à jour la base de véhicules
        plate = detection.plate_text
        
        if plate in self.vehicle_database:
            record = self.vehicle_database[plate]
            record.last_seen = detection.timestamp
            record.visit_count += 1
            if detection.camera_id not in record.cameras_seen:
                record.cameras_seen.append(detection.camera_id)
        else:
            self.vehicle_database[plate] = VehicleRecord(
                plate=plate,
                first_seen=detection.timestamp,
                last_seen=detection.timestamp,
                cameras_seen=[detection.camera_id]
            )
        
        # Stats journalières
        today = detection.timestamp.strftime("%Y-%m-%d")
        self.daily_stats[today]["unique_plates"].add(plate)
    
    # =========================================================================
    # Gestion des listes
    # =========================================================================
    
    def add_to_vip(self, plate: str, notes: str = ""):
        """Ajoute une plaque à la liste VIP"""
        plate = plate.upper().replace(' ', '-')
        self.vip_list.add(plate)
        
        if plate in self.vehicle_database:
            self.vehicle_database[plate].category = "vip"
            self.vehicle_database[plate].notes = notes
        else:
            self.vehicle_database[plate] = VehicleRecord(
                plate=plate,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                category="vip",
                notes=notes
            )
    
    def add_to_blacklist(self, plate: str, reason: str = ""):
        """Ajoute une plaque à la liste noire"""
        plate = plate.upper().replace(' ', '-')
        self.blacklist.add(plate)
        
        if plate in self.vehicle_database:
            self.vehicle_database[plate].category = "blacklist"
            self.vehicle_database[plate].notes = reason
    
    def add_authorized(self, plate: str, category: str = "employee"):
        """Ajoute une plaque autorisée"""
        plate = plate.upper().replace(' ', '-')
        self.authorized_list.add(plate)
        
        if plate in self.vehicle_database:
            self.vehicle_database[plate].category = category
    
    def remove_from_list(self, plate: str, list_type: str):
        """Retire une plaque d'une liste"""
        plate = plate.upper()
        
        if list_type == "vip":
            self.vip_list.discard(plate)
        elif list_type == "blacklist":
            self.blacklist.discard(plate)
        elif list_type == "authorized":
            self.authorized_list.discard(plate)
    
    # =========================================================================
    # Recherche et statistiques
    # =========================================================================
    
    def search_plate(self, plate: str) -> Optional[Dict]:
        """Recherche une plaque dans la base"""
        plate = plate.upper().replace(' ', '-')
        
        if plate in self.vehicle_database:
            record = self.vehicle_database[plate]
            return {
                "plate": record.plate,
                "category": record.category,
                "first_seen": record.first_seen.isoformat(),
                "last_seen": record.last_seen.isoformat(),
                "visit_count": record.visit_count,
                "is_vip": plate in self.vip_list,
                "is_blacklisted": plate in self.blacklist,
                "notes": record.notes
            }
        return None
    
    def get_recent_detections(self, limit: int = 50, 
                               camera_id: int = None) -> List[Dict]:
        """Récupère les détections récentes"""
        detections = self.detection_history[-limit*2:]
        
        if camera_id:
            detections = [d for d in detections if d.camera_id == camera_id]
        
        return [
            {
                "plate": d.plate_text,
                "confidence": d.confidence,
                "timestamp": d.timestamp.isoformat(),
                "camera_id": d.camera_id,
                "is_vip": d.is_vip,
                "is_blacklisted": d.is_blacklisted,
                "vehicle_type": d.vehicle_type
            }
            for d in detections[-limit:]
        ]
    
    def get_statistics(self, date: str = None) -> Dict:
        """Récupère les statistiques"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        stats = self.daily_stats.get(date, {"entries": 0, "exits": 0, "unique_plates": set()})
        
        return {
            "date": date,
            "total_detections": len(self.detection_history),
            "unique_plates_today": len(stats["unique_plates"]),
            "entries_today": stats["entries"],
            "exits_today": stats["exits"],
            "vip_count": len(self.vip_list),
            "blacklist_count": len(self.blacklist),
            "authorized_count": len(self.authorized_list),
            "database_size": len(self.vehicle_database)
        }
    
    def get_frequent_visitors(self, min_visits: int = 5, limit: int = 20) -> List[Dict]:
        """Récupère les visiteurs fréquents"""
        frequent = [
            {
                "plate": record.plate,
                "visit_count": record.visit_count,
                "category": record.category,
                "first_seen": record.first_seen.isoformat(),
                "last_seen": record.last_seen.isoformat()
            }
            for plate, record in self.vehicle_database.items()
            if record.visit_count >= min_visits
        ]
        
        return sorted(frequent, key=lambda x: x["visit_count"], reverse=True)[:limit]


# Instance globale
plate_recognizer = PlateRecognizer()


# ============================================================================
# Fonctions utilitaires pour l'API
# ============================================================================

def process_frame_for_plates(frame: np.ndarray, camera_id: int) -> List[Dict]:
    """
    Traite une frame pour la détection de plaques
    Retourne les alertes si VIP ou blacklist détecté
    """
    detections = plate_recognizer.detect_plates(frame, camera_id)
    
    alerts = []
    for det in detections:
        result = {
            "plate": det.plate_text,
            "confidence": det.confidence,
            "box": det.box,
            "is_vip": det.is_vip,
            "is_blacklisted": det.is_blacklisted
        }
        
        if det.is_vip:
            alerts.append({
                "type": "vip_arrival",
                "plate": det.plate_text,
                "message": f"VIP détecté: {det.plate_text}"
            })
        
        if det.is_blacklisted:
            alerts.append({
                "type": "blacklist_alert",
                "plate": det.plate_text,
                "message": f"⚠️ ALERTE: Véhicule blacklisté détecté: {det.plate_text}",
                "severity": "critical"
            })
    
    return {"detections": [d.__dict__ for d in detections], "alerts": alerts}
