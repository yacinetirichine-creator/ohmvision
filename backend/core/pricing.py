"""
OhmVision - Packages & Pricing Configuration
Structure des offres commerciales et fonctionnalités associées
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field


class PlanType(str, Enum):
    """Types de plans disponibles"""
    FREE = "free"
    HOME = "home"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    """Cycles de facturation"""
    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class Feature:
    """Définition d'une fonctionnalité"""
    id: str
    name: str
    description: str
    category: str  # detection, analytics, notification, storage, support


@dataclass
class PlanLimit:
    """Limites d'un plan"""
    max_cameras: int
    max_users: int
    retention_days: int
    max_alerts_per_day: int
    max_recordings_gb: float
    api_calls_per_day: int


@dataclass
class Plan:
    """Définition d'un plan tarifaire"""
    id: PlanType
    name: str
    description: str
    
    # Prix
    price_monthly: float
    price_yearly: float
    price_one_time: Optional[float]
    currency: str = "EUR"
    
    # Limites
    limits: PlanLimit = None
    
    # Fonctionnalités incluses
    features: List[str] = field(default_factory=list)
    
    # Métadonnées
    is_popular: bool = False
    badge: Optional[str] = None


# ============================================================================
# DÉFINITION DES FONCTIONNALITÉS
# ============================================================================

