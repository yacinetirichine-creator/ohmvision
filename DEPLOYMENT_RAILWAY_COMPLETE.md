# 🚀 OhmVision - Déploiement Railway (Production Ready)

## Pourquoi Railway ?

✅ **Déploiement automatique** depuis GitHub  
✅ **Scaling horizontal** automatique  
✅ **PostgreSQL/Redis managés** inclus  
✅ **SSL gratuit** automatique  
✅ **Logs centralisés** et monitoring  
✅ **Zero DevOps** = Focus sur le code  
✅ **Preview deployments** pour tester  

---

## 📋 Architecture Recommandée

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAILWAY                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Backend   │  │ PostgreSQL  │  │    Redis    │            │
│  │   FastAPI   │◀─│  (Railway   │  │  (Railway   │            │
│  │   + IA      │  │   ou        │  │   natif)    │            │
│  │             │  │  Supabase)  │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│        │                                                        │
│        │ API: https://api.ohmvision.fr                         │
└────────┼────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         VERCEL                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Frontend React/Vite                         │   │
│  │           https://app.ohmvision.fr                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Étape 1 : Préparer le projet

### 1.1 Structure requise

```
ohmvision/
├── backend/
│   ├── Dockerfile          ✅ Existe
│   ├── requirements.txt    ✅ Existe
│   ├── main.py            ✅ Existe
│   └── ...
├── frontend-client/
│   └── ...
├── railway.json           ✅ Existe
└── Procfile               ✅ Existe
```

### 1.2 Vérifier le Procfile

```procfile
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 🚀 Étape 2 : Créer le projet Railway

### Option A : Via l'interface web (Recommandé pour débuter)

1. **Aller sur** https://railway.app
2. **Se connecter** avec GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Sélectionner** `ohmvision`
5. Railway détecte automatiquement Python

### Option B : Via CLI (Plus rapide)

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Se connecter
railway login

# Initialiser le projet
railway init

# Lier au repo existant
railway link
```

---

## 📦 Étape 3 : Ajouter les services

### 3.1 Ajouter PostgreSQL

Dans Railway Dashboard :
1. Cliquer **+ New**
2. Sélectionner **Database** → **PostgreSQL**
3. Railway génère automatiquement `DATABASE_URL`

### 3.2 Ajouter Redis

1. Cliquer **+ New**
2. Sélectionner **Database** → **Redis**
3. Railway génère automatiquement `REDIS_URL`

### 3.3 (Alternative) Utiliser Supabase pour PostgreSQL

