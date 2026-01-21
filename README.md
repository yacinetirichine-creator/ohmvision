# 🎥 OhmVision - Plateforme de Vidéosurveillance IA v3.0

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/react-18+-blue.svg" alt="React">
  <img src="https://img.shields.io/badge/AI-YOLO%20v8-red.svg" alt="AI">
  <img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker">
</p>

**OhmVision** transforme vos caméras de surveillance en système de sécurité intelligent grâce à l'IA. Solution tout-en-un pour les entreprises de toutes tailles.

---

## 🚀 FONCTIONNALITÉS v3.0

### 🤖 INTELLIGENCE ARTIFICIELLE

#### Détections Vidéo
| Détection | Description | Précision |
|-----------|-------------|-----------|
| 👤 **Personnes** | Tracking multi-personnes | 95%+ |
| 🏃 **Chutes** | Alerte immédiate | 92%+ |
| 🔥 **Feu (Visuel)** | Analyse colorimétrique | 88%+ |
| 🌡️ **Feu (Thermique)** | Caméras thermiques | 98%+ |
| 📈 **Élévation T°** | Variation °C/min | 99%+ |
| 💨 **Fumée** | Pattern + couleur | 85%+ |
| 🦺 **EPI Complet** | Casque, gilet, harnais, gants | 94%+ |
| 🚗 **Véhicules** | Classification type | 96%+ |
| 🅿️ **Plaques (LPR)** | Multi-pays | 93%+ |
| 👥 **Comportements** | 10+ types | 90%+ |

#### Détections Audio 🆕
| Détection | Description | Niveau |
|-----------|-------------|--------|
| 🔊 **Verre cassé** | Fréquence 2-8kHz | ALARM |
| 😱 **Cris** | Voix humaine stress | ALARM |
| 💥 **Coup de feu** | Impulsion courte | CRITICAL |
| 💣 **Explosion** | Basse fréquence | CRITICAL |
| 🚨 **Alarme incendie** | Pattern périodique | ALARM |
| 🚗 **Alarme voiture** | Pattern reconnu | WARNING |
| 🐕 **Aboiement** | Fréquence typique | INFO |
| 🔇 **Silence anormal** | Absence de bruit | WARNING |
| 😠 **Ton agressif** | Analyse vocale | WARNING |

### 📊 ANALYTICS PAR SECTEUR (7 Verticales)

<details>
<summary><b>🛒 RETAIL</b></summary>

- Comptage visiteurs temps réel
- Heatmaps zones chaudes/froides
- Temps de présence (dwell time)
- Files d'attente intelligentes
- Taux de conversion
- Heures de pointe
- Ratio staff/clients
</details>

<details>
<summary><b>🏭 INDUSTRIE</b></summary>

- Conformité EPI temps réel
- Score sécurité automatique
- Zones dangereuses surveillées
- Détection postures à risque
- Alertes véhicules/piétons
- Near-miss tracking
- Rapport sécurité quotidien
</details>

<details>
<summary><b>🏥 SANTÉ</b></summary>

- Détection chute patients
- Temps d'attente
- Conformité masques
- Alertes urgences (Code Blue)
- Ratio soignants/patients
- Hygiène des mains
</details>

<details>
<summary><b>📦 LOGISTIQUE</b></summary>

- Comptage véhicules
- Occupation des quais
- Temps de chargement
- Piétons en zone véhicules
- Comptage palettes
- Zones de goulot
</details>

<details>
<summary><b>🏗️ CHANTIERS</b></summary>

- Casque obligatoire 100%
- Gilet haute visibilité
- Harnais pour hauteur
- Zones d'exclusion
- Incidents évités
- Comportements dangereux
</details>

<details>
<summary><b>🅿️ PARKINGS</b></summary>

- Occupation temps réel
- Places par zone/niveau
- Reconnaissance plaques
- VIP / Liste noire
- Durée moyenne
- Véhicules abandonnés
</details>

<details>
<summary><b>🌆 SMART CITY</b></summary>

- Densité trafic
- Comptage multimodal
- Détection accidents
- Formation de foule
- Dépôts sauvages
- Sécurité publique
</details>

### 🎨 INTERFACE MODERNE

