"""
evaluate.py — Computes MAP, P@1, P@5, P@10, Recall and Recall-Precision curves.
All metrics are computed manually — no ir_measures version dependency.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os

matplotlib.rcParams['figure.figsize'] = (12, 5)

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QRELS_FILE  = os.path.join(BASE_DIR, 'phase1', 'qrels.txt')
RESULTS_DIR = os.path.join(BASE_DIR, 'phase2', 'results')
CHARTS_DIR  = os.path.join(BASE_DIR, 'phase2', 'charts')

MODELS = ['TF_IDF', 'BM25', 'PL2', 'DPH']
COLORS = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']



def load_qrels():
    rows = []
    with open(QRELS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 4:
                rows.append({
                    'query_id' : parts[0],
                    'doc_id'   : str(parts[2]),
                    'relevance': int(parts[3])
                })
    df = pd.DataFrame(rows)
    print(f"  Loaded {len(df)} qrels ({(df['relevance']==1).sum()} relevant)")
    return df


def load_run(filename):
    rows = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                rows.append({
                    'query_id': parts[0],
                    'doc_id'  : str(parts[2]),
                    'rank'    : int(parts[3]),
                    'score'   : float(parts[4])
                })
    return pd.DataFrame(rows)



def precision_at_k(retrieved_docs, relevant_set, k):
    top_k = retrieved_docs[:k]
    return sum(1 for d in top_k if d in relevant_set) / k if k > 0 else 0.0


def average_precision(retrieved_docs, relevant_set):
    if not relevant_set:
        return 0.0
    hits, sum_prec = 0, 0.0
    for rank, doc in enumerate(retrieved_docs, 1):
        if doc in relevant_set:
            hits += 1
            sum_prec += hits / rank
    return sum_prec / len(relevant_set)


def recall_at_k(retrieved_docs, relevant_set, k):
    if not relevant_set:
        return 0.0
    top_k = retrieved_docs[:k]
    return sum(1 for d in top_k if d in relevant_set) / len(relevant_set)


def compute_metrics(run_df, qrels_df):
    map_vals, p1_vals, p5_vals, p10_vals, rec_vals = [], [], [], [], []
    for qid in qrels_df['query_id'].unique():
        q_run   = run_df[run_df['query_id'] == qid].sort_values('rank')
        q_qrels = qrels_df[(qrels_df['query_id'] == qid) & (qrels_df['relevance'] == 1)]
        rel_set = set(q_qrels['doc_id'].astype(str).tolist())
        docs    = q_run['doc_id'].astype(str).tolist()
        map_vals.append(average_precision(docs, rel_set))
        p1_vals.append(precision_at_k(docs, rel_set, 1))
        p5_vals.append(precision_at_k(docs, rel_set, 5))
        p10_vals.append(precision_at_k(docs, rel_set, 10))
        rec_vals.append(recall_at_k(docs, rel_set, 30))
    n = len(map_vals) if map_vals else 1
    return {
        'MAP'    : round(sum(map_vals) / n, 4),
        'P@1'    : round(sum(p1_vals)  / n, 4),
        'P@5'    : round(sum(p5_vals)  / n, 4),
        'P@10'   : round(sum(p10_vals) / n, 4),
        'Recall' : round(sum(rec_vals) / n, 4),
    }


def compute_rp_curve(run_df, qrels_df, num_results=30):
    recall_levels = [i / 10 for i in range(11)]
    all_interp    = []
    for qid in qrels_df['query_id'].unique():
        q_res   = run_df[run_df['query_id'] == qid].sort_values('rank').head(num_results)
        q_qrels = qrels_df[(qrels_df['query_id'] == qid) & (qrels_df['relevance'] == 1)]
        rel_set = set(q_qrels['doc_id'].astype(str).tolist())
        if not rel_set:
            continue
        total = len(rel_set)
        prec, rec, hits = [], [], 0
        for rank, (_, row) in enumerate(q_res.iterrows(), 1):
            if str(row['doc_id']) in rel_set:
                hits += 1
            prec.append(hits / rank)
            rec.append(hits / total)
        interp = [max((p for r, p in zip(rec, prec) if r >= rl), default=0.0)
                  for rl in recall_levels]
        all_interp.append(interp)
    if not all_interp:
        return recall_levels, [0.0] * 11
    avg = [sum(col) / len(col) for col in zip(*all_interp)]
    return recall_levels, avg



def evaluate_all():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    qrels_df = load_qrels()

    print("\nEvaluating models...")
    summary_rows = []
    for name in MODELS:
        run_file = os.path.join(RESULTS_DIR, f'run_{name.lower()}.txt')
        if not os.path.exists(run_file):
            print(f"  Warning: {run_file} not found — skipping")
            continue
        res    = load_run(run_file)
        scores = compute_metrics(res, qrels_df)
        summary_rows.append({'Model': name, **scores})
        print(f"  {name:8s} | MAP={scores['MAP']:.4f} | P@1={scores['P@1']:.4f} "
              f"| P@5={scores['P@5']:.4f} | P@10={scores['P@10']:.4f} | Recall={scores['Recall']:.4f}")

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(RESULTS_DIR, 'evaluation_summary.csv'), index=False)
    best = summary_df.loc[summary_df['MAP'].idxmax()]
    print(f"\n  Best model: {best['Model']} (MAP={best['MAP']})")

    print("\nGenerating charts...")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, metric, title in zip(axes, ['MAP', 'P@10'],
            ['MAP - Mean Average Precision', 'P@10 - Precision at Rank 10']):
        vals = summary_df[metric].tolist()
        bars = ax.bar(summary_df['Model'].tolist(), vals, color=COLORS[:len(vals)])
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel(metric)
        ax.set_ylim(0, max(max(vals) * 1.4, 0.1))
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.003,
                    f'{v:.4f}', ha='center', fontsize=10)
    plt.suptitle('Retrieval Model Comparison - Iran War Tweet Collection',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'model_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved model_comparison.png")

    fig, ax = plt.subplots(figsize=(12, 5))
    x, width = range(len(summary_df)), 0.18
    for i, (metric, color) in enumerate(zip(['MAP', 'P@1', 'P@5', 'P@10'], COLORS)):
        vals = summary_df[metric].tolist()
        ax.bar([xi + (i - 1.5) * width for xi in x], vals, width, label=metric, color=color)
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary_df['Model'].tolist())
    ax.set_title('All Metrics per Model', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score')
    ax.legend()
    max_val = summary_df[['MAP', 'P@1', 'P@5', 'P@10']].max().max()
    ax.set_ylim(0, max(max_val * 1.4, 0.1))
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'all_metrics.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved all_metrics.png")

    idx_rows = []
    for label, fname in [('Lexemes', 'run_bm25.txt'),
                          ('Stems',   'run_bm25_stems.txt'),
                          ('Lemmas',  'run_bm25_lemmas.txt')]:
        fpath = os.path.join(RESULTS_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  Warning: {fname} not found — skipping")
            continue
        res    = load_run(fpath)
        scores = compute_metrics(res, qrels_df)
        idx_rows.append({'Index': label, **scores})

    if idx_rows:
        idx_df = pd.DataFrame(idx_rows)
        idx_df.to_csv(os.path.join(RESULTS_DIR, 'indexation_comparison.csv'), index=False)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(idx_df['Index'], idx_df['MAP'], color=['#4C72B0', '#55A868', '#DD8452'])
        ax.set_title('BM25 - Indexation Strategy Comparison (MAP)',
                     fontsize=12, fontweight='bold')
        ax.set_ylabel('MAP')
        ax.set_ylim(0, max(idx_df['MAP'].max() * 1.4, 0.1))
        for i, v in enumerate(idx_df['MAP']):
            ax.text(i, v + 0.003, f'{v:.4f}', ha='center', fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, 'indexation_comparison.png'),
                    dpi=150, bbox_inches='tight')
        plt.close()
        print("  Saved indexation_comparison.png")

    
    print("\nGenerating Recall-Precision curves...")
    linestyles = ['-o', '-s', '-^', '-D']
    fig, ax    = plt.subplots(figsize=(10, 6))
    for name, color, ls in zip(MODELS, COLORS, linestyles):
        run_file = os.path.join(RESULTS_DIR, f'run_{name.lower()}.txt')
        if not os.path.exists(run_file):
            continue
        res       = load_run(run_file)
        rec, prec = compute_rp_curve(res, qrels_df)
        ax.plot(rec, prec, ls, color=color, label=name, linewidth=2, markersize=6)
    ax.set_xlabel('Rappel (Recall)', fontsize=12)
    ax.set_ylabel('Precision', fontsize=12)
    ax.set_title('Courbes Rappel-Precision - Iran War Tweet Collection',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'recall_precision_curves.png'),
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved recall_precision_curves.png")

    print("\n Evaluation complete!")
    print("   Charts  -> phase2/charts/")
    print("   Results -> phase2/results/")


if __name__ == '__main__':
    print("=" * 50)
    print("Phase 2 - Step 3: Evaluation")
    print("=" * 50)
    evaluate_all()