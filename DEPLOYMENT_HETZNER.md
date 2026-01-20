# 🚀 Déploiement OhmVision sur Hetzner Cloud

Guide complet pour déployer OhmVision sur un VPS Hetzner Cloud avec Docker, Nginx, SSL, et PostgreSQL.

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Choix du serveur Hetzner](#choix-du-serveur-hetzner)
3. [Déploiement automatique](#déploiement-automatique)
4. [Déploiement manuel (étape par étape)](#déploiement-manuel)
5. [Configuration DNS](#configuration-dns)
6. [Monitoring et Maintenance](#monitoring-et-maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Backups](#backups)

---

## ✅ Prérequis

### Votre machine locale
- SSH client installé
- Git installé
- Clé SSH générée (`ssh-keygen -t rsa -b 4096`)

### Compte Hetzner Cloud
1. Créer un compte sur [hetzner.com](https://www.hetzner.com/cloud)
2. Ajouter un moyen de paiement
3. Crédits: ~5€ minimum pour démarrer

### Nom de domaine
- Nom de domaine configuré (ex: ohmvision.com)
- Accès aux paramètres DNS

---

## 💻 Choix du Serveur Hetzner

### Recommandations selon votre usage

| Serveur | Prix/mois | RAM | CPU | Storage | Bande passante | Usage |
|---------|-----------|-----|-----|---------|----------------|-------|
| **CAX11** | **€4.51** | 4GB | 2 vCPUs ARM | 40GB | 20TB | ✅ **Recommandé** - Production (jusqu'à 20 caméras) |
| CX21 | €5.83 | 4GB | 2 vCPUs x86 | 40GB | 20TB | Alternative x86 si besoin |
| CAX21 | €8.77 | 8GB | 4 vCPUs ARM | 80GB | 20TB | Production intensive (50+ caméras) |
| CX31 | €10.27 | 8GB | 2 vCPUs x86 | 80GB | 20TB | Très haute performance |

**💡 Choix recommandé**: **CAX11** (€4.51/mois)
- Excellent rapport performance/prix
- ARM efficace pour traitement vidéo
- 20TB bande passante = ~40 caméras 1080p 24/7
- Scalable facilement vers CAX21 si besoin

### Création du serveur

1. **Accéder à Hetzner Cloud Console**
   - https://console.hetzner.cloud/

2. **Créer un nouveau projet**
   - Cliquer sur "New Project"
   - Nom: `OhmVision Production`

3. **Créer un serveur**
   ```
   Location: Nuremberg (proche Europe)
   OS: Ubuntu 24.04 LTS
   Type: CAX11 (Shared vCPU ARM - €4.51/mois)
   Volume: Non (pas nécessaire pour démarrer)
   Network: Default
   SSH Key: [Ajouter votre clé publique]
   Name: ohmvision-prod
   ```

4. **Noter l'adresse IP**
   - Exemple: `95.217.123.45`

---

## ⚡ Déploiement Automatique

### Option 1: Script automatisé (RECOMMANDÉ)

```bash
# 1. Cloner le repository en local
git clone https://github.com/yacinetirichine-creator/ohmvision.git
cd ohmvision

# 2. Rendre le script exécutable
chmod +x deploy-hetzner.sh

# 3. Lancer le déploiement
./deploy-hetzner.sh
```

**Le script va:**
1. ✅ Installer Docker + Docker Compose
2. ✅ Configurer le firewall (UFW)
3. ✅ Cloner le repository
4. ✅ Générer les secrets (.env)
5. ✅ Configurer SSL (Let's Encrypt)
6. ✅ Démarrer tous les services
7. ✅ Vérifier la santé de l'application

**Informations demandées:**
- IP du serveur Hetzner
- Votre nom de domaine
- Votre email (pour SSL)
- Chemin de votre clé SSH

**Durée totale**: ~10 minutes

---

## 🔧 Déploiement Manuel

### Étape 1: Connexion au serveur

```bash
# Remplacer par votre IP
ssh root@95.217.123.45
```

### Étape 2: Installation des dépendances

```bash
# Mise à jour du système
apt-get update && apt-get upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Installation Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Vérification
docker --version
docker-compose --version

# Autres outils
apt-get install -y git curl wget ufw fail2ban htop
```

### Étape 3: Configuration du firewall

```bash
# Activer UFW
ufw --force enable

# Autoriser SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Vérifier
ufw status
```

### Étape 4: Cloner le repository

```bash
# Créer le répertoire
mkdir -p /opt/ohmvision
cd /opt/ohmvision

# Cloner
git clone https://github.com/yacinetirichine-creator/ohmvision.git .
```

### Étape 5: Configuration de l'environnement

```bash
# Copier le template
cp .env.production.example .env

# Générer les secrets
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
POSTGRES_PASS=$(openssl rand -base64 32)
REDIS_PASS=$(openssl rand -base64 32)

# Éditer .env
nano .env
```

**Remplir avec vos valeurs:**
```bash
DOMAIN=votre-domaine.com
POSTGRES_PASSWORD=$POSTGRES_PASS
REDIS_PASSWORD=$REDIS_PASS
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET

# Email (Gmail exemple)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password

# Stripe (optionnel au début)
# STRIPE_PUBLIC_KEY=pk_live_...
# STRIPE_SECRET_KEY=sk_live_...
```

**Sauvegarder**: `Ctrl+O`, `Enter`, `Ctrl+X`

### Étape 6: Mise à jour Nginx avec domaine

```bash
# Remplacer DOMAIN par votre domaine réel
sed -i "s/DOMAIN/votre-domaine.com/g" docker/nginx-production.conf

# Vérifier
grep "votre-domaine.com" docker/nginx-production.conf
```

### Étape 7: Création des répertoires

```bash
mkdir -p uploads logs logs/nginx docker/ssl
chmod -R 755 uploads logs
chmod 600 .env
```

### Étape 8: Démarrage des services

```bash
# Build et démarrage
docker-compose -f docker-compose.production.yml up -d --build

# Vérifier les logs
docker-compose -f docker-compose.production.yml logs -f
```

**Attendre ~2 minutes** que tous les services soient "healthy"

### Étape 9: Configuration SSL

```bash
# Obtenir le certificat SSL
docker-compose -f docker-compose.production.yml exec certbot certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email votre-email@gmail.com \
  --agree-tos \
  --no-eff-email \
  -d votre-domaine.com \
  -d www.votre-domaine.com

# Redémarrer Nginx
docker-compose -f docker-compose.production.yml restart nginx
```

### Étape 10: Vérification

```bash
# Status des services
docker-compose -f docker-compose.production.yml ps

# Health check
curl https://votre-domaine.com/health

# Logs en direct
docker-compose -f docker-compose.production.yml logs -f backend
```

---

## 🌐 Configuration DNS

### Chez votre registrar (OVH, Cloudflare, etc.)

**Type A Records:**
```
Type: A
Name: @
Value: 95.217.123.45  (IP de votre serveur Hetzner)
TTL: 3600

Type: A
Name: www
Value: 95.217.123.45
TTL: 3600
```

**Propagation**: 5 minutes à 24h (généralement <1h)

**Vérifier la propagation:**
```bash
# Depuis votre machine locale
dig votre-domaine.com
nslookup votre-domaine.com
```

---

## 📊 Monitoring et Maintenance

### Commandes utiles

```bash
# Connexion SSH
ssh root@95.217.123.45

# Aller dans le répertoire
cd /opt/ohmvision

# Voir les services
docker-compose -f docker-compose.production.yml ps

# Logs en temps réel
docker-compose -f docker-compose.production.yml logs -f

# Logs d'un service spécifique
docker-compose -f docker-compose.production.yml logs -f backend

# Redémarrer un service
docker-compose -f docker-compose.production.yml restart backend

# Redémarrer tout
docker-compose -f docker-compose.production.yml restart

# Rebuild après changements code
git pull origin master
docker-compose -f docker-compose.production.yml up -d --build

# Monitoring ressources
htop
docker stats

# Espace disque
df -h
```

### Monitoring automatique

Les services incluent déjà:
- ✅ **Health checks** automatiques (toutes les 30s)
- ✅ **Auto-restart** si un service crash
- ✅ **Watchtower** pour mises à jour auto des images Docker
- ✅ **Certbot** pour renouvellement SSL automatique (tous les 12h)

### Métriques importantes

```bash
# Utilisation CPU/RAM
docker stats

# Logs Nginx (trafic)
tail -f /opt/ohmvision/logs/nginx/access.log

# Connexions caméras actives
docker-compose -f docker-compose.production.yml exec backend python -c "
from backend.services.stream_manager import get_active_streams
print(f'Streams actifs: {len(get_active_streams())}')
"
```

---

## 🔥 Troubleshooting

### Problème: Service ne démarre pas

```bash
# Vérifier les logs
docker-compose -f docker-compose.production.yml logs backend

# Vérifier la santé
docker-compose -f docker-compose.production.yml ps

# Redémarrer
docker-compose -f docker-compose.production.yml restart backend
```

### Problème: Erreur 502 Bad Gateway

```bash
# Vérifier que backend répond
docker-compose -f docker-compose.production.yml exec backend curl http://localhost:8000/health

# Vérifier Nginx
docker-compose -f docker-compose.production.yml logs nginx

# Redémarrer Nginx
docker-compose -f docker-compose.production.yml restart nginx
```

### Problème: SSL ne fonctionne pas

```bash
# Vérifier les certificats
docker-compose -f docker-compose.production.yml exec nginx ls -la /etc/letsencrypt/live/

# Renouveler manuellement
docker-compose -f docker-compose.production.yml exec certbot certbot renew --force-renewal

# Redémarrer Nginx
docker-compose -f docker-compose.production.yml restart nginx
```

### Problème: Base de données inaccessible

```bash
# Vérifier PostgreSQL
docker-compose -f docker-compose.production.yml logs postgres

# Se connecter à la DB
docker-compose -f docker-compose.production.yml exec postgres psql -U ohmvision -d ohmvision

# Lister les tables
\dt

# Quitter
\q
```

### Problème: Manque d'espace disque

```bash
# Voir l'utilisation
df -h

# Nettoyer les images Docker non utilisées
docker system prune -a --volumes

# Nettoyer les logs anciens
find /opt/ohmvision/logs -name "*.log" -mtime +30 -delete

# Voir les gros fichiers
du -h /opt/ohmvision | sort -rh | head -20
```

---

## 💾 Backups

### Backup PostgreSQL automatique

```bash
# Créer le script de backup
cat > /opt/ohmvision/backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/ohmvision/backups"
mkdir -p $BACKUP_DIR

cd /opt/ohmvision
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U ohmvision ohmvision > $BACKUP_DIR/ohmvision_$DATE.sql

# Garder seulement les 7 derniers jours
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: ohmvision_$DATE.sql"
EOF

chmod +x /opt/ohmvision/backup-db.sh
```

### Cron automatique (tous les jours à 3h)

```bash
# Ajouter au cron
crontab -e

# Ajouter cette ligne
0 3 * * * /opt/ohmvision/backup-db.sh >> /var/log/ohmvision-backup.log 2>&1
```

### Backup manuel

```bash
# Database
docker-compose -f docker-compose.production.yml exec postgres pg_dump -U ohmvision ohmvision > backup_$(date +%Y%m%d).sql

# Fichiers uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Télécharger sur votre machine
scp root@95.217.123.45:/opt/ohmvision/backup_*.sql ./
```

### Restauration

```bash
# Database
cat backup_20260120.sql | docker-compose -f docker-compose.production.yml exec -T postgres psql -U ohmvision ohmvision

# Uploads
tar -xzf uploads_backup_20260120.tar.gz -C /opt/ohmvision/
```

---

## 🎯 Optimisations Avancées

### Augmenter les performances

```bash
# Éditer docker-compose.production.yml
nano docker-compose.production.yml

# Augmenter les workers backend
WORKERS=8  # Au lieu de 4

# Augmenter la RAM PostgreSQL
deploy:
  resources:
    limits:
      memory: 2G  # Au lieu de 1G
```

### Monitoring avec Grafana (optionnel)

```bash
# Ajouter Prometheus + Grafana
# Documentation: https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/
```

---

## 📞 Support

**En cas de problème:**

1. **Vérifier les logs**: `docker-compose logs -f`
2. **Health checks**: `curl https://votre-domaine.com/health`
3. **Status services**: `docker-compose ps`
4. **GitHub Issues**: https://github.com/yacinetirichine-creator/ohmvision/issues

---

## ✅ Checklist Déploiement

- [ ] Serveur Hetzner CAX11 créé
- [ ] SSH configuré avec clé publique
- [ ] Nom de domaine configuré (DNS)
- [ ] Docker + Docker Compose installés
- [ ] Firewall (UFW) activé
- [ ] Repository cloné
- [ ] `.env` configuré avec secrets
- [ ] Nginx configuré avec domaine
- [ ] Services démarrés (`docker-compose up -d`)
- [ ] SSL configuré (Let's Encrypt)
- [ ] Health check OK (`/health`)
- [ ] Application accessible via HTTPS
- [ ] Compte admin créé
- [ ] Backup automatique configuré
- [ ] SMTP configuré (emails)
- [ ] Stripe configuré (paiements - optionnel)

---

## 🎉 Félicitations!

Votre instance OhmVision est maintenant déployée sur Hetzner Cloud!

**Accès**: https://votre-domaine.com

**Coût mensuel**: ~€4.51/mois (CAX11)

**Capacité**: Jusqu'à 20-40 caméras simultanées

**Mise à l'échelle**: Upgrade vers CAX21 (€8.77) pour 50+ caméras
