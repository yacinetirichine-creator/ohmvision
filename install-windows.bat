@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: OhmVision - Installation Windows
:: ============================================================================

title OhmVision Installer
color 0B

echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║   🎥  OhmVision - Installation                               ║
echo  ║       Vidéosurveillance Intelligente                          ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERREUR] Veuillez executer en tant qu'administrateur
    echo           Clic droit sur le fichier ^> Executer en tant qu'administrateur
    pause
    exit /b 1
)

:: Check if Docker is installed
echo [1/5] Verification de Docker...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [INFO] Docker n'est pas installe.
    echo        Installation de Docker Desktop...
    echo.
    
    :: Download Docker Desktop
    echo Telechargement de Docker Desktop...
    curl -L -o docker-installer.exe "https://desktop.docker.com/win/main/amd64/Docker%%20Desktop%%20Installer.exe"
    
    if exist docker-installer.exe (
        echo Installation de Docker Desktop...
        start /wait docker-installer.exe install --quiet
        del docker-installer.exe
        
        echo.
        echo [IMPORTANT] Docker Desktop a ete installe.
        echo             Veuillez REDEMARRER votre ordinateur, puis relancer ce script.
        echo.
        pause
        exit /b 0
    ) else (
        echo [ERREUR] Impossible de telecharger Docker Desktop
        echo          Veuillez l'installer manuellement depuis: https://docker.com
        pause
        exit /b 1
    )
) else (
    echo [OK] Docker est installe
)

:: Check if Docker is running
echo [2/5] Verification que Docker est demarre...
docker info >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Demarrage de Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    echo Attente du demarrage de Docker (peut prendre 1-2 minutes)...
    :waitloop
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    if %errorLevel% neq 0 goto waitloop
)
echo [OK] Docker est en cours d'execution

:: Create data directory
echo [3/5] Creation des dossiers...
set OHMVISION_DIR=%USERPROFILE%\OhmVision
if not exist "%OHMVISION_DIR%" mkdir "%OHMVISION_DIR%"
if not exist "%OHMVISION_DIR%\data" mkdir "%OHMVISION_DIR%\data"
if not exist "%OHMVISION_DIR%\recordings" mkdir "%OHMVISION_DIR%\recordings"
echo [OK] Dossiers crees: %OHMVISION_DIR%

:: Pull OhmVision image
echo [4/5] Telechargement d'OhmVision (peut prendre quelques minutes)...
docker pull ohmvision/ohmvision:latest 2>nul
if %errorLevel% neq 0 (
    echo [INFO] Image non disponible sur Docker Hub, construction locale...
    
    :: Check if we have the source
    if exist Dockerfile.allinone (
        docker build -t ohmvision/ohmvision:latest -f Dockerfile.allinone .
    ) else (
        echo [ERREUR] Impossible de trouver l'image OhmVision
        pause
        exit /b 1
    )
)
echo [OK] OhmVision telecharge

:: Run OhmVision
echo [5/5] Demarrage d'OhmVision...

:: Stop existing container if any
docker stop ohmvision 2>nul
docker rm ohmvision 2>nul

:: Run new container
docker run -d ^
    --name ohmvision ^
    --restart unless-stopped ^
    -p 8080:8080 ^
    -v "%OHMVISION_DIR%\data:/app/data" ^
    -v "%OHMVISION_DIR%\recordings:/app/recordings" ^
    ohmvision/ohmvision:latest

if %errorLevel% neq 0 (
    echo [ERREUR] Impossible de demarrer OhmVision
    pause
    exit /b 1
)

:: Wait for startup
echo.
echo Attente du demarrage...
timeout /t 10 /nobreak >nul

:: Check if running
docker ps | findstr ohmvision >nul
if %errorLevel% equ 0 (
    echo.
    echo  ╔═══════════════════════════════════════════════════════════════╗
    echo  ║                                                               ║
    echo  ║   ✅  OhmVision est installe et demarre !                    ║
    echo  ║                                                               ║
    echo  ║   Ouvrez votre navigateur:                                   ║
    echo  ║   👉  http://localhost:8080                                  ║
    echo  ║                                                               ║
    echo  ║   Dossier des donnees:                                       ║
    echo  ║   📁  %OHMVISION_DIR%                                        ║
    echo  ║                                                               ║
    echo  ╚═══════════════════════════════════════════════════════════════╝
    echo.
    
    :: Open browser
    start http://localhost:8080
) else (
    echo [ERREUR] OhmVision n'a pas demarre correctement
    echo          Verifiez les logs avec: docker logs ohmvision
)

pause
