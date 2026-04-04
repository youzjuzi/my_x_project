from pathlib import Path

from . import config
from .apps import create_scene_app
from .routes import polish_router
from .scenes import RecognitionSession
from .strategies.hand_command import HandCommandRecognizer

STATIC_DIR = Path(__file__).resolve().parent / "static"


def build_session(pc, mode):
    return RecognitionSession(
        pc,
        mode,
        command_recognizer=HandCommandRecognizer(config.MEDIAPIPE_TASK),
    )


app = create_scene_app(
    title="Hand Recognition WebRTC Server",
    description="FastAPI WebRTC service for browser camera streaming and mode-switchable hand recognition.",
    session_factory=build_session,
    static_dir=STATIC_DIR,
)

# 单独注册润色路由，前缀与前端 URL 约定一致：/recognition/webrtc/polish
app.include_router(polish_router, prefix="/recognition")


def main() -> None:
    import uvicorn

    uvicorn.run("server.app_recognition:app", host=config.HOST, port=config.WEBRTC_PORT, reload=False)


if __name__ == "__main__":
    main()
