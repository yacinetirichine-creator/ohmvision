# 🚀 Guide de Démarrage Rapide - OhmVision

**Transformez vos caméras en système de sécurité intelligent en 5 minutes !**

---

## ⚡ Installation Express

### Option 1: Script Automatique (Recommandé)

```bash
cd ohmvision-platform
./install-dev.sh
```

Le script va:
- ✅ Vérifier les pré-requis (Python, Docker, Node.js)
- ✅ Créer l'environnement virtuel Python
- ✅ Installer toutes les dépendances
- ✅ Configurer PostgreSQL et Redis (Docker)
- ✅ Initialiser la base de données
- ✅ Lancer les tests

### Option 2: Installation Manuelle

```bash
# 1. Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Base de données (Docker)
cd ..
docker-compose up -d postgres redis

# 3. Initialiser DB
cd backend
python init_db.py

# 4. Frontend
cd ../frontend-client
npm install
```

---

## 🎮 Démarrage

### Terminal 1: Backend API

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**✅ API accessible:** http://localhost:8000
**📚 Documentation:** http://localhost:8000/docs

### Terminal 2: Frontend

```bash
cd frontend-client
npm run dev
```

**✅ Application:** http://localhost:5173

---

## 📹 Ajouter Votre Première Caméra

### 1. Accéder à l'application
Ouvrez http://localhost:5173

### 2. Créer un compte
- Email: `admin@test.com`
- Password: `admin123`

### 3. Setup Wizard
L'assistant de configuration s'affiche automatiquement:

#### Étape 1: Découverte automatique
- Cliquez sur "Scanner le réseau"
- OhmVision détecte toutes les caméras ONVIF

#### Étape 2: Configuration caméra
- Nom: `Entrée principale`
- URL RTSP: `rtsp://192.168.1.100:554/stream`
- Username: `admin`
- Password: `[votre mot de passe]`

#### Étape 3: Détections IA
Activez les détections souhaitées:
- ✅ Personnes
- ✅ Véhicules
- ✅ Chutes (si package HOME+)
- ✅ Détection feu

#### Étape 4: Zones de surveillance
- Dessinez les zones d'intérêt sur l'image
- Configurez les alertes par zone

### 4. C'est prêt !
Votre caméra analyse maintenant en temps réel 🎉

---

## 🧪 Tests

```bash
cd backend
source venv/bin/activate

# Tests rapides
pytest tests/test_suite.py -v

# Tests avec couverture
pytest tests/test_suite.py --cov=backend --cov-report=html

# Voir le rapport
open htmlcov/index.html
```

---

## 📊 Fonctionnalités Principales

### 🤖 IA Intégrée
- **Détection personnes** - Comptage, tracking
- **Détection véhicules** - Classification type
- **Détection chutes** - Alerte immédiate
- **Détection feu/fumée** - Prévention incendie
- **EPI conformité** - Casque, gilet (PRO+)
- **Reconnaissance plaques** - LPR (BUSINESS+)

### 📈 Analytics Temps Réel
- Comptage entrées/sorties
- Heatmaps de présence
- Temps de présence (dwell time)
- Détection comportements suspects

### 🔔 Alertes Intelligentes
- Email instantané
- Notifications push
- SMS (PRO+)
- Webhooks (BUSINESS+)

### 🔒 RGPD Compliant
- Anonymisation automatique
- Consentements gérés
- Droit à l'oubli
- Export de données

---

## 🐛 Dépannage

### Erreur: Cannot connect to PostgreSQL

```bash
# Vérifier que Docker est lancé
docker ps

# Démarrer PostgreSQL
docker-compose up -d postgres

# Vérifier les logs
docker logs ohmvision-db
```

### Erreur: Port 8000 already in use

```bash
# Trouver le processus
lsof -i :8000

# Tuer le processus
kill -9 [PID]
```

### Erreur: YOLO model not found

```bash
# Télécharger le modèle YOLO
cd backend
source venv/bin/activate
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Erreur: Permission denied (install-dev.sh)

```bash
chmod +x install-dev.sh
./install-dev.sh
```

---

## 🎯 Prochaines Étapes

1. **Personnaliser `.env`**
   - Ajouter votre clé Stripe
   - Configurer l'email SMTP
   - Activer Sentry (monitoring)

2. **Ajouter plus de caméras**
   - Jusqu'à 2 en FREE
   - Jusqu'à 4 en HOME (29€)
   - Jusqu'à 16 en PRO (99€/an)

3. **Explorer les analytics**
   - Dashboard exécutif
   - Rapports PDF
   - Export CSV

4. **Configurer les alertes**
   - Email, SMS, Telegram
   - Webhooks personnalisés
   - Intégration Slack/Discord

---

## 📚 Documentation Complète

- **Architecture**: `ARCHITECTURE_SCALABLE.md`
- **Plan d'action**: `PLAN_ACTION.md`
- **API**: http://localhost:8000/docs
- **Tests**: `backend/tests/test_suite.py`

---

## 💡 Exemples d'Utilisation

### Retail (Magasin)
- Comptage visiteurs temps réel
- Heatmaps zones chaudes
- Temps d'attente en caisse
- Taux de conversion

### Industrie
- Conformité EPI (casque, gilet)
- Zones dangereuses
- Détection chute
- Score sécurité

### Résidentiel
- Détection intrusion
- Alerte chute personne âgée
- Détection feu/fumée
- Notifications mobiles

---

## 🆘 Support

- **Email**: support@ohmvision.com
- **Discord**: https://discord.gg/ohmvision
- **GitHub Issues**: https://github.com/ohmvision/platform/issues

---

**Prêt à démarrer ? Lancez `./install-dev.sh` !** 🚀
