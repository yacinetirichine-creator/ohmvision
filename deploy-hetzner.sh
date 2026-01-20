#!/bin/bash

###############################################################################
# OHMVISION - HETZNER CLOUD DEPLOYMENT SCRIPT
# Déploiement automatisé sur VPS Hetzner avec Docker
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
echo -e "${BLUE}"
cat << "EOF"
   ____  _   ____  ____     _______  _____ ___  _   __
  / __ \/ | / /  |/  / |   / /  _/ |/ / _ | _ \/ | / /
 / /_/ /  |/ / /|_/ /| |  / // //    / __ |  _/  |/ / 
 \____/_/|_/_/  /_/ |_|__/_/___/_/|_/_/ |_|_| /_/|_/  
                   |_____|                             
  HETZNER CLOUD DEPLOYMENT
EOF
echo -e "${NC}"

###############################################################################
# VARIABLES
###############################################################################

DOMAIN=""
EMAIL=""
SSH_KEY=""
SERVER_IP=""

###############################################################################
# FUNCTIONS
###############################################################################

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_requirements() {
    print_info "Vérification des prérequis..."
    
    if ! command -v ssh &> /dev/null; then
        print_error "SSH n'est pas installé"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git n'est pas installé"
        exit 1
    fi
    
    print_success "Prérequis validés"
}

get_user_input() {
    echo ""
    print_info "Configuration du déploiement"
    echo ""
    
    read -p "Adresse IP du serveur Hetzner: " SERVER_IP
    read -p "Votre nom de domaine (ex: ohmvision.com): " DOMAIN
    read -p "Votre email (pour SSL): " EMAIL
    read -p "Chemin vers votre clé SSH privée (défaut: ~/.ssh/id_rsa): " SSH_KEY
    SSH_KEY=${SSH_KEY:-~/.ssh/id_rsa}
    
    echo ""
    print_info "Récapitulatif:"
    echo "  Serveur: $SERVER_IP"
    echo "  Domaine: $DOMAIN"
    echo "  Email: $EMAIL"
    echo "  Clé SSH: $SSH_KEY"
    echo ""
    
    read -p "Confirmer le déploiement? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        print_warning "Déploiement annulé"
        exit 0
    fi
}

prepare_server() {
    print_info "Préparation du serveur Hetzner..."
    
    # Update and install dependencies
    ssh -i "$SSH_KEY" root@"$SERVER_IP" << 'ENDSSH'
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install other dependencies
apt-get install -y git curl wget ufw fail2ban htop

# Configure firewall
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Create app directory
mkdir -p /opt/ohmvision
chown -R root:root /opt/ohmvision

# Enable Docker service
systemctl enable docker
systemctl start docker

echo "Server preparation completed!"
ENDSSH
    
    print_success "Serveur préparé avec Docker et dépendances"
}

deploy_application() {
    print_info "Déploiement de l'application..."
    
    # Clone repository
    ssh -i "$SSH_KEY" root@"$SERVER_IP" << ENDSSH
set -e

cd /opt/ohmvision

# Clone or update repository
if [ -d ".git" ]; then
    git pull origin master
else
    git clone https://github.com/yacinetirichine-creator/ohmvision.git .
fi

# Create .env file
cat > .env << EOF
DOMAIN=$DOMAIN
BACKEND_URL=https://$DOMAIN
FRONTEND_URL=https://$DOMAIN

POSTGRES_DB=ohmvision
POSTGRES_USER=ohmvision
POSTGRES_PASSWORD=$(openssl rand -base64 32)

REDIS_PASSWORD=$(openssl rand -base64 32)

SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)

WORKERS=4
FFMPEG_THREADS=2

CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
EOF

# Update Nginx config with actual domain
sed -i "s/DOMAIN/$DOMAIN/g" docker/nginx-production.conf

# Create required directories
mkdir -p uploads logs logs/nginx docker/ssl

# Set permissions
chmod 600 .env
chmod -R 755 uploads logs

echo "Application deployed!"
ENDSSH
    
    print_success "Application déployée"
}

setup_ssl() {
    print_info "Configuration SSL avec Let's Encrypt..."
    
    ssh -i "$SSH_KEY" root@"$SERVER_IP" << ENDSSH
set -e

cd /opt/ohmvision

# Start only Nginx and Certbot first
docker-compose -f docker-compose.production.yml up -d nginx certbot

# Wait for Nginx
sleep 10

# Obtain SSL certificate
docker-compose -f docker-compose.production.yml exec -T certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Reload Nginx with SSL
docker-compose -f docker-compose.production.yml restart nginx

echo "SSL configured!"
ENDSSH
    
    print_success "SSL configuré avec Let's Encrypt"
}

start_services() {
    print_info "Démarrage des services..."
    
    ssh -i "$SSH_KEY" root@"$SERVER_IP" << 'ENDSSH'
set -e

cd /opt/ohmvision

# Build and start all services
docker-compose -f docker-compose.production.yml up -d --build

# Wait for services to be healthy
sleep 30

# Check service status
docker-compose -f docker-compose.production.yml ps

echo "Services started!"
ENDSSH
    
    print_success "Tous les services sont démarrés"
}

verify_deployment() {
    print_info "Vérification du déploiement..."
    
    # Test health endpoint
    if curl -f -k "https://$DOMAIN/health" &> /dev/null; then
        print_success "Health check OK"
    else
        print_warning "Health check échoué, vérifier les logs"
    fi
    
    # Show service status
    ssh -i "$SSH_KEY" root@"$SERVER_IP" "cd /opt/ohmvision && docker-compose -f docker-compose.production.yml ps"
}

show_next_steps() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          DÉPLOIEMENT TERMINÉ AVEC SUCCÈS! 🚀              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_info "Votre application est accessible à:"
    echo -e "  ${BLUE}https://$DOMAIN${NC}"
    echo ""
    print_info "Prochaines étapes:"
    echo "  1. Configurer DNS: Pointer $DOMAIN vers $SERVER_IP"
    echo "  2. Accéder à l'application et créer le compte admin"
    echo "  3. Configurer SMTP dans .env pour les emails"
    echo "  4. Configurer Stripe pour les paiements"
    echo ""
    print_info "Commandes utiles:"
    echo "  • Logs: ssh root@$SERVER_IP 'cd /opt/ohmvision && docker-compose -f docker-compose.production.yml logs -f'"
    echo "  • Restart: ssh root@$SERVER_IP 'cd /opt/ohmvision && docker-compose -f docker-compose.production.yml restart'"
    echo "  • Status: ssh root@$SERVER_IP 'cd /opt/ohmvision && docker-compose -f docker-compose.production.yml ps'"
    echo ""
    print_warning "N'oubliez pas de:"
    echo "  • Sauvegarder le fichier .env depuis le serveur"
    echo "  • Configurer les backups PostgreSQL automatiques"
    echo "  • Surveiller les ressources avec 'htop'"
    echo ""
}

###############################################################################
# MAIN EXECUTION
###############################################################################

main() {
    clear
    
    print_info "Déploiement OhmVision sur Hetzner Cloud"
    echo ""
    
    check_requirements
    get_user_input
    
    echo ""
    print_info "Début du déploiement..."
    echo ""
    
    prepare_server
    deploy_application
    setup_ssl
    start_services
    verify_deployment
    
    show_next_steps
}

# Run main function
main
