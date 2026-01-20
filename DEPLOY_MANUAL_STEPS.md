# 🚀 Déploiement Manuel OhmVision sur Hetzner

## Serveur: 195.201.123.92 (CAX11)

---

## ÉTAPE 1: Connexion SSH

Ouvrez un nouveau terminal et connectez-vous:

```bash
ssh root@195.201.123.92
# Mot de passe: Milhanou@141511
```

---

## ÉTAPE 2: Préparation du Serveur

Une fois connecté, exécutez ces commandes:

```bash
# Mise à jour du système
apt-get update && apt-get upgrade -y

# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Installation de Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Vérification
docker --version
docker-compose --version
```

---

## ÉTAPE 3: Installation des Outils

```bash
# Outils essentiels
apt-get install -y git curl wget ufw htop

# Configuration du firewall
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8554/tcp
ufw status
```

---

## ÉTAPE 4: Clonage du Repository

```bash
# Créer le répertoire
mkdir -p /opt/ohmvision
cd /opt/ohmvision

# Cloner le repository
git clone https://github.com/yacinetirichine-creator/ohmvision.git .
```

---

## ÉTAPE 5: Configuration de l'Environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer les variables d'environnement
nano .env
```

Modifiez ces valeurs dans `.env`:

```bash
# SECRETS (Générer des clés aléatoires)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# DATABASE (PostgreSQL local via Docker)
DATABASE_URL=postgresql+asyncpg://ohmvision:OhmVision2026Secure!@postgres:5432/ohmvision

# REDIS
REDIS_URL=redis://redis:6379/0

# APPLICATION
APP_ENV=production
DEBUG=false
CORS_ORIGINS=["*"]

# API KEYS (Optionnels pour IA)
ANTHROPIC_API_KEY=your_key_here  # Si vous utilisez Claude
OPENAI_API_KEY=your_key_here     # Si vous utilisez OpenAI
```

Pour sauvegarder dans nano: `Ctrl+X`, puis `Y`, puis `Enter`

---

## ÉTAPE 6: Créer le Fichier docker-compose.yml

```bash
nano docker-compose.production.yml
```

Vérifiez que le contenu contient bien les services: backend, frontend, postgres, redis, nginx

---

## ÉTAPE 7: Démarrage des Services

```bash
# Construction des images
docker-compose -f docker-compose.production.yml build

# Démarrage en arrière-plan
docker-compose -f docker-compose.production.yml up -d

# Vérifier les logs
docker-compose -f docker-compose.production.yml logs -f
```

---

## ÉTAPE 8: Initialisation de la Base de Données

```bash
# Attendre 10 secondes que PostgreSQL démarre
sleep 10

# Exécuter la migration
docker-compose -f docker-compose.production.yml exec backend python init_db.py
```

---

## ÉTAPE 9: Vérification

```bash
# Vérifier que tous les services tournent
docker-compose -f docker-compose.production.yml ps

# Test de l'API
curl http://localhost/api/health

# Logs en temps réel
docker-compose -f docker-compose.production.yml logs -f backend
```

---

## ÉTAPE 10: Accès à l'Application

L'application est maintenant accessible via:
- **HTTP**: `http://195.201.123.92`
- **API**: `http://195.201.123.92/api/docs`

---

## 🔧 Commandes Utiles

```bash
# Voir les logs
docker-compose -f docker-compose.production.yml logs -f [service]

# Redémarrer un service
docker-compose -f docker-compose.production.yml restart [service]

# Arrêter tous les services
docker-compose -f docker-compose.production.yml down

# Voir l'utilisation des ressources
docker stats

# Moniteur système
htop
```

---

## 🌐 Configuration DNS (Optionnel)

Si vous avez un nom de domaine (ex: ohmvision.com):

1. Allez chez votre registrar (OVH, Cloudflare, etc.)
2. Ajoutez un enregistrement A:
   - Type: A
   - Name: @ (ou www)
   - Value: 195.201.123.92
   - TTL: 300

3. Une fois le DNS propagé, configurez SSL avec Certbot:

```bash
# Installer Certbot
apt-get install -y certbot python3-certbot-nginx

# Obtenir un certificat SSL
certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

---

## 🆘 Dépannage

### Les services ne démarrent pas
```bash
# Voir les logs détaillés
docker-compose -f docker-compose.production.yml logs backend
docker-compose -f docker-compose.production.yml logs postgres
```

### Port déjà utilisé
```bash
# Vérifier les ports utilisés
netstat -tulpn | grep LISTEN
```

### Redémarrage complet
```bash
docker-compose -f docker-compose.production.yml down -v
docker-compose -f docker-compose.production.yml up -d --build
```
