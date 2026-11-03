from uuid import uuid4

# Temporary in-memory storage for chat sessions
chat_sessions = {}


def create_session():
    """Create a new chat session with a unique ID."""
    session_id = str(uuid4())
    chat_sessions[session_id] = []
    return session_id


def get_history(session_id: str):
    """Get conversation history for a session."""
    return chat_sessions.get(session_id)


def add_message(session_id: str, role: str, content: str):
    """Store a user or assistant message."""
    if session_id not in chat_sessions:
        raise ValueError("Invalid session ID")

    chat_sessions[session_id].append({
        "role": role,
        "content": content
    })