# 🎯 GUIDE ULTRA-SIMPLIFIÉ - OhmVision

**Pour novices** - Suivez étape par étape !

---

## 📋 Avant de commencer

Tu auras besoin de :
- ✅ Un compte Hetzner (https://console.hetzner.cloud/) - gratuit à créer
- ✅ Une carte bancaire (serveur = €4.51/mois)
- ✅ 15 minutes de ton temps

---

## 🎮 OPTION A : TEST LOCAL (5 minutes)

**Objectif:** Tester que tout fonctionne sur ton ordi avant de déployer.

### Étape 1 : Configurer le fichier .env

```bash
# Dans le terminal VS Code, tape:
./setup-simple.sh local
```

### Étape 2 : Lancer avec Docker

```bash
docker compose up -d
```

### Étape 3 : Accéder à l'app

Ouvre ton navigateur : **http://localhost:8000**

**C'est tout !** Tu peux tester l'application.

---

## 🌐 OPTION B : DÉPLOIEMENT HETZNER (15 minutes)

### Étape 1 : Créer un serveur Hetzner

1. Va sur https://console.hetzner.cloud/
2. Crée un compte (email + mot de passe)
3. Clique "**+ Create a server**"

**Choisis :**
```
📍 Location: Falkenstein (le moins cher)
🖥️ Image: Ubuntu 24.04
💻 Type: CAX11 (€4.51/mois) - ARM, super rapport qualité/prix
🔑 SSH Key: Ajoute ta clé publique (voir ci-dessous si tu n'en as pas)
📝 Name: ohmvision
```

4. Clique "**Create & Buy Now**"
5. **Note l'adresse IP** qui s'affiche (ex: 195.201.123.92)

### Étape 2 : Générer une clé SSH (si tu n'en as pas)

```bash
# Dans le terminal VS Code:
ssh-keygen -t ed25519 -C "ton-email@gmail.com"
# Appuie Entrée 3 fois

# Affiche ta clé publique:
cat ~/.ssh/id_ed25519.pub
```
Copie le contenu et colle-le dans Hetzner lors de la création du serveur.

### Étape 3 : Déployer automatiquement

```bash
# Dans le terminal VS Code:
./setup-simple.sh deploy TON_IP_SERVEUR
```

Remplace `TON_IP_SERVEUR` par l'IP de ton serveur Hetzner.

**Le script fait TOUT automatiquement en ~10 minutes :**
- ✅ Installe Docker sur le serveur
- ✅ Copie l'application
- ✅ Configure la base de données
- ✅ Démarre tout

### Étape 4 : C'est terminé !

Ouvre ton navigateur : **http://TON_IP_SERVEUR**

---

## 🔧 Commandes utiles

| Action | Commande |
|--------|----------|
| Voir les logs | `docker compose logs -f` |
| Redémarrer | `docker compose restart` |
| Arrêter | `docker compose down` |
| Mise à jour | `git pull && docker compose up -d --build` |

---

## 🆘 En cas de problème

### "Docker not found"
```bash
# Installer Docker Desktop sur ton ordi
# https://www.docker.com/products/docker-desktop/
```

### "Connection refused"
```bash
# Attends 2-3 minutes que les services démarrent
docker compose logs backend
```

### "Permission denied (SSH)"
```bash
# Vérifie que ta clé SSH est bien ajoutée sur Hetzner
cat ~/.ssh/id_ed25519.pub
```

---

## 📞 Support

Si tu bloques, tape dans le chat :
- "Aide moi à déployer sur Hetzner"
- "Le backend ne démarre pas"
- "Comment voir les logs ?"

Je t'aiderai étape par étape ! 🤝
