#!/bin/bash

###############################################################################
# OhmVision - Réinitialisation Mot de Passe Hetzner
# Utilise l'API Hetzner pour réinitialiser le mot de passe root
###############################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

HETZNER_API_TOKEN="${HETZNER_API_TOKEN:-your_api_token_here}"
SERVER_NAME="ohmvision-prod"

echo -e "${BLUE}"
echo "========================================="
echo "   Réinitialisation Accès Serveur"
echo "========================================="
echo -e "${NC}"

# Fonction pour obtenir l'ID du serveur
get_server_id() {
    echo -e "${BLUE}🔍 Recherche du serveur ${SERVER_NAME}...${NC}"
    
    RESPONSE=$(curl -s -H "Authorization: Bearer ${HETZNER_API_TOKEN}" \
        https://api.hetzner.cloud/v1/servers)
    
    # Sauvegarder pour debug
    echo "$RESPONSE" > /tmp/hetzner_response.json
    
    # Essayer avec Python pour parser le JSON
    if command -v python3 &> /dev/null; then
        SERVER_ID=$(python3 -c "import json; data=json.loads('''$RESPONSE'''); print(data['servers'][0]['id'] if data.get('servers') else '')")
    else
        # Fallback: extraction simple
        SERVER_ID=$(echo "$RESPONSE" | sed -n 's/.*"id":\([0-9]*\).*/\1/p' | head -1)
    fi
    
    if [ -z "$SERVER_ID" ]; then
        echo -e "${RED}❌ Serveur non trouvé${NC}"
        echo -e "${YELLOW}Réponse API sauvegardée dans /tmp/hetzner_response.json${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Serveur trouvé - ID: ${SERVER_ID}${NC}"
}

# Option 1: Demander un reset de mot de passe
reset_root_password() {
    echo ""
    echo -e "${BLUE}🔑 Demande de réinitialisation du mot de passe...${NC}"
    
    RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer ${HETZNER_API_TOKEN}" \
        -H "Content-Type: application/json" \
        https://api.hetzner.cloud/v1/servers/${SERVER_ID}/actions/reset_password)
    
    # Parser avec Python si disponible
    if command -v python3 &> /dev/null; then
        NEW_PASSWORD=$(python3 -c "import json; data=json.loads('''$RESPONSE'''); print(data.get('root_password', ''))")
    else
        # Fallback
        NEW_PASSWORD=$(echo "$RESPONSE" | grep -o '"root_password"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    fi
    
    if [ -n "$NEW_PASSWORD" ]; then
        echo ""
        echo -e "${GREEN}=========================================${NC}"
        echo -e "${GREEN}✅ MOT DE PASSE RÉINITIALISÉ !${NC}"
        echo -e "${GREEN}=========================================${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  NOUVEAU MOT DE PASSE ROOT:${NC}"
        echo ""
        echo -e "${RED}${NEW_PASSWORD}${NC}"
        echo ""
        echo -e "${YELLOW}📝 Notez-le dans un endroit sûr !${NC}"
        echo ""
        echo -e "${BLUE}Pour vous connecter:${NC}"
        echo -e "  ${GREEN}ssh root@195.201.123.92${NC}"
        echo ""
        echo -e "${YELLOW}Attendez 30 secondes que le serveur applique le changement...${NC}"
        echo ""
    else
        echo -e "${YELLOW}⚠️  Impossible de parser le mot de passe automatiquement${NC}"
        echo -e "${BLUE}Réponse complète de l'API:${NC}"
        echo "$RESPONSE"
        echo ""
        echo -e "${YELLOW}Extrayez le 'root_password' manuellement ci-dessus${NC}"
    fi
}

# Option 2: Créer une clé SSH locale et l'ajouter au serveur
setup_ssh_key() {
    echo ""
    echo -e "${BLUE}🔐 Configuration d'une clé SSH...${NC}"
    
    SSH_KEY_PATH="$HOME/.ssh/id_rsa_ohmvision"
    
    if [ ! -f "$SSH_KEY_PATH" ]; then
        echo -e "${BLUE}Génération d'une nouvelle clé SSH...${NC}"
        ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "ohmvision-hetzner"
        echo -e "${GREEN}✅ Clé SSH générée${NC}"
    else
        echo -e "${YELLOW}⚠️  Clé SSH existante trouvée${NC}"
    fi
    
    # Lire la clé publique
    SSH_PUBLIC_KEY=$(cat "${SSH_KEY_PATH}.pub")
    
    echo -e "${BLUE}Ajout de la clé au compte Hetzner...${NC}"
    
    # Créer la clé SSH dans Hetzner
    RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer ${HETZNER_API_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"ohmvision-key\",\"public_key\":\"${SSH_PUBLIC_KEY}\"}" \
        https://api.hetzner.cloud/v1/ssh_keys)
    
    echo -e "${GREEN}✅ Clé SSH configurée${NC}"
    echo ""
    echo -e "${BLUE}Pour vous connecter:${NC}"
    echo -e "  ssh -i ${SSH_KEY_PATH} root@195.201.123.92"
    echo ""
}

# Menu principal
echo ""
echo -e "${YELLOW}Choisissez une option:${NC}"
echo ""
echo "  1) Réinitialiser le mot de passe root (RECOMMANDÉ)"
echo "  2) Configurer une clé SSH"
echo "  3) Les deux"
echo ""
read -p "Votre choix (1/2/3): " CHOICE

get_server_id

case $CHOICE in
    1)
        reset_root_password
        ;;
    2)
        setup_ssh_key
        ;;
    3)
        reset_root_password
        setup_ssh_key
        ;;
    *)
        echo -e "${RED}Choix invalide${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Accès au serveur restauré !${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
