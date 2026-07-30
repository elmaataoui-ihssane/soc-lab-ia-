# Architecture Technique - SOC Lab

## 🏗️ Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                      COUCHE PRÉSENTATION                        │
│  ┌──────────────────┐         ┌──────────────────────────────┐  │
│  │   Dashboard      │         │   SOC Copilot (Chat)         │  │
│  │   Streamlit      │         │   Streamlit                  │  │
│  └────────┬─────────┘         └───────────────┬──────────────┘  │
└───────────┼─────────────────────────────────────┼──────────────┘
            │                                     │
            └─────────────────┬───────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE ORCHESTRATION                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          LangGraph State Machine                         │  │
│  │  ┌────────┐ → ┌──────────┐ → ┌──────────┐               │  │
│  │  │Alerte  │   │Contexte  │   │Priorité  │ →  LLM  ...  │  │
│  │  │Wazuh   │   │MITRE RAG │   │Calc      │               │  │
│  │  └────────┘   └──────────┘   └──────────┘               │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐  ┌────▼──────┐  ┌───▼──────────┐
│ Wazuh Index  │  │ Ollama    │  │ Chroma RAG  │
│ (OpenSearch) │  │ (LLM)     │  │ (Vectors)   │
└──────────────┘  └───────────┘  └─────────────┘
```

---

## 📊 Flux de Données - Triage Automatique

### 1. **Nœud : Récupération Alerte**
- **Entrée** : État initial vide `{}`
- **Traitement** : Requête API OpenSearch → dernière alerte
- **Sortie** : 
  ```json
  {
    "alerte_brute": {...},
    "regle_description": "sshd: brute force trying...",
    "severite": 10,
    "agent_nom": "ubuntu-agent",
    "rule_mitre_id": "T1110.001"
  }
  ```

### 2. **Nœud : Contexte MITRE**

**Priorité 1 : Lookup Exact** (déterministe)
```python
if rule.mitre.id exists:
    resultat = chroma.get(ids=[rule_mitre_id])  # O(1)
    → Retour fiche MITRE directe
```

**Priorité 2 : Recherche Sémantique** (RAG)
```python
else:
    embedding = nomic_embed_text(rule_description)
    resultats = chroma.query(embeddings=[embedding], n_results=1)
    → Recherche vectorielle avec similarité cosinus
```

**Sortie** :
```json
{
  "mitre_contexte": "T1110.001 - Brute Force: Password Guessing...",
  "mitre_methode": "exact" // ou "semantique"
}
```

### 3. **Nœud : Calcul Priorité** (déterministe)
```python
def calculer_priorite(severite):
    if severite >= 8: return "Elevee"
    elif severite >= 4: return "Moyenne"
    else: return "Faible"
```

### 4. **Nœud : Génération LLM** (non-déterministe)

**Input** :
- Alerte brute
- Fiche MITRE
- Priorité calculée

**Prompt** :
```
Tu es un analyste SOC expérimenté.

ALERTE :
Agent: ubuntu-agent
Regle: sshd: brute force...
Severite: 10

FICHE DE REFERENCE :
T1110.001 - Brute Force: Password Guessing
Tentative de deviner un mot de passe par essais répétés...

PRIORITE CALCULEE : Elevee (sévérité 10/10)

Consignes importantes selon la priorité :
- Si "Elevee" : urgence + actions IMMEDIATES...

Réponds UNIQUEMENT avec un objet JSON valide :
{
  "urgence": "...",
  "resume": "...",
  "contexte_mitre": "...",
  "recommandation": "..."
}
```

**Output** :
```json
{
  "urgence": "Elevee",
  "resume": "L'agent ubuntu-agent est victime d'une attaque SSH brute-force...",
  "contexte_mitre": "T1110.001 : Tentative de découvrir un mot de passe...",
  "recommandation": "Isolement immédiat du serveur SSH, blocage des connexions..."
}
```

### 5. **Nœud : Validation** (déterministe)

```python
if json.valid and all_fields_present:
    return "fin"  // Succès
else if retries < MAX_RETRIES:
    return "reessayer"  // Relancer la génération LLM
else:
    return "echec"  // Abandon
```

---

## 🔄 Flux de Données - RAG Conversationnel (Chat)

```
Question Analyste
    ↓
[1] Embedding : nomic_embed_text(question)
    ↓
[2] Query Chroma : similarité cosinus
    ↓
[3] Top-K fiches MITRE les plus proches
    ↓
[4] Construction du prompt :
    - Contexte MITRE injecté
    - Historique conversation (6 derniers échanges)
    - Question actuelle
    ↓
[5] LLM génère réponse texte libre
    ↓
Réponse opérationnelle
```

**Exemple** :
```
Question : "Quelle est la différence entre T1110 et T1110.001 ?"

→ Recherche Chroma : top-2 fiches
  1. T1110 - Brute Force (score 0.92)
  2. T1110.001 - Brute Force: Password Guessing (score 0.95)

→ Injection dans prompt

→ Réponse LLM :
   "T1110 est la technique générale de brute force (tous les types).
    T1110.001 est sa sous-technique : découverte de mot de passe
    par essais répétés. Les techniques enfants de T1110 incluent
    aussi T1110.002 (Password Spraying), T1110.003 (Credential Stuffing)..."
