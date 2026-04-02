import asyncio
from pathlib import Path
from typing import Callable, Optional

from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..webrtc import OfferPayload, receive_video_track, run_inference_loop, wait_for_ice_gathering
from ..scenes import BaseSession
from .shared import SharedAppResources, shared_resources

SessionFactory = Callable[[RTCPeerConnection, str], BaseSession]


def create_scene_app(
    *,
    title: str,
    description: str,
    session_factory: SessionFactory,
    resources: SharedAppResources = shared_resources,
    version: str = "1.0.0",
    static_dir: Optional[Path] = None,
    extra_router: Optional[APIRouter] = None,
) -> FastAPI:
    app = FastAPI(title=title, description=description, version=version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if static_dir is not None:
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        @app.get("/")
        async def index() -> FileResponse:
            return FileResponse(static_dir / "index.html")

    @app.get("/health")
    async def health():
        return resources.health_payload()

    @app.post("/webrtc/offer")
    async def create_offer(payload: OfferPayload):
        pc = RTCPeerConnection()
        session = session_factory(pc, payload.mode)
        resources.peer_connections.add(pc)
        session.add_track_task(asyncio.create_task(run_inference_loop(session, resources.get_detector)))

        @pc.on("connectionstatechange")
        async def on_connectionstatechange() -> None:
            if pc.connectionState in {"failed", "closed"}:
                resources.peer_connections.discard(pc)
                await session.close()

        @pc.on("datachannel")
        def on_datachannel(channel) -> None:
            session.attach_channel(channel)

        @pc.on("track")
        def on_track(track) -> None:
            if track.kind == "video":
                task = asyncio.create_task(receive_video_track(track, session))
                session.add_track_task(task)

        try:
            await pc.setRemoteDescription(RTCSessionDescription(sdp=payload.sdp, type=payload.type))
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await wait_for_ice_gathering(pc)
            local_description = pc.localDescription
            if local_description is None:
                raise RuntimeError("Failed to create local WebRTC description")
            return {"sdp": local_description.sdp, "type": local_description.type}
        except Exception as exc:
            resources.peer_connections.discard(pc)
            await session.close()
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    if extra_router is not None:
        app.include_router(extra_router)

    return app
