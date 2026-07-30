# Guide d'Installation - SOC Lab

## 📋 Prérequis

### Système
- **OS** : Linux (Ubuntu 22.04+) ou macOS
- **RAM** : 8GB minimum (16GB recommandé)
- **Disque** : 20GB libre
- **Python** : 3.9+

### Logiciels
- **Wazuh** 4.14+ (déjà déployé et opérationnel)
- **Ollama** (pour les modèles LLM locaux)
- **Docker & Docker Compose** (optionnel, pour déploiement rapide)

---

## 🚀 Installation Rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/yourusername/soc-lab-ia.git
cd soc-lab-ia
```

### 2. Créer l'environnement Python

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos paramètres
nano .env
```

**Paramètres essentiels à remplacer** :
- `INDEXER_HOST` : IP de votre serveur Wazuh
- `INDEXER_USER` / `INDEXER_PASSWORD` : Identifiants OpenSearch (Wazuh)
- `OLLAMA_HOST` : Adresse du serveur Ollama

### 5. Extraire et indexer le corpus MITRE ATT&CK

```bash
# Extraire 709 techniques depuis le repo MITRE officiel
python3 scripts/extraire_mitre.py

# Générer les embeddings et indexer dans Chroma
python3 scripts/indexer_mitre_chroma.py
```

⏱️ *La première indexation prend 5-10 min (génération des embeddings)*

### 6. Démarrer l'agent IA

```bash
# Test rapide du pipeline complet
python3 agent_graph.py
```

Vous devriez voir :
```
Méthode contexte MITRE : exact (ou semantique)
Priorité : Elevee/Moyenne/Faible (sévérité X/10)
Tentatives de génération : 1
=== Analyse IA ===
{
  "urgence": "...",
  "resume": "...",
  "contexte_mitre": "...",
  "recommandation": "..."
}
```

### 7. Démarrer le dashboard

```bash
streamlit run dashboard.py
```

Accès : **http://localhost:8501**

---

## 🐳 Installation avec Docker Compose (Optionnel)

Si vous avez Docker et Docker Compose :

```bash
docker-compose up -d
```

Services lancés :
- Dashboard Streamlit : http://localhost:8501
- Ollama : http://localhost:11434
- Chroma : Port 8000

---

## 🔧 Configuration Détaillée

### Wazuh Indexer (OpenSearch)

Par défaut, Wazuh utilise :
- **Host** : `https://<IP_Wazuh>:9200`
- **Utilisateur** : `admin`
- **Mot de passe** : Défini lors du déploiement Wazuh

**Vérifier la connexion** :
```bash
curl -u admin:PASSWORD -k https://192.168.10.135:9200/_cat/indices
```

### Ollama

**Installation** :
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

**Lancer Ollama** :
```bash
ollama serve
```

**Télécharger le modèle** (dans un autre terminal) :
```bash
ollama pull llama3.2:3b
```

Vérifier :
```bash
curl http://localhost:11434/api/tags
```

### Chroma

Généré automatiquement lors de la première indexation.
Emplacement : `./chroma_mitre/`

---

## ✅ Validation

### Test complet du pipeline

```bash
python3 agent_graph.py
```

Résultat attendu :
```
✓ Récupération alerte depuis Wazuh
✓ Contexte MITRE trouvé (exact ou sémantique)
✓ Priorité calculée
✓ Analyse IA générée
✓ Validation JSON réussie
```

### Test du RAG (Recherche sémantique)

```bash
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='./chroma_mitre')
collection = client.get_or_create_collection('mitre_attack')
print(f'Techniques indexées : {collection.count()}')
"
```

Résultat : `Techniques indexées : 709`

### Test du Dashboard

1. Accéder à http://localhost:8501
2. Vérifier que les alertes s'affichent
3. Cliquer sur "Analyser" pour une alerte
4. Vérifier que l'analyse IA s'affiche

### Test du Chat SOC Copilot

1. Cliquer sur "SOC Copilot" dans la barre latérale
2. Poser une question : "C'est quoi T1110.001 ?"
3. Vérifier que la réponse contient le contexte MITRE

---

## 🐛 Troubleshooting

### ❌ "Impossible de se connecter à Wazuh"

```bash
# Vérifier la connectivité
curl -u admin:PASSWORD -k https://192.168.10.135:9200/

# Vérifier les paramètres dans .env
grep INDEXER .env
```

### ❌ "Ollama n'est pas accessible"

```bash
# Vérifier qu'Ollama est en cours d'exécution
curl http://localhost:11434/api/tags

# Relancer Ollama
ollama serve
```

### ❌ "Erreur : JSON invalide du LLM"

Cela peut arriver occasionnellement. Le pipeline réessaiera automatiquement.

Limiter les retries (MAX_RETRIES dans agent_graph.py) :
```python
MAX_RETRIES = 2  # Augmenter à 3 ou 4 si nécessaire
```

### ❌ "Chroma vide ou non indexée"

```bash
# Réindexer
python3 scripts/indexer_mitre_chroma.py

# Vérifier le nombre de techniques
python3 -c "
import chromadb
c = chromadb.PersistentClient(path='./chroma_mitre')
col = c.get_or_create_collection('mitre_attack')
print(f'Techniques : {col.count()}')
"
```

---

## 🔒 Configuration Sécurité (Production)

### 1. Remplacer les identifiants par défaut

```bash
# .env (avant déploiement)
INDEXER_USER=soc_lab_user
INDEXER_PASSWORD=$(openssl rand -base64 32)
WAZUH_API_USER=soc_lab_api
WAZUH_API_PASSWORD=$(openssl rand -base64 32)
```

### 2. Valider les certificats SSL

```bash
# Au lieu de verify=False, utiliser un CA bundle
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
```

### 3. Isoler Ollama et Chroma

```bash
# Ne pas exposer Ollama publiquement
# Firewall : autoriser localhost:11434 uniquement
```

### 4. Audit des analyses

Activer la journalisation :
```python
# Dans agent_graph.py
import logging
logging.basicConfig(filename='soc_lab.log', level=logging.INFO)
```

---

## 📦 Mise à Jour

### Mettre à jour les dépendances

```bash
pip install --upgrade -r requirements.txt
```

### Mettre à jour le corpus MITRE

```bash
# Extraire la dernière version du repo MITRE
python3 scripts/extraire_mitre.py

# Réindexer
python3 scripts/indexer_mitre_chroma.py
```

---

## 🆘 Support

- 📧 Ouvrir une **Issue** sur GitHub
- 💬 Consulter la **documentation complète** en ../docs/
- 📖 Lire le **rapport d'étape** (../RAPPORT_STAGE.pdf)
