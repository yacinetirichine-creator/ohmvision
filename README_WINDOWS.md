# 🎥 OhmVision - Installation Windows/PC

Guide d'installation et configuration pour **Windows 10/11** avec support GPU NVIDIA.

---

## 📋 Prérequis

### Configuration minimale
- **OS**: Windows 10 (64-bit) ou Windows 11
- **RAM**: 8 GB minimum, 16 GB recommandé
- **CPU**: Intel Core i5 ou AMD Ryzen 5 (4 cœurs minimum)
- **Disque**: 50 GB d'espace libre (SSD recommandé)
- **Réseau**: Connexion Internet pour l'installation

### Configuration recommandée avec GPU
- **GPU**: NVIDIA GTX 1060 ou supérieur
- **RAM**: 16 GB ou plus
- **CUDA**: Version 11.8 ou 12.x
- **Disque**: 100 GB d'espace libre (SSD NVMe)

---

## 🚀 Installation rapide

### Option 1: Script PowerShell (Recommandé)

1. **Ouvrir PowerShell en tant qu'Administrateur**
   - Clic droit sur le menu Démarrer → "Windows PowerShell (Admin)"

2. **Naviguer vers le dossier du projet**
   ```powershell
   cd C:\chemin\vers\ohmvision
   ```

3. **Exécuter le script d'installation**
   ```powershell
   PowerShell -ExecutionPolicy Bypass -File setup-windows.ps1
   ```

Le script va automatiquement:
- ✅ Vérifier et installer Docker Desktop si nécessaire
- ✅ Détecter votre GPU NVIDIA (si présent)
- ✅ Créer les dossiers nécessaires
- ✅ Configurer l'environnement
- ✅ Démarrer tous les services

### Option 2: Installation manuelle avec Docker

1. **Installer Docker Desktop**
   - Télécharger depuis: https://www.docker.com/products/docker-desktop
   - Installer et redémarrer l'ordinateur
   - Démarrer Docker Desktop

2. **Cloner ou extraire le projet**
   ```cmd
   cd C:\Projects
   git clone https://github.com/votre-repo/ohmvision.git
   cd ohmvision
   ```

3. **Créer le fichier .env**
   ```cmd
   copy .env.example .env
   ```

4. **Démarrer les services**
   ```cmd
   docker compose up -d --build
   ```

### Option 3: Script Batch simple

Double-cliquer sur `install-windows.bat` ou:

```cmd
install-windows.bat
```

---

## 🎮 Support GPU NVIDIA (Accélération CUDA)

### Vérifier votre GPU

```powershell
nvidia-smi
```

Si la commande fonctionne, vous avez un GPU NVIDIA compatible.

### Installation des drivers CUDA

1. **Installer NVIDIA Driver** (dernière version)
   - https://www.nvidia.com/Download/index.aspx

2. **Installer CUDA Toolkit** (version 11.8 ou 12.x)
   - https://developer.nvidia.com/cuda-downloads

3. **Installer cuDNN** (optionnel, pour meilleures performances)
   - https://developer.nvidia.com/cudnn

### Activer GPU dans OhmVision

#### Méthode 1: Docker Compose avec GPU

```cmd
docker compose -f docker-compose.gpu.yml up -d
```

#### Méthode 2: Installation Python avec GPU

```cmd
cd backend
pip install -r requirements-gpu.txt
```

### Vérifier que le GPU est utilisé

```python
import torch
print(f"CUDA disponible: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

---

## 📂 Structure des dossiers Windows

```
C:\Users\VotreNom\OhmVision\
├── data\              # Base de données et cache
├── recordings\        # Enregistrements vidéo
└── logs\             # Fichiers de logs
```

---

## 🔧 Configuration

### Fichier .env

Éditez `.env` avec Notepad++ ou VS Code:

```env
# Base de données
DATABASE_URL=postgresql+asyncpg://ohmvision:votreMotDePasse@postgres:5432/ohmvision

# Redis (cache)
REDIS_URL=redis://redis:6379/0

# Sécurité
SECRET_KEY=votre-clé-secrète-très-longue
JWT_SECRET_KEY=votre-jwt-secret-très-long

# IA (optionnel)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# GPU (si disponible)
CUDA_VISIBLE_DEVICES=0
```

---

## 🌐 Accès aux services

Une fois installé, accédez à:

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | Backend FastAPI |
| **Documentation API** | http://localhost:8000/docs | Swagger UI |
| **Interface Admin** | http://localhost:3000 | Panneau d'administration |
| **Application** | http://localhost:3001 | Interface utilisateur |

### Identifiants par défaut

```
Email: admin@ohmvision.fr
Mot de passe: admin123
```

⚠️ **Changez ces identifiants immédiatement après la première connexion !**

---

## 🛠 Commandes utiles

### Docker Compose

```cmd
# Démarrer
docker compose up -d

