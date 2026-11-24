import os
import chromadb
from openai import OpenAI
from embed_demo import embed
from chunk_demo import chunk_text

MAX_DISTANCE = 1.5
chroma_client = chromadb.PersistentClient(path = "chroma_db")
collection = chroma_client.get_or_create_collection(name = "docs")
llm = OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key = os.environ["OPENROUTER_API_KEY"],
)

def index_document(source, text, collection):
    collection.delete(where = {"source": source})
    chunks = chunk_text(text, 600, 120)
    ids = [f"{source} - {i}" for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk": i} for i in range(len(chunks))]
    collection.upsert(ids = ids, documents = chunks, embeddings = embed(chunks), metadatas = metadatas)
    return len(chunks)

def answer_with_rag(question, collection):
    results = collection.query(query_embeddings = embed([question]), n_results = 5)
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0] 
    distances = results["distances"][0]

    pairs = [(c, m) for c, m, d in zip(chunks, metadatas, distances) if d < MAX_DISTANCE]
    if not pairs:
        return {"answer": "문서에서 찾을 수 없습니다", "sources": []}
    chunks = [c for c, m in pairs]
    metadatas = [m for c, m in pairs]

    context = "\n\n".join(chunks)

    prompt = f"""아래 문서만 근거로 한국어로 답하세요.
    문서에 없는 내용이면 "문서에서 찾을 수 없습니다"라고 답하세요.

    [문서]
    {context}

    [질문]
    {question}"""

    response = llm.chat.completions.create(
        model = "openrouter/free",
        messages =[
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": metadatas
        }
