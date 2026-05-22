# EpiGraph

Plateforme desktop d'analyse et de prédiction épidémiologique par GraphRAG, interrogeable en langage naturel.

## Prérequis

- Docker & Docker Compose
- Node.js ≥ 20
- Python ≥ 3.11 (dev local)

## Démarrage rapide

```bash
# 1. Copier et remplir les variables d'environnement
cp .env.example .env

# 2. Lancer les services backend (PostgreSQL + ChromaDB + API)
docker compose up -d

# 3. Lancer en mode développement (hot-reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# 4. Lancer l'app Electron (dans un second terminal)
cd electron
npm install
npm run dev
```

## Structure

```
EpiVec/
├── backend/          # FastAPI — API REST, NLP, GraphRAG, prédiction
├── electron/         # App desktop Electron + React
├── docker-compose.yml
└── .env.example
```

## Ingestion des données

```bash
# Via API (une fois le backend démarré)
curl -X POST http://localhost:8000/ingest/spf
curl -X POST http://localhost:8000/ingest/all
```

## LLM

Par défaut l'app utilise Claude (Anthropic). Pour utiliser Ollama en local :

```bash
# Démarrer avec Ollama
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile ollama up

# Puis dans .env :
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3
```

## Stack

| Couche | Techno |
|---|---|
| Frontend | Electron + React + Sigma.js |
| Backend | FastAPI + Python |
| BDD | PostgreSQL |
| Vecteurs | ChromaDB |
| Graphe | NetworkX |
| NLP | spaCy (fr_core_news_lg) |
| RAG | LangChain |
| LLM | Claude API / Ollama |
| Prédiction | SIR/SEIR + scikit-learn |
