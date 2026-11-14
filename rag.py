import os
import chromadb
from openai import OpenAI
from embed_demo import embed
from chunk_demo import chunk_text

chroma_client = chromadb.PersistentClient(path = "chroma_db")
collection = chroma_client.get_or_create_collection(name = "docs")
llm = OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key = os.environ["OPENROUTER_API_KEY"],
)

def index_document(doc_id, chunks):
    ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
    collection.upsert(ids = ids, documents = chunks, embeddings = embed(chunks))

def answer_with_rag(question, collection):
    results = collection.query(query_embeddings = embed([question]), n_results = 3)
    chunks = results["documents"][0]

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

    return response.choices[0].message.content

if __name__ == "__main__":
    text = open("sample.txt", encoding = "utf-8").read()
    chunks = chunk_text(text, 200, 40)
    index_document("sample", chunks)
    print(collection.count())
