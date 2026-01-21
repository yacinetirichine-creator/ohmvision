# 🎯 GUIDE ULTRA-SIMPLIFIÉ - OhmVision

**Pour novices** - Suivez étape par étape !

---

## 📋 Avant de commencer

Tu auras besoin de :
- ✅ Un compte GitHub (https://github.com) - gratuit
- ✅ Un compte Railway (https://railway.app) - gratuit pour démarrer
- ✅ 10 minutes de ton temps

---

## 🎮 OPTION A : TEST LOCAL (5 minutes)

**Objectif:** Tester que tout fonctionne sur ton ordi avant de déployer.

### Étape 1 : Installer Docker Desktop

Télécharge et installe Docker Desktop :
- **Windows**: https://www.docker.com/products/docker-desktop/
- **Mac**: https://www.docker.com/products/docker-desktop/

### Étape 2 : Lancer avec Docker

```bash
# Dans le terminal VS Code:
docker compose up -d
```

### Étape 3 : Accéder à l'app

Ouvre ton navigateur : **http://localhost:8000**

**C'est tout !** Tu peux tester l'application.

---

## 🚀 OPTION B : DÉPLOIEMENT RAILWAY (10 minutes)

Railway = Hébergement cloud simple, pas de serveur à gérer !

### Étape 1 : Créer un compte Railway

1. Va sur https://railway.app
2. Clique "**Login**" puis "**Continue with GitHub**"
3. Autorise Railway à accéder à ton GitHub

### Étape 2 : Créer un nouveau projet

1. Clique "**New Project**"
2. Sélectionne "**Deploy from GitHub repo**"
3. Choisis ton repo **ohmvision**
4. Railway détecte automatiquement que c'est du Python

### Étape 3 : Ajouter PostgreSQL

1. Dans ton projet, clique "**+ New**"
2. Sélectionne "**Database**" → "**PostgreSQL**"
3. Railway crée automatiquement la base de données

### Étape 4 : Ajouter Redis

1. Clique encore "**+ New**"
2. Sélectionne "**Database**" → "**Redis**"
3. C'est fait !

### Étape 5 : Configurer les variables

Clique sur ton service **backend**, puis "**Variables**" et ajoute :

```
SECRET_KEY=clique-generate-pour-generer-automatiquement
JWT_SECRET_KEY=clique-generate-pour-generer-automatiquement
DEBUG=false
CORS_ORIGINS=http://localhost:3000,https://ton-frontend.vercel.app
```

💡 **Astuce**: Railway connecte automatiquement `DATABASE_URL` et `REDIS_URL` !

### Étape 6 : Déployer

Railway déploie automatiquement ! Attends 2-3 minutes.

### Étape 7 : Accéder à ton app

1. Clique "**Settings**" → "**Generate Domain**"
2. Railway te donne une URL comme : `https://ohmvision-xxx.up.railway.app`

**C'est terminé !** 🎉

---

## 🔧 Commandes utiles (Local)

| Action | Commande |
|--------|----------|
| Voir les logs | `docker compose logs -f` |
| Redémarrer | `docker compose restart` |
| Arrêter | `docker compose down` |
| Mise à jour | `git pull && docker compose up -d --build` |

---

## 💰 Coûts

| Plateforme | Prix | Notes |
|------------|------|-------|
| **Railway Hobby** | $5/mois | Parfait pour démarrer |
| **Railway Pro** | $20/mois | Production sérieuse |
| **Local (Docker)** | Gratuit | Sur ton PC |

---

## 🆘 En cas de problème

### "Docker not found"
```bash
# Installer Docker Desktop sur ton ordi
# https://www.docker.com/products/docker-desktop/
```

### "Build failed" sur Railway
```bash
# Vérifie les logs dans Railway Dashboard
# Onglet "Deployments" → Clique sur le build
```

### "Connection refused"
```bash
# Attends 2-3 minutes que les services démarrent
# Vérifie que PostgreSQL et Redis sont verts sur Railway
```

---

## 📞 Support

Si tu bloques, tape dans le chat :
- "Aide-moi à déployer sur Railway"
- "Le backend ne démarre pas"
- "Comment voir les logs ?"

Je t'aiderai étape par étape ! 🤝

---

## 📖 Documentation complète

- **Railway**: [DEPLOYMENT_RAILWAY_COMPLETE.md](DEPLOYMENT_RAILWAY_COMPLETE.md)
- **Windows**: [README_WINDOWS.md](README_WINDOWS.md)
- **Migration Mac→PC**: [MIGRATION_MAC_TO_PC.md](MIGRATION_MAC_TO_PC.md)
