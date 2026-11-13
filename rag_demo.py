import os
import chromadb
from openai import OpenAI
from embed_demo import embed
from chunk_demo import chunk_text

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)

text = open("sample.txt", encoding = "utf-8").read()
chunks = chunk_text(text, 200, 40)

db = chromadb.Client()
collection = db. create_collection(name="docs")
collection.add(
    ids = [f"chunk-{i}" for i in range(len(chunks))],
    documents = chunks,
    embeddings = embed(chunks),
)

question = "이 프로젝트는 점심메뉴 뭐먹지인가요"
'''result = collection.query(query_embeddings = embed([question]), n_results = 3)
for doc in result["documents"][0]:
    print(doc)
    print("---")
'''
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

    response = client.chat.completions.create(
        model = "openrouter/free",
        messages =[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

answer = answer_with_rag(question,collection)

print("질문:", question)
print("답변:", answer)