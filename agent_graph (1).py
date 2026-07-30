"""
agent_graph.py - Pipeline d'orchestration LangGraph pour triage IA des alertes Wazuh

Flux :
  1. Récupération alerte via API Wazuh indexer
  2. Contexte MITRE (lookup exact → RAG sémantique)
  3. Calcul priorité (déterministe)
  4. Génération analyse (LLM Ollama)
  5. Validation JSON + Retry automatique
"""

import requests
import json
import chromadb
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

# ====================================================================
# Configuration
# ====================================================================

INDEXER_HOST = "https://192.168.10.135:9200"
INDEXER_USER = "admin"
INDEXER_PASSWORD = "admin"
OLLAMA_HOST = "http://localhost:11434"
MAX_RETRIES = 2

client = chromadb.PersistentClient(path="./chroma_mitre")
collection = client.get_or_create_collection("mitre_attack")


# ====================================================================
# État partagé du graphe
# ====================================================================

class AgentState(TypedDict, total=False):
    """État partagé circulant dans le graphe LangGraph"""
    
    alerte_brute: dict
    regle_description: str
    severite: int
    agent_nom: str
    rule_mitre_id: Optional[str]
    
    mitre_contexte: str
    mitre_methode: str  # "exact" ou "semantique"
    
    priorite: str
    
    llm_sortie: Optional[dict]
    retries: int
    erreur: Optional[str]


# ====================================================================
# Fonctions utilitaires
# ====================================================================

def get_embedding(text):
    """Génère un embedding via Ollama"""
    resp = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    return resp.json()["embedding"]


def calculer_priorite(severite):
    """Calcule la priorité en fonction de la sévérité Wazuh"""
    if severite >= 8:
        return "Elevee"
    elif severite >= 4:
        return "Moyenne"
    else:
        return "Faible"


# ====================================================================
# Nœud 1 : Récupération de la dernière alerte
# ====================================================================

def noeud_recuperer_alerte(state: AgentState) -> AgentState:
    """Récupère la dernière alerte depuis wazuh-alerts-* via OpenSearch"""
    import urllib3
    urllib3.disable_warnings()
    
    response = requests.get(
        f"{INDEXER_HOST}/wazuh-alerts-*/_search",
        auth=(INDEXER_USER, INDEXER_PASSWORD),
        verify=False,
        json={"size": 1, "sort": [{"timestamp": {"order": "desc"}}]}
    )
    
    hit = response.json()["hits"]["hits"][0]["_source"]
    
    rule = hit.get("rule", {})
    mitre = rule.get("mitre", {})
    mitre_id = mitre.get("id")
    
    return {
        **state,
        "alerte_brute": hit,
        "regle_description": rule.get("description", ""),
        "severite": rule.get("level", 0),
        "agent_nom": hit.get("agent", {}).get("name", "inconnu"),
        "rule_mitre_id": mitre_id[0] if isinstance(mitre_id, list) else mitre_id,
        "retries": 0
    }


# ====================================================================
# Nœud 2 : Contexte MITRE (lookup exact → RAG sémantique)
# ====================================================================

def noeud_contexte_mitre(state: AgentState) -> AgentState:
    """
    Priorité 1 : Lookup exact si rule.mitre.id existe
    Priorité 2 : Recherche sémantique en secours
    """
    mitre_id = state.get("rule_mitre_id")
    
    # Priorité 1 : Lookup exact
    if mitre_id:
        resultat = collection.get(ids=[mitre_id])
        if resultat["documents"]:
            return {
                **state,
                "mitre_contexte": resultat["documents"][0],
                "mitre_methode": "exact"
            }
    
    # Priorité 2 : Recherche sémantique
    embedding = get_embedding(state["regle_description"])
    resultats = collection.query(query_embeddings=[embedding], n_results=1)
    if resultats["documents"][0]:
        return {
            **state,
            "mitre_contexte": resultats["documents"][0][0],
            "mitre_methode": "semantique"
        }
    
    # Fallback
    return {
        **state,
        "mitre_contexte": "Aucune fiche MITRE trouvée.",
        "mitre_methode": "aucun"
    }


# ====================================================================
# Nœud 3 : Calcul de la priorité (déterministe, pas de LLM)
# ====================================================================

