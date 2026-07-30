"""
dashboard.py - Interface Streamlit pour consultation et triage IA des alertes

Fonctionnalités :
  - Liste des alertes récentes avec indicateurs de sévérité
  - Bouton "Analyser" par alerte déclenchant le pipeline IA
  - Affichage du résultat avec urgence, résumé, contexte MITRE, recommandation
"""

import streamlit as st
import requests
import urllib3
import json
from agent_graph import app as langgraph_app

urllib3.disable_warnings()

INDEXER_HOST = "https://192.168.10.135:9200"
INDEXER_USER = "admin"
INDEXER_PASSWORD = "admin"

# ====================================================================
# Configuration Streamlit
# ====================================================================

st.set_page_config(
    page_title="SOC Dashboard - MANAGEM",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ SOC Dashboard — Agent IA de Triage")
st.caption("Wazuh + LangGraph + RAG MITRE ATT&CK + Ollama")


# ====================================================================
# Fonctions utilitaires
# ====================================================================

@st.cache_data(ttl=15)
def recuperer_alertes(taille=20):
    """Récupère les N dernières alertes de Wazuh"""
    response = requests.get(
        f"{INDEXER_HOST}/wazuh-alerts-*/_search",
        auth=(INDEXER_USER, INDEXER_PASSWORD),
        verify=False,
        json={"size": taille, "sort": [{"timestamp": {"order": "desc"}}]}
    )
    
    data = response.json()
    alertes = []
    
    for hit in data.get("hits", {}).get("hits", []):
        source = hit["_source"]
        rule = source.get("rule", {})
        mitre_id = rule.get("mitre", {}).get("id")
        
        alertes.append({
            "id": hit["_id"],
            "timestamp": source.get("timestamp", ""),
            "agent": source.get("agent", {}).get("name", "inconnu"),
            "description": rule.get("description", ""),
            "severite": rule.get("level", 0),
            "mitre_id": mitre_id[0] if isinstance(mitre_id, list) else mitre_id,
        })
    
    return alertes


def couleur_severite(niveau):
    """Retourne un emoji coloré selon la sévérité"""
    if niveau >= 8:
        return "🔴"  # Rouge - critique
    elif niveau >= 4:
        return "🟠"  # Orange - moyen
    else:
        return "🟢"  # Vert - faible


def couleur_urgence(urgence):
    """Retourne un emoji coloré selon l'urgence"""
    u = (urgence or "").lower()
    if "élev" in u or "elev" in u or "critique" in u:
        return "🔴"
    elif "moy" in u:
        return "🟠"
    return "🟢"


def analyser_alerte(alerte):
    """
    Exécute le pipeline LangGraph SANS récupérer une nouvelle alerte
    (utilise l'alerte sélectionnée par l'utilisateur)
    """
    etat_initial = {
        "regle_description": alerte["description"],
        "severite": alerte["severite"],
        "agent_nom": alerte["agent"],
        "rule_mitre_id": alerte["mitre_id"],
        "retries": 0
    }
    
    # Importer les nœuds du graphe
    from agent_graph import (
        noeud_contexte_mitre,
        noeud_calculer_priorite,
        noeud_generer_llm,
        noeud_valider,
        route_apres_validation,
        MAX_RETRIES
    )
    
    # Exécuter le pipeline SANS le nœud recuperer_alerte
    state = noeud_contexte_mitre(etat_initial)
    state = noeud_calculer_priorite(state)
    
    # Boucle retry
    for _ in range(MAX_RETRIES + 1):
        state = noeud_generer_llm(state)
        state = noeud_valider(state)
        if state.get("erreur") is None:
            break
    
    return state


# ====================================================================
# Sidebar
# ====================================================================

with st.sidebar:
    st.markdown("### ⚙️ Contrôles")
    if st.button("🔄 Rafraîchir les alertes", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache vidé ✓")
    
    st.divider()
    st.markdown("### 📊 Statistiques")
    alertes = recuperer_alertes()
    
    crit = len([a for a in alertes if a["severite"] >= 8])
    moy = len([a for a in alertes if 4 <= a["severite"] < 8])
    faible = len([a for a in alertes if a["severite"] < 4])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 Critique", crit)
    with col2:
        st.metric("🟠 Moyen", moy)
    with col3:
        st.metric("🟢 Faible", faible)


# ====================================================================
# Affichage principal
# ====================================================================

alertes = recuperer_alertes()
st.subheader(f"Alertes Récentes ({len(alertes)})")

if "analyses" not in st.session_state:
    st.session_state.analyses = {}

# Boucle sur chaque alerte
for alerte in alertes:
    icone = couleur_severite(alerte["severite"])
    mitre_txt = f" — `{alerte['mitre_id']}`" if alerte["mitre_id"] else ""
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([5, 1, 1.2])
        
        # Colonne 1 : Description
        with col1:
            st.markdown(f"**{icone} {alerte['description']}**{mitre_txt}")
            st.caption(f"Agent : `{alerte['agent']}` | {alerte['timestamp']}")
        
        # Colonne 2 : Sévérité
        with col2:
            st.metric("Sévérité", f"{alerte['severite']}/10")
        
        # Colonne 3 : Bouton Analyser
        with col3:
            if st.button("🤖 Analyser", key=f"btn_{alerte['id']}", use_container_width=True):
                with st.spinner("Analyse par l'agent IA en cours..."):
                    resultat = analyser_alerte(alerte)
                    st.session_state.analyses[alerte["id"]] = resultat
        
        # Affichage du résultat si analysé
        if alerte["id"] in st.session_state.analyses:
            resultat = st.session_state.analyses[alerte["id"]]
            sortie = resultat.get("llm_sortie")
            
            if resultat.get("erreur") and not sortie:
                st.error(f"❌ Échec de l'analyse : {resultat['erreur']}")
            
            elif sortie:
                urgence_icone = couleur_urgence(sortie.get("urgence"))
                
                st.divider()
                
                # Ligne de synthèse
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.markdown(f"**{urgence_icone} Urgence :** {sortie.get('urgence', 'N/A')}")
                with col_b:
                    st.markdown(f"**Priorité :** `{resultat['priorite']}`")
                with col_c:
                    st.markdown(f"**MITRE :** `{resultat['mitre_methode']}`")
                
                # Résumé
                st.write(f"**📋 Résumé :**\n{sortie.get('resume', '')}")
                
                # Contexte MITRE
                st.write(f"**🎯 Contexte MITRE :**\n{sortie.get('contexte_mitre', '')}")
                
                # Recommandation
                st.write(f"**✅ Recommandation :**\n{sortie.get('recommandation', '')}")

# ====================================================================
# Footer
# ====================================================================

st.divider()
st.markdown(
    "---\n"
    "**SOC Lab** | Wazuh + LangGraph + RAG MITRE ATT&CK | "
    "Groupe MANAGEM — Juillet 2026"
)
