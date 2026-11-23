import json
from rag import collection
from embed_demo import embed

DOC_PATH = "openrouter_terms.txt"
KS = [1, 3, 5, 8]

def normalize(text):
    return " ".join(text.split())

def search(question, n_results):
    results = collection.query(query_embeddings = embed([question]), n_results = n_results)
    return results["documents"][0]

def main():
    with open("eval/golden_set.json", encoding = "utf-8") as f:
        items = json.load(f)

    with open(DOC_PATH, encoding = "utf-8") as f:
        doc = normalize(f.read())

    for item in items:
        if normalize(item["evidence"]) not in doc:
            print("원문에 없음:", item["evidence"])

    hits = {k: 0 for k in KS}
    missed = []
    for item in items:
        chunks = search(item["question"], max(KS))
        evidence = normalize(item["evidence"])
        for k in KS:
            if any(evidence in normalize(c) for c in chunks[:k]):
                hits[k] += 1
        
        if not any(evidence in normalize(c) for c in chunks):
            missed.append(item["question"])
                
    for k in KS:
        print(f"hit rate@{k}: {hits[k]} / {len(items)} = {hits[k] / len(items):.0%}")
    print("k = 8에서도 실패:",missed)

    all_chunks = collection.get()["documents"]

    for item in items:
        evidence = normalize(item["evidence"])
        in_top8 = any(evidence in normalize(c) for c in search(item["question"], 8))
        if in_top8:
            continue
        exists = any(evidence in normalize(c) for c in all_chunks)
        print(("순위 문제" if exists else "분할 문제"), "|", item["question"])
if __name__ == "__main__":
    main()