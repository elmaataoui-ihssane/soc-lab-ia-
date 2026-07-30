"""
scripts/extraire_mitre.py - Extraction du corpus MITRE ATT&CK depuis le repo officiel

Récupère l'ensemble des techniques et sous-techniques depuis mitre/cti (GitHub)
et génère un JSON contenant : id, nom, description
"""

import requests
import json

URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

print("Téléchargement du bundle MITRE ATT&CK...")
resp = requests.get(URL)
bundle = resp.json()

techniques = []

for obj in bundle["objects"]:
    # Filtrer les techniques (attack-pattern) et exclure les révoquées
    if obj.get("type") == "attack-pattern" and not obj.get("revoked", False):
        attack_id = None
        
        # Extraire l'ID MITRE depuis les références externes
        for ref in obj.get("external_references", []):
            if ref.get("source_name") == "mitre-attack":
                attack_id = ref.get("external_id")
                break
        
        if not attack_id:
            continue
        
        # Ajouter à la liste
        techniques.append({
            "id": attack_id,
            "nom": obj.get("name", ""),
            "description": obj.get("description", "").split("\n")[0]  # Premier paragraphe
        })

print(f"{len(techniques)} techniques extraites.")

# Sauvegarder en JSON
with open("mitre_techniques.json", "w", encoding="utf-8") as f:
    json.dump(techniques, f, ensure_ascii=False, indent=2)

print("✓ Corpus sauvegardé en 'mitre_techniques.json'")
