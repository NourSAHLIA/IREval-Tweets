import pyterrier as pt
import pandas as pd
import json
import os
import shutil
import nltk

nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
from nltk.stem import WordNetLemmatizer

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TWEETS_FILE = os.path.join(BASE_DIR, 'phase1', 'tweets.jsonl')
INDEX_DIR   = os.path.join(BASE_DIR, 'phase2', 'indexes')

def load_corpus():
    tweets = []
    with open(TWEETS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            t = json.loads(line.strip())
            
            tweets.append({
                'docno': str(t.get('doc_id', t.get('id', t.get('tweet_id', len(tweets))))),
                'text':  t.get('text', t.get('full_text', ''))
            })
    df = pd.DataFrame(tweets)
    df = df.drop_duplicates(subset='docno')
    df = df[df['text'].str.strip() != '']
    print(f"  Loaded {len(df)} unique tweets")
    return df

def build_indexes():
    if not pt.started():
        pt.init()

    os.makedirs(INDEX_DIR, exist_ok=True)
    corpus = load_corpus()

   
    print("\nBuilding index 1/3: Lexemes...")
    idx_lex = pt.IterDictIndexer(
        os.path.join(INDEX_DIR, 'lexemes'), overwrite=True, fields=['text']
    )
    idx_lex.index(corpus.to_dict(orient='records'))
    print("  Lexemes index ready")

    print("\nBuilding index 2/3: Stems (Porter)...")
    idx_stem = pt.IterDictIndexer(
        os.path.join(INDEX_DIR, 'stems'), overwrite=True,
        stemmer='PorterStemmer', fields=['text']
    )
    idx_stem.index(corpus.to_dict(orient='records'))
    print("  Stems index ready")

    
    print("\nBuilding index 3/3: Lemmas (WordNet)...")
    lemmatizer   = WordNetLemmatizer()
    corpus_lemma = corpus.copy()
    corpus_lemma['text'] = corpus_lemma['text'].apply(
        lambda t: ' '.join([lemmatizer.lemmatize(w) for w in t.split()])
    )
    idx_lemma = pt.IterDictIndexer(
        os.path.join(INDEX_DIR, 'lemmas'), overwrite=True, fields=['text']
    )
    idx_lemma.index(corpus_lemma.to_dict(orient='records'))
    print(" Lemmas index ready")

   
    for block_size in [2, 4, 8]:
        print(f"\nBuilding block index (size={block_size})...")
        block_path = os.path.join(INDEX_DIR, f'blocks_{block_size}')
        
        if os.path.exists(block_path):
            shutil.rmtree(block_path)
        os.makedirs(block_path, exist_ok=True)
        
        pt.set_property('block.size', str(block_size))
        idx_block = pt.IterDictIndexer(
            block_path,
            overwrite=True,
            fields=['text'],
            blocks=True,
        )
        idx_block.index(corpus.to_dict(orient='records'))
        print(f" Block index (size={block_size}) ready")

    print("\n All indexes built in phase2/indexes/")

if __name__ == '__main__':
    print("=" * 50)
    print("Phase 2 — Step 1: Indexation")
    print("=" * 50)
    build_indexes()