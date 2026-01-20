"""
OhmVision - Configuration
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "OhmVision"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "ohmvision-super-secret-key-change-in-production"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # Database - Automatique depuis variable d'environnement
    # Local: SQLite / Production: Supabase PostgreSQL depuis RAILWAY
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./ohmvision.db"  # Fallback pour développement local
    )
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 heures
    
    # CORS - Accepte soit une liste JSON soit une chaîne séparée par des virgules
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:8080"

    # Optionnel: regex d'origines autorisées (utile pour les URLs preview Vercel)
    # Exemple: https://.*\\.vercel\\.app$
    CORS_ORIGIN_REGEX: Optional[str] = None
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS correctement depuis .env"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@ohmvision.fr"
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # AI / LLM
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    
    # Packages & Pricing
    PACKAGES: dict = {
        "starter": {
            "name": "Starter",
            "price_monthly": 49,
            "price_yearly": 490,
            "max_cameras": 4,
            "features": ["person_detection", "counting_basic", "alerts_email"],
            "ai_agent": False,
            "api_access": False,
            "history_days": 7
        },
        "business": {
            "name": "Business",
            "price_monthly": 149,
            "price_yearly": 1490,
            "max_cameras": 20,
            "features": ["person_detection", "counting", "fall_detection", "ppe_detection", "alerts_all", "reports"],
            "ai_agent": True,
            "api_access": False,
            "history_days": 30
        },
        "enterprise": {
            "name": "Enterprise",
            "price_monthly": 499,
            "price_yearly": 4990,
            "max_cameras": -1,  # Illimité
            "features": ["all", "fire_detection", "lpr", "multi_site", "on_premise"],
            "ai_agent": True,
            "api_access": True,
            "history_days": 365
        },
        "platinum": {
            "name": "Platinum",
            "price_monthly": 1499,
            "price_yearly": 14990,
            "max_cameras": -1,
            "features": ["all", "custom_models", "sla_247", "dedicated_support", "custom_integrations"],
            "ai_agent": True,
            "api_access": True,
            "history_days": -1  # Illimité
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorer les champs supplémentaires du .env

settings = Settings()
