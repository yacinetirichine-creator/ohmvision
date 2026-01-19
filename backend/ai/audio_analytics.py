"""
OhmVision - Audio Analytics Engine
Détection d'événements sonores: verre cassé, cris, alarmes, coups de feu, etc.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AudioEventType(str, Enum):
    """Types d'événements audio détectables"""
    GLASS_BREAK = "glass_break"           # Verre cassé
    SCREAM = "scream"                     # Cri
    GUNSHOT = "gunshot"                   # Coup de feu
    EXPLOSION = "explosion"               # Explosion
    DOG_BARK = "dog_bark"                 # Aboiement
    CAR_ALARM = "car_alarm"               # Alarme voiture
    FIRE_ALARM = "fire_alarm"             # Alarme incendie
    DOOR_SLAM = "door_slam"               # Claquement de porte
    CROWD_NOISE = "crowd_noise"           # Bruit de foule
    AGGRESSION = "aggression"             # Ton agressif
    BABY_CRY = "baby_cry"                 # Pleur de bébé
    SIREN = "siren"                       # Sirène
    MACHINERY = "machinery"               # Machine industrielle
    VEHICLE = "vehicle"                   # Véhicule (moteur)
    SILENCE = "silence"                   # Silence anormal
    SPEECH = "speech"                     # Parole détectée
    MUSIC = "music"                       # Musique


class AudioAlertLevel(str, Enum):
    """Niveaux d'alerte audio"""
    INFO = "info"
    WARNING = "warning"
    ALARM = "alarm"
    CRITICAL = "critical"


@dataclass
class AudioEvent:
    """Événement audio détecté"""
    event_id: str
    event_type: AudioEventType
    timestamp: datetime
    camera_id: int
    
    # Caractéristiques
    confidence: float
    duration_ms: int
    decibel_level: float
    frequency_range: Tuple[int, int]  # Hz
    
    # Localisation (si array de micros)
    direction: Optional[float] = None  # Angle en degrés
    distance: Optional[float] = None   # Distance estimée
    
    # Alerte
    alert_level: AudioAlertLevel = AudioAlertLevel.INFO
    is_confirmed: bool = False


@dataclass
class AudioZone:
    """Zone de surveillance audio"""
    zone_id: str
    name: str
    camera_ids: List[int]
    
    # Configuration
    enabled_events: List[AudioEventType] = field(default_factory=list)
    sensitivity: float = 0.7  # 0-1
    min_confidence: float = 0.6
    
    # Seuils personnalisés
    decibel_threshold: float = 70.0  # dB
    silence_threshold: float = 30.0  # dB
    silence_duration: int = 60  # secondes avant alerte silence


