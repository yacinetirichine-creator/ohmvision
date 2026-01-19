"""
OhmVision - Advanced Industry Analytics
Analyses spécifiques par secteur d'activité
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class IndustryType(str, Enum):
    """Secteurs d'activité supportés"""
    RETAIL = "retail"              # Commerce de détail
    INDUSTRIAL = "industrial"      # Industrie/Usine
    HEALTHCARE = "healthcare"      # Santé/Hôpitaux
    HOSPITALITY = "hospitality"    # Hôtellerie/Restauration
    LOGISTICS = "logistics"        # Logistique/Entrepôts
    BANKING = "banking"            # Banques/Finance
    EDUCATION = "education"        # Écoles/Universités
    CONSTRUCTION = "construction"  # Chantiers BTP
    PARKING = "parking"            # Parkings
    SMART_CITY = "smart_city"      # Villes intelligentes


@dataclass
class RetailAnalytics:
    """Analyses spécifiques au Retail"""
    
    # Comptage et flux
    visitors_today: int = 0
    visitors_hourly: Dict[int, int] = field(default_factory=dict)
    conversion_rate: float = 0.0  # Visiteurs vs acheteurs
    
    # Temps et parcours
    avg_dwell_time: float = 0.0  # Temps moyen en magasin (minutes)
    dwell_time_by_zone: Dict[str, float] = field(default_factory=dict)
    
    # Zones chaudes
    heatmap_data: List[List[float]] = field(default_factory=list)
    hot_zones: List[str] = field(default_factory=list)
    cold_zones: List[str] = field(default_factory=list)
    
    # Files d'attente
    queue_length: int = 0
    avg_wait_time: float = 0.0  # minutes
    queue_alerts: int = 0
    
    # Performance
    staff_customer_ratio: float = 0.0
    peak_hours: List[int] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "visitors_today": self.visitors_today,
            "visitors_hourly": self.visitors_hourly,
            "conversion_rate": self.conversion_rate,
            "avg_dwell_time": self.avg_dwell_time,
            "dwell_time_by_zone": self.dwell_time_by_zone,
            "hot_zones": self.hot_zones,
            "cold_zones": self.cold_zones,
            "queue_length": self.queue_length,
            "avg_wait_time": self.avg_wait_time,
            "staff_customer_ratio": self.staff_customer_ratio,
            "peak_hours": self.peak_hours
        }


@dataclass
class IndustrialAnalytics:
    """Analyses spécifiques à l'Industrie"""
    
    # Sécurité
    ppe_compliance_rate: float = 0.0  # % de conformité EPI
    ppe_violations_today: int = 0
    safety_score: float = 100.0
    
    # Zones dangereuses
    restricted_zone_breaches: int = 0
    near_miss_incidents: int = 0
    
    # Productivité
    workers_present: int = 0
    active_workstations: int = 0
    idle_time_detected: float = 0.0  # minutes
    
    # Équipements
    forklift_movements: int = 0
    vehicle_near_pedestrian_alerts: int = 0
    
    # Ergonomie
    poor_posture_alerts: int = 0
    repetitive_motion_warnings: int = 0
    
    def to_dict(self) -> dict:
        return {
            "ppe_compliance_rate": self.ppe_compliance_rate,
            "ppe_violations_today": self.ppe_violations_today,
            "safety_score": self.safety_score,
            "restricted_zone_breaches": self.restricted_zone_breaches,
            "near_miss_incidents": self.near_miss_incidents,
            "workers_present": self.workers_present,
            "forklift_movements": self.forklift_movements,
            "vehicle_near_pedestrian_alerts": self.vehicle_near_pedestrian_alerts,
            "poor_posture_alerts": self.poor_posture_alerts
        }


