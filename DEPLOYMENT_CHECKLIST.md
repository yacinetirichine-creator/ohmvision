# ✅ Checklist Déploiement OhmVision - Production Ready

## 🎯 Objectif: Déployer une plateforme scalable pour 100-1000+ clients

---

## Phase 1: Setup Comptes Cloud (15 min)

### ✅ Vercel (Frontend)
- [ ] Créer compte: https://vercel.com/signup
- [ ] Connecter GitHub
- [ ] Vérifier email

### ✅ Railway (Backend)
- [ ] Créer compte: https://railway.app
- [ ] Connecter GitHub
- [ ] Ajouter carte bancaire (pour éviter sleep après 5h inactivité)

### ✅ Upstash (Redis - Cache)
- [ ] Créer compte: https://upstash.com
- [ ] Créer database Redis (région: eu-central-1)
- [ ] Copier REDIS_URL

### ✅ Cloudflare (Storage - optionnel)
- [ ] Créer compte: https://cloudflare.com
- [ ] Activer R2 Storage
- [ ] Créer bucket `ohmvision-videos`
- [ ] Copier credentials S3-compatible

---

## Phase 2: Déploiement Backend (20 min)

### Railway - FastAPI

1. **Nouveau projet**
   - [ ] Railway.app → New Project
   - [ ] Deploy from GitHub repo
   - [ ] Sélectionner `yacinetirichine-creator/ohmvision`

2. **Configuration**
   - [ ] Settings → Root Directory: `backend`
   - [ ] Settings → Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Variables d'environnement**
   ```bash
   # Application
   APP_NAME=OhmVision
   APP_ENV=production
   DEBUG=false
   SECRET_KEY=GENERE_NOUVELLE_CLE_SECRETE_32_CHARS
   JWT_SECRET_KEY=GENERE_AUTRE_CLE_SECRETE_32_CHARS
   
   # Database (Supabase)
   DATABASE_URL=postgresql+asyncpg://postgres:aSuJAIPxnKoUDrQX@db.igpraulohtflbjvacgvo.supabase.co:5432/postgres
   
   # Supabase
   SUPABASE_URL=https://igpraulohtflbjvacgvo.supabase.co
   SUPABASE_ANON_KEY=sb_publishable_M8Ja4cb5DpLb92rOWdD81Q_9aRaeAAS
   
   # Redis (Upstash - copier depuis dashboard)
   REDIS_URL=redis://default:VOTRE_PASSWORD@eu1-charming-mantis-12345.upstash.io:6379
   
   # Email (Gmail App Password)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=votre-email@gmail.com
   SMTP_PASSWORD=votre-app-password-16-chars
   EMAIL_FROM=noreply@ohmvision.fr
   
   # CORS (mettre URL frontend Vercel)
   CORS_ORIGINS=https://ohmvision.vercel.app,https://www.ohmvision.fr
   
   # AI (optionnel - pour agent IA)
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-...
   ```

4. **Déploiement**
   - [ ] Deploy → Attendre build (3-5 min)
   - [ ] Copier URL publique: `https://ohmvision-production.up.railway.app`

5. **Test**
   - [ ] Ouvrir `https://votre-url.railway.app/docs`
   - [ ] Tester endpoint `/api/auth/login`

---

## Phase 3: Déploiement Frontend (10 min)

### Vercel - React

1. **Import projet**
   - [ ] Vercel.com → New Project
   - [ ] Import Git Repository → `ohmvision`

2. **Configuration**
   - [ ] Framework Preset: Vite
   - [ ] Root Directory: `frontend-client`
   - [ ] Build Command: `npm run build`
   - [ ] Output Directory: `dist`

3. **Variables d'environnement**
   ```bash
   VITE_API_URL=https://ohmvision-production.up.railway.app
   VITE_SUPABASE_URL=https://igpraulohtflbjvacgvo.supabase.co
   VITE_SUPABASE_ANON_KEY=sb_publishable_M8Ja4cb5DpLb92rOWdD81Q_9aRaeAAS
   ```

4. **Deploy**
   - [ ] Deploy → Attendre (2-3 min)
   - [ ] URL: `https://ohmvision.vercel.app`

