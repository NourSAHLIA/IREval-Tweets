# SRI Project — 2ème ING IMD (2025-2026)

Information Retrieval System project using PyTerrier on a self-built tweet collection.  
**Topic: Iran War & Geopolitical Impact**

## Team

- Sahlia Nour
- Chaabani Adem
- Mannai Eya
- Mohamed Ismail

---

## Our 5 Queries

| ID  | Search Text                     | Topic                                  |
| --- | ------------------------------- | -------------------------------------- |
| Q1  | `Iran oil prices sanctions`     | Effect of Iran sanctions on oil prices |
| Q2  | `Iran Israel war attack`        | Iran-Israel military conflict          |
| Q3  | `Iran nuclear deal JCPOA`       | Iran nuclear program and negotiations  |
| Q4  | `Iran drone missile strike`     | Iran drone and missile warfare         |
| Q5  | `Iran economy inflation crisis` | Iran economic collapse and inflation   |

---

## Phase 1 — Building the test collection

**Deadline: 18 April 2026**

### What it produces

| File                  | Description                                         |
| --------------------- | --------------------------------------------------- |
| `phase1/tweets.jsonl` | 500 tweets (100 per query)                          |
| `phase1/queries.txt`  | 5 queries in TREC format                            |
| `phase1/qrels.txt`    | Relevance judgments (first 30 per query = relevant) |

---

## Setup — Step by Step

### Step 1 — Clone the repo

```bash
git clone <your-repo-url>
cd IREval-Tweets
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 4 — Get your X (Twitter) session cookies

> **Important:** One team member must have an X/Twitter account (free signup at x.com).  
> You do NOT need to post anything — just log in to copy the cookies.

1. Open [x.com](https://x.com/) in your browser and log in.
2. Press **F12** to open Developer Tools.
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
4. On the left, expand **Cookies** → click `https://x.com`.
5. Find and copy the values of `auth_token` and `ct0`.
6. Create your `.env` file:
   ```bash
   cp .env.example .env
   ```
7. Open `.env` and paste the values:
   ```env
   X_AUTH_TOKEN=paste_your_auth_token_here
   X_CT0=paste_your_ct0_here
   ```

> ⚠️ Never push your `.env` file to GitHub — it's already in `.gitignore`.

### Step 5 — Run Phase 1

```bash
python -m scripts.main
```

The script will open a visible browser window, search each query, and collect 100 tweets per query automatically.

---

## Project Structure

```
IREval-Tweets/
├── .env                  ← YOUR credentials (never pushed)
├── .env.example          ← Template for teammates
├── .gitignore
├── requirements.txt
├── config/
│   ├── queries.yaml      ← The 5 queries
│   └── settings.yaml     ← Collection settings
├── phase1/               ← OUTPUT folder (deliverables)
│   ├── tweets.jsonl
│   ├── queries.txt
│   └── qrels.txt
└── scripts/
    ├── __init__.py
    ├── main.py           ← Entry point
    ├── fetch_tweets.py   ← Playwright scraper
    ├── build_qrels.py    ← Relevance judgment builder
    ├── save_corpus.py    ← File writer
    └── utils.py          ← Shared helpers
```
