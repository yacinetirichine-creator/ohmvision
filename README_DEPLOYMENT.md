# 🚀 OhmVision - Guide de Déploiement

## ✅ Ce qui est fait

- ✅ Code poussé sur GitHub: https://github.com/yacinetirichine-creator/ohmvision
- ✅ Base de données Supabase configurée et initialisée
- ✅ Backend FastAPI avec 15+ endpoints
- ✅ Frontend React moderne
- ✅ Module RGPD/GDPR complet
- ✅ Moteur IA (YOLO v8)
- ✅ Tests automatisés

## 🎯 Options de déploiement

### Option 1: Railway (Recommandé - Le plus simple)

**Backend FastAPI**
1. Va sur https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. Sélectionne `yacinetirichine-creator/ohmvision`
4. **Settings** → **Root Directory**: `backend`
5. **Variables d'environnement** (copie depuis `.env`):
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:aSuJAIPxnKoUDrQX@db.igpraulohtflbjvacgvo.supabase.co:5432/postgres
   SUPABASE_URL=https://igpraulohtflbjvacgvo.supabase.co
   SUPABASE_ANON_KEY=sb_publishable_M8Ja4cb5DpLb92rOWdD81Q_9aRaeAAS
   SECRET_KEY=ton-secret-key-production
   ```
6. **Deploy** → Railway va build et déployer automatiquement
7. Récupère l'URL publique (ex: `https://ohmvision-backend.up.railway.app`)

**Frontend React**
1. **New Project** → Même repo
2. **Settings** → **Root Directory**: `frontend-client`
3. **Variables**:
   ```
   VITE_API_URL=https://ohmvision-backend.up.railway.app
   ```
4. **Deploy**

### Option 2: Vercel (Frontend) + Railway (Backend)

**Backend sur Railway** (voir Option 1)

**Frontend sur Vercel**
1. Va sur https://vercel.com
2. **Import Project** → GitHub → `ohmvision`
3. **Root Directory**: `frontend-client`
4. **Environment Variables**:
   ```
   VITE_API_URL=https://ohmvision-backend.up.railway.app
   ```
5. **Deploy**

### Option 3: Render.com (Tout en un)

**Backend**
1. https://render.com → **New Web Service**
2. Connect GitHub → `ohmvision`
3. **Root Directory**: `backend`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables**: (comme Railway)

**Frontend**
1. **New Static Site**
2. **Root Directory**: `frontend-client`
3. **Build Command**: `npm install && npm run build`
4. **Publish Directory**: `dist`

### Option 4: Déploiement Docker local

Si tu veux tester en local avec Docker:

```bash
# Arrêter les services locaux
docker-compose down

# Mettre à jour .env avec les credentials Supabase
cd backend
nano .env  # Mettre DATABASE_URL Supabase

# Rebuild et lancer
cd ..
docker-compose up --build backend frontend-client
```

Accès:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Docs API: http://localhost:8000/docs

## 📝 Configuration Production

### Variables d'environnement Backend

Créer un fichier `.env.production`:

```bash
# Application
APP_NAME=OhmVision
APP_ENV=production
DEBUG=false
SECRET_KEY=GENERE_UNE_CLE_SECRETE_FORTE
JWT_SECRET_KEY=GENERE_UNE_AUTRE_CLE_SECRETE

# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://postgres:aSuJAIPxnKoUDrQX@db.igpraulohtflbjvacgvo.supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://igpraulohtflbjvacgvo.supabase.co
SUPABASE_ANON_KEY=sb_publishable_M8Ja4cb5DpLb92rOWdD81Q_9aRaeAAS

# Redis (optionnel - Upstash gratuit)
REDIS_URL=redis://default:password@redis.upstash.io:6379

# Email (Gmail SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ton-email@gmail.com
SMTP_PASSWORD=ton-app-password
EMAIL_FROM=noreply@ohmvision.fr

# AI (optionnel)
ANTHROPIC_API_KEY=ton-api-key
OPENAI_API_KEY=ton-api-key

# CORS
CORS_ORIGINS=https://ohmvision.vercel.app,https://ohmvision.fr
```

### Variables d'environnement Frontend

`.env.production`:

```bash
VITE_API_URL=https://ohmvision-backend.up.railway.app
VITE_SUPABASE_URL=https://igpraulohtflbjvacgvo.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_M8Ja4cb5DpLb92rOWdD81Q_9aRaeAAS
```

## 🔐 Sécurité

Avant de déployer en production:

1. ✅ Change tous les secrets (SECRET_KEY, JWT_SECRET_KEY)
2. ✅ Active HTTPS (automatique sur Railway/Vercel)
3. ✅ Configure CORS avec tes vrais domaines
4. ✅ Active le rate limiting
5. ✅ Vérifie les permissions Supabase (RLS policies)

## 🧪 Tester après déploiement

```bash
# Backend health check
curl https://ton-backend.railway.app/docs

# Test API
curl https://ton-backend.railway.app/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ohmvision.fr","password":"admin123"}'

# Frontend
curl https://ton-frontend.vercel.app
```

## 📊 Monitoring

- **Railway**: Dashboard intégré (logs, metrics, alertes)
- **Supabase**: Dashboard → Database → Performance
- **Sentry**: Ajouter pour tracking d'erreurs (optionnel)

## 🆘 Support

Si tu as des problèmes:
1. Check les logs sur Railway/Vercel
2. Vérifie que Supabase est accessible
3. Teste les endpoints un par un sur `/docs`
4. Vérifie les CORS si erreur frontend

## 🚀 Prochaines étapes

1. **Déployer sur Railway** (5 minutes)
2. **Tester les endpoints** (`/docs`)
3. **Configurer le domaine custom** (optionnel)
4. **Ajouter des caméras** via l'API
5. **Tester la détection IA** avec un flux RTSP

Bonne chance! 🎉
