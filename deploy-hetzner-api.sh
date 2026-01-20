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
USE_SUPABASE="yes"
DATABASE_URL=""
SUPABASE_URL=""
SUPABASE_ANON_KEY=""

print_info "Configuration Hetzner (backend-only)"
read -r -p "IP du serveur Hetzner: " SERVER_IP
read -r -p "Domaine API (ex: api.ohmvision.app): " API_DOMAIN
read -r -p "Email (Let's Encrypt): " EMAIL
read -r -p "URL Frontend (défaut: https://ohmvision.app): " FRONTEND_URL
read -r -p "Clé SSH (défaut: ~/.ssh/id_rsa): " SSH_KEY
SSH_KEY=${SSH_KEY:-~/.ssh/id_rsa}
FRONTEND_URL=${FRONTEND_URL:-https://ohmvision.app}

echo ""
print_info "Base de données: tu es sur Supabase, donc on peut utiliser Supabase (recommandé)."
read -r -p "Utiliser Supabase (DATABASE_URL) ? (yes/no) [yes]: " USE_SUPABASE
USE_SUPABASE=${USE_SUPABASE:-yes}

if [[ "$USE_SUPABASE" == "yes" ]]; then
  read -r -p "DATABASE_URL Supabase (postgresql+asyncpg://...): " DATABASE_URL
  read -r -p "SUPABASE_URL (optionnel): " SUPABASE_URL
  read -r -p "SUPABASE_ANON_KEY (optionnel): " SUPABASE_ANON_KEY

  if [[ -z "${DATABASE_URL}" ]]; then
    print_error "DATABASE_URL est requis si USE_SUPABASE=yes"
    exit 1
  fi
fi

print_info "CORS: ajoute ton domaine Vercel + domaine prod."
DEFAULT_CORS="https://ohmvision.app,https://www.ohmvision.app,https://ohmvision.fr,https://www.ohmvision.fr"
read -r -p "CORS_ORIGINS (défaut: ${DEFAULT_CORS}): " CORS_ORIGINS
CORS_ORIGINS=${CORS_ORIGINS:-$DEFAULT_CORS}
read -r -p "CORS_ORIGIN_REGEX optionnel (ex: https://.*\\.vercel\\.app$) [laisser vide si non]: " CORS_ORIGIN_REGEX

if [[ -z "${SERVER_IP}" || -z "${API_DOMAIN}" || -z "${EMAIL}" ]]; then
  print_error "Champs requis manquants (SERVER_IP, API_DOMAIN, EMAIL)"
  exit 1
fi

echo ""
print_info "Récapitulatif"
echo "  Server:     $SERVER_IP"
echo "  API domain:  $API_DOMAIN"
echo "  Frontend:    $FRONTEND_URL"
echo "  Supabase:    $USE_SUPABASE"
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

# Si Supabase
DATABASE_URL=$DATABASE_URL
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY

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

# Phase 1: nginx HTTP-only (permet l'ACME challenge)
cp docker/nginx-api.http.conf docker/nginx-api.conf
sed -i "s/__DOMAIN__/$API_DOMAIN/g" docker/nginx-api.conf

# Start nginx + certbot for initial challenge
COMPOSE_FILE="docker-compose.hetzner.api.yml"
if [ "$USE_SUPABASE" = "yes" ]; then
  COMPOSE_FILE="docker-compose.hetzner.api.supabase.yml"
fi

docker compose -f "$COMPOSE_FILE" up -d nginx certbot
sleep 5

# Issue cert
docker compose -f "$COMPOSE_FILE" exec -T certbot certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  -d $API_DOMAIN

# Phase 2: activer HTTPS (certificat maintenant présent)
cp docker/nginx-api.https.conf docker/nginx-api.conf
sed -i "s/__DOMAIN__/$API_DOMAIN/g" docker/nginx-api.conf
docker compose -f "$COMPOSE_FILE" restart nginx

# Restart full stack
docker compose -f "$COMPOSE_FILE" up -d --build

echo "Deployed OK"
ENDSSH

print_success "Déployé"
print_info "Test: https://$API_DOMAIN/health et https://$API_DOMAIN/docs"
print_info "Sur Vercel: mettre VITE_API_BASE=https://$API_DOMAIN/api"
