
import pytest

from app.services import chat_memory


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.filters = {}
        self.operation = "select"
        self.values = None

    def select(self, columns):
        self.operation = "select"
        return self

    def insert(self, values):
        self.operation = "insert"
        self.values = values
        return self

    def eq(self, column, value):
        self.filters[column] = value
        return self

    def order(self, column):
        return self

    def execute(self):
        records = self.database.setdefault(self.table, [])

        if self.operation == "insert":
            records.append(self.values.copy())
            return FakeResponse([self.values])

        result = [
            record for record in records
            if all(record.get(key) == value
                   for key, value in self.filters.items())
        ]

        return FakeResponse(result)


class FakeSupabase:
    def __init__(self):
        self.database = {
            "chat_sessions": [],
            "chat_messages": []
        }

    def table(self, name):
        return FakeQuery(self.database, name)


@pytest.fixture
def fake_supabase(monkeypatch):
    client = FakeSupabase()
    monkeypatch.setattr(
        chat_memory,
        "get_supabase_client",
        lambda: client
    )
    return client


def test_create_session(fake_supabase):
    session_id = chat_memory.create_session()

    assert session_id is not None
    assert chat_memory.get_history(session_id) == []


def test_add_and_get_messages(fake_supabase):
    session_id = chat_memory.create_session()

    chat_memory.add_message(session_id, "user", "Hello")
    chat_memory.add_message(session_id, "assistant", "Hi!")

    history = chat_memory.get_history(session_id)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi!"


def test_sessions_are_isolated(fake_supabase):
    session_one = chat_memory.create_session()
    session_two = chat_memory.create_session()

    chat_memory.add_message(
        session_one,
        "user",
        "My name is Deekshitha."
    )

    assert len(chat_memory.get_history(session_one)) == 1
    assert chat_memory.get_history(session_two) == []


def test_invalid_session(fake_supabase):
    with pytest.raises(ValueError, match="Invalid session ID"):
        chat_memory.add_message(
            "invalid-session",
            "user",
            "Hello"
        )
