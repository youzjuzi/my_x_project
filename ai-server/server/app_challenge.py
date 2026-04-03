from . import config
from .apps import create_scene_app
from .scenes import ChallengeSession


def build_session(pc, mode):
    return ChallengeSession(
        pc,
        mode,
    )


app = create_scene_app(
    title="Hand Challenge WebRTC Server",
    description="FastAPI WebRTC service for challenge scene recognition.",
    session_factory=build_session,
)


def main() -> None:
    import uvicorn

    uvicorn.run("server.app_challenge:app", host=config.HOST, port=config.WEBRTC_PORT, reload=False)


if __name__ == "__main__":
    main()
