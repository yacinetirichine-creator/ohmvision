# 🔄 Migration Mac → PC - Notes importantes

## Changements effectués pour la compatibilité PC/Windows

### ✅ Fichiers ajoutés

1. **[README_WINDOWS.md](README_WINDOWS.md)** - Guide complet d'installation Windows
2. **[setup-windows.ps1](setup-windows.ps1)** - Script PowerShell d'installation automatique
3. **[start-windows.bat](start-windows.bat)** - Script de démarrage rapide
4. **[backend/requirements-gpu.txt](backend/requirements-gpu.txt)** - Dépendances optimisées GPU NVIDIA
5. **[docker-compose.gpu.yml](docker-compose.gpu.yml)** - Configuration Docker avec support GPU

### 🔧 Fichiers modifiés

1. **[backend/requirements.txt](backend/requirements.txt)**
   - Mise à jour du commentaire ONNX Runtime (Mac ARM → PC/Windows)
   - Support GPU CUDA explicite

2. **[backend/Dockerfile](backend/Dockerfile)**
   - Ajout support multi-stage build
   - Option `USE_GPU` pour basculer CPU/GPU
   - Installation conditionnelle des dépendances

### 📊 Avantages de votre nouveau PC

#### Puissance accrue
- ✅ Plus de RAM → Traitement de plus de flux vidéo simultanés
- ✅ Plus d'espace disque → Stockage enregistrements longue durée
- ✅ GPU NVIDIA (si présent) → Inférence IA 5-10x plus rapide

#### Compatibilité GPU
| Plateforme | GPU | Framework | Performance |
|------------|-----|-----------|-------------|
| Mac M1/M2 | Apple Silicon | MPS | Moyen |
| PC NVIDIA | RTX 3060+ | CUDA | Excellent |
| PC AMD | RX 6000+ | ROCm | Bon (limité) |

### 🎯 Pour démarrer sur votre PC

#### Option 1: Démarrage ultra-rapide
```cmd
start-windows.bat
```

#### Option 2: Installation complète
```powershell
PowerShell -ExecutionPolicy Bypass -File setup-windows.ps1
```

#### Option 3: Avec GPU NVIDIA
```cmd
docker compose -f docker-compose.gpu.yml up -d
```

### 🔥 Configuration GPU optimale

Si vous avez une carte NVIDIA (GTX 1060, RTX 2060, RTX 3060, etc.):

1. **Installer les drivers NVIDIA** (dernière version)
2. **Installer CUDA Toolkit 11.8 ou 12.x**
3. **Activer le support GPU Docker**:
   - Docker Desktop → Settings → Resources → Enable GPU

4. **Vérifier le GPU**:
   ```cmd
   nvidia-smi
   ```

5. **Utiliser la config GPU**:
   ```cmd
   docker compose -f docker-compose.gpu.yml up -d
   ```

### 📈 Gain de performance attendu

| Tâche | Mac (CPU) | PC CPU | PC GPU NVIDIA |
|-------|-----------|--------|---------------|
| Détection objet (YOLO) | 15 FPS | 20 FPS | 120+ FPS |
| Analyse multi-caméra | 2-3 flux | 4-6 flux | 15+ flux |
| Reconnaissance faciale | 8 FPS | 12 FPS | 60+ FPS |
| Training modèles | ❌ Lent | Moyen | ⚡ Rapide |

### 🛠 Différences principales

#### Chemins de fichiers
```bash
# Mac
/Users/nom/OhmVision/

# PC Windows
C:\Users\nom\OhmVision\
```

#### Scripts
```bash
# Mac/Linux
./install.sh
./setup-simple.sh

# PC Windows
.\setup-windows.ps1
install-windows.bat
start-windows.bat
```

#### Commandes Docker
```bash
# Identiques sur Mac et PC
docker compose up -d
docker compose down
docker compose logs -f
```

### ⚡ Tips pour maximiser les performances PC

1. **Installer sur SSD NVMe** (pas HDD)
2. **Allouer plus de RAM à Docker** (Settings → Resources)
3. **Activer WSL 2** (plus rapide que Hyper-V)
4. **Utiliser le mode GPU** si disponible
5. **Désactiver l'antivirus pour le dossier Docker** (temporairement)

### 🔍 Troubleshooting

#### Docker lent sur Windows
- Activer WSL 2: `wsl --install`
- Installer Docker avec backend WSL 2
- Déplacer les volumes Docker sur SSD

#### GPU non reconnu
- Vérifier `nvidia-smi`
- Installer NVIDIA Container Toolkit
- Activer GPU dans Docker Desktop

#### Port déjà utilisé
```powershell
# Trouver le process
netstat -ano | findstr :8000

# Tuer le process
taskkill /PID <PID> /F
```

### 📚 Documentation

- **Guide Windows complet**: [README_WINDOWS.md](README_WINDOWS.md)
- **Guide général**: [README.md](README.md)
- **Déploiement**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

**Profitez de la puissance de votre nouveau PC ! 🚀**
