#!/bin/bash

###############################################################################
# OhmVision - Script de Déploiement Hetzner Simplifié
# Serveur: 195.201.123.92
###############################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SERVER_IP="195.201.123.92"
SERVER_USER="root"

echo -e "${BLUE}"
echo "========================================="
echo "   OhmVision - Déploiement Hetzner"
echo "========================================="
echo -e "${NC}"

# Créer le package à déployer
echo -e "${BLUE}📦 Préparation du package de déploiement...${NC}"
tar -czf ohmvision-deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='storage' \
  backend/ \
  frontend-client/ \
  docker/ \
  docker-compose.production.yml \
  .env.hetzner \
  Dockerfile.allinone

echo -e "${GREEN}✅ Package créé${NC}"

# Copier sur le serveur
echo ""
echo -e "${BLUE}📤 Envoi vers le serveur...${NC}"
echo -e "${BLUE}ℹ️  Entrez le mot de passe du serveur quand demandé${NC}"
scp -o StrictHostKeyChecking=no ohmvision-deploy.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/

# Exécuter le déploiement sur le serveur
echo ""
echo -e "${BLUE}🚀 Déploiement sur le serveur...${NC}"
echo -e "${BLUE}ℹ️  Entrez le mot de passe du serveur à nouveau${NC}"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

echo "📁 Création des répertoires..."
mkdir -p /opt/ohmvision
cd /opt/ohmvision

echo "📦 Extraction du package..."
tar -xzf /tmp/ohmvision-deploy.tar.gz -C /opt/ohmvision/
rm /tmp/ohmvision-deploy.tar.gz

echo "🔧 Configuration de l'environnement..."
cp .env.hetzner .env

echo "📁 Création des répertoires de stockage..."
mkdir -p /opt/ohmvision/storage/{recordings,snapshots,reports}
chmod -R 755 /opt/ohmvision/storage

echo "🐳 Arrêt des anciens conteneurs (si existants)..."
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

echo "🏗️ Construction des images Docker..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "🚀 Démarrage des services..."
docker-compose -f docker-compose.production.yml up -d

echo "⏳ Attente du démarrage des services (30s)..."
sleep 30

echo "🗄️ Initialisation de la base de données..."
docker-compose -f docker-compose.production.yml exec -T backend python init_db.py || echo "⚠️ DB déjà initialisée"

echo ""
echo "✅ Déploiement terminé!"
echo ""
echo "📊 État des services:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "🌐 Application accessible sur:"
echo "   http://195.201.123.92"
echo "   API Docs: http://195.201.123.92/api/docs"
echo ""
echo "📝 Logs:"
echo "   docker-compose -f docker-compose.production.yml logs -f"

ENDSSH

# Nettoyage local
rm ohmvision-deploy.tar.gz

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ Déploiement réussi!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "🌐 Application: ${BLUE}http://195.201.123.92${NC}"
echo -e "📚 API Docs: ${BLUE}http://195.201.123.92/api/docs${NC}"
echo ""
