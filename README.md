# SRI Project — 2ème ING IMD (2025-2026)

Information Retrieval System project using PyTerrier on a self-built tweet collection.
**Topic: Iran War & Geopolitical Impact**

## Team

- Sahlia Nour
- Chaabani Adem
- Mannai Ey
- Mohamed Ismail

---

## Our 5 Queries

| ID | Search Text | Topic |
|----|-------------|-------|
| Q1 | `Iran oil prices sanctions` | Effect of Iran sanctions on oil prices |
| Q2 | `Iran Israel war attack` | Iran-Israel military conflict |
| Q3 | `Iran nuclear deal JCPOA` | Iran nuclear program and negotiations |
| Q4 | `Iran drone missile strike` | Iran drone and missile warfare |
| Q5 | `Iran economy inflation crisis` | Iran economic collapse and inflation |

---

## Phase 1 — Building the test collection ✅

**Status: Complete**

| File | Description |
|------|-------------|
| `phase1/tweets.jsonl` | 500 tweets (100 per query) |
| `phase1/queries.txt` | 5 queries in TREC format |
| `phase1/qrels.txt` | 500 relevance judgments (first 30 per query = relevant) |

---

## Phase 2 — Indexation, Retrieval & Evaluation ✅

**Status: Complete**

### Indexation strategies (Task 2)

| Index | Description |
|-------|-------------|
| Lexemes | Raw words as they appear in text |
| Stems | Porter Stemmer applied |
| Lemmas | WordNet Lemmatizer applied |
| Blocks (size 2) | Block indexing — window of 2 words |
| Blocks (size 4) | Block indexing — window of 4 words |
| Blocks (size 8) | Block indexing — window of 8 words |

### Retrieval models (Task 3)

TF-IDF · BM25 · PL2 · DPH — top 30 tweets returned per query

### Evaluation results (Task 4)

| Model | MAP | P@1 | P@5 | P@10 | Recall |
|-------|-----|-----|-----|------|--------|
| **DPH** | **0.2441** | **0.6** | 0.48 | 0.46 | 0.4267 |
| TF-IDF | 0.2349 | 0.4 | 0.48 | 0.48 | 0.4133 |
| PL2 | 0.2248 | 0.4 | 0.52 | 0.46 | 0.3933 |
| BM25 | 0.1465 | 0.2 | 0.28 | 0.28 | 0.3267 |

**Best model: DPH (MAP = 0.2441)**

---

## Setup

> ⚠️ **Requires Python 3.11** and **Java 11+** (for PyTerrier)

### Phase 1 — Tweet collection

```bash
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
# Fill in X_AUTH_TOKEN and X_CT0
python -m scripts.main
```

### Phase 2 — IR System

```bash
cd phase2
python run_all.py
```

Outputs saved to `phase2/results/` and `phase2/charts/`.

---

## Project Structure

```
IREval-Tweets/
├── .env                     credentials 
├── .env.example
├── .gitignore
├── requirements.txt
├── config/
│   ├── queries.yaml
│   └── settings.yaml
├── phase1/                  Phase 1 output 
│   ├── tweets.jsonl
│   ├── queries.txt
│   └── qrels.txt
├── phase2/
│   ├── run_all.py           entry point
│   ├── index_tweets.py      6 indexes
│   ├── retrieve.py          4 retrieval models
│   ├── evaluate.py          metrics + charts
│   ├── indexes/             generated 
│   ├── results/             generated
│   └── charts/              generated 
└── scripts/
    ├── main.py
    ├── fetch_tweets.py
    ├── build_qrels.py
    ├── save_corpus.py
    └── utils.py
```