# 📝 Guide Complet : Comment Poster sur GitHub

## 🎯 Étapes pour Mettre Ton Projet sur GitHub

### **Étape 1️⃣ : Créer un compte GitHub (si pas déjà fait)**

1. Aller sur **[github.com](https://github.com)**
2. Cliquer sur **"Sign up"** (en haut à droite)
3. Suivre les étapes :
   - Email
   - Mot de passe fort
   - Nom d'utilisateur unique
   - Vérifier ton email
4. ✅ Compte créé !

---

### **Étape 2️⃣ : Créer un nouveau dépôt (Repository)**

1. Une fois connecté, clique sur **"+"** en haut à droite
2. Sélectionner **"New repository"**
3. Remplir les champs :

   | Champ | Valeur |
   |-------|--------|
   | **Repository name** | `soc-lab-ia` |
   | **Description** | `Intelligence Artificielle pour triage d'alertes Wazuh - Agent IA + Dashboard + Chat` |
   | **Public/Private** | ✅ **Public** |
   | **Add .gitignore** | ✅ Sélectionner "Python" |
   | **Choose a license** | ✅ "MIT License" |
   | **Add a README** | ⚠️ **NON** (tu l'as déjà) |

4. Cliquer sur **"Create repository"**
5. ✅ Dépôt créé !

---

### **Étape 3️⃣ : Cloner et pousser tes fichiers**

#### **Option A : Depuis ton terminal (recommandé)**

```bash
# 1. Aller dans le dossier soc-lab-ia
cd /chemin/vers/soc-lab-ia

# 2. Initialiser Git (si pas déjà fait)
git init
git add .
git commit -m "Initial commit: SOC Lab avec agent IA MITRE"

# 3. Ajouter le lien vers GitHub
# Remplacer "yourusername" par ton username GitHub
git remote add origin https://github.com/yourusername/soc-lab-ia.git

# 4. Pousser les fichiers
git branch -M main
git push -u origin main
```

**Entrer tes identifiants** :
- Username : ton username GitHub
- Password : ton **Personal Access Token** (pas ton mot de passe !)

#### **Générer un Personal Access Token :**

1. Aller sur [github.com/settings/tokens](https://github.com/settings/tokens)
2. Cliquer "Generate new token"
3. Sélectionner les scopes :
   - ✅ `repo` (accès complet aux dépôts)
   - ✅ `workflow` (pour CI/CD futur)
4. Générer le token
5. **Copier et sauvegarder** (tu ne pourras plus le voir après !)
6. Utiliser ce token comme mot de passe

#### **Option B : Interface GitHub (plus simple)**

1. Sur la page du dépôt, cliquer "Upload files"
2. Glisser-déposer tous les fichiers du dossier `soc-lab-ia`
3. Ajouter un message de commit
4. Cliquer "Commit changes"

---

### **Étape 4️⃣ : Vérifier que tout est là**

Une fois poussé, ton dépôt devrait contenir :

```
soc-lab-ia/
├── README.md ✅
├── LICENSE ✅
├── CHANGELOG.md ✅
├── CONTRIBUTING.md ✅
├── requirements.txt ✅
├── .env.example ✅
├── .gitignore ✅
├── architecture.jpg ✅ (L'image importante !)
├── agent_graph.py ✅
├── dashboard.py ✅
├── Dockerfile ✅
├── docker-compose.yml ✅
├── pages/
│   └── 1_Chat_SOC_Copilot.py ✅
├── scripts/
│   ├── extraire_mitre.py ✅
│   ├── indexer_mitre_chroma.py ✅
│   └── ground_truth.py ✅
└── docs/
    ├── INSTALLATION.md ✅
    └── ARCHITECTURE.md ✅
```

---

## 🎨 Améliorer ton Dépôt GitHub

### **Ajouter des Badges dans le README**

Dans le README.md, en haut, ajouter :

```markdown
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/yourusername/soc-lab-ia?style=social)](https://github.com/yourusername/soc-lab-ia)
```

### **Ajouter des Topics**

1. Aller dans **Settings** → **Topics**
2. Ajouter les topics :
   - `soc`
   - `wazuh`
   - `artificial-intelligence`
   - `security`
   - `mitre-attack`
   - `langgraph`
   - `streamlit`
   - `rag`
   - `llm`

### **Configurer les Pages GitHub (optionnel)**

Pour avoir une documentation en ligne :

1. Aller dans **Settings** → **Pages**
2. Sélectionner **"Main branch"** → **"docs folder"**
3. Attendre quelques minutes
4. Accès : `https://yourusername.github.io/soc-lab-ia/`

---

## 📋 Checklist Avant de Poster

Avant de pousser, vérifier que :

- ✅ Tous les fichiers sont présents
- ✅ Le `.gitignore` est correct (pas de `.env` ni `chroma_mitre/`)
- ✅ Le README est clair et à jour
- ✅ Les liens dans la doc sont valides
- ✅ Les images s'affichent (`architecture.jpg`)
- ✅ Le LICENSE est présent (MIT)
- ✅ Pas de secrets sensibles dans le code (API keys, passwords)

### Avant de pousser, nettoyer :

```bash
# Vérifier que les fichiers sensibles ne seront pas poussés
git status

# Ne JAMAIS pousser :
# - .env (avec vraies creds)
# - chroma_mitre/ (données volumineuses)
# - __pycache__/
# - *.log
```

---

## 🚀 Après la Publication

### **Partager le Lien**

Ton projet sera accessible à :
```
https://github.com/yourusername/soc-lab-ia
```

Partager ce lien :
- 📧 Email professionnel
- 📋 CV/Portfolio
- 💼 LinkedIn
- 🤝 Groupe de sécurité

### **Faire une Release (optionnel)**

Pour un vrai release (avec version) :

1. Aller dans **Releases** → **Draft a new release**
2. Tag version : `v1.0.0`
3. Title : "SOC Lab v1.0.0 - Initial Release"
4. Description : Résumé des features
5. Créer la release

---

## 📊 Metrics GitHub à Suivre

Après publication, tu pourras voir :
- 🌟 Nombre de **Stars** (favoris)
- 👁️ Nombre de **Watchers** (abonnés)
- 🔀 Nombre de **Forks** (copies du projet)
- 📈 Trafic (nombre de visiteurs)

Ces métriques montrent l'intérêt pour ton projet !

---

## 🆘 Aide & Ressources

### Si tu as un problème :

1. **"My repository is empty"**
   ```bash
   # Vérifie que Git est installé
   git --version
   # Puis refais : git add . && git commit && git push
   ```

2. **"Permission denied"**
   - Utilise ton Personal Access Token, pas ton mot de passe
   - Ou configure les clés SSH (plus avancé)

3. **"Large files not allowed"**
   - GitHub a une limite de 100MB par fichier
   - Le projet ici fait ~200KB total, donc pas de problème

### Ressources utiles :

- 📖 [GitHub Docs Officiel](https://docs.github.com/)
- 🎓 [Hello World GitHub](https://guides.github.com/activities/hello-world/)
- 💡 [Best Practices pour README](https://github.com/matiassingers/awesome-readme)

---

## 📝 Template pour Publication

Une fois ton dépôt en ligne, tu peux publier :

### Sur LinkedIn :

```
🔒 Projet : SOC Lab - Intelligence Artificielle pour la Sécurité

J'ai développé une solution complète de triage automatique d'alertes de sécurité :
✅ SIEM Wazuh + Agent IA (LangGraph)
✅ Dashboard Streamlit interactif
✅ RAG MITRE ATT&CK (80% précision)
✅ Chat conversationnel SOC Copilot

📦 Code source open-source sur GitHub
#SOC #Wazuh #AI #Cybersecurity #Python

[Lien vers le dépôt]
```

### Partage interne (équipe MANAGEM) :

```
Bonjour,

Projet SOC Lab publié sur GitHub :
- Complet et documenté (15+ fichiers)
- Prêt pour production
- Architecture extensible
- Tests documentés

Lien : https://github.com/yourusername/soc-lab-ia

Vous pouvez :
✓ Fork et déployer
✓ Contribuer
✓ Signaler des améliorations
```

---

## ✨ Félicitations ! 🎉

Ton projet est maintenant public et accessible au monde entier !

**Les prochaines étapes** :
- 📈 Attendre les réactions (stars, forks)
- 💬 Répondre aux questions (Issues)
- 🔄 Mettre à jour avec les améliorations
- 📢 Promouvoir le projet

Bon luck ! 🚀
