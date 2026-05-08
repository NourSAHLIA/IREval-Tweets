
import pyterrier as pt
import pandas as pd
import os

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUERIES_FILE = os.path.join(BASE_DIR, 'phase1', 'queries.txt')
INDEX_DIR    = os.path.join(BASE_DIR, 'phase2', 'indexes')
RESULTS_DIR  = os.path.join(BASE_DIR, 'phase2', 'results')

def load_queries():
    queries = []
    with open(QUERIES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    queries.append({'qid': parts[0], 'query': parts[1]})
    df = pd.DataFrame(queries)
    print(f"  Loaded {len(df)} queries")
    return df

def save_trec_run(results_df, filepath, run_name):
    with open(filepath, 'w') as f:
        for _, row in results_df.iterrows():
            f.write(f"{row['qid']} Q0 {row['docno']} {int(row['rank'])+1} {row['score']:.6f} {run_name}\n")
    print(f"  Saved {os.path.basename(filepath)}")

def run_retrieval():
    if not pt.started():
        pt.init()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    queries_df = load_queries()


    print("\nLoading indexes...")
    index_lex   = pt.IndexFactory.of(os.path.join(INDEX_DIR, 'lexemes'))
    index_stem  = pt.IndexFactory.of(os.path.join(INDEX_DIR, 'stems'))
    index_lemma = pt.IndexFactory.of(os.path.join(INDEX_DIR, 'lemmas'))

    print("\nRunning retrieval models on lexemes index...")
    models = {
        'TF_IDF': pt.BatchRetrieve(index_lex, wmodel='TF_IDF', num_results=30),
        'BM25':   pt.BatchRetrieve(index_lex, wmodel='BM25',   num_results=30),
        'PL2':    pt.BatchRetrieve(index_lex, wmodel='PL2',    num_results=30),
        'DPH':    pt.BatchRetrieve(index_lex, wmodel='DPH',    num_results=30),
    }

    results = {}
    for name, model in models.items():
        res = model.transform(queries_df)
        results[name] = res
        save_trec_run(res, os.path.join(RESULTS_DIR, f'run_{name.lower()}.txt'), name)

    print("\nRunning BM25 on all 3 index types (for indexation comparison)...")
    bm25_stem  = pt.BatchRetrieve(index_stem,  wmodel='BM25', num_results=30)
    bm25_lemma = pt.BatchRetrieve(index_lemma, wmodel='BM25', num_results=30)

    res_stem  = bm25_stem.transform(queries_df)
    res_lemma = bm25_lemma.transform(queries_df)

    save_trec_run(res_stem,  os.path.join(RESULTS_DIR, 'run_bm25_stems.txt'),  'BM25_STEMS')
    save_trec_run(res_lemma, os.path.join(RESULTS_DIR, 'run_bm25_lemmas.txt'), 'BM25_LEMMAS')

    results['BM25_STEMS']  = res_stem
    results['BM25_LEMMAS'] = res_lemma

    print("\n All run files saved to phase2/results/")
    return results, queries_df

if __name__ == '__main__':
    print("=" * 50)
    print("Phase 2 — Step 2: Retrieval")
    print("=" * 50)
    run_retrieval()
