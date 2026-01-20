# 🔌 OhmVision - Système Multi-Canal de Connexion Caméra

## 🎯 Vue d'ensemble

OhmVision est désormais une plateforme **TOUT-EN-UN** pour la connexion et la gestion de caméras de vidéosurveillance, supportant **tous les types de connexion** et **tous les fabricants majeurs**.

---

## ✨ Nouvelles Fonctionnalités v3.1

### 🌐 Connexion Multi-Canal

OhmVision supporte maintenant **12 types de connexion** différents :

| Type | Description | Utilisation |
|------|-------------|-------------|
| 🎥 **RTSP** | Real-Time Streaming Protocol | Caméras IP professionnelles |
| 📺 **RTMP** | Real-Time Messaging Protocol | Streaming live, encoders |
| 🔧 **ONVIF** | Open Network Video Interface | Auto-découverte, PTZ |
| 🌍 **HTTP/MJPEG** | Motion JPEG over HTTP | Caméras anciennes, webcams |
| 🔒 **HTTPS** | HTTP Secure | Connexions sécurisées |
| 🌐 **WebRTC** | Web Real-Time Communication | Navigateurs, faible latence |
| 📡 **HLS** | HTTP Live Streaming | Streaming adaptatif |
| ☁️ **Cloud API** | APIs fabricants (Nest, Ring, Arlo) | Caméras cloud |
| 🔔 **Webhook** | Push notifications | Événements caméra |
| 📼 **NVR/DVR** | Enregistreurs réseau | Systèmes existants |
| 💻 **USB** | Caméras USB locales | Webcams, caméras PC |
| 📁 **Fichier** | Vidéos enregistrées | Tests, replay |

---

## 🏭 Fabricants Supportés (21+)

### Professionnels
- **Hikvision** 🇨🇳 - Leader mondial
- **Dahua** 🇨🇳 - 2ème fabricant mondial
- **Axis** 🇸🇪 - Haute qualité
- **Bosch** 🇩🇪 - Industriel
- **Hanwha** 🇰🇷 - Samsung Techwin
- **Avigilon** 🇨🇦 - Analytics avancées

### Grand Public
- **Foscam** - Caméras WiFi
- **TP-Link** - Tapo/Kasa
- **Reolink** - DIY populaire
- **Xiaomi** - Mi Home
- **Vivotek** - Taiwan
- **Uniview** - Concurrent Hikvision

### Cloud
- **Google Nest** ☁️
- **Amazon Ring** ☁️
- **Arlo** ☁️
- **Wyze** ☁️

### Autres
- **Sony**, **Panasonic**, **Mobotix**, **Generic**

---

## 🚀 Auto-Détection Intelligente

### Comment ça marche ?

1. **Scan réseau** - Détecte tous les appareils IP
2. **Découverte ONVIF** - Identifie les caméras compatibles
3. **Test multi-canal** - Essaie toutes les méthodes de connexion
4. **Sélection optimale** - Choisit la meilleure méthode

```python
# Exemple d'utilisation
POST /api/discovery/auto-detect
{
  "ip": "192.168.1.100",
  "username": "admin",
  "password": "password123",
  "manufacturer": "hikvision"  # optionnel
}

# Réponse
{
  "success": true,
  "recommended_method": "rtsp",
  "recommended_url": "rtsp://admin:password123@192.168.1.100:554/Streaming/Channels/101",
  "all_results": [
    {
      "success": true,
      "connection_type": "rtsp",
      "response_time_ms": 245,
      "resolution": "1920x1080",
      "fps": 25.0
    }
  ]
}
```

---

## 📊 Surveillance de Santé (Health Check)

### Fonctionnalités

✅ **Vérification périodique** - Toutes les 60 secondes par défaut  
✅ **Détection offline** - Alerte immédiate  
✅ **Reconnexion automatique** - Backoff exponentiel  
✅ **Statistiques uptime** - 30 derniers jours  
✅ **Scoring santé** - Excellent / Good / Fair / Poor / Offline

### Niveaux de Santé

| Niveau | Temps de Réponse | Description |
|--------|------------------|-------------|
| 🟢 **Excellent** | < 500ms | Connexion parfaite |
| 🔵 **Good** | 500-1500ms | Connexion stable |
| 🟡 **Fair** | 1500-3000ms | Connexion acceptable |
| 🟠 **Poor** | > 3000ms | Connexion lente |
| 🔴 **Offline** | Timeout | Pas de connexion |

### API Health Check

```bash
# Statut global du système
GET /api/health/status

# Santé de toutes les caméras
GET /api/health/cameras

# Santé d'une caméra spécifique
GET /api/health/cameras/{id}

# Statut de reconnexion
GET /api/health/cameras/{id}/reconnection

# Forcer un check
POST /api/health/cameras/{id}/check-now

# Forcer une reconnexion
POST /api/health/cameras/{id}/reconnect
```

