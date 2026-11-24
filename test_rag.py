import rag

class FakeCollection:
    def query(self, query_embeddings, n_results):
        return {
            "documents": [["멀리 있는 청크"]],
            "metadatas": [[{"source": "a.txt", "chunk": 0}]],
            "distances": [[2.0]],
            }
    
def test_answer_with_rag_returns_not_found_when_all_chunks_far(monkeypatch):
    monkeypatch.setattr(rag, "embed", lambda texts: [[0.0]])

    result = rag.answer_with_rag("질문", FakeCollection())

    assert result["answer"] == "문서에서 찾을 수 없습니다"
    assert result["sources"] == []