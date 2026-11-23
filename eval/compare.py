import json
import chromadb
from rag import collection
from chunk_demo import chunk_text
from embed_demo import embed

DOC_PATH = "openrouter_terms.txt"
KS = [1, 3, 5, 8]
CONFIGS = [(200, 40), (400, 80), (600, 120), (1000, 200)]

def normalize(text):
    return " ".join(text.split())

def build_collection(text, size, overlap):
    client = chromadb.EphemeralClient()
    col = client.create_collection(f"eval_{size}_{overlap}", metadata = collection.metadata)
    chunks = chunk_text(text, size, overlap)
    for i in range(0, len(chunks), 100):
        batch = chunks[i : i + 100]
        col.add(
            ids = [f"c{j}" for j in range(i, i + len(batch))],
            documents = batch,
            embeddings = embed(batch)
        )
    return col, len(chunks)

def main():
    with open("eval/golden_set.json", encoding="utf-8") as f:
        items = json.load(f)
    with open(DOC_PATH, encoding="utf-8") as f:
        text = f.read()
    
    q_embs = embed([item["question"] for item in items])

    for size, overlap in CONFIGS:
        col, n = build_collection(text, size, overlap)
        hits = {k: 0 for k in KS}
        for item, q_emb in zip(items, q_embs):
            res = col.query(query_embeddings = [q_emb], n_results = max(KS))["documents"][0]
            evidence = normalize(item["evidence"])
            for k in KS:
                if any(evidence in normalize(c) for c in res[:k]):
                    hits[k] += 1
        rates = " ".join(f"@{k} {hits[k] / len(items):.0%}" for k in KS)
        print(f"{size}/{overlap} (청크 {n}개): {rates}")

if __name__ == "__main__":
    main()