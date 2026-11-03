from app.services.chat_memory import (
    create_session,
    get_history,
    add_message,
)


def test_create_session():
    session_id = create_session()

    assert session_id is not None
    assert get_history(session_id) == []


def test_add_and_get_messages():
    session_id = create_session()

    add_message(session_id, "user", "Hello")
    add_message(session_id, "assistant", "Hi!")

    history = get_history(session_id)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi!"


def test_sessions_are_isolated():
    session_one = create_session()
    session_two = create_session()

    add_message(session_one, "user", "My name is Deekshitha.")

    assert get_history(session_one) != get_history(session_two)
    assert get_history(session_two) == []


def test_invalid_session():
    try:
        add_message("invalid-session", "user", "Hello")
        assert False, "Expected ValueError"
    except ValueError as error:
        assert str(error) == "Invalid session ID"