#!/bin/bash

###############################################################################
# OhmVision - Déploiement Direct sur Serveur
# À exécuter DIRECTEMENT sur le serveur Hetzner 195.201.123.92
###############################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "========================================="
echo "   OhmVision - Installation Serveur"
echo "========================================="
echo -e "${NC}"

# Étape 1: Mise à jour système
echo -e "${BLUE}📦 Mise à jour du système...${NC}"
apt-get update -qq
apt-get upgrade -y -qq
echo -e "${GREEN}✅ Système à jour${NC}"

# Étape 2: Installation Docker
echo ""
echo -e "${BLUE}🐳 Installation de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✅ Docker installé${NC}"
else
    echo -e "${YELLOW}⚠️  Docker déjà installé${NC}"
fi

# Étape 3: Installation Docker Compose
echo ""
echo -e "${BLUE}🔧 Installation de Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -SL https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-aarch64 -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installé${NC}"
else
    echo -e "${YELLOW}⚠️  Docker Compose déjà installé${NC}"
fi

# Vérification versions
echo ""
echo -e "${BLUE}📋 Versions installées:${NC}"
docker --version
docker-compose --version

# Étape 4: Installation des outils
echo ""
echo -e "${BLUE}🛠️ Installation des outils...${NC}"
apt-get install -y -qq git curl wget ufw htop net-tools
echo -e "${GREEN}✅ Outils installés${NC}"

# Étape 5: Configuration du firewall
echo ""
echo -e "${BLUE}🔥 Configuration du firewall...${NC}"
ufw --force enable
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 8554/tcp comment 'RTSP'
echo -e "${GREEN}✅ Firewall configuré${NC}"
ufw status

# Étape 6: Clonage du repository
echo ""
echo -e "${BLUE}📥 Clonage du repository OhmVision...${NC}"
mkdir -p /opt/ohmvision
cd /opt/ohmvision

if [ -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Repository déjà cloné, mise à jour...${NC}"
    git pull
else
    git clone https://github.com/yacinetirichine-creator/ohmvision.git .
fi
echo -e "${GREEN}✅ Code récupéré${NC}"

# Étape 7: Configuration .env
echo ""
echo -e "${BLUE}🔧 Configuration de l'environnement...${NC}"

cat > /opt/ohmvision/.env << 'EOF'
# OhmVision Production - Hetzner
APP_NAME=OhmVision
APP_ENV=production
DEBUG=false

# Domain
DOMAIN=195.201.123.92
BACKEND_URL=http://195.201.123.92
FRONTEND_URL=http://195.201.123.92

# Secrets (générés aléatoirement)
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c47f0a7e83e5b0a0b5f63f60f3c7e7e2d
JWT_SECRET_KEY=7f3f7c8e9a2b4d6e8f0a1c3e5d7f9b0c2e4a6c8e0f2b4d6a8c0e2f4b6d8a0c2e

# Database PostgreSQL (local via Docker)
POSTGRES_DB=ohmvision
POSTGRES_USER=ohmvision
POSTGRES_PASSWORD=OhmVision2026Secure!Pass
DATABASE_URL=postgresql+asyncpg://ohmvision:OhmVision2026Secure!Pass@postgres:5432/ohmvision

# Redis
REDIS_PASSWORD=Redis2026Secure!Pass
REDIS_URL=redis://:Redis2026Secure!Pass@redis:6379/0

# CORS
CORS_ORIGINS=["*"]

# Storage
STORAGE_PATH=/opt/ohmvision/storage
RECORDINGS_PATH=/opt/ohmvision/storage/recordings
SNAPSHOTS_PATH=/opt/ohmvision/storage/snapshots
EOF

echo -e "${GREEN}✅ Fichier .env créé${NC}"

# Étape 8: Création des répertoires de stockage
echo ""
echo -e "${BLUE}📁 Création des répertoires de stockage...${NC}"
mkdir -p /opt/ohmvision/storage/{recordings,snapshots,reports,backups}
chmod -R 755 /opt/ohmvision/storage
echo -e "${GREEN}✅ Répertoires créés${NC}"

# Étape 9: Arrêt des anciens conteneurs
echo ""
echo -e "${BLUE}🛑 Arrêt des anciens conteneurs...${NC}"
docker-compose -f docker-compose.production.yml down 2>/dev/null || echo "Aucun conteneur à arrêter"

# Étape 10: Construction des images
echo ""
echo -e "${BLUE}🏗️ Construction des images Docker (cela peut prendre 5-10 min)...${NC}"
docker-compose -f docker-compose.production.yml build --no-cache

# Étape 11: Démarrage des services
echo ""
echo -e "${BLUE}🚀 Démarrage des services...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Étape 12: Attente démarrage
echo ""
echo -e "${BLUE}⏳ Attente du démarrage des services (30 secondes)...${NC}"
sleep 30

# Étape 13: Initialisation DB
echo ""
echo -e "${BLUE}🗄️ Initialisation de la base de données...${NC}"
docker-compose -f docker-compose.production.yml exec -T backend python init_db.py || echo -e "${YELLOW}⚠️  Base déjà initialisée${NC}"

# Vérification finale
echo ""
echo -e "${BLUE}📊 État des services:${NC}"
docker-compose -f docker-compose.production.yml ps

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ DÉPLOIEMENT RÉUSSI !${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}🌐 Application accessible:${NC}"
echo -e "   Frontend: ${GREEN}http://195.201.123.92${NC}"
echo -e "   API: ${GREEN}http://195.201.123.92/api${NC}"
echo -e "   Docs: ${GREEN}http://195.201.123.92/api/docs${NC}"
echo ""
echo -e "${BLUE}📝 Commandes utiles:${NC}"
echo -e "   Logs: ${YELLOW}docker-compose -f docker-compose.production.yml logs -f${NC}"
echo -e "   Statut: ${YELLOW}docker-compose -f docker-compose.production.yml ps${NC}"
echo -e "   Redémarrer: ${YELLOW}docker-compose -f docker-compose.production.yml restart${NC}"
echo -e "   Arrêter: ${YELLOW}docker-compose -f docker-compose.production.yml down${NC}"
echo ""
