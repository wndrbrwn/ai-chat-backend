import chromadb
from embed_demo import embed
from chunk_demo import chunk_text

text = open("sample.txt", encoding = "utf-8").read()
chunks = chunk_text(text, 200, 40)

db = chromadb.Client()
collection = db. create_collection(name="docs")
collection.add(
    ids = [f"chunk-{i}" for i in range(len(chunks))],
    documents = chunks,
    embeddings = embed(chunks),
)

question = "이 프로젝트의 주제는 무엇인가요"
result = collection.query(query_embeddings = embed([question]), n_results = 3)
for doc in result["documents"][0]:
    print(doc)
    print("---")