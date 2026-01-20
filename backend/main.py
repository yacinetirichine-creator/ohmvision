"""
OhmVision Platform - Backend API
================================
API REST complète pour la plateforme OhmVision
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from core.database import engine, Base
from api import auth, users, clients, contracts, cameras, alerts, analytics, ai_agent, billing, admin
from api.discovery import router as discovery_router
from api.setup import router as setup_router
from api.streaming import router as streaming_router
from api.advanced_analytics import router as advanced_router
from api.health import router as health_router
from api import gdpr
from services.health_check_service import start_health_check_service, stop_health_check_service

# Lifespan pour init/cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage OhmVision API...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Base de données initialisée")
    
    # Démarrer le service de health check
    print("🏥 Démarrage du service Health Check...")
    await start_health_check_service()
    print("✅ Service Health Check démarré")
    
    yield
    
    # Shutdown
    print("🏥 Arrêt du service Health Check...")
    await stop_health_check_service()
    print("👋 Arrêt OhmVision API...")

# Application FastAPI
app = FastAPI(
    title="OhmVision API",
    description="API de la plateforme d'analyse vidéo intelligente OhmVision",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )

# Routes API
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(users.router, prefix="/api/users", tags=["Utilisateurs"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["Contrats"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["Caméras"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alertes"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ai_agent.router, prefix="/api/ai", tags=["Agent IA"])
app.include_router(billing.router, prefix="/api/billing", tags=["Facturation"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])
app.include_router(gdpr.router)  # Déjà préfixé /api/gdpr
app.include_router(discovery_router)  # Déjà préfixé /api/discovery
app.include_router(setup_router)  # Déjà préfixé /api/setup
app.include_router(streaming_router)  # Déjà préfixé /api/streaming
app.include_router(advanced_router)  # Déjà préfixé /api/advanced
app.include_router(health_router)  # Déjà préfixé /api/health

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "OhmVision API"
    }

# Root
@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API OhmVision",
        "docs": "/docs",
        "version": "1.0.0"
    }

# Serve static files (Frontend) - pour le mode all-in-one
import os
if os.path.exists("/app/static"):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    # Serve static assets
    app.mount("/assets", StaticFiles(directory="/app/static/assets"), name="assets")
    
    # Catch-all pour SPA - doit être en dernier
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Si c'est une route API, laisser passer
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
            return {"detail": "Not found"}
        # Sinon servir index.html pour le SPA
        return FileResponse("/app/static/index.html")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
