import json
from rag import collection
from embed_demo import embed

in_doc = ["How are users advised to keep track of revisions to the agreement?", 
          "Which organization is identified as the operator of the platform?",
          "What form of court proceeding do both parties agree to give up?"]

out_doc = ["What is the best food in Korea?",
           "What degree is it right now?",
           "What climate is Poland?",
           "오늘 기분이 어떄?",
           "서울 맛집 알려줘",
           "서울에서 부산가는 버스 시간표 알려줘"]

def top_distance(question):
    results = collection.query(
        query_embeddings = embed([question]),
        n_results = 1,
        include = ["distances"],
    )
    return results["distances"][0][0]

for label, questions in [("있음", in_doc), ("없음", out_doc)]:
    for q in questions:
        print(label, round(top_distance(q), 3), q)

golden = json.load(open("eval/golden_set.json", encoding = "utf-8"))
in_values = [top_distance(item["question"]) for item in golden]
out_values = [top_distance(q) for q in out_doc]
    
print("있음 최대", round(max(in_values), 3))
print("없음 최소", round(min(out_values), 3))