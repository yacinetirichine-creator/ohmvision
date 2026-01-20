#!/bin/bash

# OhmVision - Hetzner backend-only deploy (for Vercel frontend)
# - Deploys backend + postgres + redis + nginx + certbot
# - Exposes API over https://api.your-domain

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { print_error "Commande manquante: $1"; exit 1; }
}

require_cmd ssh
require_cmd git

SERVER_IP=""
SSH_KEY=""
API_DOMAIN=""
EMAIL=""
FRONTEND_URL=""
CORS_ORIGINS=""
CORS_ORIGIN_REGEX=""

print_info "Configuration Hetzner (backend-only)"
read -r -p "IP du serveur Hetzner: " SERVER_IP
read -r -p "Domaine API (ex: api.ohmvision.com): " API_DOMAIN
read -r -p "Email (Let's Encrypt): " EMAIL
read -r -p "URL Frontend (ex: https://ohmvision.vercel.app ou https://ohmvision.com): " FRONTEND_URL
read -r -p "Clé SSH (défaut: ~/.ssh/id_rsa): " SSH_KEY
SSH_KEY=${SSH_KEY:-~/.ssh/id_rsa}

print_info "CORS: ajoute ton domaine Vercel + domaine prod."
read -r -p "CORS_ORIGINS (ex: https://ohmvision.vercel.app,https://ohmvision.com): " CORS_ORIGINS
read -r -p "CORS_ORIGIN_REGEX optionnel (ex: https://.*\\.vercel\\.app$) [laisser vide si non]: " CORS_ORIGIN_REGEX

echo ""
print_info "Récapitulatif"
echo "  Server:     $SERVER_IP"
echo "  API domain:  $API_DOMAIN"
echo "  Frontend:    $FRONTEND_URL"
echo "  CORS:        $CORS_ORIGINS"
echo "  CORS regex:  ${CORS_ORIGIN_REGEX:-<none>}"
echo "  SSH key:     $SSH_KEY"
echo ""
read -r -p "Confirmer ? (yes/no): " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
  print_warning "Annulé"
  exit 0
fi

print_info "Préparation serveur (Docker, ufw, fail2ban)"
ssh -i "$SSH_KEY" root@"$SERVER_IP" <<'ENDSSH'
set -e
apt-get update
apt-get upgrade -y

# Docker
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  rm get-docker.sh
fi

# Docker Compose plugin
apt-get install -y docker-compose-plugin git curl ufw fail2ban

ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

mkdir -p /opt/ohmvision
ENDSSH
print_success "Serveur prêt"

print_info "Déploiement application (/opt/ohmvision)"
ssh -i "$SSH_KEY" root@"$SERVER_IP" <<ENDSSH
set -e
cd /opt/ohmvision

if [ -d .git ]; then
  git fetch origin master
  git reset --hard origin/master
else
  git clone https://github.com/yacinetirichine-creator/ohmvision.git .
fi

# Env
cat > .env <<EOF
DOMAIN=$API_DOMAIN
FRONTEND_URL=$FRONTEND_URL

POSTGRES_DB=ohmvision
POSTGRES_USER=ohmvision
POSTGRES_PASSWORD=\$(openssl rand -base64 32)

REDIS_PASSWORD=\$(openssl rand -base64 32)

SECRET_KEY=\$(openssl rand -base64 48)
JWT_SECRET_KEY=\$(openssl rand -base64 48)

CORS_ORIGINS=$CORS_ORIGINS
CORS_ORIGIN_REGEX=$CORS_ORIGIN_REGEX
EOF
chmod 600 .env

mkdir -p uploads logs logs/nginx

# Inject domain placeholder in nginx config
sed -i "s/__DOMAIN__/$API_DOMAIN/g" docker/nginx-api.conf

# Start nginx + certbot for initial challenge
docker compose -f docker-compose.hetzner.api.yml up -d nginx certbot
sleep 5

# Issue cert
docker compose -f docker-compose.hetzner.api.yml exec -T certbot certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  -d $API_DOMAIN

# Restart full stack
docker compose -f docker-compose.hetzner.api.yml up -d --build

echo "Deployed OK"
ENDSSH

print_success "Déployé"
print_info "Test: https://$API_DOMAIN/health et https://$API_DOMAIN/docs"
print_info "Sur Vercel: mettre VITE_API_BASE=https://$API_DOMAIN/api"
