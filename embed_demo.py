import math
import os
from openai import OpenAI

client = OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key = os.environ["OPENROUTER_API_KEY"],
)

def embed(texts):
    resp = client.embeddings.create(model = "openai/text-embedding-3-small", input=texts)
    return [item.embedding for item in resp.data]

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)

if __name__ == "__main__":
    sentences = [
        "강아지가 공원에서 뛰어논다",
        "개가 야외에서 달리고 있다",
        "주식 시장이 하락했다",
    ]
    vectors = embed(sentences)
    print(len(vectors[0]))                            # 벡터 차원
    print(cosine_similarity(vectors[0], vectors[1]))  # 비슷한 문장
    print(cosine_similarity(vectors[0], vectors[2]))  # 다른 문장