def noeud_calculer_priorite(state: AgentState) -> AgentState:
    """Calcul déterministe basé sur la sévérité Wazuh"""
    return {**state, "priorite": calculer_priorite(state["severite"])}


# ====================================================================
# Nœud 4 : Génération de l'analyse par le LLM
# ====================================================================

def noeud_generer_llm(state: AgentState) -> AgentState:
    """Génère l'analyse structurée via Ollama"""
    
    prompt = f"""Tu es un analyste SOC expérimenté. Voici une alerte
de sécurité et une fiche de référence MITRE ATT&CK.

ALERTE :
Agent: {state['agent_nom']}
Regle: {state['regle_description']}
Severite: {state['severite']}

FICHE DE REFERENCE :
{state['mitre_contexte']}

PRIORITE CALCULEE : {state['priorite']} (sévérité {state['severite']}/10)

Consignes importantes selon la priorité :
- Si la priorité est "Elevee" : le résumé doit commencer par signaler
clairement l'urgence et le risque immédiat. La recommandation doit inclure
une action IMMEDIATE (isolement, blocage, escalade vers l'analyste N2)
en plus des mesures de durcissement.
- Si la priorité est "Moyenne" : signaler le comportement suspect sans
urgence excessive, recommandation orientée surveillance renforcée.
- Si la priorité est "Faible" : ton informatif, recommandation orientée
bonnes pratiques.

Reponds UNIQUEMENT avec un objet JSON valide, exactement ce
format, sans aucun texte avant ou apres :
{{
"urgence": "...",
"resume": "...",
"contexte_mitre": "...",
"recommandation": "..."
}}
"""
    
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
    )
    
    try:
        sortie = json.loads(response.json()["response"])
        return {**state, "llm_sortie": sortie, "erreur": None}
    except (json.JSONDecodeError, KeyError) as e:
        return {**state, "llm_sortie": None, "erreur": str(e)}


# ====================================================================
# Nœud 5 : Validation JSON
# ====================================================================

CHAMPS_ATTENDUS = {"urgence", "resume", "contexte_mitre", "recommandation"}


def noeud_valider(state: AgentState) -> AgentState:
    """Vérifie que le JSON contient tous les champs attendus"""
    sortie = state.get("llm_sortie")
    if sortie and CHAMPS_ATTENDUS.issubset(sortie.keys()):
        return {**state, "erreur": None}
    return {
        **state,
        "erreur": "JSON invalide ou champs manquants",
        "retries": state.get("retries", 0) + 1
    }


def route_apres_validation(state: AgentState) -> str:
    """Route conditionnelle après validation"""
    if state.get("erreur") is None:
        return "fin"
    if state.get("retries", 0) < MAX_RETRIES:
        return "reessayer"
    return "echec"


# ====================================================================
# Construction du graphe
# ====================================================================

graphe = StateGraph(AgentState)

graphe.add_node("recuperer_alerte", noeud_recuperer_alerte)
graphe.add_node("contexte_mitre", noeud_contexte_mitre)
graphe.add_node("calculer_priorite", noeud_calculer_priorite)
graphe.add_node("generer_llm", noeud_generer_llm)
graphe.add_node("valider", noeud_valider)

graphe.set_entry_point("recuperer_alerte")
graphe.add_edge("recuperer_alerte", "contexte_mitre")
graphe.add_edge("contexte_mitre", "calculer_priorite")
graphe.add_edge("calculer_priorite", "generer_llm")
graphe.add_edge("generer_llm", "valider")

graphe.add_conditional_edges(
    "valider",
    route_apres_validation,
    {
        "fin": END,
        "reessayer": "generer_llm",
        "echec": END
    }
)

app = graphe.compile()


# ====================================================================
# Exécution autonome
# ====================================================================

if __name__ == "__main__":
    resultat = app.invoke({})
    
    print(f"Méthode contexte MITRE : {resultat['mitre_methode']}")
    print(f"Priorité : {resultat['priorite']} (sévérité {resultat['severite']}/10)")
    print(f"Tentatives de génération : {resultat.get('retries', 0) + 1}")
    
    if resultat.get("erreur"):
        print(f"ECHEC : {resultat['erreur']}")
    else:
        print("\n=== Analyse IA ===")
        print(json.dumps(resultat["llm_sortie"], indent=2, ensure_ascii=False))
