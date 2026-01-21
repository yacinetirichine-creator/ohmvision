#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# OhmVision - Script de déploiement Railway
# Usage: ./deploy-railway.sh
# ═══════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Functions
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# Banner
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   🚀 OhmVision - Déploiement Railway                          ║"
echo "║   Production Ready • Scalable • Zero DevOps                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    warning "Railway CLI n'est pas installé"
    info "Installation de Railway CLI..."
    
    # Try npm first
    if command -v npm &> /dev/null; then
        npm install -g @railway/cli
    # Try curl
    elif command -v curl &> /dev/null; then
        curl -fsSL https://railway.app/install.sh | sh
    else
        error "Veuillez installer Railway CLI: npm install -g @railway/cli"
    fi
fi

success "Railway CLI installé"

# Check if logged in
info "Vérification de la connexion Railway..."
if ! railway whoami &> /dev/null; then
    warning "Vous n'êtes pas connecté à Railway"
    info "Ouverture du navigateur pour connexion..."
    railway login
fi

success "Connecté à Railway"

# Generate secrets if needed
generate_secret() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
    openssl rand -base64 32 | tr -d '/+=' | head -c 32
}

# Menu
echo ""
echo "Que souhaitez-vous faire ?"
echo ""
echo "  1) 🆕 Créer un nouveau projet Railway"
echo "  2) 🔗 Lier à un projet existant"
echo "  3) 🚀 Déployer maintenant"
echo "  4) 📊 Voir les logs"
echo "  5) ⚙️  Configurer les variables d'environnement"
echo "  6) 🌐 Configurer le domaine personnalisé"
echo "  7) ❌ Quitter"
echo ""
read -p "Votre choix [1-7]: " choice

case $choice in
    1)
        info "Création d'un nouveau projet Railway..."
        railway init
        
        echo ""
        info "Ajout de PostgreSQL..."
        echo "Dans le dashboard Railway, cliquez sur '+ New' puis 'Database' → 'PostgreSQL'"
        echo ""
        info "Ajout de Redis..."
        echo "Dans le dashboard Railway, cliquez sur '+ New' puis 'Database' → 'Redis'"
        echo ""
        
        # Generate secrets
        SECRET_KEY=$(generate_secret)
        JWT_SECRET=$(generate_secret)
        
        success "Projet créé!"
        echo ""
        echo -e "${YELLOW}Variables d'environnement à configurer dans Railway:${NC}"
        echo ""
        echo "SECRET_KEY=$SECRET_KEY"
        echo "JWT_SECRET_KEY=$JWT_SECRET"
        echo "DEBUG=false"
        echo "ENVIRONMENT=production"
        echo "PYTHONUNBUFFERED=1"
        echo "CORS_ORIGINS=https://votre-frontend.vercel.app"
        echo ""
        
        read -p "Ouvrir le dashboard Railway ? [O/n]: " open_dash
        if [[ "$open_dash" != "n" ]]; then
            railway open
        fi
        ;;
        
    2)
        info "Liaison à un projet existant..."
        railway link
        success "Projet lié!"
        ;;
        
    3)
        info "Déploiement en cours..."
        railway up --detach
        
        echo ""
        success "Déploiement lancé!"
        echo ""
        info "Suivez le déploiement avec: railway logs -f"
        
        read -p "Voir les logs maintenant ? [O/n]: " view_logs
        if [[ "$view_logs" != "n" ]]; then
            railway logs -f
        fi
        ;;
        
    4)
        info "Affichage des logs..."
        railway logs -f
        ;;
        
    5)
        info "Configuration des variables d'environnement..."
        echo ""
        
        # Generate secrets
        SECRET_KEY=$(generate_secret)
        JWT_SECRET=$(generate_secret)
        
        echo "Variables générées:"
        echo ""
        echo "SECRET_KEY=$SECRET_KEY"
        echo "JWT_SECRET_KEY=$JWT_SECRET"
        echo ""
        
        read -p "Configurer automatiquement ces variables ? [O/n]: " auto_config
        if [[ "$auto_config" != "n" ]]; then
            railway variables set SECRET_KEY="$SECRET_KEY"
            railway variables set JWT_SECRET_KEY="$JWT_SECRET"
            railway variables set DEBUG="false"
            railway variables set ENVIRONMENT="production"
            railway variables set PYTHONUNBUFFERED="1"
            success "Variables configurées!"
        fi
        
        echo ""
        warning "N'oubliez pas de configurer également:"
        echo "  - DATABASE_URL (depuis PostgreSQL Railway)"
        echo "  - REDIS_URL (depuis Redis Railway)"
        echo "  - CORS_ORIGINS (URL de votre frontend)"
        echo "  - ANTHROPIC_API_KEY (optionnel)"
        echo "  - STRIPE_SECRET_KEY (optionnel)"
        echo ""
        
        read -p "Ouvrir le dashboard pour finir la configuration ? [O/n]: " open_dash
        if [[ "$open_dash" != "n" ]]; then
            railway open
        fi
        ;;
        
    6)
        info "Configuration du domaine personnalisé..."
        echo ""
        read -p "Entrez votre domaine (ex: api.ohmvision.fr): " domain
        
        if [[ -n "$domain" ]]; then
            railway domain "$domain"
            success "Domaine configuré: $domain"
            echo ""
            warning "Configurez votre DNS avec l'enregistrement CNAME affiché ci-dessus"
        else
            warning "Aucun domaine spécifié"
        fi
        ;;
        
    7)
        info "Au revoir!"
        exit 0
        ;;
        
    *)
        error "Choix invalide"
        ;;
esac

echo ""
success "Terminé!"
echo ""
echo "Commandes utiles:"
echo "  railway logs -f     # Voir les logs"
echo "  railway status      # Status du projet"
echo "  railway open        # Ouvrir le dashboard"
echo "  railway up          # Déployer"
echo ""