@dataclass
class HealthcareAnalytics:
    """Analyses spécifiques à la Santé"""
    
    # Patients
    patients_in_waiting: int = 0
    avg_wait_time: float = 0.0
    patient_falls_detected: int = 0
    
    # Personnel
    staff_present: int = 0
    nurse_patient_ratio: float = 0.0
    
    # Hygiène
    hand_hygiene_compliance: float = 0.0  # % lavage mains
    mask_compliance: float = 0.0
    
    # Urgences
    emergency_response_time: float = 0.0  # secondes
    code_blue_alerts: int = 0
    
    # Flux
    bed_occupancy_rate: float = 0.0
    discharge_predictions: int = 0
    
    def to_dict(self) -> dict:
        return {
            "patients_in_waiting": self.patients_in_waiting,
            "avg_wait_time": self.avg_wait_time,
            "patient_falls_detected": self.patient_falls_detected,
            "staff_present": self.staff_present,
            "hand_hygiene_compliance": self.hand_hygiene_compliance,
            "mask_compliance": self.mask_compliance,
            "emergency_response_time": self.emergency_response_time
        }


@dataclass
class LogisticsAnalytics:
    """Analyses spécifiques à la Logistique"""
    
    # Flux véhicules
    trucks_in_yard: int = 0
    loading_docks_occupied: int = 0
    avg_loading_time: float = 0.0  # minutes
    
    # Inventaire visuel
    pallet_count: int = 0
    package_throughput: int = 0
    
    # Sécurité
    forklift_count: int = 0
    pedestrian_in_vehicle_zone: int = 0
    speed_violations: int = 0
    
    # Efficacité
    dock_utilization: float = 0.0
    idle_equipment: int = 0
    bottleneck_zones: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "trucks_in_yard": self.trucks_in_yard,
            "loading_docks_occupied": self.loading_docks_occupied,
            "avg_loading_time": self.avg_loading_time,
            "pallet_count": self.pallet_count,
            "package_throughput": self.package_throughput,
            "forklift_count": self.forklift_count,
            "pedestrian_in_vehicle_zone": self.pedestrian_in_vehicle_zone,
            "dock_utilization": self.dock_utilization
        }


@dataclass
class ConstructionAnalytics:
    """Analyses spécifiques aux Chantiers BTP"""
    
    # Sécurité
    workers_with_helmet: int = 0
    workers_without_helmet: int = 0
    helmet_compliance: float = 0.0
    vest_compliance: float = 0.0
    harness_compliance: float = 0.0  # Pour travaux en hauteur
    
    # Zones
    exclusion_zone_breaches: int = 0
    crane_operation_alerts: int = 0
    
    # Progression
    workers_on_site: int = 0
    active_zones: int = 0
    equipment_utilization: float = 0.0
    
    # Incidents
    near_miss_count: int = 0
    unsafe_behavior_alerts: int = 0
    falling_object_risks: int = 0
    
    def to_dict(self) -> dict:
        return {
            "workers_with_helmet": self.workers_with_helmet,
            "workers_without_helmet": self.workers_without_helmet,
            "helmet_compliance": self.helmet_compliance,
            "vest_compliance": self.vest_compliance,
            "harness_compliance": self.harness_compliance,
            "exclusion_zone_breaches": self.exclusion_zone_breaches,
            "workers_on_site": self.workers_on_site,
            "near_miss_count": self.near_miss_count,
            "unsafe_behavior_alerts": self.unsafe_behavior_alerts
        }


@dataclass
class ParkingAnalytics:
    """Analyses spécifiques aux Parkings"""
    
    # Occupation
    total_spaces: int = 0
    occupied_spaces: int = 0
    available_spaces: int = 0
    occupancy_rate: float = 0.0
    
    # Par zone/niveau
    occupancy_by_zone: Dict[str, float] = field(default_factory=dict)
    
    # Flux
    entries_today: int = 0
    exits_today: int = 0
    avg_parking_duration: float = 0.0  # minutes
    
    # Reconnaissance plaques (LPR)
    plates_recognized: int = 0
    vip_vehicles_detected: int = 0
    blacklisted_vehicles: int = 0
    
    # Anomalies
    wrong_way_alerts: int = 0
    abandoned_vehicle_alerts: int = 0
    
    def to_dict(self) -> dict:
        return {
            "total_spaces": self.total_spaces,
            "occupied_spaces": self.occupied_spaces,
            "available_spaces": self.available_spaces,
            "occupancy_rate": self.occupancy_rate,
            "occupancy_by_zone": self.occupancy_by_zone,
            "entries_today": self.entries_today,
            "exits_today": self.exits_today,
            "avg_parking_duration": self.avg_parking_duration,
            "plates_recognized": self.plates_recognized
        }


