# Guide de Contribution

Merci de l'intérêt que vous portez à ce projet ! Voici comment contribuer.

## 📋 Avant de commencer

1. **Fork** le dépôt
2. **Clone** votre fork : `git clone https://github.com/yourname/soc-lab-ia.git`
3. **Créer une branche** : `git checkout -b feature/votre-feature`

## ✨ Types de contributions bienvenues

### 🐛 Rapporter des bugs

1. Vérifier que le bug n'existe pas déjà dans [Issues](https://github.com/yourusername/soc-lab-ia/issues)
2. Créer une nouvelle Issue avec :
   - Titre clair
   - Description détaillée
   - Étapes pour reproduire
   - Résultats attendus vs. observés
   - Environnement (OS, versions, etc.)

### 🚀 Proposer des features

1. Vérifier qu'une feature similaire n'existe pas
2. Créer une Issue avec le libellé `enhancement`
3. Décrire :
   - Cas d'usage
   - Solution proposée
   - Alternatives envisagées

### 📚 Améliorer la documentation

- Corriger les typos ou imprécisions
- Clarifier les explications
- Ajouter des exemples

### 💻 Code

Domaines d'amélioration :

- **RAG MITRE** : Optimiser la recherche sémantique (précision@3 = 80%)
- **LLM** : Améliorer le prompt engineering
- **Dashboard** : Nouvelles visualisations
- **Tests** : Augmenter la couverture de test
- **Performance** : Réduire les latences

## 🛠️ Workflow de contribution

### 1. Configurer l'environnement

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Développement
pip install black flake8 mypy pytest
```

### 2. Faire les changements

```bash
# Votre code
git add .
git commit -m "feat: description courte (impératif)"
```

**Format des commits** :
- `feat:` nouvelle feature
- `fix:` correction bug
- `docs:` documentation
- `test:` tests
- `refactor:` refactoring
- `perf:` performance

### 3. Formatter et vérifier

```bash
# Formatter
black *.py scripts/*.py pages/*.py

# Linter
flake8 --max-line-length=100

# Type checking
mypy agent_graph.py

# Tests
pytest
```

### 4. Pousser et créer une PR

```bash
git push origin feature/votre-feature
```

Créer une Pull Request sur GitHub avec :
- Titre descriptif
- Description détaillée
- Référence à l'Issue associée (`Fixes #123`)
- Screenshots si pertinent

## 📝 Guidelines de code

### Python

- Python 3.9+
- PEP 8 (via Black)
- Docstrings sur tous les modules/fonctions
- Type hints (`TypedDict`, `Optional`, etc.)

### Exemple

```python
def calculer_priorite(severite: int) -> str:
    """
    Calcule la priorité en fonction de la sévérité Wazuh.
    
    Args:
        severite: Niveau de sévérité (0-15)
    
    Returns:
        Priorité : "Elevee", "Moyenne", ou "Faible"
    
    Examples:
        >>> calculer_priorite(10)
        'Elevee'
    """
    if severite >= 8:
        return "Elevee"
    # ...
```

## 🧪 Tests

Ajouter des tests pour toute nouvelle feature :

```python
# tests/test_agent_graph.py
import pytest
from agent_graph import calculer_priorite

def test_calculer_priorite_elevee():
    assert calculer_priorite(10) == "Elevee"

def test_calculer_priorite_moyenne():
    assert calculer_priorite(5) == "Moyenne"
```

Lancer les tests :
```bash
pytest tests/
pytest --cov  # Avec couverture
```

## 🚀 Déploiement

### Pour les mainteneurs

1. Vérifier que tous les tests passent
2. Mettre à jour la version dans `setup.py` (si présent)
3. Mettre à jour `CHANGELOG.md`
4. Merger la PR
5. Créer un tag : `git tag v1.x.y && git push --tags`

## ❓ Questions ou suggestions ?

- 💬 Ouvrir une [Discussion](https://github.com/yourusername/soc-lab-ia/discussions)
- 📧 Contacter les mainteneurs
- 📚 Consulter la [FAQ](docs/FAQ.md)

---

**Merci de votre contribution ! 🙏**

Tout le monde est bienvenue, peu importe votre niveau d'expérience.
