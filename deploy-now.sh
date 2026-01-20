#!/bin/bash

# Script de déploiement OhmVision sur Hetzner
# IP: 195.201.123.92

SERVER_IP="195.201.123.92"

echo "🚀 Déploiement OhmVision sur Hetzner"
echo "======================================"

# Étape 1: Vérifier la connexion
echo ""
echo "📡 Connexion au serveur..."
ssh root@$SERVER_IP << 'ENDSSH'
echo "✅ Connexion réussie!"
echo ""
echo "📊 Informations système:"
uname -a
cat /etc/os-release | grep PRETTY_NAME
echo ""

# Étape 2: Mise à jour du système
echo "📦 Mise à jour du système..."
apt-get update -qq
apt-get upgrade -y -qq

# Étape 3: Installation Docker
echo ""
echo "🐳 Installation de Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installé"
else
    echo "✅ Docker déjà installé"
fi

# Étape 4: Installation Docker Compose
echo ""
echo "🔧 Installation de Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installé"
else
    echo "✅ Docker Compose déjà installé"
fi

# Vérification
docker --version
docker-compose --version

# Étape 5: Installation des outils
echo ""
echo "🛠️ Installation des outils..."
apt-get install -y -qq git curl wget ufw

# Étape 6: Configuration du firewall
echo ""
echo "🔥 Configuration du firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8554/tcp  # RTSP
echo "✅ Firewall configuré"

# Étape 7: Création du répertoire
echo ""
echo "📁 Création du répertoire d'application..."
mkdir -p /opt/ohmvision
cd /opt/ohmvision

echo ""
echo "✅ Serveur préparé avec succès!"
echo ""
echo "Prochaines étapes:"
echo "1. Cloner le repository"
echo "2. Configurer les variables d'environnement"
echo "3. Démarrer les services"

ENDSSH

echo ""
echo "✅ Préparation terminée!"
