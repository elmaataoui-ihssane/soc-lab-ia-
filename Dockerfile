FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers
COPY requirements.txt .
COPY agent_graph.py .
COPY dashboard.py .
COPY pages ./pages
COPY scripts ./scripts

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port Streamlit
EXPOSE 8501

# Commande de démarrage
CMD ["streamlit", "run", "dashboard.py"]