---

## 🔄 Reconnexion Automatique

### Stratégie de Reconnexion

Le système utilise un **backoff exponentiel** pour éviter la surcharge :

| Tentative | Délai | Cumul |
|-----------|-------|-------|
| 1 | 10s | 10s |
| 2 | 20s | 30s |
| 3 | 40s | 1m10s |
| 4 | 80s | 2m30s |
| 5 | 160s | 5m10s |
| Max | 300s | - |

Après 5 échecs, la reconnexion automatique s'arrête. Vous pouvez :
- Forcer une reconnexion manuelle
- Corriger les paramètres de connexion
- Le système retente automatiquement après mise à jour

---

## 📝 Templates par Fabricant

### Hikvision

```python
# URLs RTSP
rtsp://{user}:{pass}@{ip}:554/Streaming/Channels/101  # Main stream
rtsp://{user}:{pass}@{ip}:554/Streaming/Channels/102  # Sub stream

# URL HTTP
http://{ip}/ISAPI/Streaming/channels/1/httpPreview

# Snapshot
http://{ip}/ISAPI/Streaming/channels/1/picture
```

### Dahua

```python
# URLs RTSP
rtsp://{user}:{pass}@{ip}:554/cam/realmonitor?channel=1&subtype=0  # Main
rtsp://{user}:{pass}@{ip}:554/cam/realmonitor?channel=1&subtype=1  # Sub

# Snapshot
http://{ip}/cgi-bin/snapshot.cgi?channel=1
```

### Axis

```python
# URLs RTSP
rtsp://{user}:{pass}@{ip}:554/axis-media/media.amp

# HTTP MJPEG
http://{ip}/mjpg/video.mjpg

# Snapshot
http://{ip}/axis-cgi/jpg/image.cgi
```

> Voir [camera_profiles.py](backend/services/camera_profiles.py) pour tous les templates

---

## 🎯 Utilisation

### 1. Scan Réseau Complet

```bash
# Démarrer un scan
POST /api/discovery/scan/start

# Vérifier le statut
GET /api/discovery/scan/status

# Arrêter le scan
POST /api/discovery/scan/stop
```

### 2. Découverte ONVIF Seule

```bash
POST /api/discovery/onvif/discover
```

### 3. Auto-Détection d'une Caméra

```bash
POST /api/discovery/auto-detect
{
  "ip": "192.168.1.100",
  "username": "admin",
  "password": "admin123"
}
```

### 4. Test Batch de Caméras

```bash
POST /api/discovery/batch-test
[
  {"ip": "192.168.1.100", "username": "admin", "password": "pass1"},
  {"ip": "192.168.1.101", "username": "admin", "password": "pass2"},
  {"ip": "192.168.1.102", "username": "admin", "password": "pass3"}
]
```

### 5. Obtenir les Templates d'un Fabricant

```bash
GET /api/discovery/stream-templates/hikvision
```

### 6. Générer les URLs pour une Caméra

```bash
POST /api/discovery/generate-urls
{
  "ip": "192.168.1.100",
  "username": "admin",
  "password": "admin123",
  "manufacturer": "hikvision"
}
```

---

## 🔧 Configuration du Modèle Camera

### Nouveaux Champs

```python
class Camera:
    # Manufacturer
    manufacturer: CameraManufacturer  # hikvision, dahua, axis, etc.
    model: str
    firmware_version: str
    serial_number: str
    
    # Connection Type
    connection_type: ConnectionType  # rtsp, onvif, http_mjpeg, etc.
    primary_stream_url: str
    secondary_stream_url: str  # Stream basse qualité
    snapshot_url: str
    
    # Advanced Config
    connection_config: dict  # timeout, retry, transport, etc.
    cloud_config: dict  # Pour APIs cloud
    
    # Health Monitoring
    connection_health: str  # excellent, good, fair, poor, offline
    last_health_check: datetime
    uptime_percentage: float
    failed_connection_attempts: int
    last_error_message: str
```

---

## 📈 Statistiques & Analytics

### Métriques Disponibles

- **Uptime %** - Disponibilité sur 30 jours
- **Temps de réponse moyen** - Performance connexion
- **Nombre de déconnexions** - Fiabilité
- **Tentatives de reconnexion** - Diagnostics
- **Distribution de santé** - Vue d'ensemble

### Dashboard Health

```bash
GET /api/health/status
```

Retourne :
```json
{
  "total_cameras": 25,
  "online_cameras": 23,
  "offline_cameras": 2,
  "average_uptime": 98.5,
  "cameras_excellent": 15,
  "cameras_good": 7,
  "cameras_fair": 1,
  "cameras_poor": 0,
  "cameras_offline": 2
}
```

