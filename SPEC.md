# EpiGraph — Spécification projet

Plateforme desktop d'analyse et de prédiction épidémiologique par GraphRAG,
interrogeable en langage naturel.

---

## Concept

Ingérer des données épidémiologiques publiques (SPF, ECDC, OMS, data.gouv.fr),
les modéliser comme un graphe de connaissances (triples sujet–prédicat–objet),
et exposer une interface Electron permettant :
- d'interroger le graphe en français via une pipeline NLP/GraphRAG
- de visualiser la propagation géographique et temporelle
- d'obtenir des analyses prédictives (SIR/SEIR + scikit-learn sur features de graphe)

---

## Stack technique

| Couche | Technologie | Rôle |
|---|---|---|
| Frontend | Electron + React | UI desktop, graphe interactif (Sigma.js / D3), chat NLP |
| Backend | FastAPI (Python) | API REST, pipeline NLP, GraphRAG, prédiction |
| Base de données | PostgreSQL | Données ingérées + table de triples (sujet, prédicat, objet) |
| Vectorisation | ChromaDB | Embeddings pour le retrieval RAG |
| LLM | Claude API (Anthropic) ou Ollama local | Synthèse des réponses NLP |
| Graphe | NetworkX | Graphe en mémoire, feature extraction, traversal |
| NLP | spaCy | Extraction d'entités (maladie, région, date, indicateur) |
| Orchestration RAG | LangChain | Graph chains, retrieval hybride vecteur + graphe |
| Prédiction | scikit-learn | Modèles sur features de graphe (centralité, propagation) |
| Conteneurisation | Docker Compose | Backend + PostgreSQL + ChromaDB (+ Ollama optionnel) |

Electron n'est PAS conteneurisé — il tourne en natif et consomme l'API sur localhost:8000.

---

## Architecture

