@echo off
REM ================================================================
REM OhmVision - Quick Start Windows avec support GPU
REM ================================================================

title OhmVision Quick Start
color 0B

echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║   🎥  OhmVision - Demarrage Rapide                           ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Detect GPU
echo Detection du materiel...
nvidia-smi >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] GPU NVIDIA detecte
    set HAS_GPU=1
    echo.
    echo Quelle version souhaitez-vous lancer ?
    echo   1. Version CPU ^(compatible toutes machines^)
    echo   2. Version GPU ^(acceleration CUDA^)
    echo.
    set /p CHOICE="Votre choix [1 ou 2]: "
    
    if "!CHOICE!"=="2" (
        echo.
        echo Lancement avec acceleration GPU...
        docker compose -f docker-compose.gpu.yml up -d
    ) else (
        echo.
        echo Lancement version CPU...
        docker compose up -d
    )
) else (
    echo [INFO] Aucun GPU NVIDIA detecte - mode CPU uniquement
    echo.
    echo Lancement...
    docker compose up -d
)

if %errorLevel% neq 0 (
    echo.
    echo [ERREUR] Echec du demarrage
    echo.
    echo Assurez-vous que:
    echo   - Docker Desktop est installe et demarre
    echo   - Le fichier .env existe
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo    OhmVision demarre avec succes!
echo ═══════════════════════════════════════════════════════════
echo.
echo Services disponibles:
echo   • API:          http://localhost:8000
echo   • API Docs:     http://localhost:8000/docs
echo   • Admin:        http://localhost:3000
echo   • Application:  http://localhost:3001
echo.
echo Commandes utiles:
echo   • Arreter:     docker compose down
echo   • Logs:        docker compose logs -f
echo   • Redemarrer:  docker compose restart
echo.
pause
