import rag
from types import SimpleNamespace

class FakeCollection:
    def query(self, query_embeddings, n_results):
        return {
            "documents": [["멀리 있는 청크"]],
            "metadatas": [[{"source": "a.txt", "chunk": 0}]],
            "distances": [[2.0]],
            }

class FakeCollection_2:
    def query(self, query_embeddings, n_results):
        return {
            "documents": [["멀리 있는 청크"]],
            "metadatas": [[{"source": "a.txt", "chunk": 0}]],
            "distances": [[0.5]],
            }    
    
def test_answer_with_rag_returns_not_found_when_all_chunks_far(monkeypatch):
    monkeypatch.setattr(rag, "embed", lambda texts: [[0.0]])

    result = rag.answer_with_rag("질문", FakeCollection())

    assert result["answer"] == "문서에서 찾을 수 없습니다"
    assert result["sources"] == []

def test_answer_with_rag_sends_flat_message_dicts(monkeypatch):
    sent = {}

    def fake_create(model, messages):
        sent["messages"] = messages
        return SimpleNamespace(choices = [SimpleNamespace(message = SimpleNamespace(content = "답"))])

    monkeypatch.setattr(rag, "embed", lambda texts: [[0.0]])
    monkeypatch.setattr(rag.llm.chat.completions, "create", fake_create)

    history = [{"role": "user", "content": "이전 질문"}, {"role": "assistant", "content": "이전 답"}]
    result = rag.answer_with_rag("질문", FakeCollection_2(), history)

    assert all(isinstance(m, dict) for m in sent["messages"])
    assert sent["messages"][-1]["role"] == "user"
    assert len(sent["messages"]) == 3
    assert result["answer"] == "답"