#### Vue Multi-Caméras
- ✅ Layouts configurables: 1x1, 2x2, 3x3, 4x4
- ✅ Overlay détections temps réel (bounding boxes)
- ✅ Compteurs LIVE sur chaque caméra
- ✅ Indicateur LIVE + REC
- ✅ Fullscreen par double-clic
- ✅ Pagination pour >16 caméras

#### Plan Interactif du Site 🆕
- ✅ Vue 2D du bâtiment avec positions caméras
- ✅ Zoom et pan fluides
- ✅ Champ de vision des caméras
- ✅ Zones de détection visuelles
- ✅ Alertes géolocalisées
- ✅ Heatmap overlay
- ✅ Multi-étages

#### Timeline Vidéo 🆕
- ✅ Lecture avec buffer pré-événement
- ✅ Marqueurs d'événements sur timeline
- ✅ Vitesse de lecture variable (0.5x - 8x)
- ✅ Export de clips
- ✅ Prévisualisation au survol
- ✅ Navigation par date/heure

#### Contrôle PTZ & Zoom 🆕
- ✅ Contrôle Pan-Tilt-Zoom complet
- ✅ 8 préréglages par caméra
- ✅ Zoom numérique jusqu'à 8x
- ✅ Focus, Iris, Luminosité
- ✅ Auto-tracking (suivre un objet)
- ✅ Grille et viseur

#### Thèmes Personnalisables 🆕
- ✅ Mode sombre / clair
- ✅ 6 thèmes: Dark, Light, Midnight, Ocean, Forest, Sunset
- ✅ 9 couleurs d'accent
- ✅ Prévisualisation en direct

### 🔔 NOTIFICATIONS MULTI-CANAL

| Canal | Support | Configuration |
|-------|---------|---------------|
| 📧 Email | ✅ | SMTP |
| 📱 Telegram | ✅ | Bot Token |
| 💬 Discord | ✅ | Webhook |
| 📲 SMS | ✅ | Twilio |
| 🔔 Slack | ✅ | Webhook |
| 👥 Teams | ✅ | Webhook |
| 🔗 Webhook | ✅ | URL personnalisée |

**Fonctionnalités:**
- Filtrage par sévérité / type / caméra
- Rate limiting & cooldown anti-spam
- Snapshot inclus dans les alertes

### 📹 ENREGISTREMENT INTELLIGENT

- **Pre-event buffer**: 10 secondes avant l'alerte
- **Post-event**: 30 secondes après
- **Conversion H.264**: Compatible navigateurs
- **Gestion stockage**: Nettoyage automatique
- **Rétention configurable**: 7-365 jours

### 📄 RAPPORTS PDF

- Journalier / Hebdomadaire / Mensuel
- Rapport d'incident détaillé
- Audit conformité EPI
- Synthèse exécutive
- Graphiques et KPIs
- Insights IA + Recommandations

---

## 📁 STRUCTURE DU PROJET

```
ohmvision-platform/
│
├── 📂 backend/
│   ├── 📂 ai/
│   │   ├── engine.py              # Moteur YOLO
│   │   ├── thermal_fire_detector.py # Feu thermique
│   │   ├── audio_analytics.py     # 🆕 Détection audio
│   │   ├── industry_analytics.py  # Analytics sectoriels
│   │   ├── behavior_analytics.py  # Comportements
│   │   ├── plate_recognition.py   # LPR/ANPR
│   │   └── predictive_engine.py   # Prédiction
│   │
│   ├── 📂 api/
│   │   ├── auth.py, cameras.py, alerts.py
│   │   ├── discovery.py, setup.py, streaming.py
│   │   └── advanced_analytics.py
│   │
│   ├── 📂 services/
│   │   ├── notification_manager.py
│   │   ├── smart_recorder.py
│   │   ├── report_generator.py
│   │   └── stream_manager.py
│   │
│   └── 📂 core/
│       └── pricing.py             # Packages & tarifs
│
├── 📂 frontend-client/src/
│   ├── 📂 components/
│   │   ├── MultiCameraView.jsx    # Vue multi-caméras
│   │   ├── InteractiveSiteMap.jsx # 🆕 Plan interactif
│   │   ├── VideoTimelinePlayer.jsx # 🆕 Timeline vidéo
│   │   ├── PTZControl.jsx         # 🆕 Contrôle PTZ
│   │   ├── ThemeSystem.jsx        # 🆕 Thèmes
│   │   ├── RealTimeStats.jsx      # Stats temps réel
│   │   └── LiveStream.jsx
│   │
│   └── 📂 pages/
│       ├── ModernDashboard.jsx
│       ├── ExecutiveDashboard.jsx
│       ├── NotificationsConfig.jsx
│       └── ...
│
├── PRICING.md                     # Guide tarifs
├── Dockerfile.allinone
├── docker-compose.yml
├── install.sh / install-windows.bat
└── README.md
```

