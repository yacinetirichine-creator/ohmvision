# Railway Deployment Guide - OhmVision Backend

## 🚀 Déploiement sur Railway avec Supabase

### Prérequis
- ✅ Compte Railway : https://railway.app
- ✅ Compte Supabase : https://supabase.com (déjà fait)
- ✅ Repository Git (GitHub)

---

## 📋 Étape 1 : Récupérer les informations Supabase

1. **Aller sur votre projet Supabase** : https://supabase.com/dashboard
2. **Aller dans Settings → Database**
3. **Copier la "Connection String" en mode "URI"**

Format :
```
postgresql://postgres.[project-ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

⚠️ **IMPORTANT** : Remplacez `postgresql://` par `postgresql+asyncpg://` pour AsyncPG !

---

## 📋 Étape 2 : Créer le projet sur Railway

### 2.1 Se connecter à Railway
```bash
# Installer Railway CLI (optionnel)
npm i -g @railway/cli

# Ou utiliser l'interface web : https://railway.app/new
```

### 2.2 Créer un nouveau projet
1. Cliquez sur **"New Project"**
2. Sélectionnez **"Deploy from GitHub repo"**
3. Choisissez votre repository `ohmvision`
4. Railway détectera automatiquement Python/FastAPI

---

## 📋 Étape 3 : Configurer les variables d'environnement

Dans Railway, allez dans **Variables** et ajoutez :

### Variables obligatoires :
```env
# Database Supabase
DATABASE_URL=postgresql+asyncpg://postgres.[REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# Supabase (optionnel pour auth)
SUPABASE_URL=https://[votre-projet].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Sécurité
SECRET_KEY=votre-clé-secrète-ultra-complexe-générez-la
JWT_SECRET_KEY=autre-clé-jwt-secrète

# Python
PYTHONUNBUFFERED=1
```

### Variables optionnelles :
```env
# SMTP pour emails
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre.email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# Stripe (si facturation)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Redis (optionnel - Railway peut fournir)
REDIS_URL=redis://default:password@redis.railway.internal:6379
```

---

## 📋 Étape 4 : Générer les clés secrètes

```bash
# Générer SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Générer JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📋 Étape 5 : Déployer

### Option A : Via Git Push (automatique)
```bash
git add .
git commit -m "Configure Railway deployment"
git push origin master
```
Railway déploiera automatiquement ! ✨

### Option B : Via Railway CLI
```bash
railway login
railway link
railway up
```

---

## 📋 Étape 6 : Vérifier le déploiement

1. **Attendre la fin du build** (2-3 minutes)
2. **Railway vous donnera une URL** : `https://ohmvision-production.up.railway.app`
3. **Tester** :
   ```
   https://votre-app.up.railway.app/docs
   ```

---

## 🔧 Commandes utiles

### Voir les logs
```bash
railway logs
```

### Redéployer
```bash
railway up --detach
```

### Variables d'environnement
```bash
railway variables
```

---

## 📊 Structure de déploiement finale

```
┌─────────────────────────────┐
│   SUPABASE PostgreSQL       │  Base de données
│   postgresql+asyncpg://...  │
└──────────┬──────────────────┘
           │
           │ DATABASE_URL
           │
┌──────────▼──────────────────┐
│   RAILWAY Backend           │  API FastAPI
│   https://xxx.railway.app   │
│   • Health check 24/7       │
│   • Multi-canal cameras     │
│   • AI Analytics            │
└──────────┬──────────────────┘
           │
           │ API Calls
           │
┌──────────▼──────────────────┐
│   Frontend (Vercel/Local)   │  Interface utilisateur
└─────────────────────────────┘
```

---

## ✅ Checklist de déploiement

- [ ] Compte Railway créé
- [ ] Repository GitHub connecté
- [ ] DATABASE_URL Supabase configuré (avec +asyncpg)
- [ ] SECRET_KEY et JWT_SECRET_KEY générés
- [ ] Variables d'environnement ajoutées
- [ ] Premier déploiement réussi
- [ ] URL de production testée (/docs accessible)
- [ ] Base de données Supabase accessible depuis Railway

---

## 🐛 Dépannage

### Erreur : "Connection refused"
→ Vérifiez que DATABASE_URL contient bien `postgresql+asyncpg://`

### Erreur : "Module not found"
→ Vérifiez que `requirements.txt` est à la racine

### Build échoue
→ Vérifiez les logs : `railway logs`

### Base de données vide
→ Exécutez les migrations manuellement via Railway Shell

---

## 📝 Support

- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs
- OhmVision: Voir MULTI_CHANNEL_CONNECTIVITY.md

---

🎉 **Votre backend OhmVision sera accessible 24/7 sur Railway !**
