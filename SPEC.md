# EpiVec — Spécification projet

Plateforme desktop d'analyse épidémiologique par GraphRAG,
interrogeable en langage naturel — conçue comme une initiation pratique aux fondamentaux du RAG et du GraphRAG.

---

## Objectif pédagogique

Ce projet n'a pas pour ambition d'être state-of-the-art. Il sert à comprendre, en contexte réel, comment fonctionne la chaîne complète :

1. **Ingestion** — transformer des données brutes en chunks indexables et en triples de graphe
2. **Retrieval vectoriel (RAG)** — retrouver les passages les plus proches d'une question via embeddings
3. **Retrieval par graphe (GraphRAG)** — traverser un graphe de connaissances pour enrichir le contexte récupéré
4. **Réponse sans LLM** — assembler une réponse structurée depuis les faits récupérés, sans génération probabiliste

Chaque couche est intentionnellement écrite à la main (pas de framework d'orchestration) pour rendre visible ce qui se passe.

---

## Concept

Ingérer des données épidémiologiques publiques (SPF, ECDC, OMS, data.gouv.fr),
les modéliser sous deux formes complémentaires :

- **Chunks textuels vectorisés** — pour le retrieval sémantique
- **Graphe de connaissances** (triples sujet–prédicat–objet) — pour le raisonnement structuré

Et exposer une interface Electron permettant :
- d'interroger les données en français via la pipeline RAG/GraphRAG
- de visualiser la propagation géographique et temporelle
- d'afficher des métriques de graphe (centralité, clustering, propagation)

---

## Fondamentaux RAG et GraphRAG

### RAG (Retrieval-Augmented Generation — ici sans génération)

```
Question utilisateur
        │
        ▼
  Embedding de la question        ← sentence-transformers (local, pas d'API)
        │
        ▼
  Recherche cosinus dans ChromaDB ← top-k chunks les plus proches
        │
        ▼
  Assemblage de la réponse        ← template structuré depuis les chunks récupérés
```

Le retrieval vectoriel repose sur la similarité cosinus entre l'embedding de la question
et les embeddings pré-calculés des chunks lors de l'ingestion.

### GraphRAG (enrichissement par le graphe)

```
Entités extraites de la question  ← spaCy NER (maladie, région, date)
        │
        ▼
  Nœuds correspondants dans NetworkX
        │
        ▼
  Traversal du graphe (voisins, chemins) ← sous-graphe contextuel
        │
        ▼
  Fusion avec les chunks RAG       ← contexte étendu par les relations structurées
        │
        ▼
  Réponse enrichie
```

Le graphe apporte ce que le retrieval vectoriel ne peut pas donner seul :
les **relations explicites** entre entités (région A → cas → maladie B à date T).

### Pipeline complète

```
[Ingestion]
  données brutes → chunking → embeddings → ChromaDB
                → parsing   → triples    → PostgreSQL + NetworkX (chargé en mémoire)

[Query]
  question → NER spaCy → embedding
           ├── ChromaDB top-k chunks
           └── NetworkX traversal depuis entités détectées
                        └── fusion → réponse structurée (template)
```

---

## Stack technique

| Couche | Technologie | Rôle |
|---|---|---|
| Frontend | Electron + React | UI desktop, graphe interactif (Sigma.js), interface de requête |
| Backend | FastAPI (Python) | API REST, pipeline RAG/GraphRAG |
| Base de données | PostgreSQL | Données ingérées + table de triples (sujet, prédicat, objet) |
| Vectorisation | ChromaDB | Embeddings des chunks + retrieval cosinus |
| Embeddings | sentence-transformers | Calcul local des vecteurs (pas d'API externe) |
| Graphe | NetworkX | Graphe en mémoire, traversal, métriques de centralité |
| NLP | spaCy | NER — extraction d'entités (maladie, région, date, indicateur) |
| Conteneurisation | Docker Compose | Backend + PostgreSQL + ChromaDB |

**Ce qui est volontairement absent :**
- Pas de LLM (Claude API, Ollama, OpenAI) — la réponse est assemblée par template, pas générée
- Pas de LangChain / LlamaIndex — la pipeline RAG est écrite à la main pour être lisible
- Pas de fine-tuning ni de modèle custom

Electron n'est PAS conteneurisé — il tourne en natif et consomme l'API sur localhost:8000.

---

## Architecture des composants

```
┌─────────────────────────────────────────────────────────┐
│                    Electron + React                      │
│  ┌──────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │  Chat / Query│  │  Graphe Sigma.js│  │  Dashboard │ │
│  └──────┬───────┘  └────────┬────────┘  └─────┬──────┘ │
└─────────┼────────────────────┼─────────────────┼────────┘
          │         HTTP / localhost:8000         │
┌─────────▼───────────────────────────────────────▼──────┐
│                     FastAPI Backend                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Pipeline RAG/GraphRAG               │   │
│  │  spaCy NER → embedding → ChromaDB retrieval      │   │
│  │            → NetworkX traversal                  │   │
│  │            → template answer builder             │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  PostgreSQL │  │   ChromaDB   │  │   NetworkX   │   │
│  │  (triples)  │  │  (vecteurs)  │  │  (en mémoire)│   │
│  └─────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Structure des données

### Triples (PostgreSQL)

```sql
CREATE TABLE triples (
    id         SERIAL PRIMARY KEY,
    subject    TEXT NOT NULL,   -- ex: "COVID-19"
    predicate  TEXT NOT NULL,   -- ex: "cas_confirmés_dans"
    object     TEXT NOT NULL,   -- ex: "Île-de-France"
    value      FLOAT,           -- ex: 12450.0
    date       DATE,
    source     TEXT
);
```

### Chunks (ChromaDB)

Chaque chunk = passage textuel de ~200 tokens issu des rapports sources,
associé à ses métadonnées (maladie, région, date, source) et son vecteur embedding.

---

## Modules backend (FastAPI)

```
backend/
├── ingestion/
│   ├── fetcher.py        # téléchargement des données sources
│   ├── chunker.py        # découpage en chunks textuels
│   ├── embedder.py       # calcul des embeddings (sentence-transformers)
│   ├── triple_parser.py  # extraction de triples depuis les données structurées
│   └── graph_builder.py  # construction du graphe NetworkX depuis les triples
│
├── rag/
│   ├── retriever.py      # recherche vectorielle ChromaDB (top-k)
│   ├── graph_retriever.py# traversal NetworkX depuis entités détectées
│   ├── ner.py            # extraction d'entités via spaCy
│   └── answer_builder.py # assemblage de la réponse par template
│
├── api/
│   ├── query.py          # POST /query — pipeline RAG complète
│   ├── graph.py          # GET /graph — export du sous-graphe pour Sigma.js
│   └── stats.py          # GET /stats — métriques épidémiologiques agrégées
│
└── main.py
```

---

## Données sources

| Source | Format | Contenu |
|---|---|---|
| Santé Publique France | CSV / JSON | Cas, hospitalisations, décès par département |
| ECDC | CSV | Données européennes par pays et semaine |
| data.gouv.fr | CSV | Indicateurs régionaux (vaccination, SI-DEP) |

L'ingestion est déclenchée manuellement via un endpoint `POST /ingest`
(pas de scheduler — hors périmètre pédagogique).
