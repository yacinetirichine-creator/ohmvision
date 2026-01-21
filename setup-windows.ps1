# ============================================================================
# OhmVision - Installation PowerShell (Windows 10/11)
# ============================================================================
# Usage: .\setup-windows.ps1
# Ou: PowerShell -ExecutionPolicy Bypass -File setup-windows.ps1
# ============================================================================

# Require admin privileges
#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

# Colors
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }

# Banner
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║                                                               ║" -ForegroundColor Blue
Write-Host "║   🎥  OhmVision - Installation Windows                       ║" -ForegroundColor Blue
Write-Host "║       Vidéosurveillance Intelligente                          ║" -ForegroundColor Blue
Write-Host "║                                                               ║" -ForegroundColor Blue
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check Windows version
$osVersion = [System.Environment]::OSVersion.Version
Write-Info "Système détecté: Windows $($osVersion.Major).$($osVersion.Minor)"

if ($osVersion.Major -lt 10) {
    Write-Error "Windows 10 ou supérieur est requis"
    exit 1
}

# Check if Docker is installed
Write-Info "[1/6] Vérification de Docker..."
try {
    $dockerVersion = docker --version
    Write-Success "[OK] Docker est installé: $dockerVersion"
} catch {
    Write-Warning "Docker n'est pas installé"
    Write-Info "Téléchargement de Docker Desktop..."
    
    $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    $installerPath = "$env:TEMP\DockerDesktopInstaller.exe"
    
    try {
        Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath -UseBasicParsing
        Write-Info "Installation de Docker Desktop..."
        Start-Process -FilePath $installerPath -ArgumentList "install --quiet" -Wait
        Remove-Item $installerPath
        
        Write-Warning "Docker Desktop installé. Veuillez REDÉMARRER votre ordinateur, puis relancer ce script."
        Read-Host "Appuyez sur Entrée pour quitter"
        exit 0
    } catch {
        Write-Error "Échec de l'installation de Docker. Veuillez l'installer manuellement depuis https://docker.com"
        exit 1
    }
}

# Check if Docker is running
Write-Info "[2/6] Vérification que Docker est démarré..."
try {
    docker info | Out-Null
    Write-Success "[OK] Docker est en cours d'exécution"
} catch {
    Write-Warning "Docker n'est pas démarré. Démarrage de Docker Desktop..."
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    Write-Info "Attente du démarrage de Docker (peut prendre 1-2 minutes)..."
    $maxAttempts = 24
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 5
        try {
            docker info | Out-Null
            Write-Success "[OK] Docker est démarré"
            break
        } catch {
            $attempt++
        }
    }
    
    if ($attempt -eq $maxAttempts) {
        Write-Error "Docker n'a pas pu démarrer. Veuillez le démarrer manuellement."
        exit 1
    }
}

# Check GPU support (NVIDIA)
Write-Info "[3/6] Vérification du support GPU..."
$hasNvidiaGPU = $false
try {
    $gpuInfo = nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        $hasNvidiaGPU = $true
        Write-Success "[OK] GPU NVIDIA détecté - support CUDA disponible"
        Write-Info "Pour activer l'accélération GPU, installez: pip install -r backend/requirements-gpu.txt"
    }
} catch {
    Write-Info "Aucun GPU NVIDIA détecté - mode CPU uniquement"
}

# Create directories
Write-Info "[4/6] Création des dossiers..."
$ohmvisionDir = "$env:USERPROFILE\OhmVision"
$dirs = @(
    $ohmvisionDir,
    "$ohmvisionDir\data",
    "$ohmvisionDir\recordings",
    "$ohmvisionDir\logs"
)

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Success "[OK] Dossiers créés: $ohmvisionDir"

# Create .env file if not exists
Write-Info "[5/6] Configuration de l'environnement..."
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Success "[OK] Fichier .env créé depuis .env.example"
    } else {
        # Create minimal .env
        @"
# OhmVision Configuration
DATABASE_URL=postgresql+asyncpg://ohmvision:ohmvision_secret@postgres:5432/ohmvision
REDIS_URL=redis://redis:6379/0
SECRET_KEY=$(([guid]::NewGuid().ToString() -replace '-',''))
JWT_SECRET_KEY=$(([guid]::NewGuid().ToString() -replace '-',''))
DEBUG=false
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "[OK] Fichier .env créé avec des valeurs par défaut"
    }
    Write-Warning "IMPORTANT: Modifiez le fichier .env avec vos paramètres avant la production!"
}

# Build and start with Docker Compose
Write-Info "[6/6] Démarrage des services OhmVision..."
Write-Info "Cela peut prendre plusieurs minutes lors du premier lancement..."

try {
    docker compose up -d --build
    Write-Success ""
    Write-Success "═══════════════════════════════════════════════════════════"
    Write-Success "   Installation terminée avec succès!"
    Write-Success "═══════════════════════════════════════════════════════════"
    Write-Success ""
    Write-Host "Services disponibles:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   API:          http://localhost:8000" -ForegroundColor White
    Write-Host "   API Docs:     http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   Admin:        http://localhost:3000" -ForegroundColor White
    Write-Host "   Application:  http://localhost:3001" -ForegroundColor White
    Write-Host ""
    Write-Host "Identifiants par défaut:" -ForegroundColor Cyan
    Write-Host "   Email: admin@ohmvision.fr" -ForegroundColor White
    Write-Host "   Mot de passe: admin123" -ForegroundColor White
    Write-Host ""
    Write-Host "Commandes utiles:" -ForegroundColor Cyan
    Write-Host "   Arrêter:     docker compose down" -ForegroundColor White
    Write-Host "   Logs:        docker compose logs -f" -ForegroundColor White
    Write-Host "   Redémarrer:  docker compose restart" -ForegroundColor White
    Write-Host ""
    
    if ($hasNvidiaGPU) {
        Write-Host "💡 Support GPU:" -ForegroundColor Yellow
        Write-Host "   Pour activer CUDA: docker compose -f docker-compose.gpu.yml up -d" -ForegroundColor White
        Write-Host ""
    }
    
} catch {
    Write-Error "Échec du démarrage des services: $_"
    Write-Host ""
    Write-Host "Pour les logs détaillés, exécutez: docker compose logs" -ForegroundColor Yellow
    exit 1
}

Read-Host "Appuyez sur Entrée pour quitter"
