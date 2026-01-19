"""
OhmVision - Predictive AI Engine
Intelligence artificielle prédictive pour anticiper les incidents
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum
import logging
import math
import json

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Niveaux de risque"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentType(str, Enum):
    """Types d'incidents prédictibles"""
    INTRUSION = "intrusion"
    THEFT = "theft"
    VIOLENCE = "violence"
    FIRE = "fire"
    ACCIDENT = "accident"
    CROWD_CRUSH = "crowd_crush"
    VANDALISM = "vandalism"
    SAFETY_VIOLATION = "safety_violation"


@dataclass
class PredictionResult:
    """Résultat d'une prédiction"""
    incident_type: IncidentType
    probability: float  # 0-1
    risk_level: RiskLevel
    time_window: str  # "next_hour", "next_4h", "next_day"
    confidence: float
    contributing_factors: List[str]
    recommended_actions: List[str]
    affected_zones: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HistoricalPattern:
    """Pattern historique d'incidents"""
    incident_type: str
    hour_distribution: Dict[int, float]  # Heure -> fréquence
    day_distribution: Dict[int, float]   # Jour semaine -> fréquence
    zone_distribution: Dict[str, float]  # Zone -> fréquence
    avg_duration: float
    seasonal_factor: float  # Multiplicateur saisonnier