---

## 💰 PACKAGES & TARIFS

| Plan | Prix | Caméras | Fonctionnalités clés |
|------|------|---------|---------------------|
| **FREE** | 0€ | 1-2 | Détections base, 24h historique |
| **HOME** | 29€ unique | 1-4 | Feu/fumée visuel, 7j historique |
| **PRO** | 99€/an | 5-16 | Analytics sectoriels, Notifications |
| **BUSINESS** | 299€/an | 17-50 | 🔥 Thermique, LPR, Audio, PDF |
| **ENTERPRISE** | Sur devis | Illimité | Tout + Support dédié |

**Options:**
- 🌡️ Caméras Thermiques: +15€/mois
- 🅿️ LPR Avancé: +10€/mois
- 🔊 Détection Audio: +10€/mois
- ☁️ Cloud +50GB: +5€/mois

---

## 🚀 INSTALLATION

### Option 1: **Railway (Recommandé - Production)**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/ohmvision)

```bash
# Ou via CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

📖 Guide complet: [DEPLOYMENT_RAILWAY_COMPLETE.md](DEPLOYMENT_RAILWAY_COMPLETE.md)

### Option 2: Script automatique (Local)

**Windows:**
```cmd
.\setup-windows.ps1
# Ou: start-windows.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh && ./install.sh
```

### Option 3: Docker

```bash
docker build -t ohmvision:latest -f Dockerfile.allinone .
docker run -d -p 8080:8080 --name ohmvision ohmvision:latest
# Ouvrir http://localhost:8080
```

### Option 4: Développement local

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend-client && npm install && npm run dev
# Ouvrir http://localhost:5173
```

---

## ☁️ DÉPLOIEMENT PRODUCTION

| Plateforme | Difficulté | Coût | Documentation |
|------------|------------|------|---------------|
| **Railway** ⭐ | Facile | ~$35/mois | [Guide](DEPLOYMENT_RAILWAY_COMPLETE.md) |
| Render | Facile | ~$25/mois | - |
| Vercel + Supabase | Moyen | ~$20/mois | - |
| AWS/GCP | Expert | Variable | - |

---

## 📊 COMPARAISON CONCURRENCE

| Fonctionnalité | OhmVision | Milestone | Genetec | Hikvision |
|----------------|-----------|-----------|---------|-----------|
| Prix entrée | **GRATUIT** | ~1000€ | ~2000€ | ~500€ |
| Analytics sectoriels | ✅ **7** | ❌ | Partiel | ❌ |
| Détection audio | ✅ **17 types** | Plugin | Plugin | Basique |
| LPR inclus | ✅ | Option | Option | Option |
| Détection thermique | ✅ | Option | Option | Option |
| Plan interactif | ✅ | ✅ | ✅ | ❌ |
| Timeline vidéo | ✅ | ✅ | ✅ | ✅ |
| PTZ control | ✅ | ✅ | ✅ | ✅ |
| Thèmes | ✅ **6** | ❌ | ❌ | ❌ |
| Open Source | ✅ | ❌ | ❌ | ❌ |
| Installation | **1 click** | Complexe | Complexe | Moyen |

---

## 🔒 SÉCURITÉ

- ✅ Authentification JWT
- ✅ HTTPS/TLS
- ✅ Données chiffrées
- ✅ RGPD compliant
- ✅ Logs d'audit
- ✅ Rôles et permissions

---

## 📞 SUPPORT

- 📧 Email: contact@ohmvision.fr
- 📖 Documentation: https://docs.ohmvision.fr
- 🐛 Issues: GitHub

---

## 📜 LICENCE

© 2024 OhmVision by Ohmtronic. Tous droits réservés.

---

<p align="center">
  <b>🚀 La solution de vidéosurveillance IA la plus complète du marché</b>
</p>
