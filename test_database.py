import sqlite3
import pytest
import database

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_database()

def test_sessions_are_separated(temp_db):
    database.save_message("a", "user", "hi a")
    database.save_message("b", "user", "hi b")
    assert database.get_messages("a") == [{"role": "user", "content": "hi a"}]

def test_delete_messages(temp_db):
    database.save_message("a", "user", "hi")
    database.delete_messages("a")
    assert database.get_messages("a") == []

def test_get_sessions(temp_db):
    database.save_message("b", "user", "x")
    database.save_message("a", "user", "y")
    assert database.get_sessions() == ["a", "b"]

def test_save_exchange_rolls_back(temp_db):
    with pytest.raises(sqlite3.IntegrityError):
        database.save_exchange("a", "question", None)
    assert database.get_messages("a") == []
    
def test_update_message(temp_db):
    database.save_message("a", "user", "old")
    database.update_message(1, "new")
    assert database.get_messages("a") == [{"role": "user", "content": "new"}]