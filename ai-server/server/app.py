from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .app_challenge import app as challenge_app
from .app_practice import app as practice_app
from .app_recognition import app as recognition_app

app = FastAPI(
    title="Hand Recognition Unified Server",
    description="Unified FastAPI entrypoint for recognition, practice, and challenge scenes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "scenes": {
            "recognition": "/recognition",
            "practice": "/practice",
            "challenge": "/challenge",
        },
    }


app.mount("/recognition", recognition_app)
app.mount("/practice", practice_app)
app.mount("/challenge", challenge_app)

# Legacy compatibility: keep the old recognition scene mounted under a stable fallback path.
app.mount("/legacy-recognition", recognition_app)
