#!/bin/bash

# OhmVision Platform - Installation Script (Development)
# ======================================================

set -e  # Exit on error

echo "🚀 Installation OhmVision Platform (Development)"
echo "=================================================="

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo -e "${GREEN}✓${NC} OS détecté: ${MACHINE}"

# =============================================================================
# 1. VÉRIFICATIONS PRÉ-REQUIS
# =============================================================================

echo ""
echo "📋 Vérification des pré-requis..."

# Python 3.11+
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} installé"
else
    echo -e "${RED}✗${NC} Python 3.11+ requis"
    echo "   Installation: brew install python@3.11 (Mac) ou apt install python3.11 (Linux)"
    exit 1
fi

# Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo -e "${GREEN}✓${NC} Docker ${DOCKER_VERSION} installé"
else
    echo -e "${YELLOW}⚠${NC}  Docker non installé (optionnel mais recommandé)"
    echo "   Installation: https://docs.docker.com/get-docker/"
fi

# Node.js (pour frontend)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js ${NODE_VERSION} installé"
else
    echo -e "${YELLOW}⚠${NC}  Node.js non installé (requis pour frontend)"
    echo "   Installation: https://nodejs.org/"
fi

# =============================================================================
# 2. CONFIGURATION ENVIRONNEMENT
# =============================================================================

echo ""
echo "⚙️  Configuration de l'environnement..."

# Copier .env.example vers .env si n'existe pas
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Fichier .env créé (à personnaliser)"
else
    echo -e "${YELLOW}⚠${NC}  Fichier .env existe déjà"
fi

# =============================================================================
# 3. INSTALLATION BACKEND
# =============================================================================

echo ""
echo "🐍 Installation du backend Python..."

cd backend

# Créer environnement virtuel si n'existe pas
if [ ! -d "venv" ]; then
    echo "   Création environnement virtuel..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Environnement virtuel créé"
else
    echo -e "${YELLOW}⚠${NC}  Environnement virtuel existe déjà"
fi

# Activer environnement virtuel
source venv/bin/activate

# Installer dépendances
echo "   Installation des dépendances Python..."
pip install --upgrade pip setuptools wheel > /dev/null
pip install -r requirements.txt

echo -e "${GREEN}✓${NC} Dépendances backend installées"

cd ..

# =============================================================================
# 4. INSTALLATION FRONTEND
# =============================================================================

if command -v node &> /dev/null; then
    echo ""
    echo "⚛️  Installation du frontend React..."
    
    cd frontend-client
    
    if [ ! -d "node_modules" ]; then
        npm install
        echo -e "${GREEN}✓${NC} Dépendances frontend installées"
    else
        echo -e "${YELLOW}⚠${NC}  node_modules existe déjà (lancez 'npm install' pour mettre à jour)"
    fi
    
    cd ..
fi

# =============================================================================
# 5. DOCKER (OPTIONNEL)
# =============================================================================

if command -v docker &> /dev/null; then
    echo ""
    echo "🐳 Configuration Docker..."
    
    # Vérifier si docker-compose est installé
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker Compose disponible"
        
        read -p "Démarrer PostgreSQL et Redis avec Docker ? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose up -d postgres redis
            echo -e "${GREEN}✓${NC} PostgreSQL et Redis démarrés"
            echo "   PostgreSQL: localhost:5432"
            echo "   Redis: localhost:6379"
            
            # Attendre que PostgreSQL soit prêt
            echo "   Attente démarrage PostgreSQL..."
            sleep 5
        fi
    fi
fi

# =============================================================================
# 6. INITIALISATION BASE DE DONNÉES
# =============================================================================

echo ""
echo "💾 Initialisation de la base de données..."

# Vérifier si PostgreSQL est accessible
if command -v psql &> /dev/null || docker ps | grep -q ohmvision-db; then
    cd backend
    source venv/bin/activate
    
    # Exécuter init_db.py
    python init_db.py
    
    echo -e "${GREEN}✓${NC} Base de données initialisée"
    cd ..
else
    echo -e "${YELLOW}⚠${NC}  PostgreSQL non accessible, skip initialisation DB"
    echo "   Lancez manuellement: cd backend && python init_db.py"
fi

# =============================================================================
# 7. TESTS
# =============================================================================

echo ""
echo "🧪 Exécution des tests..."

cd backend
source venv/bin/activate

# Lancer tests rapides (sans slow)
pytest tests/test_suite.py -v -m "not slow" --tb=short || true

cd ..

# =============================================================================
# 8. RÉSUMÉ
# =============================================================================

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Installation terminée !${NC}"
echo "=================================================="
echo ""
echo "📚 Prochaines étapes:"
echo ""
echo "1. Personnaliser le fichier .env avec vos paramètres"
echo ""
echo "2. Démarrer le backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload"
echo "   → API: http://localhost:8000"
echo "   → Docs: http://localhost:8000/docs"
echo ""
echo "3. Démarrer le frontend:"
echo "   cd frontend-client"
echo "   npm run dev"
echo "   → App: http://localhost:5173"
echo ""
echo "4. Tester avec une caméra ONVIF:"
echo "   - Accéder à http://localhost:5173"
echo "   - Suivre le Setup Wizard"
echo "   - Scanner le réseau pour découvrir les caméras"
echo ""
echo "📖 Documentation complète: PLAN_ACTION.md"
echo ""
