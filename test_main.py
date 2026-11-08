import os
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

import database
import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

def test_ask_returns_fake_answer(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_database()
    monkeypatch.setattr(main, "get_ai_response", lambda question, messages: "fake answer")

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

    def fail(question, messages):
        raise EXCEPTION("AI DOWN")

    monkeypatch.setattr(main, "get_ai_response", fail)

    response = client.post("/ask", json={"session_id": "a", "question": "hi"})

    assert response.status_code == 502
    assert database.get_messages("a") == []