FEATURES = {
    # === DÉTECTIONS DE BASE ===
    "detection_person": Feature(
        "detection_person", "Détection personnes", 
        "Détecte et compte les personnes dans le champ de vision",
        "detection"
    ),
    "detection_vehicle": Feature(
        "detection_vehicle", "Détection véhicules",
        "Détecte voitures, camions, motos, vélos",
        "detection"
    ),
    "detection_counting": Feature(
        "detection_counting", "Comptage entrées/sorties",
        "Compte les passages via lignes virtuelles",
        "detection"
    ),
    "detection_zone": Feature(
        "detection_zone", "Zones de détection",
        "Définir des zones personnalisées pour les alertes",
        "detection"
    ),
    
    # === DÉTECTIONS AVANCÉES ===
    "detection_fall": Feature(
        "detection_fall", "Détection de chutes",
        "Alerte immédiate en cas de chute d'une personne",
        "detection"
    ),
    "detection_fire_visual": Feature(
        "detection_fire_visual", "Détection feu (visuel)",
        "Détection de flammes par analyse colorimétrique",
        "detection"
    ),
    "detection_smoke": Feature(
        "detection_smoke", "Détection fumée",
        "Détection de fumée par pattern et couleur",
        "detection"
    ),
    "detection_ppe_basic": Feature(
        "detection_ppe_basic", "Détection EPI (base)",
        "Vérification casque et gilet haute visibilité",
        "detection"
    ),
    
    # === DÉTECTIONS PREMIUM ===
    "detection_fire_thermal": Feature(
        "detection_fire_thermal", "Détection feu (thermique)",
        "Détection par caméra thermique avec seuils de température",
        "detection"
    ),
    "detection_thermal_rate": Feature(
        "detection_thermal_rate", "Élévation température",
        "Alerte sur variation rapide de température (°C/min)",
        "detection"
    ),
    "detection_ppe_advanced": Feature(
        "detection_ppe_advanced", "Détection EPI (avancé)",
        "Casque, gilet, harnais, gants, lunettes",
        "detection"
    ),
    "detection_lpr": Feature(
        "detection_lpr", "Reconnaissance plaques (LPR)",
        "Lecture automatique des plaques d'immatriculation",
        "detection"
    ),
    "detection_behavior": Feature(
        "detection_behavior", "Analyse comportementale",
        "Flânerie, course, bagarre, foule, intrusion",
        "detection"
    ),
    
    # === ANALYTICS DE BASE ===
    "analytics_dashboard": Feature(
        "analytics_dashboard", "Dashboard temps réel",
        "Tableau de bord avec statistiques en direct",
        "analytics"
    ),
    "analytics_history_24h": Feature(
        "analytics_history_24h", "Historique 24h",
        "Consultation des événements des dernières 24h",
        "analytics"
    ),
    "analytics_history_7d": Feature(
        "analytics_history_7d", "Historique 7 jours",
        "Consultation des événements sur 7 jours",
        "analytics"
    ),
    "analytics_history_30d": Feature(
        "analytics_history_30d", "Historique 30 jours",
        "Consultation des événements sur 30 jours",
        "analytics"
    ),
    "analytics_history_90d": Feature(
        "analytics_history_90d", "Historique 90 jours",
        "Consultation des événements sur 90 jours",
        "analytics"
    ),
    "analytics_history_unlimited": Feature(
        "analytics_history_unlimited", "Historique illimité",
        "Conservation illimitée des données",
        "analytics"
    ),
    
    # === ANALYTICS SECTORIELS ===
    "analytics_retail": Feature(
        "analytics_retail", "Analytics Retail",
        "Heatmaps, dwell time, files d'attente, conversion",
        "analytics"
    ),
    "analytics_industrial": Feature(
        "analytics_industrial", "Analytics Industrie",
        "Score sécurité, conformité EPI, productivité",
        "analytics"
    ),
    "analytics_healthcare": Feature(
        "analytics_healthcare", "Analytics Santé",
        "Chutes patients, temps attente, hygiène",
        "analytics"
    ),
    "analytics_logistics": Feature(
        "analytics_logistics", "Analytics Logistique",
        "Occupation quais, flux véhicules, palettes",
        "analytics"
    ),
    "analytics_construction": Feature(
        "analytics_construction", "Analytics Chantiers",
        "Conformité EPI 100%, zones exclusion",
        "analytics"
    ),
    "analytics_parking": Feature(
        "analytics_parking", "Analytics Parkings",
        "Occupation, durée, VIP/blacklist",
        "analytics"
    ),
    "analytics_smartcity": Feature(
        "analytics_smartcity", "Analytics Smart City",
        "Trafic, foule, incidents publics",
        "analytics"
    ),
    "analytics_heatmap": Feature(
        "analytics_heatmap", "Heatmaps",
        "Cartes de chaleur des mouvements",
        "analytics"
    ),
    "analytics_executive": Feature(
        "analytics_executive", "Dashboard Exécutif",
        "KPIs, tendances, insights IA, recommandations",
        "analytics"
    ),
    
    # === NOTIFICATIONS ===
    "notif_email": Feature(
        "notif_email", "Notifications Email",
        "Alertes par email avec snapshots",
        "notification"
    ),
    "notif_app": Feature(
        "notif_app", "Notifications App",
        "Notifications dans l'application web/mobile",
        "notification"
    ),
    "notif_telegram": Feature(
        "notif_telegram", "Notifications Telegram",
        "Alertes via bot Telegram",
        "notification"
    ),
    "notif_discord": Feature(
        "notif_discord", "Notifications Discord",
        "Alertes via webhook Discord",
        "notification"
    ),
    "notif_sms": Feature(
        "notif_sms", "Notifications SMS",
        "Alertes par SMS (via Twilio)",
        "notification"
    ),
    "notif_slack": Feature(
        "notif_slack", "Notifications Slack",
        "Alertes dans vos canaux Slack",
        "notification"
    ),
    "notif_teams": Feature(
        "notif_teams", "Notifications Teams",
        "Alertes Microsoft Teams",
        "notification"
    ),
    "notif_webhook": Feature(
        "notif_webhook", "Webhooks personnalisés",
        "Envoi vers vos propres endpoints",
        "notification"
    ),
    
    # === ENREGISTREMENT ===
    "recording_alert": Feature(
        "recording_alert", "Enregistrement sur alerte",
        "Capture vidéo automatique lors des événements",
        "storage"
    ),
    "recording_preevent": Feature(
        "recording_preevent", "Buffer pré-événement",
        "Capture des 10 secondes avant l'alerte",
        "storage"
    ),
    "recording_continuous": Feature(
        "recording_continuous", "Enregistrement continu",
        "Enregistrement 24/7 de tous les flux",
        "storage"
    ),
    "recording_cloud": Feature(
        "recording_cloud", "Stockage cloud",
        "Sauvegarde automatique dans le cloud",
        "storage"
    ),
    
    # === RAPPORTS ===
    "report_daily": Feature(
        "report_daily", "Rapports journaliers",
        "Rapport PDF automatique chaque jour",
        "analytics"
    ),
    "report_weekly": Feature(
        "report_weekly", "Rapports hebdomadaires",
        "Rapport PDF automatique chaque semaine",
        "analytics"
    ),
    "report_monthly": Feature(
        "report_monthly", "Rapports mensuels",
        "Rapport PDF automatique chaque mois",
        "analytics"
    ),
    "report_custom": Feature(
        "report_custom", "Rapports personnalisés",
        "Génération à la demande avec filtres",
        "analytics"
    ),
    "report_compliance": Feature(
        "report_compliance", "Rapports conformité",
        "Audit sécurité et conformité EPI",
        "analytics"
    ),
    
    # === INTÉGRATIONS ===
    "integration_api": Feature(
        "integration_api", "API REST",
        "Accès complet à l'API OhmVision",
        "integration"
    ),
    "integration_onvif": Feature(
        "integration_onvif", "Support ONVIF",
        "Compatible avec toutes les caméras ONVIF",
        "integration"
    ),
    "integration_rtsp": Feature(
        "integration_rtsp", "Support RTSP",
        "Connexion à tout flux RTSP",
        "integration"
    ),
    "integration_vms": Feature(
        "integration_vms", "Plugins VMS",
        "Intégration Milestone, Genetec, etc.",
        "integration"
    ),
    "integration_access": Feature(
        "integration_access", "Contrôle d'accès",
        "Intégration systèmes de contrôle d'accès",
        "integration"
    ),
    
    # === SUPPORT ===
    "support_community": Feature(
        "support_community", "Support communautaire",
        "Forum et documentation en ligne",
        "support"
    ),
    "support_email": Feature(
        "support_email", "Support email",
        "Réponse sous 48h ouvrées",
        "support"
    ),
    "support_priority": Feature(
        "support_priority", "Support prioritaire",
        "Réponse sous 24h ouvrées",
        "support"
    ),
    "support_phone": Feature(
        "support_phone", "Support téléphonique",
        "Ligne directe avec un technicien",
        "support"
    ),
    "support_dedicated": Feature(
        "support_dedicated", "Account Manager dédié",
        "Interlocuteur unique pour votre compte",
        "support"
    ),
    "support_onsite": Feature(
        "support_onsite", "Support sur site",
        "Intervention sur site si nécessaire",
        "support"
    ),
    "support_sla": Feature(
        "support_sla", "SLA garanti",
        "Contrat de niveau de service",
        "support"
    ),
}


