
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.schemas.ingestion import IngestionRequest, IngestionResult
from app.services.llm_service import analyze_message, generate_response
from app.utils.token_counter import estimate_tokens

app = FastAPI(
    title="Enterprise Structured Ingestion Firewall",
    description="Classifies messages and generates helpful Markdown responses.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Ingestion Firewall API is running"}


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
        # Avoid exposing API keys or internal exception details.
        print(f"LLM request failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail=(
                "LLM request failed. Check the backend terminal, API key, "
                "model name, network, and provider limits."
            ),
        ) from exc