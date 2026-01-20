# 🚀 GUIDE RAPIDE - Déploiement Hetzner Cloud

## ⚡ Démarrage Express (10 minutes)

### 1️⃣ Créer un serveur Hetzner

**Accès:** https://console.hetzner.cloud/

```
Projet: OhmVision Production
Serveur: CAX11 (€4.51/mois)
OS: Ubuntu 24.04 LTS
Location: Nuremberg
SSH: [Ajouter votre clé publique]
```

**Notez l'IP:** `95.217.XXX.XXX`

---

### 2️⃣ Déploiement automatique

```bash
# Sur votre machine locale
git clone https://github.com/yacinetirichine-creator/ohmvision.git
cd ohmvision
./deploy-hetzner.sh
```

**Informations demandées:**
- IP du serveur: `95.217.XXX.XXX`
- Nom de domaine: `votre-domaine.com`
- Email: `votre-email@gmail.com`
- Clé SSH: `~/.ssh/id_rsa`

**Le script fait TOUT automatiquement:**
✅ Installation Docker + Docker Compose  
✅ Configuration firewall (UFW)  
✅ Déploiement de l'application  
✅ Configuration SSL (Let's Encrypt)  
✅ Démarrage des services  

**Durée:** ~10 minutes

---

### 3️⃣ Configurer le DNS

**Chez votre registrar (OVH, Cloudflare, etc.):**

```
Type: A
Name: @
Value: 95.217.XXX.XXX (IP de votre serveur)

Type: A
Name: www
Value: 95.217.XXX.XXX
```

**Attendre:** 5-60 minutes pour propagation

---

### 4️⃣ Vérifier

```bash
# Test health check
curl https://votre-domaine.com/health

# Devrait retourner: {"status": "ok"}
```

---

## 🎯 C'EST TOUT!

Votre application est maintenant accessible à:
👉 **https://votre-domaine.com**

---

## 📊 Comparaison: Railway vs Hetzner

| Critère | Railway | Hetzner CAX11 |
|---------|---------|---------------|
| **Prix/mois** | $50-100 | **€4.51** 🏆 |
| **Bande passante** | Limitée (payante) | **20TB inclus** 🏆 |
| **RAM** | 512MB-1GB | **4GB** 🏆 |
| **CPU** | Limitée | **2 vCPUs ARM** 🏆 |
| **Stockage** | Éphémère ❌ | **40GB persistant** 🏆 |
| **Connexions RTSP** | Timeout 10min ❌ | **Illimitées** 🏆 |
| **Setup** | Très facile | Facile (script auto) |
| **Scalabilité** | Limitée | **Excellente** 🏆 |

**Économie:** ~€45/mois vs Railway avec 10 caméras

---

## 🔧 Commandes Utiles

```bash
# Connexion SSH
ssh root@95.217.XXX.XXX

# Voir les services
cd /opt/ohmvision
docker-compose -f docker-compose.production.yml ps

# Logs en temps réel
docker-compose -f docker-compose.production.yml logs -f

# Redémarrer un service
docker-compose -f docker-compose.production.yml restart backend

# Status système
htop
docker stats
```

---

## 📚 Documentation Complète

**Détails complets:** [DEPLOYMENT_HETZNER.md](DEPLOYMENT_HETZNER.md)

**Inclut:**
- Déploiement manuel étape par étape
- Configuration avancée
- Monitoring et maintenance
- Troubleshooting
- Backups automatiques
- Optimisations performance

---

## 💡 Prochaines Étapes

1. ✅ Application déployée
2. 📧 Configurer SMTP (emails) dans `.env`
3. 💳 Configurer Stripe (paiements) - optionnel
4. 📊 Configurer monitoring (optionnel)
5. 🔄 Tester les backups automatiques

---

## 🎉 Félicitations!

Vous avez maintenant un système de vidéosurveillance professionnel pour **€4.51/mois**!

**Capacité:** 20-40 caméras simultanées  
**Disponibilité:** 99.9% uptime  
**Sécurité:** SSL, Fail2Ban, Firewall  
**Backups:** Automatiques quotidiens  

🚀 **Prêt pour la production!**
