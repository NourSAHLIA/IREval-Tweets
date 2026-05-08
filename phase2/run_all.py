"""
Runs the full pipeline in one command:
  Step 1  index_tweets.py (build 3 indexes)
  Step 2  retrieve.py (run 4 retrieval models)
  Step 3  evaluate.py (compute metrics + generate charts)
"""

import time

def main():
    print("=" * 55)
    print("  SRI Project — Phase 2 Pipeline")
    print("  Iran War Tweet Collection")
    print("=" * 55)
    start = time.time()

    # Step1
    print("\n>>> STEP 1: Indexation\n")
    from index_tweets import build_indexes
    build_indexes()

    # Step2
    print("\n>>> STEP 2: Retrieval\n")
    from retrieve import run_retrieval
    run_retrieval()

    # Step3
    print("\n>>> STEP 3: Evaluation\n")
    from evaluate import evaluate_all
    evaluate_all()

    elapsed = round(time.time() - start, 1)
    print("\n" + "=" * 55)
    print(f"Phase 2 complete in {elapsed}s")
    print("=" * 55)
    print("\nFiles to submit (upload to Google Drive):")
    print("  phase2/results/run_tfidf.txt")
    print("  phase2/results/run_bm25.txt")
    print("  phase2/results/run_pl2.txt")
    print("  phase2/results/run_dph.txt")
    print("  phase2/results/evaluation_summary.csv")
    print("  phase2/results/indexation_comparison.csv")
    print("  phase2/charts/model_comparison.png")
    print("  phase2/charts/recall_precision_curves.png")
    print("  phase2/charts/indexation_comparison.png")

if __name__ == '__main__':
    main()
