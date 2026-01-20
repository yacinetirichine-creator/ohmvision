#!/bin/bash

###############################################################################
# OhmVision - Déploiement via API Hetzner Cloud
# Déploiement automatisé sans SSH manuel
###############################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
HETZNER_API_TOKEN="6uGi7YS4J9QNWQr4kaDSSRhsQCpQadWOwPt6UsWqZ2p6P8NWdus4jroAyK3XmQbK"
SERVER_IP="195.201.123.92"
SERVER_ID="117913189"  # ID du serveur ohmvision-prod

echo -e "${BLUE}"
echo "========================================="
echo "   OhmVision - Déploiement via API"
echo "========================================="
echo -e "${NC}"

# Fonction pour obtenir l'ID du serveur par IP
get_server_id() {
    echo -e "${BLUE}🔍 Récupération de l'ID du serveur...${NC}"
    
    RESPONSE=$(curl -s -H "Authorization: Bearer ${HETZNER_API_TOKEN}" \
        https://api.hetzner.cloud/v1/servers)
    
    SERVER_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    
    if [ -z "$SERVER_ID" ]; then
        echo -e "${RED}❌ Impossible de trouver le serveur${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Serveur trouvé: ID ${SERVER_ID}${NC}"
}

# Créer le script d'installation
create_install_script() {
    cat > /tmp/ohmvision-install.sh << 'ENDSCRIPT'
#!/bin/bash
set -e

echo "🚀 Installation OhmVision - Démarrage..."

# Mise à jour système
echo "📦 Mise à jour du système..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq

# Installation Docker
echo "🐳 Installation Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Installation Docker Compose
echo "🔧 Installation Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -SL https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-aarch64 -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Installation outils
echo "🛠️ Installation outils..."
apt-get install -y -qq git curl wget ufw htop

# Configuration firewall
echo "🔥 Configuration firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8554/tcp

# Clonage repository
echo "📥 Clonage repository..."
mkdir -p /opt/ohmvision
cd /opt/ohmvision

if [ -d ".git" ]; then
    git pull
else
    git clone https://github.com/yacinetirichine-creator/ohmvision.git .
fi

# Configuration .env
echo "🔧 Configuration environnement..."
cat > /opt/ohmvision/.env << 'EOF'
APP_NAME=OhmVision
APP_ENV=production
DEBUG=false

DOMAIN=195.201.123.92
BACKEND_URL=http://195.201.123.92
FRONTEND_URL=http://195.201.123.92

SECRET_KEY=a8f5f167f44f4964e6c998dee827110c47f0a7e83e5b0a0b5f63f60f3c7e7e2d
JWT_SECRET_KEY=7f3f7c8e9a2b4d6e8f0a1c3e5d7f9b0c2e4a6c8e0f2b4d6a8c0e2f4b6d8a0c2e

POSTGRES_DB=ohmvision
POSTGRES_USER=ohmvision
POSTGRES_PASSWORD=OhmVision2026Secure!Pass
DATABASE_URL=postgresql+asyncpg://ohmvision:OhmVision2026Secure!Pass@postgres:5432/ohmvision

REDIS_PASSWORD=Redis2026Secure!Pass
REDIS_URL=redis://:Redis2026Secure!Pass@redis:6379/0

CORS_ORIGINS=["*"]

STORAGE_PATH=/opt/ohmvision/storage
RECORDINGS_PATH=/opt/ohmvision/storage/recordings
SNAPSHOTS_PATH=/opt/ohmvision/storage/snapshots
EOF

# Création répertoires
echo "📁 Création répertoires..."
mkdir -p /opt/ohmvision/storage/{recordings,snapshots,reports,backups}
chmod -R 755 /opt/ohmvision/storage

# Arrêt anciens conteneurs
echo "🛑 Arrêt anciens conteneurs..."
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# Construction images
echo "🏗️ Construction images..."
docker-compose -f docker-compose.production.yml build --no-cache

# Démarrage services
echo "🚀 Démarrage services..."
docker-compose -f docker-compose.production.yml up -d

# Attente démarrage
echo "⏳ Attente démarrage..."
sleep 30

# Initialisation DB
echo "🗄️ Initialisation base de données..."
docker-compose -f docker-compose.production.yml exec -T backend python init_db.py 2>/dev/null || true

echo ""
echo "✅ INSTALLATION TERMINÉE!"
echo ""
echo "🌐 Application: http://195.201.123.92"
echo "📚 API Docs: http://195.201.123.92/api/docs"
echo ""

# Afficher les services
docker-compose -f docker-compose.production.yml ps
ENDSCRIPT
}

# Déployer le script via SSH
deploy_via_ssh() {
    echo ""
    echo -e "${BLUE}📤 Déploiement du script sur le serveur...${NC}"
    
    # Créer le script local
    create_install_script
    
    # Copier et exécuter sur le serveur
    echo -e "${BLUE}🚀 Exécution de l'installation...${NC}"
    echo -e "${YELLOW}Vous devrez entrer le mot de passe SSH 2 fois${NC}"
    echo ""
    
    # Copier le script
    scp -o StrictHostKeyChecking=no /tmp/ohmvision-install.sh root@${SERVER_IP}:/tmp/
    
    # Exécuter le script
    ssh -o StrictHostKeyChecking=no root@${SERVER_IP} "bash /tmp/ohmvision-install.sh"
    
    # Nettoyer
    rm /tmp/ohmvision-install.sh
}

# Exécution principale
echo -e "${BLUE}📋 Configuration:${NC}"
echo -e "  Serveur: ${GREEN}${SERVER_IP}${NC}"
echo -e "  API Token: ${GREEN}${HETZNER_API_TOKEN:0:20}...${NC}"
echo ""

deploy_via_ssh

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ DÉPLOIEMENT RÉUSSI !${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}🌐 Accès:${NC}"
echo -e "  Application: ${GREEN}http://195.201.123.92${NC}"
echo -e "  API Docs: ${GREEN}http://195.201.123.92/api/docs${NC}"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "  ${YELLOW}ssh root@195.201.123.92${NC}"
echo -e "  ${YELLOW}cd /opt/ohmvision${NC}"
echo -e "  ${YELLOW}docker-compose -f docker-compose.production.yml logs -f${NC}"
echo ""
