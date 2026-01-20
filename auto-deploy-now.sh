#!/bin/bash

###############################################################################
# Déploiement Automatique OhmVision - Avec nouveau mot de passe
###############################################################################

set -e

SERVER_IP="195.201.123.92"
PASSWORD="tUUFWCRgJ3TV"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Déploiement OhmVision${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Test de connexion
echo -e "${BLUE}1. Test de connexion SSH...${NC}"
if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP "echo 'Connexion OK'" 2>/dev/null; then
    echo -e "${GREEN}✅ Connexion réussie${NC}"
else
    echo "⚠️  sshpass non installé, installation..."
    # Copier le script sur le serveur manuellement
    echo ""
    echo "Copiez et collez cette commande dans un nouveau terminal:"
    echo ""
    echo "ssh root@195.201.123.92"
    echo "# Mot de passe: tUUFWCRgJ3TV"
    echo ""
    echo "Puis exécutez:"
    echo "bash <(curl -s https://raw.githubusercontent.com/yacinetirichine-creator/ohmvision/master/install-on-server.sh)"
    echo ""
    exit 0
fi

# Copier le script d'installation
echo ""
echo -e "${BLUE}2. Envoi du script d'installation...${NC}"
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no \
    /workspaces/ohmvision/install-on-server.sh \
    root@$SERVER_IP:/tmp/install.sh

echo -e "${GREEN}✅ Script envoyé${NC}"

# Exécuter l'installation
echo ""
echo -e "${BLUE}3. Exécution de l'installation (cela prendra 5-10 minutes)...${NC}"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "bash /tmp/install.sh"

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ DÉPLOIEMENT TERMINÉ !${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${BLUE}🌐 Application: http://195.201.123.92${NC}"
echo -e "${BLUE}📚 API Docs: http://195.201.123.92/api/docs${NC}"
echo ""