# Arrêter
docker compose down

# Voir les logs
docker compose logs -f

# Redémarrer un service
docker compose restart backend

# Reconstruire
docker compose up -d --build

# Voir l'état des services
docker compose ps
```

### Gestion des containers

```cmd
# Liste des containers
docker ps

# Logs d'un container spécifique
docker logs ohmvision-api

# Accéder au shell d'un container
docker exec -it ohmvision-api bash
```

---

## 🐛 Résolution des problèmes

### Docker ne démarre pas

1. Vérifier que la virtualisation est activée dans le BIOS
2. Activer Hyper-V (Windows 10 Pro/Enterprise):
   ```powershell
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```
3. Activer WSL 2:
   ```powershell
   wsl --install
   wsl --set-default-version 2
   ```

### Port déjà utilisé

Si le port 8000 ou 3000 est utilisé:

```powershell
# Trouver le processus utilisant le port
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

Ou modifier les ports dans `docker-compose.yml`.

### GPU non détecté

1. Vérifier l'installation CUDA:
   ```cmd
   nvcc --version
   ```

2. Installer NVIDIA Container Toolkit pour Docker:
   https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

3. Vérifier dans Docker Desktop:
   - Settings → Resources → WSL Integration → Enable GPU

### Erreurs de mémoire

Si vous manquez de RAM:

1. Augmenter la mémoire allouée à Docker:
   - Docker Desktop → Settings → Resources → Memory: 8 GB minimum

2. Limiter les services actifs dans `docker-compose.yml`

### Performance lente

1. **Utiliser un SSD** pour le projet et Docker
2. **Désactiver l'antivirus** pour le dossier Docker (temporairement)
3. **Augmenter les ressources Docker** (CPU et RAM)
4. **Activer WSL 2** au lieu d'Hyper-V

---

## 🚀 Optimisation pour PC puissant

### Configuration haute performance

Si vous avez un PC puissant (16+ GB RAM, GPU NVIDIA):

1. **Éditer docker-compose.yml**:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '4'
             memory: 8G
           reservations:
             devices:
               - driver: nvidia
                 count: 1
                 capabilities: [gpu]
   ```

2. **Activer tous les workers Celery**:
   ```yaml
   celery:
     command: celery -A core.celery worker --loglevel=info --concurrency=8
   ```

3. **Installer la version GPU**:
   ```cmd
   cd backend
   pip install -r requirements-gpu.txt
   ```

### Variables d'environnement pour GPU

Ajouter dans `.env`:

```env
# GPU Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=7.5;8.0;8.6
OMP_NUM_THREADS=8
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

---

## 📊 Monitoring des ressources

### Surveiller l'utilisation du GPU

```cmd
# En continu
nvidia-smi -l 1

# Utilisation mémoire
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### Surveiller Docker

```cmd
# Stats en temps réel
docker stats

# Utilisation disque
docker system df
```

---

## 🔄 Mise à jour

```cmd
# Arrêter les services
docker compose down

# Récupérer les dernières modifications
git pull

# Reconstruire et redémarrer
docker compose up -d --build
```

---

## 📞 Support

- **Documentation**: Voir README.md principal
- **Issues**: https://github.com/votre-repo/ohmvision/issues
- **Discord**: [Lien vers votre Discord]

---

## 📝 Différences Mac → PC

### Chemins de fichiers
- Mac: `/Users/nom/OhmVision/`
- PC: `C:\Users\nom\OhmVision\`

### Commandes
- Mac/Linux: `./install.sh`
- PC: `.\setup-windows.ps1` ou `install-windows.bat`

### GPU
- Mac M1/M2: Metal (MPS)
- PC NVIDIA: CUDA
- PC AMD: ROCm (support limité)

### Docker
- Mac: Docker Desktop (inclut VM)
- PC: Docker Desktop + WSL 2 (recommandé)

---

## ✅ Checklist post-installation

- [ ] Docker Desktop installé et démarré
- [ ] Services OhmVision en cours d'exécution (`docker ps`)
- [ ] Accès à http://localhost:8000/docs
- [ ] Connexion avec identifiants par défaut
- [ ] Changement du mot de passe admin
- [ ] Configuration du fichier .env
- [ ] Test d'une caméra de démonstration
- [ ] Vérification des logs (`docker compose logs -f`)

---

**Bon développement sur votre nouveau PC ! 🚀**