---

## 🔐 Sécurité

### Bonnes Pratiques

✅ **Credentials chiffrés** - Passwords stockés de manière sécurisée  
✅ **HTTPS recommandé** - Pour les connexions HTTP  
✅ **Authentification forte** - Mots de passe complexes  
✅ **VLAN séparé** - Isoler le réseau caméras  
✅ **Mise à jour firmware** - Patch de sécurité réguliers  
✅ **Monitoring actif** - Détection d'anomalies

---

## 🚦 Migration depuis Ancienne Version

Si vous avez déjà des caméras configurées :

1. **Pas d'action requise** - Compatibilité totale
2. Les champs `rtsp_url`, `ip_address`, `port` restent fonctionnels
3. Le système détecte automatiquement le type de connexion
4. Vous pouvez migrer progressivement vers les nouveaux champs

### Migration Automatique

```python
# L'API reconnaît automatiquement :
{
  "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/stream1"
}

# Et crée :
{
  "connection_type": "rtsp",
  "primary_stream_url": "rtsp://admin:pass@192.168.1.100:554/stream1",
  "ip_address": "192.168.1.100",
  "port": 554
}
```

---

## 📚 Documentation API Complète

### Discovery Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/discovery/network-info` | GET | Info réseau local |
| `/api/discovery/scan/start` | POST | Scan réseau complet |
| `/api/discovery/scan/status` | GET | Statut du scan |
| `/api/discovery/onvif/discover` | POST | Découverte ONVIF |
| `/api/discovery/auto-detect` | POST | **Auto-détection intelligente** |
| `/api/discovery/batch-test` | POST | Test multiple caméras |
| `/api/discovery/manufacturers` | GET | Liste fabricants supportés |
| `/api/discovery/stream-templates/{mfr}` | GET | Templates fabricant |
| `/api/discovery/generate-urls` | POST | Générer URLs |

### Health Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health/status` | GET | **Statut global système** |
| `/api/health/cameras` | GET | Santé toutes caméras |
| `/api/health/cameras/{id}` | GET | Santé caméra spécifique |
| `/api/health/cameras/{id}/reconnection` | GET | Statut reconnexion |
| `/api/health/cameras/{id}/check-now` | POST | Forcer health check |
| `/api/health/cameras/{id}/reconnect` | POST | Forcer reconnexion |

---

## 🎓 Exemples d'Utilisation

### Scénario 1 : Ajout Simple d'une Caméra Hikvision

```bash
# 1. Auto-détection
curl -X POST http://localhost:8000/api/discovery/auto-detect \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.168.1.100",
    "username": "admin",
    "password": "Hik12345",
    "manufacturer": "hikvision"
  }'

# 2. Créer la caméra avec l'URL recommandée
curl -X POST http://localhost:8000/api/cameras/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Entrée Principale",
    "ip_address": "192.168.1.100",
    "primary_stream_url": "rtsp://admin:Hik12345@192.168.1.100:554/Streaming/Channels/101",
    "connection_type": "rtsp",
    "manufacturer": "hikvision"
  }'
```

### Scénario 2 : Scan Complet du Réseau

```bash
# 1. Démarrer le scan
curl -X POST http://localhost:8000/api/discovery/scan/start

# 2. Vérifier la progression
curl http://localhost:8000/api/discovery/scan/status

# Réponse :
{
  "status": "scanning",
  "progress": 75,
  "scanned_ips": 191,
  "total_ips": 254,
  "devices": [
    {
      "ip": "192.168.1.100",
      "manufacturer": "Hikvision",
      "is_onvif": true,
      "rtsp_url": "rtsp://192.168.1.100:554/Streaming/Channels/101"
    }
  ]
}
```

### Scénario 3 : Monitoring Santé

```bash
# Dashboard santé global
curl http://localhost:8000/api/health/status

# Détails d'une caméra
curl http://localhost:8000/api/health/cameras/1

# Si offline, forcer reconnexion
curl -X POST http://localhost:8000/api/health/cameras/1/reconnect
```

---

## 🔮 Roadmap Future

### À venir

- [ ] Support WebRTC natif
- [ ] Intégration Frigate NVR
- [ ] Support Wyze RTSP
- [ ] APIs Eufy, Unifi Protect
- [ ] Auto-tuning qualité stream
- [ ] Failover multi-stream
- [ ] Edge recording local
- [ ] P2P direct connection

---

## 💡 Support

Pour toute question ou problème :

- 📧 **Email** : support@ohmvision.com
- 📚 **Documentation** : https://docs.ohmvision.com
- 💬 **Discord** : https://discord.gg/ohmvision
- 🐛 **Issues** : https://github.com/ohmvision/issues

---

## 📄 Licence

OhmVision © 2026 - Tous droits réservés
