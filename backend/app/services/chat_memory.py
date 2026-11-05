
from uuid import uuid4

from app.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY


_supabase_client = None


def get_supabase_client():
    """Create and reuse the Supabase client."""
    global _supabase_client

    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError("Supabase configuration is missing.")

        # Import Supabase only when a database connection is needed.
        from supabase import create_client

        _supabase_client = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_ROLE_KEY
        )

    return _supabase_client


def create_session():
    """Create a new chat session in Supabase."""
    session_id = str(uuid4())

    client = get_supabase_client()

    client.table("chat_sessions").insert({
        "id": session_id
    }).execute()

    return session_id


def get_history(session_id: str):
    """Get conversation history from Supabase."""
    client = get_supabase_client()

    session = (
        client.table("chat_sessions")
        .select("id")
        .eq("id", session_id)
        .execute()
    )

    if not session.data:
        return None

    response = (
        client.table("chat_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )

    return response.data


def add_message(session_id: str, role: str, content: str):
    """Save a user or assistant message in Supabase."""
    if role not in ("user", "assistant"):
        raise ValueError("Invalid message role")

    client = get_supabase_client()

    session = (
        client.table("chat_sessions")
        .select("id")
        .eq("id", session_id)
        .execute()
    )

    if not session.data:
        raise ValueError("Invalid session ID")

    client.table("chat_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()