class AudioAnalyzer:
    """
    Analyseur audio pour la détection d'événements sonores
    
    Note: En production, utiliser des modèles ML pré-entraînés comme:
    - YAMNet (Google)
    - VGGish
    - AudioSet
    """
    
    # Caractéristiques fréquentielles des événements
    EVENT_SIGNATURES = {
        AudioEventType.GLASS_BREAK: {
            'freq_range': (2000, 8000),  # Hz
            'duration': (50, 500),        # ms
            'pattern': 'impulse',
            'decibel_min': 75
        },
        AudioEventType.SCREAM: {
            'freq_range': (500, 4000),
            'duration': (500, 3000),
            'pattern': 'sustained',
            'decibel_min': 70
        },
        AudioEventType.GUNSHOT: {
            'freq_range': (100, 5000),
            'duration': (10, 200),
            'pattern': 'impulse',
            'decibel_min': 90
        },
        AudioEventType.EXPLOSION: {
            'freq_range': (20, 2000),
            'duration': (100, 1000),
            'pattern': 'impulse',
            'decibel_min': 95
        },
        AudioEventType.DOG_BARK: {
            'freq_range': (500, 2000),
            'duration': (100, 500),
            'pattern': 'repetitive',
            'decibel_min': 60
        },
        AudioEventType.CAR_ALARM: {
            'freq_range': (1000, 3000),
            'duration': (500, 2000),
            'pattern': 'periodic',
            'decibel_min': 80
        },
        AudioEventType.FIRE_ALARM: {
            'freq_range': (2000, 4000),
            'duration': (500, 2000),
            'pattern': 'periodic',
            'decibel_min': 85
        },
        AudioEventType.SIREN: {
            'freq_range': (500, 2000),
            'duration': (1000, 5000),
            'pattern': 'sweeping',
            'decibel_min': 80
        },
        AudioEventType.AGGRESSION: {
            'freq_range': (200, 3000),
            'duration': (500, 5000),
            'pattern': 'sustained',
            'decibel_min': 65
        },
    }
    
    # Niveaux d'alerte par type d'événement
    ALERT_LEVELS = {
        AudioEventType.GUNSHOT: AudioAlertLevel.CRITICAL,
        AudioEventType.EXPLOSION: AudioAlertLevel.CRITICAL,
        AudioEventType.GLASS_BREAK: AudioAlertLevel.ALARM,
        AudioEventType.SCREAM: AudioAlertLevel.ALARM,
        AudioEventType.FIRE_ALARM: AudioAlertLevel.ALARM,
        AudioEventType.AGGRESSION: AudioAlertLevel.WARNING,
        AudioEventType.CAR_ALARM: AudioAlertLevel.WARNING,
        AudioEventType.DOG_BARK: AudioAlertLevel.INFO,
        AudioEventType.SIREN: AudioAlertLevel.WARNING,
    }
    
    def __init__(self):
        self.zones: Dict[str, AudioZone] = {}
        self.event_history: deque = deque(maxlen=1000)
        self.pending_events: Dict[str, List[AudioEvent]] = {}
        
        # État par caméra/micro
        self.audio_levels: Dict[int, deque] = {}
        self.last_sound_time: Dict[int, datetime] = {}
        
        # Compteurs pour confirmation
        self.confirmation_count = 3  # Confirmer sur 3 détections
        self.confirmation_window = 5.0  # Secondes
        
        # Statistiques
        self.stats = {
            "total_events": 0,
            "confirmed_events": 0,
            "false_positives": 0,
            "by_type": {t.value: 0 for t in AudioEventType}
        }
    
    def add_zone(self, zone: AudioZone):
        """Ajoute une zone de surveillance audio"""
        self.zones[zone.zone_id] = zone
        logger.info(f"Audio zone added: {zone.name}")
    
    def process_audio(self, 
                      audio_data: np.ndarray, 
                      sample_rate: int,
                      camera_id: int) -> List[AudioEvent]:
        """
        Traite un segment audio et détecte les événements
        
        Args:
            audio_data: Données audio (1D numpy array)
            sample_rate: Taux d'échantillonnage (Hz)
            camera_id: ID de la caméra/micro
        
        Returns:
            Liste des événements détectés
        """
        events = []
        timestamp = datetime.now()
        
        # 1. Calculer le niveau en dB
        db_level = self._calculate_db(audio_data)
        
        # Stocker l'historique des niveaux
        if camera_id not in self.audio_levels:
            self.audio_levels[camera_id] = deque(maxlen=100)
        self.audio_levels[camera_id].append((timestamp, db_level))
        
        # 2. Extraire les caractéristiques fréquentielles
        freq_spectrum = self._compute_spectrum(audio_data, sample_rate)
        
        # 3. Détecter les événements
        for event_type, signature in self.EVENT_SIGNATURES.items():
            if self._matches_signature(freq_spectrum, db_level, signature):
                confidence = self._calculate_confidence(freq_spectrum, db_level, signature)
                
                if confidence >= 0.5:
                    event = AudioEvent(
                        event_id=f"audio_{camera_id}_{timestamp.timestamp()}_{event_type.value}",
                        event_type=event_type,
                        timestamp=timestamp,
                        camera_id=camera_id,
                        confidence=confidence,
                        duration_ms=len(audio_data) * 1000 // sample_rate,
                        decibel_level=db_level,
                        frequency_range=signature['freq_range'],
                        alert_level=self.ALERT_LEVELS.get(event_type, AudioAlertLevel.INFO)
                    )
                    events.append(event)
        
        # 4. Détecter le silence anormal
        silence_event = self._detect_silence(camera_id, db_level, timestamp)
        if silence_event:
            events.append(silence_event)
        
        # 5. Confirmer les événements
        confirmed_events = self._confirm_events(events)
        
        # 6. Mettre à jour les statistiques
        self._update_stats(confirmed_events)
        
        return confirmed_events
    
    def _calculate_db(self, audio_data: np.ndarray) -> float:
        """Calcule le niveau en décibels"""
        rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))
        if rms > 0:
            db = 20 * np.log10(rms / 32768)  # Référence 16-bit
            return max(-80, min(120, db + 80))  # Normaliser 0-120 dB
        return 0
    
    def _compute_spectrum(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """Calcule le spectre fréquentiel"""
        # FFT
        n = len(audio_data)
        fft = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(n, 1/sample_rate)
        magnitudes = np.abs(fft)
        
        # Trouver les pics
        peak_indices = np.argsort(magnitudes)[-10:]
        peak_freqs = freqs[peak_indices]
        
        # Calculer l'énergie par bande
        bands = {
            'low': (20, 200),
            'mid_low': (200, 500),
            'mid': (500, 2000),
            'mid_high': (2000, 4000),
            'high': (4000, 10000)
        }
        
        band_energy = {}
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs < high)
            band_energy[band_name] = np.sum(magnitudes[mask])
        
        return {
            'peak_freqs': peak_freqs.tolist(),
            'band_energy': band_energy,
            'dominant_freq': freqs[np.argmax(magnitudes)],
            'spectral_centroid': np.sum(freqs * magnitudes) / np.sum(magnitudes) if np.sum(magnitudes) > 0 else 0
        }
    
    def _matches_signature(self, spectrum: Dict, db_level: float, signature: Dict) -> bool:
        """Vérifie si le spectre correspond à une signature"""
        # Vérifier le niveau dB minimum
        if db_level < signature['decibel_min']:
            return False
        
        # Vérifier la plage de fréquence dominante
        freq_low, freq_high = signature['freq_range']
        dominant = spectrum['dominant_freq']
        
        if not (freq_low <= dominant <= freq_high):
            # Vérifier si au moins un pic est dans la plage
            peaks_in_range = [f for f in spectrum['peak_freqs'] 
                            if freq_low <= f <= freq_high]
            if len(peaks_in_range) < 2:
                return False
        
        return True
    
    def _calculate_confidence(self, spectrum: Dict, db_level: float, signature: Dict) -> float:
        """Calcule la confiance de la détection"""
        confidence = 0.0
        
        # Score basé sur le niveau dB
        db_score = min(1.0, (db_level - signature['decibel_min'] + 10) / 30)
        confidence += db_score * 0.3
        
        # Score basé sur la fréquence dominante
        freq_low, freq_high = signature['freq_range']
        dominant = spectrum['dominant_freq']
        
        if freq_low <= dominant <= freq_high:
            # Plus proche du centre = meilleur score
            center = (freq_low + freq_high) / 2
            distance = abs(dominant - center) / (freq_high - freq_low)
            freq_score = 1.0 - distance
            confidence += freq_score * 0.4
        
        # Score basé sur la distribution d'énergie
        total_energy = sum(spectrum['band_energy'].values())
        if total_energy > 0:
            # Calculer l'énergie dans la bande cible
            target_bands = []
            if freq_low < 500:
                target_bands.append('low')
                target_bands.append('mid_low')
            if 500 <= freq_low < 2000 or freq_high > 500:
                target_bands.append('mid')
            if freq_high > 2000:
                target_bands.append('mid_high')
            if freq_high > 4000:
                target_bands.append('high')
            
            target_energy = sum(spectrum['band_energy'].get(b, 0) for b in target_bands)
            energy_ratio = target_energy / total_energy
            confidence += energy_ratio * 0.3
        
        return min(1.0, confidence)
    
    def _detect_silence(self, camera_id: int, db_level: float, 
                        timestamp: datetime) -> Optional[AudioEvent]:
        """Détecte un silence anormal"""
        # Trouver la zone associée
        zone = None
        for z in self.zones.values():
            if camera_id in z.camera_ids:
                zone = z
                break
        
        if not zone:
            return None
        
        silence_threshold = zone.silence_threshold
        silence_duration = zone.silence_duration
        
        if db_level < silence_threshold:
            # Vérifier depuis combien de temps
            if camera_id in self.last_sound_time:
                elapsed = (timestamp - self.last_sound_time[camera_id]).total_seconds()
                
                if elapsed >= silence_duration:
                    return AudioEvent(
                        event_id=f"silence_{camera_id}_{timestamp.timestamp()}",
                        event_type=AudioEventType.SILENCE,
                        timestamp=timestamp,
                        camera_id=camera_id,
                        confidence=0.9,
                        duration_ms=int(elapsed * 1000),
                        decibel_level=db_level,
                        frequency_range=(0, 0),
                        alert_level=AudioAlertLevel.WARNING
                    )
        else:
            # Son détecté, reset du timer
            self.last_sound_time[camera_id] = timestamp
        
        return None
    
    def _confirm_events(self, events: List[AudioEvent]) -> List[AudioEvent]:
        """Confirme les événements sur plusieurs détections"""
        confirmed = []
        
        for event in events:
            key = f"{event.camera_id}_{event.event_type.value}"
            
            if key not in self.pending_events:
                self.pending_events[key] = []
            
            self.pending_events[key].append(event)
            
            # Nettoyer les anciennes détections
            cutoff = datetime.now() - timedelta(seconds=self.confirmation_window)
            self.pending_events[key] = [
                e for e in self.pending_events[key]
                if e.timestamp > cutoff
            ]
            
            # Vérifier si confirmé
            if len(self.pending_events[key]) >= self.confirmation_count:
                event.is_confirmed = True
                confirmed.append(event)
                self.event_history.append(event)
                
                # Reset pour éviter les doublons
                self.pending_events[key] = []
            elif event.alert_level in [AudioAlertLevel.CRITICAL, AudioAlertLevel.ALARM]:
                # Les alertes graves sont transmises même non confirmées
                confirmed.append(event)
        
        return confirmed
    
    def _update_stats(self, events: List[AudioEvent]):
        """Met à jour les statistiques"""
        for event in events:
            self.stats["total_events"] += 1
            self.stats["by_type"][event.event_type.value] += 1
            
            if event.is_confirmed:
                self.stats["confirmed_events"] += 1
    
    def get_audio_level(self, camera_id: int) -> Optional[float]:
        """Récupère le niveau audio actuel"""
        if camera_id in self.audio_levels and self.audio_levels[camera_id]:
            return self.audio_levels[camera_id][-1][1]
        return None
    
    def get_audio_history(self, camera_id: int, seconds: int = 60) -> List[Tuple[datetime, float]]:
        """Récupère l'historique des niveaux audio"""
        if camera_id not in self.audio_levels:
            return []
        
        cutoff = datetime.now() - timedelta(seconds=seconds)
        return [(t, level) for t, level in self.audio_levels[camera_id] if t > cutoff]
    
    def get_recent_events(self, camera_id: int = None, 
                          event_type: AudioEventType = None,
                          limit: int = 50) -> List[Dict]:
        """Récupère les événements récents"""
        events = list(self.event_history)
        
        if camera_id:
            events = [e for e in events if e.camera_id == camera_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [
            {
                "id": e.event_id,
                "type": e.event_type.value,
                "timestamp": e.timestamp.isoformat(),
                "camera_id": e.camera_id,
                "confidence": e.confidence,
                "decibel_level": e.decibel_level,
                "alert_level": e.alert_level.value,
                "is_confirmed": e.is_confirmed
            }
            for e in events[-limit:]
        ]
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques"""
        return self.stats


# Instance globale
audio_analyzer = AudioAnalyzer()


# Fonction utilitaire pour l'API
def analyze_audio_stream(audio_chunk: bytes, 
                         sample_rate: int,
                         camera_id: int) -> List[Dict]:
    """
    Analyse un chunk audio et retourne les événements détectés
    """
    # Convertir bytes en numpy array
    audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
    
    # Analyser
    events = audio_analyzer.process_audio(audio_data, sample_rate, camera_id)
    
    # Formater la réponse
    return [
        {
            "type": e.event_type.value,
            "confidence": e.confidence,
            "decibel": e.decibel_level,
            "alert_level": e.alert_level.value,
            "timestamp": e.timestamp.isoformat()
        }
        for e in events
    ]