5. **Test**
   - [ ] Ouvrir frontend
   - [ ] Login avec admin@ohmvision.fr / admin123
   - [ ] Vérifier dashboard

---

## Phase 4: Configuration Domaine (optionnel)

### Si tu as un domaine (ex: ohmvision.fr)

**Backend (Railway)**
- [ ] Settings → Domains → Add Custom Domain
- [ ] Ajouter `api.ohmvision.fr`
- [ ] Configurer DNS CNAME: `api.ohmvision.fr` → `ohmvision-production.up.railway.app`

**Frontend (Vercel)**
- [ ] Settings → Domains → Add
- [ ] Ajouter `ohmvision.fr` et `www.ohmvision.fr`
- [ ] Configurer DNS:
  - A record `@` → `76.76.21.21`
  - CNAME `www` → `cname.vercel-dns.com`

---

## Phase 5: Sécurité & Optimisations (30 min)

### Backend

- [ ] **Générer secrets forts**
  ```bash
  # Sur ton Mac
  python -c "import secrets; print(secrets.token_urlsafe(32))"  # SECRET_KEY
  python -c "import secrets; print(secrets.token_urlsafe(32))"  # JWT_SECRET_KEY
  ```

- [ ] **Rate Limiting** (ajouter dans `main.py`)
  ```python
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address
  
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
  ```

- [ ] **HTTPS Only** (Railway auto)

- [ ] **CORS Production** (vérifier CORS_ORIGINS)

### Supabase

- [ ] **RLS Policies** (Row Level Security)
  - Dashboard → Authentication → Policies
  - Activer RLS sur tables sensibles
  - Créer policies par client_id

- [ ] **Backup automatique** (déjà actif)

- [ ] **Monitoring** (activer alertes email si DB >80%)

### Frontend

- [ ] **Environnement variables** (vérifier VITE_API_URL)

- [ ] **Analytics** (optionnel - Vercel Analytics)

---

## Phase 6: Monitoring & Logs (15 min)

### Railway
- [ ] Dashboard → Metrics (voir CPU, RAM, requêtes/sec)
- [ ] Logs → Activer email alerts si erreurs

### Supabase
- [ ] Dashboard → Reports → Database Health
- [ ] Activer alertes si connexions >80%

### Uptime Monitoring (gratuit)
- [ ] BetterUptime.com ou UptimeRobot.com
- [ ] Ajouter `https://votre-api.railway.app/docs`
- [ ] Alertes email/SMS si down

---

## Phase 7: Tests Production (30 min)

### Backend API
```bash
# Test health
curl https://votre-api.railway.app/docs

# Test login
curl -X POST https://votre-api.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ohmvision.fr","password":"admin123"}'

# Test GDPR endpoint
curl https://votre-api.railway.app/api/gdpr/privacy-policy
```

### Frontend
- [ ] Login/Logout
- [ ] Créer client
- [ ] Ajouter caméra (RTSP)
- [ ] Voir alerts
- [ ] Dashboard analytics

### Performance
- [ ] Google PageSpeed: >90/100
- [ ] Latence API: <200ms
- [ ] Load test: https://loader.io (1000 req/min)

---

## Phase 8: Documentation Client

- [ ] **URL Production**: https://ohmvision.vercel.app
- [ ] **URL API**: https://votre-api.railway.app
- [ ] **Docs API**: https://votre-api.railway.app/docs
- [ ] **Admin**: admin@ohmvision.fr / admin123

---

## 🎯 Résultat Attendu

✅ Frontend déployé sur Vercel (CDN mondial)
✅ Backend scalable sur Railway (auto-scaling)
✅ Base de données Supabase (backups auto)
✅ Redis cache Upstash (performances)
✅ SSL/HTTPS partout
✅ Monitoring actif
✅ Prêt pour 100-1000+ clients
✅ Coût: $0-50/mois initialement

---

## 📞 Support

- Railway: https://railway.app/help
- Vercel: https://vercel.com/support
- Supabase: https://supabase.com/docs

---

## ⏰ Temps Total Estimé: **2h30**

Bonne chance demain! 🚀
