"""
scripts/ground_truth.py - Jeu de vérité terrain pour évaluation de la recherche sémantique

Contient des couples (description_règle_Wazuh, identifiant_MITRE_attendu)
vérifiés manuellement contre le rapport d'étape
"""

# Jeu de vérité terrain : couples (description, ID MITRE attendu)
verite_terrain = [
    ("sshd: Attempt to login using a non-existent user", "T1110.001"),
    ("PAM: User login failed", "T1110.001"),
    ("Successful sudo to ROOT executed", "T1548.003"),
    ("PAM: Login session opened", "T1078"),
    ("New user added to the system", "T1136"),
    ("Group (or user) deleted from the system", "T1531"),
    ("Logon Failure - Unknown user or bad password", "T1531"),
    ("Windows Workstation Logon Success", "T1078"),
    ("User account created", "T1098"),
    ("Domain Users Group Changed", "T1484"),
]

if __name__ == "__main__":
    print(f"Jeu de vérité terrain : {len(verite_terrain)} couples")
    for desc, mitre_id in verite_terrain:
        print(f"  '{desc}' → {mitre_id}")
