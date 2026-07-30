"""
scripts/indexer_mitre_chroma.py - Indexation vectorielle du corpus MITRE dans Chroma

Transforme chaque fiche MITRE en embedding via nomic-embed-text (Ollama)
et stocke dans une base Chroma persistante
"""

import json
import requests
import chromadb

OLLAMA_HOST = "http://localhost:11434"
CHROMA_PATH = "./chroma_mitre"

print("Chargement du corpus MITRE...")
with open("mitre_techniques.json", "r", encoding="utf-8") as f:
    techniques = json.load(f)

print(f"Corpus chargé : {len(techniques)} techniques")

# Initialiser Chroma
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    "mitre_attack",
    metadata={"hnsw:space": "cosine"}  # Utiliser la similarité cosinus
)

print("Génération des embeddings et indexation...")

# Boucle sur chaque technique
for i, technique in enumerate(techniques):
    if (i + 1) % 100 == 0:
        print(f"  {i + 1}/{len(techniques)}...")
    
    # Générer l'embedding via Ollama
    text_to_embed = f"{technique['id']} - {technique['nom']}. {technique['description']}"
    
    resp = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text_to_embed}
    )
    embedding = resp.json()["embedding"]
    
    # Ajouter à Chroma
    collection.add(
        ids=[technique["id"]],
        embeddings=[embedding],
        documents=[technique["description"]],
        metadatas={"nom": technique["nom"]}
    )

print(f"✓ {len(techniques)} techniques indexées dans Chroma")
print(f"  Emplacement : {CHROMA_PATH}")
print(f"  Métrique : cosine similarity")