# ============================================================================
# DÉFINITION DES PLANS
# ============================================================================

PLANS = {
    PlanType.FREE: Plan(
        id=PlanType.FREE,
        name="FREE",
        description="Découvrez OhmVision gratuitement",
        price_monthly=0,
        price_yearly=0,
        price_one_time=0,
        limits=PlanLimit(
            max_cameras=2,
            max_users=1,
            retention_days=1,
            max_alerts_per_day=50,
            max_recordings_gb=1,
            api_calls_per_day=100
        ),
        features=[
            "detection_person",
            "detection_vehicle",
            "detection_counting",
            "analytics_dashboard",
            "analytics_history_24h",
            "notif_app",
            "notif_email",
            "integration_onvif",
            "integration_rtsp",
            "support_community"
        ],
        badge="Gratuit"
    ),
    
    PlanType.HOME: Plan(
        id=PlanType.HOME,
        name="HOME",
        description="Protection intelligente pour votre domicile",
        price_monthly=0,
        price_yearly=0,
        price_one_time=29,
        limits=PlanLimit(
            max_cameras=4,
            max_users=3,
            retention_days=7,
            max_alerts_per_day=200,
            max_recordings_gb=10,
            api_calls_per_day=500
        ),
        features=[
            # Détections
            "detection_person",
            "detection_vehicle",
            "detection_counting",
            "detection_zone",
            "detection_fall",
            "detection_fire_visual",
            "detection_smoke",
            
            # Analytics
            "analytics_dashboard",
            "analytics_history_7d",
            "analytics_heatmap",
            
            # Notifications
            "notif_app",
            "notif_email",
            "notif_telegram",
            
            # Enregistrement
            "recording_alert",
            "recording_preevent",
            
            # Intégrations
            "integration_onvif",
            "integration_rtsp",
            
            # Support
            "support_community",
            "support_email"
        ],
        badge="Paiement unique"
    ),
    
    PlanType.PRO: Plan(
        id=PlanType.PRO,
        name="PRO",
        description="Solution complète pour les professionnels",
        price_monthly=12,
        price_yearly=99,
        price_one_time=None,
        limits=PlanLimit(
            max_cameras=16,
            max_users=10,
            retention_days=30,
            max_alerts_per_day=1000,
            max_recordings_gb=100,
            api_calls_per_day=5000
        ),
        features=[
            # Toutes les détections de base
            "detection_person",
            "detection_vehicle",
            "detection_counting",
            "detection_zone",
            "detection_fall",
            "detection_fire_visual",
            "detection_smoke",
            "detection_ppe_basic",
            "detection_behavior",
            
            # Analytics complets
            "analytics_dashboard",
            "analytics_history_30d",
            "analytics_heatmap",
            "analytics_retail",
            "analytics_industrial",
            "analytics_parking",
            "analytics_executive",
            
            # Toutes les notifications
            "notif_app",
            "notif_email",
            "notif_telegram",
            "notif_discord",
            "notif_slack",
            "notif_webhook",
            
            # Enregistrement
            "recording_alert",
            "recording_preevent",
            
            # Rapports
            "report_daily",
            "report_weekly",
            
            # Intégrations
            "integration_onvif",
            "integration_rtsp",
            "integration_api",
            
            # Support
            "support_community",
            "support_email",
            "support_priority"
        ],
        is_popular=True,
        badge="Le plus populaire"
    ),
    
    PlanType.BUSINESS: Plan(
        id=PlanType.BUSINESS,
        name="BUSINESS",
        description="Sécurité avancée pour les entreprises",
        price_monthly=35,
        price_yearly=299,
        price_one_time=None,
        limits=PlanLimit(
            max_cameras=50,
            max_users=50,
            retention_days=90,
            max_alerts_per_day=10000,
            max_recordings_gb=500,
            api_calls_per_day=50000
        ),
        features=[
            # TOUTES les détections
            "detection_person",
            "detection_vehicle",
            "detection_counting",
            "detection_zone",
            "detection_fall",
            "detection_fire_visual",
            "detection_smoke",
            "detection_fire_thermal",
            "detection_thermal_rate",
            "detection_ppe_basic",
            "detection_ppe_advanced",
            "detection_lpr",
            "detection_behavior",
            
            # TOUS les analytics
            "analytics_dashboard",
            "analytics_history_90d",
            "analytics_heatmap",
            "analytics_retail",
            "analytics_industrial",
            "analytics_healthcare",
            "analytics_logistics",
            "analytics_construction",
            "analytics_parking",
            "analytics_smartcity",
            "analytics_executive",
            
            # TOUTES les notifications
            "notif_app",
            "notif_email",
            "notif_telegram",
            "notif_discord",
            "notif_sms",
            "notif_slack",
            "notif_teams",
            "notif_webhook",
            
            # Enregistrement complet
            "recording_alert",
            "recording_preevent",
            "recording_continuous",
            
            # Tous les rapports
            "report_daily",
            "report_weekly",
            "report_monthly",
            "report_custom",
            "report_compliance",
            
            # Intégrations avancées
            "integration_onvif",
            "integration_rtsp",
            "integration_api",
            "integration_access",
            
            # Support avancé
            "support_community",
            "support_email",
            "support_priority",
            "support_phone"
        ],
        badge="Recommandé entreprises"
    ),
    
    PlanType.ENTERPRISE: Plan(
        id=PlanType.ENTERPRISE,
        name="ENTERPRISE",
        description="Solution sur mesure pour les grandes organisations",
        price_monthly=0,  # Sur devis
        price_yearly=0,   # Sur devis
        price_one_time=None,
        limits=PlanLimit(
            max_cameras=9999,  # Illimité
            max_users=9999,
            retention_days=365,
            max_alerts_per_day=999999,
            max_recordings_gb=9999,
            api_calls_per_day=999999
        ),
        features=[
            # TOUT est inclus
            *list(FEATURES.keys())
        ],
        badge="Sur devis"
    ),
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_plan(plan_type: PlanType) -> Plan:
    """Récupère un plan par son type"""
    return PLANS.get(plan_type)


def get_plan_features(plan_type: PlanType) -> List[Feature]:
    """Récupère les fonctionnalités d'un plan"""
    plan = PLANS.get(plan_type)
    if not plan:
        return []
    
    return [FEATURES[f_id] for f_id in plan.features if f_id in FEATURES]


def check_feature_access(plan_type: PlanType, feature_id: str) -> bool:
    """Vérifie si un plan a accès à une fonctionnalité"""
    plan = PLANS.get(plan_type)
    if not plan:
        return False
    
    return feature_id in plan.features


def get_feature_category(category: str) -> List[Feature]:
    """Récupère toutes les fonctionnalités d'une catégorie"""
    return [f for f in FEATURES.values() if f.category == category]


def compare_plans() -> Dict:
    """Compare tous les plans"""
    comparison = {}
    
    for plan_type, plan in PLANS.items():
        comparison[plan_type.value] = {
            "name": plan.name,
            "price": {
                "monthly": plan.price_monthly,
                "yearly": plan.price_yearly,
                "one_time": plan.price_one_time
            },
            "limits": {
                "cameras": plan.limits.max_cameras,
                "users": plan.limits.max_users,
                "retention": f"{plan.limits.retention_days} jours",
                "storage": f"{plan.limits.max_recordings_gb} GB"
            },
            "features_count": len(plan.features),
            "badge": plan.badge
        }
    
    return comparison


def get_pricing_table() -> List[Dict]:
    """Génère le tableau de pricing pour l'affichage"""
    return [
        {
            "plan": plan.name,
            "description": plan.description,
            "price": f"{plan.price_one_time}€" if plan.price_one_time else 
                     f"{plan.price_yearly}€/an" if plan.price_yearly > 0 else "Sur devis",
            "monthly_equivalent": f"{plan.price_monthly}€/mois" if plan.price_monthly > 0 else "-",
            "cameras": f"1-{plan.limits.max_cameras}" if plan.limits.max_cameras < 9999 else "Illimité",
            "is_popular": plan.is_popular,
            "badge": plan.badge,
            "features_highlight": plan.features[:5]  # Top 5 features
        }
        for plan in PLANS.values()
    ]


# ============================================================================
# ADDONS / OPTIONS SUPPLÉMENTAIRES
# ============================================================================

ADDONS = {
    "thermal_camera_support": {
        "name": "Support Caméras Thermiques",
        "description": "Active la détection par caméra thermique (FLIR, Hikvision Thermal, etc.)",
        "price_monthly": 15,
        "price_yearly": 150,
        "compatible_plans": [PlanType.PRO, PlanType.BUSINESS, PlanType.ENTERPRISE],
        "features_added": ["detection_fire_thermal", "detection_thermal_rate"]
    },
    "lpr_addon": {
        "name": "Module LPR Avancé",
        "description": "Reconnaissance de plaques avec VIP/Blacklist et historique complet",
        "price_monthly": 10,
        "price_yearly": 99,
        "compatible_plans": [PlanType.PRO, PlanType.BUSINESS, PlanType.ENTERPRISE],
        "features_added": ["detection_lpr"]
    },
    "cloud_storage_50gb": {
        "name": "Stockage Cloud +50GB",
        "description": "Espace de stockage cloud supplémentaire",
        "price_monthly": 5,
        "price_yearly": 49,
        "compatible_plans": [PlanType.HOME, PlanType.PRO, PlanType.BUSINESS],
        "features_added": ["recording_cloud"]
    },
    "sms_pack_100": {
        "name": "Pack 100 SMS",
        "description": "100 SMS d'alerte par mois",
        "price_monthly": 5,
        "price_yearly": 49,
        "compatible_plans": [PlanType.PRO, PlanType.BUSINESS, PlanType.ENTERPRISE],
        "features_added": ["notif_sms"]
    },
    "vms_integration": {
        "name": "Intégration VMS",
        "description": "Plugin pour Milestone, Genetec, ou autre VMS",
        "price_monthly": 25,
        "price_yearly": 249,
        "compatible_plans": [PlanType.BUSINESS, PlanType.ENTERPRISE],
        "features_added": ["integration_vms"]
    },
    "multisite": {
        "name": "Multi-sites",
        "description": "Gestion de plusieurs sites depuis une seule interface",
        "price_monthly": 20,
        "price_yearly": 199,
        "compatible_plans": [PlanType.BUSINESS, PlanType.ENTERPRISE],
        "features_added": []
    }
}
