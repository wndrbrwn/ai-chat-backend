import os
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
from types import SimpleNamespace
import database
import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

def test_ask_returns_fake_answer(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_database()
    async def fake_ai(question, message):
        return "fake answer"
    monkeypatch.setattr(main, "get_ai_response", fake_ai)

    response = client.post("/ask", json = {"session_id": "a", "question": "hi"})

    assert response.status_code == 200
    assert response.json() == {"answer": "fake answer"}
    assert database.get_messages("a") == [
        {"role": "user", "content": "hi"}, 
        {"role": "assistant", "content": "fake answer"}
        ]

def test_ask_returns_502_when_ai_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_database()

    async def fail(question, messages):
        raise Exception("AI DOWN")

    monkeypatch.setattr(main, "get_ai_response", fail)

    response = client.post("/ask", json={"session_id": "a", "question": "hi"})

    assert response.status_code == 502
    assert database.get_messages("a") == []

def make_fake_create(texts, fail = False):
    async def fake_create(**kwargs):
        if fail:
            raise Exception("fake failure")
        
        async def gen():
            for t in texts:
                yield SimpleNamespace(
                    choices = [SimpleNamespace(delta=SimpleNamespace(content = t))]
                )
        return gen()
    return fake_create

def test_stream_returns_joined_text_and_saves(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_database()
    monkeypatch.setattr(
        main.client.chat.completions, "create", make_fake_create(["안", "녕"])
    )

    response = client.post("/ask-stream", json = {"session_id": "b", "question": "hi"})

    assert response.text == "안녕"
    assert database.get_messages("b") == [
         {"role": "user", "content": "hi"}, 
        {"role": "assistant", "content": response.text}
        ]

def test_stream_failure_sends_message_and_does_not_save(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_database()
    monkeypatch.setattr(
        main.client.chat.completions, "create", make_fake_create([], fail = True)
    )

    response = client.post("/ask-stream", json={"session_id": "c", "question": "hi"})
    
    assert "AI 서비스 요청에 실패했습니다." in response.text
    assert database.get_messages("c")  == []