@echo off
REM ============================================
REM OhmVision Platform - Installation Windows
REM ============================================

echo.
echo  ========================================
echo    OhmVision Platform - Installation
echo  ========================================
echo.

REM Check for Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker n'est pas installe!
    echo.
    echo Installez Docker Desktop depuis:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo [OK] Docker detecte
echo.

REM Check for Docker Compose
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo [ERREUR] Docker Compose n'est pas installe!
        pause
        exit /b 1
    )
)

echo [OK] Docker Compose detecte
echo.

REM Create .env file if not exists
if not exist .env (
    echo Creation du fichier .env...
    copy .env.example .env >nul
    echo [OK] Fichier .env cree
    echo.
    echo IMPORTANT: Modifiez le fichier .env avec vos parametres!
    echo.
)

REM Build and start containers
echo Demarrage des services OhmVision...
echo Cela peut prendre plusieurs minutes lors du premier lancement.
echo.

docker compose up -d --build

if errorlevel 1 (
    echo [ERREUR] Echec du demarrage des services
    pause
    exit /b 1
)

echo.
echo  ========================================
echo    Installation terminee avec succes!
echo  ========================================
echo.
echo Services disponibles:
echo.
echo   API:          http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   Admin:        http://localhost:3000
echo   Application:  http://localhost:3001
echo.
echo Identifiants par defaut:
echo   Email: admin@ohmvision.fr
echo   Mot de passe: admin123
echo.
echo Pour arreter: docker compose down
echo Pour les logs: docker compose logs -f
echo.
pause
