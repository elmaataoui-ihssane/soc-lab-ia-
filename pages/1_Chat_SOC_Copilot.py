"""
pages/1_Chat_SOC_Copilot.py - Assistant conversationnel SOC

Fonctionnalités :
  - Questions libres sur techniques MITRE ATT&CK
  - Contexte injecté via RAG (recherche sémantique Chroma)
  - Historique conversation limité (6 derniers échanges)
  - Réponses texte libre (pas de validation JSON)
"""

import streamlit as st
import requests
import chromadb

st.set_page_config(
    page_title="SOC Copilot - Chat",
    layout="wide"
)

st.title("💬 SOC Copilot")
st.caption("Assistant conversationnel — Contexte MITRE ATT&CK + RAG sémantique")

OLLAMA_HOST = "http://localhost:11434"

client = chromadb.PersistentClient(path="./chroma_mitre")
collection = client.get_or_create_collection("mitre_attack")


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


def rechercher_contexte_mitre(question, top_k=2):
    """
    Recherche les fiches MITRE les plus pertinentes pour enrichir la réponse
    """
    embedding = get_embedding(question)
    resultats = collection.query(query_embeddings=[embedding], n_results=top_k)
    return resultats["documents"][0] if resultats["documents"] else []


def generer_reponse(historique, question):
    """
    Génère une réponse via Ollama enrichie du contexte MITRE
    
    Args:
        historique : liste des messages précédents
        question : la question actuelle
    
    Returns:
        str : réponse du modèle
    """
    
    # Récupérer le contexte MITRE pertinent
    contexte_mitre = rechercher_contexte_mitre(question)
    contexte_txt = "\n\n".join(contexte_mitre) if contexte_mitre else "Aucun contexte MITRE pertinent trouvé."
    
    # Construire l'historique compact (6 derniers échanges)
    fil_conversation = "\n".join(
        f"{'Analyste' if m['role'] == 'user' else 'Copilot'}: {m['content']}"
        for m in historique[-6:]
    )
    
    prompt = f"""Tu es SOC Copilot, un assistant qui aide un analyste SOC à comprendre
des alertes de sécurité et des techniques MITRE ATT&CK. Réponds de façon concise
et opérationnelle, comme un collègue analyste expérimenté.

CONTEXTE MITRE ATT&CK PERTINENT (peut être partiellement pertinent, à toi de juger) :
{contexte_txt}

HISTORIQUE DE LA CONVERSATION :
{fil_conversation}

Réponds uniquement à la dernière question de l'analyste, en texte simple (pas de JSON).
Sois concis et pratique.
"""
    
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }
    )
    
    return response.json()["response"]


# ====================================================================
# Interface de chat
# ====================================================================

# Initialiser le session_state pour les messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Champ de saisie
question = st.chat_input(
    "Pose une question sur une alerte, une technique MITRE, une recommandation..."
)

if question:
    # Ajouter le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    
    # Générer la réponse
    with st.chat_message("assistant"):
        with st.spinner("SOC Copilot réfléchit..."):
            reponse = generer_reponse(st.session_state.messages, question)
            st.markdown(reponse)
    
    # Ajouter la réponse à l'historique
    st.session_state.messages.append({"role": "assistant", "content": reponse})