```

---

## 🗂️ Structure de Données

### AgentState (TypedDict)

```python
class AgentState(TypedDict, total=False):
    # Alerte Wazuh
    alerte_brute: dict
    regle_description: str
    severite: int
    agent_nom: str
    rule_mitre_id: Optional[str]
    
    # Contexte MITRE
    mitre_contexte: str
    mitre_methode: str  # "exact" | "semantique" | "aucun"
    
    # Décisions
    priorite: str  # "Elevee" | "Moyenne" | "Faible"
    
    # LLM
    llm_sortie: Optional[dict]  # {"urgence", "resume", "contexte_mitre", "recommandation"}
    
    # Retry
    retries: int
    erreur: Optional[str]
```

### Chroma Collection (MITRE)

```
Collection: "mitre_attack"
Métric: cosine  (similarité cosinus, pas euclidienne)

Chaque document :
  id: "T1110.001"
  embedding: [float × 768]  # Embedding nomic
  document: "Tentative de deviner un mot de passe..."
  metadata: {"nom": "Brute Force: Password Guessing"}
```

---

## ⚙️ Paramètres de Tuning

### LangGraph

```python
MAX_RETRIES = 2  # Nombre de tentatives de génération LLM
```

### Chroma RAG

```python
"hnsw:space": "cosine"  # Métrique de similarité
# NB: L2 euclidienne inadaptée aux embeddings nomic
# → Passage à cosine augmente la précision de 50% → 80%
```

### Ollama

```python
model: "llama3.2:3b"  # Modèle léger, optimisé pour GPUs faibles
temperature: 0.7  # (défaut)
max_tokens: 2048
```

### Prompt Engineering

**Zones clés** :

1. **Injection de priorité explicite** (vs. noyée dans le texte)
   ```
   PRIORITE CALCULEE : {priorite}
   ```

2. **Consignes différenciées par urgence**
   ```
   - Si "Elevee" : [actions immédiates]
   - Si "Moyenne" : [surveillance]
   - Si "Faible" : [bonnes pratiques]
   ```

3. **Format JSON strict**
   ```
   Reponds UNIQUEMENT avec un objet JSON valide...
   ```

---

## 🚀 Performance

### Latence par nœud (benchmark)

| Nœud | Temps | Notes |
|------|-------|-------|
| Récupération alerte | 0.2s | API OpenSearch |
| Contexte MITRE (exact) | 0.01s | Lookup Chroma |
| Contexte MITRE (sémantique) | 0.5s | Embedding + query |
| Calcul priorité | 0.001s | Python pur |
| Génération LLM | 2-3s | Ollama llama3.2:3b |
| Validation | 0.01s | JSON parse |
| **Total pipeline** | **2.7s** | Exécution complète |

### Scalabilité

- **Nombre d'alertes** : Illimité (OpenSearch gère)
- **Nombre de techniques MITRE** : 709 (indexées)
- **Concurrent users** : Dépend de Streamlit (recommandé ≤ 10)
- **Taille Chroma** : ~500MB (entièrement en RAM recommandé)

---

## 🔐 Sécurité

### Flux d'authentification

```
Dashboard / Chat
    ↓
.env (API credentials)
    ↓
Wazuh Indexer + API
    ↓
[Vérification JWT si applicable]
    ↓
Données sensibles (isolation réseau recommandée)
```

### Points critiques

1. **Identifiants Wazuh** : Stocker dans `.env` (ignoré par Git)
2. **SSL/TLS** : `verify=False` en lab uniquement
3. **Ollama** : Ne pas exposer publiquement (localhost:11434)
4. **Chroma** : Pas d'authentification native (isolation réseau requise)
5. **Logs** : Audit des recommandations IA générées

---

## 📈 Métriques d'Évaluation

### RAG MITRE ATT&CK

- **Précision@3** : 80% (8/10)
- **Métrique** : Cosine similarity
- **Corpus** : 709 techniques
- **Cas d'échec** : Descriptions trop génériques ou courtes

### Triage d'Alertes

- **Couverture** : 6 familles de comportements
- **Techniques MITRE** : 11 distinctes
- **Systèmes d'exploitation** : 2 (Ubuntu + Windows)
- **Taux de validation JSON** : 100% (après retry)

---

## 🔧 Dépannage Technique

### Debug du graphe LangGraph

```python
# Afficher l'état à chaque nœud
resultat = app.invoke({}, debug=True)
```

### Inspecter Chroma

```python
import chromadb
client = chromadb.PersistentClient(path="./chroma_mitre")
col = client.get_or_create_collection("mitre_attack")
print(f"Techniques indexées : {col.count()}")

# Tester une requête
embedding = [...] # Un embedding de test
results = col.query(query_embeddings=[embedding], n_results=5)
```

### Tester Ollama

```bash
curl http://localhost:11434/api/generate \
  -d '{
    "model": "llama3.2:3b",
    "prompt": "What is T1110.001?",
    "stream": false
  }'
```

---

## 📚 Ressources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Wazuh Documentation](https://documentation.wazuh.com/)
