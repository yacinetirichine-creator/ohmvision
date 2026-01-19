#!/bin/bash
# ============================================================================
# OhmVision - Installation Linux/Mac
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                               ║${NC}"
echo -e "${BLUE}║   🎥  OhmVision - Installation                               ║${NC}"
echo -e "${BLUE}║       Vidéosurveillance Intelligente                          ║${NC}"
echo -e "${BLUE}║                                                               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
fi

echo -e "${YELLOW}[INFO]${NC} Système détecté: $OS"
echo ""

# Step 1: Check Docker
echo -e "${BLUE}[1/5]${NC} Vérification de Docker..."

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}[INFO]${NC} Docker n'est pas installé."
    echo ""
    
    if [[ "$OS" == "linux" ]]; then
        echo "Installation de Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
        
        sudo usermod -aG docker $USER
        
        echo -e "${YELLOW}[IMPORTANT]${NC} Docker a été installé."
        echo "Veuillez vous déconnecter et vous reconnecter, puis relancer ce script."
        exit 0
        
    elif [[ "$OS" == "mac" ]]; then
        echo "Veuillez installer Docker Desktop depuis:"
        echo "👉 https://docker.com/products/docker-desktop"
        echo ""
        echo "Puis relancez ce script."
        exit 1
    fi
else
    echo -e "${GREEN}[OK]${NC} Docker est installé"
fi

# Step 2: Check Docker is running
echo -e "${BLUE}[2/5]${NC} Vérification que Docker est démarré..."

if ! docker info &> /dev/null; then
    echo -e "${YELLOW}[INFO]${NC} Docker n'est pas démarré."
    
    if [[ "$OS" == "linux" ]]; then
        echo "Démarrage de Docker..."
        sudo systemctl start docker
        sleep 5
    elif [[ "$OS" == "mac" ]]; then
        echo "Veuillez démarrer Docker Desktop, puis relancer ce script."
        exit 1
    fi
fi
echo -e "${GREEN}[OK]${NC} Docker est en cours d'exécution"

# Step 3: Create directories
echo -e "${BLUE}[3/5]${NC} Création des dossiers..."

OHMVISION_DIR="$HOME/ohmvision"
mkdir -p "$OHMVISION_DIR/data"
mkdir -p "$OHMVISION_DIR/recordings"
mkdir -p "$OHMVISION_DIR/logs"

echo -e "${GREEN}[OK]${NC} Dossiers créés: $OHMVISION_DIR"

# Step 4: Pull/Build OhmVision
echo -e "${BLUE}[4/5]${NC} Téléchargement d'OhmVision..."

if docker pull ohmvision/ohmvision:latest 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Image téléchargée depuis Docker Hub"
else
    echo -e "${YELLOW}[INFO]${NC} Construction de l'image locale..."
    
    if [[ -f "Dockerfile.allinone" ]]; then
        docker build -t ohmvision/ohmvision:latest -f Dockerfile.allinone .
        echo -e "${GREEN}[OK]${NC} Image construite"
    else
        echo -e "${RED}[ERREUR]${NC} Impossible de trouver l'image OhmVision"
        exit 1
    fi
fi

# Step 5: Run OhmVision
echo -e "${BLUE}[5/5]${NC} Démarrage d'OhmVision..."

docker stop ohmvision 2>/dev/null || true
docker rm ohmvision 2>/dev/null || true

docker run -d \
    --name ohmvision \
    --restart unless-stopped \
    -p 8080:8080 \
    -v "$OHMVISION_DIR/data:/app/data" \
    -v "$OHMVISION_DIR/recordings:/app/recordings" \
    -v "$OHMVISION_DIR/logs:/app/logs" \
    ohmvision/ohmvision:latest

echo ""
echo "Attente du démarrage..."
sleep 10

if docker ps | grep -q ohmvision; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✅  OhmVision est installé et démarré !                    ║${NC}"
    echo -e "${GREEN}║   👉  http://localhost:8080                                  ║${NC}"
    echo -e "${GREEN}║   📁  $OHMVISION_DIR                            ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [[ "$OS" == "mac" ]]; then
        open http://localhost:8080
    elif [[ "$OS" == "linux" ]]; then
        xdg-open http://localhost:8080 2>/dev/null || true
    fi
else
    echo -e "${RED}[ERREUR]${NC} OhmVision n'a pas démarré correctement"
    echo "Vérifiez les logs avec: docker logs ohmvision"
    exit 1
fi

echo ""
echo "Commandes utiles:"
echo "  • Voir les logs:      docker logs -f ohmvision"
echo "  • Arrêter:            docker stop ohmvision"
echo "  • Redémarrer:         docker restart ohmvision"
echo "  • Désinstaller:       docker rm -f ohmvision"
echo ""