class PredictiveEngine:
    """
    Moteur d'IA prédictive
    Analyse les patterns historiques pour prédire les incidents futurs
    """
    
    def __init__(self):
        # Historique des incidents
        self.incident_history: List[Dict] = []
        
        # Patterns appris
        self.learned_patterns: Dict[str, HistoricalPattern] = {}
        
        # Facteurs contextuels actuels
        self.current_context: Dict = {
            "occupancy": 0,
            "weather": "clear",
            "special_event": False,
            "time_of_day": "day",
            "day_type": "weekday"
        }
        
        # Seuils d'alerte
        self.alert_thresholds = {
            RiskLevel.LOW: 0.2,
            RiskLevel.MODERATE: 0.4,
            RiskLevel.HIGH: 0.6,
            RiskLevel.CRITICAL: 0.8
        }
        
        # Initialiser avec des patterns de base
        self._initialize_base_patterns()
    
    def _initialize_base_patterns(self):
        """Initialise les patterns de base (basés sur des données statistiques générales)"""
        
        # Pattern intrusion
        self.learned_patterns["intrusion"] = HistoricalPattern(
            incident_type="intrusion",
            hour_distribution={
                0: 0.15, 1: 0.18, 2: 0.20, 3: 0.22, 4: 0.18, 5: 0.12,
                6: 0.05, 7: 0.02, 8: 0.01, 9: 0.01, 10: 0.01, 11: 0.01,
                12: 0.01, 13: 0.01, 14: 0.01, 15: 0.02, 16: 0.02, 17: 0.03,
                18: 0.05, 19: 0.08, 20: 0.10, 21: 0.12, 22: 0.13, 23: 0.14
            },
            day_distribution={0: 0.12, 1: 0.13, 2: 0.14, 3: 0.14, 4: 0.18, 5: 0.20, 6: 0.09},
            zone_distribution={"entrance": 0.3, "parking": 0.25, "warehouse": 0.2, "office": 0.15, "other": 0.1},
            avg_duration=15.0,
            seasonal_factor=1.0
        )
        
        # Pattern violence/bagarre
        self.learned_patterns["violence"] = HistoricalPattern(
            incident_type="violence",
            hour_distribution={
                0: 0.15, 1: 0.12, 2: 0.08, 3: 0.05, 4: 0.03, 5: 0.02,
                6: 0.01, 7: 0.02, 8: 0.03, 9: 0.03, 10: 0.04, 11: 0.05,
                12: 0.06, 13: 0.05, 14: 0.05, 15: 0.06, 16: 0.07, 17: 0.08,
                18: 0.10, 19: 0.12, 20: 0.14, 21: 0.15, 22: 0.16, 23: 0.15
            },
            day_distribution={0: 0.08, 1: 0.10, 2: 0.12, 3: 0.14, 4: 0.20, 5: 0.25, 6: 0.11},
            zone_distribution={"bar": 0.35, "entrance": 0.25, "parking": 0.2, "public": 0.15, "other": 0.05},
            avg_duration=5.0,
            seasonal_factor=1.0
        )
        
        # Pattern vol
        self.learned_patterns["theft"] = HistoricalPattern(
            incident_type="theft",
            hour_distribution={
                0: 0.02, 1: 0.01, 2: 0.01, 3: 0.01, 4: 0.01, 5: 0.02,
                6: 0.03, 7: 0.04, 8: 0.05, 9: 0.06, 10: 0.08, 11: 0.10,
                12: 0.12, 13: 0.11, 14: 0.10, 15: 0.09, 16: 0.08, 17: 0.07,
                18: 0.06, 19: 0.05, 20: 0.04, 21: 0.03, 22: 0.02, 23: 0.02
            },
            day_distribution={0: 0.12, 1: 0.14, 2: 0.15, 3: 0.16, 4: 0.18, 5: 0.15, 6: 0.10},
            zone_distribution={"retail": 0.4, "warehouse": 0.25, "parking": 0.2, "office": 0.1, "other": 0.05},
            avg_duration=3.0,
            seasonal_factor=1.2  # Plus élevé pendant les fêtes
        )
        
        # Pattern accident
        self.learned_patterns["accident"] = HistoricalPattern(
            incident_type="accident",
            hour_distribution={
                0: 0.02, 1: 0.01, 2: 0.01, 3: 0.01, 4: 0.02, 5: 0.03,
                6: 0.05, 7: 0.08, 8: 0.10, 9: 0.09, 10: 0.08, 11: 0.07,
                12: 0.06, 13: 0.07, 14: 0.08, 15: 0.09, 16: 0.10, 17: 0.11,
                18: 0.08, 19: 0.06, 20: 0.04, 21: 0.03, 22: 0.02, 23: 0.02
            },
            day_distribution={0: 0.18, 1: 0.17, 2: 0.16, 3: 0.15, 4: 0.14, 5: 0.10, 6: 0.10},
            zone_distribution={"industrial": 0.35, "warehouse": 0.25, "parking": 0.2, "loading": 0.15, "other": 0.05},
            avg_duration=30.0,
            seasonal_factor=1.0
        )
    
    def predict(self, 
                zones: List[str] = None,
                time_window: str = "next_hour",
                current_conditions: Dict = None) -> List[PredictionResult]:
        """
        Génère des prédictions d'incidents
        
        Args:
            zones: Zones à analyser (None = toutes)
            time_window: "next_hour", "next_4h", "next_day"
            current_conditions: Conditions actuelles (occupancy, weather, etc.)
        
        Returns:
            Liste de prédictions triées par probabilité
        """
        predictions = []
        
        # Mettre à jour le contexte
        if current_conditions:
            self.current_context.update(current_conditions)
        
        now = datetime.now()
        
        for incident_type, pattern in self.learned_patterns.items():
            # Calculer la probabilité de base
            base_prob = self._calculate_base_probability(pattern, now, time_window)
            
            # Appliquer les facteurs contextuels
            contextual_multiplier = self._get_contextual_multiplier(incident_type)
            
            # Appliquer le facteur saisonnier
            seasonal_multiplier = self._get_seasonal_multiplier(now, incident_type)
            
            # Probabilité finale
            final_prob = min(base_prob * contextual_multiplier * seasonal_multiplier, 1.0)
            
            # Déterminer le niveau de risque
            risk_level = self._get_risk_level(final_prob)
            
            # Générer les recommandations
            factors, actions = self._generate_recommendations(incident_type, final_prob, pattern)
            
            # Zones affectées
            affected_zones = self._get_affected_zones(pattern, zones)
            
            if final_prob > 0.1:  # Seuil minimum pour inclure
                predictions.append(PredictionResult(
                    incident_type=IncidentType(incident_type),
                    probability=round(final_prob, 3),
                    risk_level=risk_level,
                    time_window=time_window,
                    confidence=self._calculate_confidence(pattern),
                    contributing_factors=factors,
                    recommended_actions=actions,
                    affected_zones=affected_zones
                ))
        
        # Trier par probabilité décroissante
        predictions.sort(key=lambda x: x.probability, reverse=True)
        
        return predictions
    
    def _calculate_base_probability(self, pattern: HistoricalPattern, 
                                     now: datetime, time_window: str) -> float:
        """Calcule la probabilité de base basée sur les patterns historiques"""
        
        # Facteur horaire
        if time_window == "next_hour":
            hour_factor = pattern.hour_distribution.get(now.hour, 0.05)
        elif time_window == "next_4h":
            hours = [(now.hour + i) % 24 for i in range(4)]
            hour_factor = sum(pattern.hour_distribution.get(h, 0.05) for h in hours) / 4
        else:  # next_day
            hour_factor = sum(pattern.hour_distribution.values()) / 24
        
        # Facteur jour de la semaine
        day_factor = pattern.day_distribution.get(now.weekday(), 0.14)
        
        # Combiner les facteurs
        base_prob = (hour_factor * 0.6 + day_factor * 0.4)
        
        return base_prob
    
    def _get_contextual_multiplier(self, incident_type: str) -> float:
        """Calcule le multiplicateur basé sur le contexte actuel"""
        multiplier = 1.0
        
        occupancy = self.current_context.get("occupancy", 0)
        weather = self.current_context.get("weather", "clear")
        special_event = self.current_context.get("special_event", False)
        
        # Haute occupation augmente certains risques
        if occupancy > 80:
            if incident_type in ["violence", "theft", "crowd_crush"]:
                multiplier *= 1.5
        elif occupancy < 20:
            if incident_type == "intrusion":
                multiplier *= 1.3
        
        # Mauvais temps
        if weather in ["rain", "storm"]:
            if incident_type == "accident":
                multiplier *= 1.4
        
        # Événement spécial
        if special_event:
            if incident_type in ["violence", "theft"]:
                multiplier *= 1.6
            if incident_type == "crowd_crush":
                multiplier *= 2.0
        
        return multiplier
    
    def _get_seasonal_multiplier(self, now: datetime, incident_type: str) -> float:
        """Calcule le multiplicateur saisonnier"""
        month = now.month
        
        # Période des fêtes (nov-jan)
        if month in [11, 12, 1]:
            if incident_type == "theft":
                return 1.4
        
        # Été (juin-août)
        if month in [6, 7, 8]:
            if incident_type == "violence":
                return 1.2
        
        # Hiver (dec-feb)
        if month in [12, 1, 2]:
            if incident_type == "accident":
                return 1.3
        
        return 1.0
    
    def _get_risk_level(self, probability: float) -> RiskLevel:
        """Détermine le niveau de risque"""
        if probability >= self.alert_thresholds[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif probability >= self.alert_thresholds[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif probability >= self.alert_thresholds[RiskLevel.MODERATE]:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _generate_recommendations(self, incident_type: str, 
                                   probability: float,
                                   pattern: HistoricalPattern) -> Tuple[List[str], List[str]]:
        """Génère les facteurs et recommandations"""
        
        factors = []
        actions = []
        
        now = datetime.now()
        
        # Facteurs communs
        if pattern.hour_distribution.get(now.hour, 0) > 0.1:
            factors.append(f"Heure à risque élevé ({now.hour}h)")
        
        if pattern.day_distribution.get(now.weekday(), 0) > 0.15:
            days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            factors.append(f"Jour à risque ({days[now.weekday()]})")
        
        if self.current_context.get("occupancy", 0) > 70:
            factors.append("Forte affluence détectée")
        
        if self.current_context.get("special_event"):
            factors.append("Événement spécial en cours")
        
        # Recommandations par type
        if incident_type == "intrusion":
            actions.append("Renforcer la surveillance périmétrique")
            actions.append("Vérifier les points d'accès")
            if probability > 0.5:
                actions.append("Activer les rondes de sécurité")
        
        elif incident_type == "theft":
            actions.append("Augmenter la présence en zone de vente")
            actions.append("Activer les alertes anti-vol")
            if probability > 0.6:
                actions.append("Déployer un agent en civil")
        
        elif incident_type == "violence":
            actions.append("Renforcer la présence sécurité visible")
            if probability > 0.5:
                actions.append("Préparer l'équipe d'intervention")
                actions.append("Alerter les forces de l'ordre en standby")
        
        elif incident_type == "accident":
            actions.append("Vérifier les équipements de sécurité")
            actions.append("Rappeler les consignes de sécurité")
            if probability > 0.5:
                actions.append("Réduire la cadence de travail")
        
        elif incident_type == "crowd_crush":
            actions.append("Activer le monitoring densité de foule")
            actions.append("Préparer les issues de secours")
            if probability > 0.6:
                actions.append("Limiter les entrées")
                actions.append("Ouvrir des sorties supplémentaires")
        
        return factors, actions
    
    def _get_affected_zones(self, pattern: HistoricalPattern, 
                            filter_zones: List[str] = None) -> List[str]:
        """Retourne les zones les plus à risque"""
        zones = sorted(pattern.zone_distribution.items(), 
                       key=lambda x: x[1], reverse=True)
        
        affected = [z[0] for z in zones[:3]]
        
        if filter_zones:
            affected = [z for z in affected if z in filter_zones]
        
        return affected
    
    def _calculate_confidence(self, pattern: HistoricalPattern) -> float:
        """Calcule la confiance dans la prédiction"""
        # Basé sur la quantité de données historiques
        # En production, cela serait basé sur les vraies données
        return 0.75
    
    # =========================================================================
    # Apprentissage
    # =========================================================================
    
    def record_incident(self, incident: Dict):
        """
        Enregistre un incident pour l'apprentissage
        
        Args:
            incident: {
                "type": str,
                "timestamp": datetime,
                "zone": str,
                "duration": float,
                "severity": str
            }
        """
        self.incident_history.append(incident)
        
        # Mettre à jour les patterns (simplifié)
        incident_type = incident.get("type")
        if incident_type in self.learned_patterns:
            pattern = self.learned_patterns[incident_type]
            
            # Mettre à jour la distribution horaire
            hour = incident["timestamp"].hour
            pattern.hour_distribution[hour] = pattern.hour_distribution.get(hour, 0) + 0.01
            
            # Normaliser
            total = sum(pattern.hour_distribution.values())
            for h in pattern.hour_distribution:
                pattern.hour_distribution[h] /= total
    
    def update_context(self, **kwargs):
        """Met à jour le contexte actuel"""
        self.current_context.update(kwargs)
    
    # =========================================================================
    # API
    # =========================================================================
    
    def get_risk_summary(self) -> Dict:
        """Retourne un résumé des risques actuels"""
        predictions = self.predict(time_window="next_hour")
        
        risk_counts = defaultdict(int)
        for pred in predictions:
            risk_counts[pred.risk_level.value] += 1
        
        highest_risk = predictions[0] if predictions else None
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_risk": highest_risk.risk_level.value if highest_risk else "low",
            "risk_distribution": dict(risk_counts),
            "top_prediction": {
                "type": highest_risk.incident_type.value,
                "probability": highest_risk.probability,
                "actions": highest_risk.recommended_actions[:2]
            } if highest_risk else None,
            "context": self.current_context
        }
    
    def get_timeline(self, hours: int = 24) -> List[Dict]:
        """Génère une timeline de prédictions"""
        timeline = []
        now = datetime.now()
        
        for h in range(hours):
            future_time = now + timedelta(hours=h)
            
            # Simuler le contexte futur
            future_context = self.current_context.copy()
            future_context["time_of_day"] = "night" if future_time.hour < 6 or future_time.hour > 22 else "day"
            
            self.update_context(**future_context)
            predictions = self.predict(time_window="next_hour")
            
            highest = predictions[0] if predictions else None
            
            timeline.append({
                "time": future_time.isoformat(),
                "hour": future_time.hour,
                "risk_level": highest.risk_level.value if highest else "low",
                "top_threat": highest.incident_type.value if highest else None,
                "probability": highest.probability if highest else 0
            })
        
        return timeline


# Instance globale
predictive_engine = PredictiveEngine()
