# Déploiement Vercel (Frontend) + Hetzner (Backend)

Objectif: déployer le frontend React/Vite sur Vercel et exposer le backend FastAPI sur un serveur Hetzner, avec une configuration propre (CORS, URL d'API, routage SPA).

## 1) Backend (Hetzner)

### URL recommandée
- Backend: `https://api.<ton-domaine>` (ex: `https://api.ohmvision.com`)
- Les endpoints sont sous `/api/...` (ex: `/api/auth/login`, `/api/health`)

### Variables d'environnement importantes
Dans le `.env` du backend (ou variables Docker):
- `DEBUG=false`
- `SECRET_KEY=...` (fort)
- `JWT_SECRET_KEY=...` (fort)
- `DATABASE_URL=...` (PostgreSQL prod)
- `CORS_ORIGINS=https://<ton-frontend-vercel>,https://<ton-domaine-frontend>`
  - ex: `CORS_ORIGINS=https://ohmvision.vercel.app,https://www.ohmvision.com`
- (optionnel) `CORS_ORIGIN_REGEX=https://.*\\.vercel\\.app$`
  - utile pour autoriser automatiquement les URLs Preview Vercel

### Reverse proxy (Nginx)
- Terminer TLS côté Nginx (Let’s Encrypt)
- Proxy vers `http://127.0.0.1:8000` (ou le container backend)
- Conserver les headers `X-Forwarded-*`

### Vérification rapide
- `GET https://api.<ton-domaine>/health` doit répondre `{"status":"healthy", ...}`
- `GET https://api.<ton-domaine>/docs` doit afficher Swagger

## 2) Frontend (Vercel)

### Réglages du projet Vercel
- **Root Directory**: `frontend-client`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Variable d'environnement Vercel (indispensable)
Dans Vercel → Settings → Environment Variables:
- `VITE_API_BASE = https://api.<ton-domaine>/api`

Le frontend utilisera automatiquement cette base via `import.meta.env.VITE_API_BASE`.

### Routage SPA (React Router)
Le fichier `frontend-client/vercel.json` force le fallback vers `index.html` pour toutes les routes (ex: `/dashboard`, `/cameras/123`).

## 3) Notes "robustesse"

- Éviter les proxies `/api` côté Vercel si le backend est sur un domaine séparé: l’env `VITE_API_BASE` est plus simple et plus explicite.
- Si tu utilises des cookies cross-site un jour, il faudra traiter `SameSite=None; Secure` et `allow_credentials` + origins explicites.

