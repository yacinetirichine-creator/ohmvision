#!/bin/bash
#================================================================
# 🎯 OHMVISION - SCRIPT DE CONFIGURATION SIMPLIFIÉ
# Pour novices - Usage: ./setup-simple.sh [local|railway]
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
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
    openssl rand -base64 32 | tr -d '/+=' | head -c 32 || \
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
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
ENVIRONMENT=development

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

# Configuration RAILWAY
setup_railway() {
    info "Préparation pour déploiement Railway..."
    
    # Vérifier si Railway CLI est installé
    if ! command -v railway &> /dev/null; then
        warning "Railway CLI n'est pas installé"
        info "Installation..."
        npm install -g @railway/cli 2>/dev/null || {
            error "Impossible d'installer Railway CLI. Installe npm d'abord."
        }
    fi
    success "Railway CLI installé"
    
    # Générer les secrets
    local SECRET_KEY=$(generate_secret)
    local JWT_SECRET=$(generate_secret)
    
    # Créer un fichier de référence pour Railway
    cat > .env.railway.generated << EOF
# ============================================
# OhmVision - Variables pour Railway
# Généré le: $(date)
# ============================================
# Copiez ces valeurs dans Railway Dashboard → Variables

SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
DEBUG=false
ENVIRONMENT=production
PYTHONUNBUFFERED=1

# CORS - Ajoutez votre URL frontend Vercel
CORS_ORIGINS=https://votre-app.vercel.app,http://localhost:3000

# Ces variables sont auto-générées par Railway:
# DATABASE_URL=\${{Postgres.DATABASE_URL}}
# REDIS_URL=\${{Redis.REDIS_URL}}
EOF
    
    success "Fichier .env.railway.generated créé avec vos clés secrètes"
    
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Clés secrètes générées :${NC}"
    echo ""
    echo -e "  SECRET_KEY=${YELLOW}$SECRET_KEY${NC}"
    echo -e "  JWT_SECRET_KEY=${YELLOW}$JWT_SECRET${NC}"
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    read -p "Voulez-vous vous connecter à Railway maintenant ? [O/n]: " connect
    if [[ "$connect" != "n" && "$connect" != "N" ]]; then
        railway login
        
        echo ""
        read -p "Créer un nouveau projet Railway ? [O/n]: " create
        if [[ "$create" != "n" && "$create" != "N" ]]; then
            railway init
            
            echo ""
            info "Projet créé ! Maintenant :"
            echo ""
            echo "  1. Allez sur https://railway.app/dashboard"
            echo "  2. Cliquez sur votre projet"
            echo "  3. Ajoutez PostgreSQL : + New → Database → PostgreSQL"
            echo "  4. Ajoutez Redis : + New → Database → Redis"
            echo "  5. Configurez les Variables avec les clés ci-dessus"
            echo ""
            
            read -p "Déployer maintenant ? [O/n]: " deploy
            if [[ "$deploy" != "n" && "$deploy" != "N" ]]; then
                railway up --detach
                success "Déploiement lancé !"
                echo ""
                info "Suivez les logs avec : railway logs -f"
            fi
        fi
    fi
    
    echo ""
    success "Configuration Railway terminée !"
    echo ""
    info "Documentation complète : DEPLOYMENT_RAILWAY_COMPLETE.md"
}

# Menu principal
show_menu() {
    show_logo
    echo ""
    echo "Que souhaitez-vous faire ?"
    echo ""
    echo "  1) 🏠 Configuration LOCAL (Docker sur ton PC)"
    echo "  2) 🚀 Déploiement RAILWAY (Production cloud)"
    echo "  3) ❌ Quitter"
    echo ""
    read -p "Votre choix [1-3]: " choice
    
    case $choice in
        1)
            check_docker
            setup_local
            ;;
        2)
            setup_railway
            ;;
        3)
            info "Au revoir !"
            exit 0
            ;;
        *)
            error "Choix invalide"
            ;;
    esac
}

# Point d'entrée
case "${1:-}" in
    local)
        show_logo
        check_docker
        setup_local
        ;;
    railway)
        show_logo
        setup_railway
        ;;
    *)
        show_menu
        ;;
esac
