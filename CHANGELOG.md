# Changelog

Tous les changements importants du projet SOC Lab sont documentés ici.

## [1.0.0] - 2026-07-29

### ✨ Features

#### Agent IA de Triage
- **LangGraph Orchestration** : Pipeline d'orchestration avec état partagé et gestion des erreurs
- **Lookup Exact MITRE** : Récupération directe de fiches MITRE via ID natif Wazuh
- **RAG Sémantique** : Recherche vectorielle Chroma avec similarité cosinus
  - Corpus : 709 techniques MITRE ATT&CK
  - Précision@3 : 80% (8/10)
- **Génération IA** : Modèle Ollama llama3.2:3b pour analyse structurée
- **Retry Automatique** : Validation JSON + nouvelle tentative en cas d'erreur

#### Dashboard Streamlit
- Affichage alertes récentes (20 dernières)
- Indicateurs visuels de sévérité (🔴🟠🟢)
- Bouton "Analyser" par alerte
- Affichage résultats en temps réel
- Historique d'analyses en session

#### SOC Copilot (Chat)
- Questions libres sur techniques MITRE
- Recherche sémantique contextualisée
- Historique conversation (6 derniers échanges)
- Réponses texte libre opérationnelles

### 🔍 Évaluation

#### Corpus de Test
- **Windows** : 2 scénarios (brute-force, gestion comptes)
- **Ubuntu** : 6 scénarios (SSH brute-force, sudo abuse, intégrité fichiers, etc.)
- **OPNsense** : Intégration syslog
- **Atomic Red Team** : Tests atomiques (T1548.003, T1070.003, T1003.008)

#### Techniques MITRE Couvertes
- T1078 : Valid Accounts
- T1110 / T1110.001 : Brute Force / Password Guessing
- T1021.004 : Remote Services: SSH
- T1548.003 : Abuse Elevation Control Mechanism: Sudo
- T1098 / T1136 : Account Manipulation / Create Account
- T1531 : Account Access Removal
- T1484 : Domain Policy Modification
- T1565.001 : Data Destruction - Stored Data Manipulation
- T1070.003 : Defense Evasion - Clear Bash History
- T1003.008 : Data from Local System - Access /etc/shadow

### 📦 Dépendances Clés

```
langgraph==0.0.20          # Orchestration
langchain==0.1.8           # Framework LLM
chromadb==0.4.21           # Vector DB
streamlit==1.28.1          # Interface
requests==2.31.0           # HTTP client
```

### 🏗️ Architecture

- **Wazuh** 4.14.6 : SIEM, indexation OpenSearch
- **Ollama** : Serveur LLM local
- **Chroma** : Base vectorielle persistante
- **Streamlit** : Interface web interactive

### 📚 Documentation

- ✅ README.md avec guide rapide
- ✅ docs/INSTALLATION.md (7 sections)
- ✅ docs/ARCHITECTURE.md (flux détaillés)
- ✅ CONTRIBUTING.md (guidelines)
- ✅ LICENSE (MIT)

---

## [0.1.0] - Phase Expérimentale (Juillet 2026)

### ✨ Prototypes & Validation

- Prototype agent IA de triage (sections 6.1-6.5 du rapport)
- Indexation RAG MITRE (chapitre 7)
- Orchestration LangGraph (chapitre 1 - Part 2)
- Dashboard Streamlit (chapitre 2 - Part 2)
- Chat conversationnel (chapitre 3 - Part 2)

### 📊 Résultats d'Étape

- ✅ SOC lab complet déployé
- ✅ Agents Windows + Ubuntu actifs
- ✅ Intégration OPNsense validée
- ✅ 11 scénarios de test documentés
- ✅ RAG MITRE à 80% de précision
- ✅ Pipeline complètement testé

---

## Perspectives Futures

### Phase 2 (À venir)

- ⏳ Intégrations complémentaires :
  - Sysmon (visibilité processus)
  - VirusTotal (détection malware)
  - Suricata (détection réseau)
- ⏳ Couche de décision d'action (SOAR)
  - Isolation automatique d'endpoints
  - Blocage IP
  - Escalade N2/N3
- ⏳ Tests de robustesse à grande échelle
- ⏳ Amélioration RAG (fine-tuning embedding)
- ⏳ Interface de gestion d'alertes avancée

### Améliorations Continues

- 🔄 Optimisation prompt engineering
- 🔄 Support modèles LLM supplémentaires
- 🔄 Métriques d'évaluation étendues
- 🔄 Dashboard analytics avancé

---

## Notes de Release

### Installation depuis GitHub

```bash
git clone https://github.com/yourusername/soc-lab-ia.git
cd soc-lab-ia
pip install -r requirements.txt
python3 scripts/extraire_mitre.py
python3 scripts/indexer_mitre_chroma.py
streamlit run dashboard.py
```

### Upgrade depuis [0.1.0]

```bash
git pull origin main
pip install --upgrade -r requirements.txt
```

### Problèmes Connus

- Latence initiale du chat (2-3s pour première requête)
- Occasionnellement JSON invalide du LLM (retry gère)
- Dépendance vis-à-vis des identifiants Wazuh par défaut

---

## Remerciements

- **Groupe MANAGEM** : Entreprise d'accueil
- **ENSAM Casablanca** : Formation
- **Communautés** : Wazuh, LangChain, Streamlit