Si vous préférez Supabase (gratuit jusqu'à 500MB) :

1. Créer un projet sur https://supabase.com
2. Aller dans **Settings** → **Database** → **Connection string**
3. Copier l'URI et remplacer `postgresql://` par `postgresql+asyncpg://`

---

## 🔐 Étape 4 : Configurer les variables d'environnement

### Variables requises (Railway Dashboard → Variables)

```env
# ═══════════════════════════════════════════════════════════════
# DATABASE (automatique si PostgreSQL Railway, sinon Supabase)
# ═══════════════════════════════════════════════════════════════
DATABASE_URL=${{Postgres.DATABASE_URL}}
# Ou pour Supabase:
# DATABASE_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# ═══════════════════════════════════════════════════════════════
# REDIS (automatique si Redis Railway)
# ═══════════════════════════════════════════════════════════════
REDIS_URL=${{Redis.REDIS_URL}}

# ═══════════════════════════════════════════════════════════════
# SÉCURITÉ (OBLIGATOIRE - Générer des clés uniques!)
# ═══════════════════════════════════════════════════════════════
SECRET_KEY=<générer-avec-python-secrets>
JWT_SECRET_KEY=<générer-avec-python-secrets>

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION APP
# ═══════════════════════════════════════════════════════════════
DEBUG=false
ENVIRONMENT=production
PYTHONUNBUFFERED=1

# ═══════════════════════════════════════════════════════════════
# CORS (URL de votre frontend Vercel)
# ═══════════════════════════════════════════════════════════════
CORS_ORIGINS=https://app.ohmvision.fr,https://ohmvision.vercel.app
FRONTEND_URL=https://app.ohmvision.fr

# ═══════════════════════════════════════════════════════════════
# OPTIONNEL : IA
# ═══════════════════════════════════════════════════════════════
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# ═══════════════════════════════════════════════════════════════
# OPTIONNEL : Stripe (Paiements)
# ═══════════════════════════════════════════════════════════════
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# ═══════════════════════════════════════════════════════════════
# OPTIONNEL : Email
# ═══════════════════════════════════════════════════════════════
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre.email@gmail.com
SMTP_PASSWORD=app-password
```

### Générer les clés secrètes

```bash
# Exécuter dans un terminal Python
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY:', secrets.token_urlsafe(32))"
```

---

## 🌐 Étape 5 : Configurer le domaine personnalisé

### 5.1 Dans Railway

1. Aller dans **Settings** → **Domains**
2. Ajouter **Custom Domain** : `api.ohmvision.fr`
3. Railway affiche les enregistrements DNS à configurer

### 5.2 Chez votre registrar DNS

Ajouter un enregistrement CNAME :

```
Type: CNAME
Name: api
Value: <votre-projet>.up.railway.app
```

---

## 🔄 Étape 6 : CI/CD Automatique

Railway déploie automatiquement à chaque push sur `main` !

```bash
# Faire une modification
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main

# Railway déploie automatiquement ✨
```

### Voir les logs en temps réel

```bash
railway logs
```

Ou dans le dashboard Railway → **Deployments** → **View Logs**

---

## 📊 Étape 7 : Monitoring et Scaling

### Monitoring intégré

- **Metrics** : CPU, RAM, Network dans le dashboard
- **Logs** : Centralisés et searchables
- **Alertes** : Configurable par email/Slack

### Scaling

```bash
# Scaler horizontalement (plusieurs instances)
# Dans Railway Dashboard → Settings → Instances
# Ou via CLI:
railway scale web=3
```

### Auto-scaling (Pro)

Railway Pro permet l'auto-scaling basé sur :
- CPU usage
- Memory usage
- Request count

---

## 💰 Coûts estimés

| Plan | Prix | Inclus |
|------|------|--------|
| **Hobby** | $5/mois | 512MB RAM, 1 vCPU, bon pour dev |
| **Pro** | $20/mois | 8GB RAM, 8 vCPU, production |
| **Team** | $20/user/mois | Collaboration, audit logs |

### Estimation pour OhmVision Production

| Service | Coût estimé |
|---------|-------------|
| Backend (Pro) | $20/mois |
| PostgreSQL | $5-15/mois (ou Supabase gratuit) |
| Redis | $5/mois |
| Bandwidth | ~$5/mois |
| **TOTAL** | **$35-45/mois** |

💡 **Comparaison** : Configuration manuelle Hetzner = €5/mois MAIS +10h de setup et maintenance continue.

---

## 🔧 Troubleshooting

### Erreur de build

```bash
# Voir les logs de build
railway logs --build

# Rebuilder manuellement
railway up --detach
```

### Base de données non connectée

Vérifier que `DATABASE_URL` utilise `postgresql+asyncpg://` et non `postgresql://`

### CORS errors

Vérifier `CORS_ORIGINS` inclut bien l'URL de votre frontend Vercel.

---

## 🎯 Checklist de déploiement

- [ ] Compte Railway créé
- [ ] Projet lié au repo GitHub
- [ ] PostgreSQL ajouté
- [ ] Redis ajouté
- [ ] Variables d'environnement configurées
- [ ] Clés secrètes générées
- [ ] Domaine personnalisé configuré
- [ ] SSL actif (automatique)
- [ ] Healthcheck fonctionnel
- [ ] Frontend Vercel configuré avec `VITE_API_URL`

---

## 🚀 Commandes CLI utiles

```bash
# Status du projet
railway status

# Variables d'environnement
railway variables

# Ouvrir le dashboard
railway open

# Logs en temps réel
railway logs -f

# Se connecter à la DB
railway connect postgres

# Exécuter une commande
railway run python -c "print('Hello')"
```

---

## 📞 Support

- **Documentation Railway** : https://docs.railway.app
- **Discord Railway** : https://discord.gg/railway
- **Status** : https://status.railway.app

---

**Railway = La meilleure option pour OhmVision** 🚀