@dataclass
class SmartCityAnalytics:
    """Analyses spécifiques aux Villes Intelligentes"""
    
    # Trafic
    vehicle_count: int = 0
    pedestrian_count: int = 0
    cyclist_count: int = 0
    traffic_density: str = "normal"  # low, normal, high, congested
    
    # Sécurité publique
    crowd_density: float = 0.0
    crowd_alerts: int = 0
    loitering_detected: int = 0
    fight_detected: int = 0
    
    # Incidents
    accidents_detected: int = 0
    fallen_person_alerts: int = 0
    
    # Environnement
    illegal_dumping: int = 0
    graffiti_detected: int = 0
    
    # Flux piétons
    crosswalk_violations: int = 0
    jaywalking_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            "vehicle_count": self.vehicle_count,
            "pedestrian_count": self.pedestrian_count,
            "cyclist_count": self.cyclist_count,
            "traffic_density": self.traffic_density,
            "crowd_density": self.crowd_density,
            "crowd_alerts": self.crowd_alerts,
            "loitering_detected": self.loitering_detected,
            "accidents_detected": self.accidents_detected
        }


class IndustryAnalyticsEngine:
    """
    Moteur d'analyses sectorielles
    Génère des KPIs et insights spécifiques à chaque industrie
    """
    
    def __init__(self):
        self.analytics_cache: Dict[int, dict] = {}  # camera_id -> analytics
        self.historical_data: Dict[int, List[dict]] = defaultdict(list)
    
    def get_analytics(self, camera_id: int, industry: IndustryType, 
                      detections: List[dict], zones: List[dict] = None) -> dict:
        """
        Génère les analytics pour une caméra selon son secteur
        
        Args:
            camera_id: ID de la caméra
            industry: Type d'industrie
            detections: Liste des détections courantes
            zones: Zones définies pour la caméra
        
        Returns:
            Analytics spécifiques au secteur
        """
        if industry == IndustryType.RETAIL:
            return self._analyze_retail(camera_id, detections, zones)
        elif industry == IndustryType.INDUSTRIAL:
            return self._analyze_industrial(camera_id, detections, zones)
        elif industry == IndustryType.HEALTHCARE:
            return self._analyze_healthcare(camera_id, detections, zones)
        elif industry == IndustryType.LOGISTICS:
            return self._analyze_logistics(camera_id, detections, zones)
        elif industry == IndustryType.CONSTRUCTION:
            return self._analyze_construction(camera_id, detections, zones)
        elif industry == IndustryType.PARKING:
            return self._analyze_parking(camera_id, detections, zones)
        elif industry == IndustryType.SMART_CITY:
            return self._analyze_smart_city(camera_id, detections, zones)
        else:
            return self._analyze_generic(camera_id, detections, zones)
    
    def _analyze_retail(self, camera_id: int, detections: List[dict], 
                        zones: List[dict]) -> dict:
        """Analyse pour le Retail"""
        analytics = RetailAnalytics()
        
        # Compter les personnes
        persons = [d for d in detections if d.get("label") == "person"]
        analytics.visitors_today = len(persons)
        
        # Calculer le temps de présence moyen (simulé pour l'exemple)
        analytics.avg_dwell_time = 12.5  # minutes
        
        # Détecter les files d'attente
        if zones:
            queue_zones = [z for z in zones if z.get("type") == "queue"]
            for qz in queue_zones:
                persons_in_queue = self._count_in_zone(persons, qz)
                analytics.queue_length = max(analytics.queue_length, persons_in_queue)
        
        # Calculer les heures de pointe
        current_hour = datetime.now().hour
        if 12 <= current_hour <= 14 or 17 <= current_hour <= 19:
            analytics.peak_hours = [12, 13, 17, 18]
        
        # Zones chaudes/froides (basé sur la densité)
        analytics.hot_zones = ["Entrée", "Promotions", "Caisse"]
        analytics.cold_zones = ["Fond du magasin", "Rayon outillage"]
        
        return {
            "industry": "retail",
            "analytics": analytics.to_dict(),
            "insights": self._generate_retail_insights(analytics),
            "recommendations": self._generate_retail_recommendations(analytics)
        }
    
    def _analyze_industrial(self, camera_id: int, detections: List[dict],
                            zones: List[dict]) -> dict:
        """Analyse pour l'Industrie"""
        analytics = IndustrialAnalytics()
        
        # Compter les personnes et vérifier EPI
        persons = [d for d in detections if d.get("label") == "person"]
        helmets = [d for d in detections if d.get("label") == "helmet"]
        vests = [d for d in detections if d.get("label") == "vest"]
        forklifts = [d for d in detections if d.get("label") in ["forklift", "vehicle"]]
        
        analytics.workers_present = len(persons)
        analytics.forklift_movements = len(forklifts)
        
        # Calculer la conformité EPI
        if len(persons) > 0:
            # Associer les EPI aux personnes (simplifié)
            analytics.ppe_compliance_rate = min(len(helmets), len(persons)) / len(persons) * 100
            analytics.ppe_violations_today = max(0, len(persons) - len(helmets))
        
        # Score de sécurité
        analytics.safety_score = 100 - (analytics.ppe_violations_today * 5)
        analytics.safety_score = max(0, analytics.safety_score)
        
        # Vérifier les zones restreintes
        if zones:
            restricted = [z for z in zones if z.get("type") == "restricted"]
            for rz in restricted:
                breaches = self._count_in_zone(persons, rz)
                analytics.restricted_zone_breaches += breaches
        
        return {
            "industry": "industrial",
            "analytics": analytics.to_dict(),
            "insights": self._generate_industrial_insights(analytics),
            "recommendations": self._generate_industrial_recommendations(analytics)
        }
    
    def _analyze_healthcare(self, camera_id: int, detections: List[dict],
                            zones: List[dict]) -> dict:
        """Analyse pour la Santé"""
        analytics = HealthcareAnalytics()
        
        persons = [d for d in detections if d.get("label") == "person"]
        falls = [d for d in detections if d.get("label") == "fall"]
        masks = [d for d in detections if d.get("label") == "mask"]
        
        analytics.patients_in_waiting = len(persons)
        analytics.patient_falls_detected = len(falls)
        
        if len(persons) > 0:
            analytics.mask_compliance = min(len(masks), len(persons)) / len(persons) * 100
        
        # Temps d'attente moyen (simulé)
        analytics.avg_wait_time = 15.0
        
        return {
            "industry": "healthcare",
            "analytics": analytics.to_dict(),
            "insights": self._generate_healthcare_insights(analytics),
            "recommendations": []
        }
    
    def _analyze_logistics(self, camera_id: int, detections: List[dict],
                           zones: List[dict]) -> dict:
        """Analyse pour la Logistique"""
        analytics = LogisticsAnalytics()
        
        persons = [d for d in detections if d.get("label") == "person"]
        vehicles = [d for d in detections if d.get("label") in ["truck", "forklift", "vehicle"]]
        
        analytics.forklift_count = len([v for v in vehicles if v.get("label") == "forklift"])
        analytics.trucks_in_yard = len([v for v in vehicles if v.get("label") == "truck"])
        
        # Vérifier piétons dans zones véhicules
        if zones:
            vehicle_zones = [z for z in zones if z.get("type") == "vehicle_only"]
            for vz in vehicle_zones:
                analytics.pedestrian_in_vehicle_zone += self._count_in_zone(persons, vz)
        
        return {
            "industry": "logistics",
            "analytics": analytics.to_dict(),
            "insights": [],
            "recommendations": []
        }
    
    def _analyze_construction(self, camera_id: int, detections: List[dict],
                              zones: List[dict]) -> dict:
        """Analyse pour les Chantiers BTP"""
        analytics = ConstructionAnalytics()
        
        persons = [d for d in detections if d.get("label") == "person"]
        helmets = [d for d in detections if d.get("label") == "helmet"]
        vests = [d for d in detections if d.get("label") == "vest"]
        
        analytics.workers_on_site = len(persons)
        analytics.workers_with_helmet = min(len(helmets), len(persons))
        analytics.workers_without_helmet = max(0, len(persons) - len(helmets))
        
        if len(persons) > 0:
            analytics.helmet_compliance = analytics.workers_with_helmet / len(persons) * 100
            analytics.vest_compliance = min(len(vests), len(persons)) / len(persons) * 100
        
        return {
            "industry": "construction",
            "analytics": analytics.to_dict(),
            "insights": self._generate_construction_insights(analytics),
            "recommendations": self._generate_construction_recommendations(analytics)
        }
    
    def _analyze_parking(self, camera_id: int, detections: List[dict],
                         zones: List[dict]) -> dict:
        """Analyse pour les Parkings"""
        analytics = ParkingAnalytics()
        
        vehicles = [d for d in detections if d.get("label") in ["car", "vehicle", "truck"]]
        
        analytics.total_spaces = 100  # À configurer par site
        analytics.occupied_spaces = len(vehicles)
        analytics.available_spaces = analytics.total_spaces - analytics.occupied_spaces
        analytics.occupancy_rate = analytics.occupied_spaces / analytics.total_spaces * 100
        
        return {
            "industry": "parking",
            "analytics": analytics.to_dict(),
            "insights": [],
            "recommendations": []
        }
    
    def _analyze_smart_city(self, camera_id: int, detections: List[dict],
                            zones: List[dict]) -> dict:
        """Analyse pour les Villes Intelligentes"""
        analytics = SmartCityAnalytics()
        
        persons = [d for d in detections if d.get("label") == "person"]
        vehicles = [d for d in detections if d.get("label") in ["car", "vehicle", "truck", "bus"]]
        cyclists = [d for d in detections if d.get("label") == "bicycle"]
        falls = [d for d in detections if d.get("label") == "fall"]
        
        analytics.pedestrian_count = len(persons)
        analytics.vehicle_count = len(vehicles)
        analytics.cyclist_count = len(cyclists)
        analytics.fallen_person_alerts = len(falls)
        
        # Densité de trafic
        total = len(vehicles)
        if total < 5:
            analytics.traffic_density = "low"
        elif total < 15:
            analytics.traffic_density = "normal"
        elif total < 30:
            analytics.traffic_density = "high"
        else:
            analytics.traffic_density = "congested"
        
        # Densité de foule
        analytics.crowd_density = len(persons) / 100  # Normalisé
        if analytics.crowd_density > 0.8:
            analytics.crowd_alerts = 1
        
        return {
            "industry": "smart_city",
            "analytics": analytics.to_dict(),
            "insights": [],
            "recommendations": []
        }
    
    def _analyze_generic(self, camera_id: int, detections: List[dict],
                         zones: List[dict]) -> dict:
        """Analyse générique"""
        persons = [d for d in detections if d.get("label") == "person"]
        vehicles = [d for d in detections if d.get("label") in ["car", "vehicle"]]
        
        return {
            "industry": "generic",
            "analytics": {
                "person_count": len(persons),
                "vehicle_count": len(vehicles),
                "total_detections": len(detections)
            },
            "insights": [],
            "recommendations": []
        }
    
    def _count_in_zone(self, detections: List[dict], zone: dict) -> int:
        """Compte les détections dans une zone"""
        count = 0
        zone_box = zone.get("coordinates", {})
        
        for det in detections:
            box = det.get("box", [])
            if len(box) >= 4:
                center_x = (box[0] + box[2]) / 2
                center_y = (box[1] + box[3]) / 2
                
                if (zone_box.get("x1", 0) <= center_x <= zone_box.get("x2", 9999) and
                    zone_box.get("y1", 0) <= center_y <= zone_box.get("y2", 9999)):
                    count += 1
        
        return count
    
    # =========================================================================
    # Générateurs d'Insights et Recommandations
    # =========================================================================
    
    def _generate_retail_insights(self, analytics: RetailAnalytics) -> List[dict]:
        """Génère des insights pour le Retail"""
        insights = []
        
        if analytics.queue_length > 5:
            insights.append({
                "type": "warning",
                "title": "File d'attente longue",
                "message": f"{analytics.queue_length} personnes en attente aux caisses",
                "action": "Ouvrir une caisse supplémentaire"
            })
        
        if analytics.avg_dwell_time < 5:
            insights.append({
                "type": "info",
                "title": "Temps de visite court",
                "message": "Les clients passent moins de 5 minutes en magasin",
                "action": "Améliorer l'attractivité des rayons"
            })
        
        return insights
    
    def _generate_retail_recommendations(self, analytics: RetailAnalytics) -> List[str]:
        """Génère des recommandations pour le Retail"""
        recommendations = []
        
        if analytics.queue_length > 3:
            recommendations.append("Ouvrir une caisse supplémentaire")
        
        if analytics.cold_zones:
            recommendations.append(f"Dynamiser les zones froides: {', '.join(analytics.cold_zones)}")
        
        return recommendations
    
    def _generate_industrial_insights(self, analytics: IndustrialAnalytics) -> List[dict]:
        """Génère des insights pour l'Industrie"""
        insights = []
        
        if analytics.ppe_compliance_rate < 100:
            insights.append({
                "type": "critical",
                "title": "Non-conformité EPI détectée",
                "message": f"{analytics.ppe_violations_today} travailleur(s) sans casque",
                "action": "Intervention immédiate requise"
            })
        
        if analytics.restricted_zone_breaches > 0:
            insights.append({
                "type": "critical",
                "title": "Intrusion zone restreinte",
                "message": f"{analytics.restricted_zone_breaches} entrée(s) non autorisée(s)",
                "action": "Vérifier les accès"
            })
        
        return insights
    
    def _generate_industrial_recommendations(self, analytics: IndustrialAnalytics) -> List[str]:
        """Génère des recommandations pour l'Industrie"""
        recommendations = []
        
        if analytics.safety_score < 80:
            recommendations.append("Organiser une session de rappel sécurité")
        
        if analytics.ppe_violations_today > 0:
            recommendations.append("Renforcer les contrôles EPI à l'entrée")
        
        return recommendations
    
    def _generate_healthcare_insights(self, analytics: HealthcareAnalytics) -> List[dict]:
        """Génère des insights pour la Santé"""
        insights = []
        
        if analytics.patient_falls_detected > 0:
            insights.append({
                "type": "critical",
                "title": "Chute patient détectée",
                "message": "Intervention médicale requise immédiatement",
                "action": "Code d'urgence activé"
            })
        
        if analytics.avg_wait_time > 30:
            insights.append({
                "type": "warning",
                "title": "Temps d'attente élevé",
                "message": f"Attente moyenne: {analytics.avg_wait_time:.0f} minutes",
                "action": "Renforcer l'équipe d'accueil"
            })
        
        return insights
    
    def _generate_construction_insights(self, analytics: ConstructionAnalytics) -> List[dict]:
        """Génère des insights pour les Chantiers"""
        insights = []
        
        if analytics.workers_without_helmet > 0:
            insights.append({
                "type": "critical",
                "title": "⚠️ ALERTE SÉCURITÉ",
                "message": f"{analytics.workers_without_helmet} ouvrier(s) sans casque sur le chantier",
                "action": "Arrêt immédiat des travaux pour mise en conformité"
            })
        
        if analytics.helmet_compliance < 100:
            insights.append({
                "type": "warning",
                "title": "Conformité casque insuffisante",
                "message": f"Taux de port du casque: {analytics.helmet_compliance:.1f}%",
                "action": "Rappel des règles de sécurité"
            })
        
        return insights
    
    def _generate_construction_recommendations(self, analytics: ConstructionAnalytics) -> List[str]:
        """Génère des recommandations pour les Chantiers"""
        recommendations = []
        
        if analytics.helmet_compliance < 100:
            recommendations.append("Installer des points de distribution de casques aux entrées")
            recommendations.append("Afficher des rappels visuels de sécurité")
        
        if analytics.near_miss_count > 0:
            recommendations.append("Analyser les incidents évités pour prévention")
        
        return recommendations


# Instance globale
industry_analytics = IndustryAnalyticsEngine()
