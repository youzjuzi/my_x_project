from . import config
from .apps import create_scene_app
from .scenes import PracticeSession


def build_session(pc, mode):
    return PracticeSession(
        pc,
        mode,
    )


app = create_scene_app(
    title="Hand Practice WebRTC Server",
    description="FastAPI WebRTC service for practice scene recognition.",
    session_factory=build_session,
)


def main() -> None:
    import uvicorn

    uvicorn.run("server.app_practice:app", host=config.HOST, port=config.WEBRTC_PORT, reload=False)


if __name__ == "__main__":
    main()
