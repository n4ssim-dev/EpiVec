# EpiVec

Plateforme desktop d'analyse épidémiologique par GraphRAG, interrogeable en langage naturel.

Projet d'initiation aux fondamentaux du RAG et du GraphRAG en contexte réel — pas de LLM, pas de framework d'orchestration, la pipeline est écrite à la main.

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

## Ingestion des données

```bash
# Une fois le backend démarré
curl -X POST http://localhost:8000/ingest
```

L'ingestion télécharge les sources (SPF, ECDC, data.gouv.fr), génère les chunks,
calcule les embeddings et construit les triples du graphe.

## Structure

```
EpiVec/
├── backend/
│   └── app/
│       ├── api/          # Endpoints FastAPI (query, graph, stats, ingest)
│       ├── core/         # Config, connexion base de données
│       ├── graph/        # NetworkX — construction, traversal, métriques
│       ├── ingestion/    # Fetcher, chunker, embedder, triple parser
│       ├── models/       # Modèles SQLAlchemy (Triple, Region, Indicator)
│       ├── nlp/          # spaCy — NER, extraction d'entités
│       └── rag/          # Retriever ChromaDB, graph retriever, answer builder
├── electron/             # App desktop Electron + React + Sigma.js
├── docker-compose.yml
├── docker-compose.dev.yml
└── .env.example
```

## Pipeline RAG/GraphRAG

```
Question
  │
  ├── spaCy NER          → entités (maladie, région, date)
  ├── sentence-transformers → embedding de la question
  │
  ├── ChromaDB           → top-k chunks textuels proches (retrieval vectoriel)
  └── NetworkX traversal → sous-graphe depuis les entités détectées
                    │
                    └── answer_builder → réponse structurée par template
```

## Stack

| Couche | Techno |
|---|---|
| Frontend | Electron + React + Sigma.js |
| Backend | FastAPI + Python |
| BDD | PostgreSQL (triples) |
| Vecteurs | ChromaDB |
| Embeddings | sentence-transformers (local) |
| Graphe | NetworkX |
| NLP | spaCy (fr_core_news_lg) |
