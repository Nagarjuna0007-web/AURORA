import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import DEBUG
from app.engine.aurora_engine import AuroraEngine

logger = logging.getLogger("aurora.api")


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="AURORA API",
    description="API interface for AURORA AI",
    version="1.0.0",
)


# --------------------------------------------------
# AURORA ENGINE
# --------------------------------------------------

engine = AuroraEngine()


# --------------------------------------------------
# CHAT REQUEST MODEL
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


# --------------------------------------------------
# WEB UI
# --------------------------------------------------

@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# AURORA STATUS
# --------------------------------------------------

@app.get("/status")
def status():
    return {
        "name": engine.app_name,
        "version": engine.version,
        "environment": engine.environment,
        "status": "ready",
    }


# --------------------------------------------------
# NORMAL CHAT
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=422, detail="Message must not be blank.")

    try:
        response = engine.chat(request.message)
    except Exception:
        logger.exception("Chat request failed.")
        raise HTTPException(status_code=500, detail="Aurora could not process the request.")

    return {
        "response": response
    }


# --------------------------------------------------
# STREAMING CHAT
# --------------------------------------------------

@app.post("/chat/stream")
def chat_stream(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(status_code=422, detail="Message must not be blank.")

    def generate():

        try:
            for event in engine.web_stream_chat_events(
                request.message
            ):

                yield (
                    json.dumps(
                        event,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        except Exception:
            logger.exception("Streaming chat failed.")
            yield json.dumps(
                {"type": "error", "message": "Aurora could not process the request."}
            ) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
    )

# --------------------------------------------------
# SERVER STARTUP
# --------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.api:app",
        host="127.0.0.1",
        port=8000,
        reload=DEBUG,
    )