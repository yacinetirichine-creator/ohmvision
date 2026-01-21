#!/bin/bash
#================================================================
# 🎯 OHMVISION - SCRIPT DE CONFIGURATION SIMPLIFIÉ
# Pour novices - Usage: ./setup-simple.sh [local|deploy IP]
#================================================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logo
show_logo() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════╗"
    echo "║   🎥 OHMVISION - Configuration Simple     ║"
    echo "║   Plateforme IA Vidéosurveillance         ║"
    echo "╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Messages
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# Vérifications
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker n'est pas installé. Installe Docker Desktop: https://docker.com/products/docker-desktop"
    fi
    if ! docker info &> /dev/null; then
        error "Docker n'est pas démarré. Lance Docker Desktop d'abord."
    fi
    success "Docker est prêt"
}

# Générer des secrets sécurisés
generate_secret() {
    openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1
}

# Configuration LOCAL
setup_local() {
    info "Configuration pour développement LOCAL..."
    
    # Créer .env à la racine
    cat > .env << 'EOF'
# ============================================
# OhmVision - Configuration Locale
# ============================================

# Application
APP_NAME=OhmVision
DEBUG=true

# Secrets (générés automatiquement)
EOF
    echo "SECRET_KEY=$(generate_secret)" >> .env
    echo "JWT_SECRET_KEY=$(generate_secret)" >> .env
    
    cat >> .env << 'EOF'

# Database (Docker PostgreSQL local)
DB_PASSWORD=ohmvision_local_2026
DATABASE_URL=postgresql+asyncpg://ohmvision:ohmvision_local_2026@postgres:5432/ohmvision

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000

# IA (optionnel - ajoute tes clés si tu en as)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Stripe (optionnel - mode test)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
EOF
    
    # Copier aussi dans backend/
    cp .env backend/.env
    
    success "Fichier .env créé !"
    
    echo ""
    info "Maintenant, lance les services avec :"
    echo -e "${CYAN}  docker compose up -d${NC}"
    echo ""
    info "Puis ouvre : ${GREEN}http://localhost:8000${NC}"
}

# Configuration PRODUCTION (Hetzner)
setup_production() {
    local SERVER_IP=$1
    
    if [ -z "$SERVER_IP" ]; then
        error "Usage: ./setup-simple.sh deploy IP_DU_SERVEUR"
    fi
    
    info "Déploiement sur Hetzner: $SERVER_IP"
    
    # Tester la connexion SSH
    info "Test de connexion SSH..."
    if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$SERVER_IP "echo 'OK'" 2>/dev/null; then
        error "Impossible de se connecter au serveur. Vérifie ton IP et ta clé SSH."
    fi
    success "Connexion SSH OK"
    
    # Générer les secrets
    local SECRET_KEY=$(generate_secret)
    local JWT_SECRET=$(generate_secret)
    local DB_PASSWORD="OhmVision$(generate_secret | head -c 16)"
    local REDIS_PASSWORD="Redis$(generate_secret | head -c 16)"
    
    # Créer le fichier .env pour production
    cat > .env.production << EOF
# ============================================
# OhmVision - Production Hetzner
# Serveur: $SERVER_IP
# Généré le: $(date)
# ============================================

# Application
APP_NAME=OhmVision
APP_ENV=production
DEBUG=false

# URLs
DOMAIN=$SERVER_IP
BACKEND_URL=http://$SERVER_IP
FRONTEND_URL=http://$SERVER_IP

# Secrets
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET

# Database
POSTGRES_DB=ohmvision
POSTGRES_USER=ohmvision
POSTGRES_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql+asyncpg://ohmvision:$DB_PASSWORD@postgres:5432/ohmvision

# Redis
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0

# CORS (accepte tout pour commencer)
CORS_ORIGINS=*

# IA (optionnel)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Stripe (optionnel)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Storage
STORAGE_PATH=/opt/ohmvision/storage
EOF
    
    success "Configuration production générée"
    
    # Installer Docker sur le serveur
    info "Installation de Docker sur le serveur (2-3 min)..."
    ssh root@$SERVER_IP << 'INSTALL_DOCKER'
set -e
apt-get update -qq
apt-get install -y -qq ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update -qq
apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable docker
systemctl start docker
INSTALL_DOCKER
    success "Docker installé"
    
    # Créer le répertoire sur le serveur
    info "Copie des fichiers..."
    ssh root@$SERVER_IP "mkdir -p /opt/ohmvision"
    
    # Copier les fichiers
    rsync -avz --progress \
        --exclude 'node_modules' \
        --exclude '.git' \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.env' \
        ./ root@$SERVER_IP:/opt/ohmvision/
    
    # Copier la config production
    scp .env.production root@$SERVER_IP:/opt/ohmvision/.env
    scp .env.production root@$SERVER_IP:/opt/ohmvision/backend/.env
    
    success "Fichiers copiés"
    
    # Lancer les services
    info "Démarrage des services (5-8 min)..."
    ssh root@$SERVER_IP << 'START_SERVICES'
cd /opt/ohmvision
docker compose pull
docker compose up -d --build
echo "Attente du démarrage..."
sleep 30
docker compose ps
START_SERVICES
    
    success "Services démarrés !"
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !    ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "🌐 Ton application est accessible sur :"
    echo -e "   ${CYAN}http://$SERVER_IP${NC}"
    echo ""
    echo -e "📖 Documentation API :"
    echo -e "   ${CYAN}http://$SERVER_IP/docs${NC}"
    echo ""
    echo -e "🔧 Commandes utiles (sur le serveur) :"
    echo -e "   ${YELLOW}ssh root@$SERVER_IP${NC}"
    echo -e "   ${YELLOW}cd /opt/ohmvision && docker compose logs -f${NC}"
    echo ""
}

# Afficher l'aide
show_help() {
    echo "Usage: ./setup-simple.sh [COMMANDE]"
    echo ""
    echo "Commandes:"
    echo "  local          Configure pour développement local"
    echo "  deploy IP      Déploie sur un serveur Hetzner"
    echo "  help           Affiche cette aide"
    echo ""
    echo "Exemples:"
    echo "  ./setup-simple.sh local"
    echo "  ./setup-simple.sh deploy 195.201.123.92"
}

# Main
show_logo

case "${1:-help}" in
    local)
        check_docker
        setup_local
        ;;
    deploy)
        check_docker
        setup_production "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Commande inconnue: $1. Utilise './setup-simple.sh help'"
        ;;
esac
