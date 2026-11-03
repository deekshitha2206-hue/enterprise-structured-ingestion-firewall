
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

from app.schemas.ingestion import IngestionRequest, IngestionResult
from app.services.llm_service import (
    analyze_message,
    generate_response,
    generate_chat_response,
)
from app.services.chat_memory import (
    create_session,
    get_history,
    add_message,
)
from app.utils.token_counter import estimate_tokens


app = FastAPI(
    title="Enterprise Structured Ingestion Firewall",
    description="Classifies messages and supports conversation memory.",
    version="3.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Ingestion Firewall API is running"
    }


@app.post("/api/analyze")
def analyze(request: IngestionRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    try:
        analysis: IngestionResult = analyze_message(message)
        analysis.token_metadata.estimated_input_tokens = estimate_tokens(message)

        markdown_response = generate_response(message, analysis)

        return {
            "analysis": analysis.model_dump(),
            "response_markdown": markdown_response,
        }

    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "The model response did not pass schema validation.",
                "validation_errors": exc.errors(),
            },
        ) from exc

    except Exception as exc:
        print(f"LLM request failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail=(
                "LLM request failed. Check the backend terminal, API key, "
                "model name, network, and provider limits."
            ),
        ) from exc


@app.post("/api/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty."
        )

    # Create a new session or retrieve an existing one.
    if request.session_id is None:
        session_id = create_session()
        history = get_history(session_id)
    else:
        session_id = request.session_id
        history = get_history(session_id)

        if history is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please start a new chat."
            )

    # Include the latest user message when calling Groq.
    conversation = history + [
        {"role": "user", "content": message}
    ]

    try:
        ai_response = generate_chat_response(conversation)

        # Save messages only after successful response generation.
        add_message(session_id, "user", message)
        add_message(session_id, "assistant", ai_response)

        return {
            "session_id": session_id,
            "response": ai_response,
            "history": get_history(session_id),
        }

    except Exception as exc:
        print(f"Chat request failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not generate a chat response. Check the backend terminal."
        ) from exc


@app.get("/api/chat/{session_id}")
def get_chat_history(session_id: str):
    history = get_history(session_id)

    if history is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "session_id": session_id,
        "history": history,
    }
