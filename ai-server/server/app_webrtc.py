import asyncio
from pathlib import Path
from typing import Dict, Set

from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from . import config
from .detector import DetectorRegistry
from .hand_command import HandCommandRecognizer
from .pq_hybrid_detector import PQHybridDetector
from .webrtc import OfferPayload, SessionState, receive_video_track, run_inference_loop, wait_for_ice_gathering


MODEL_SETTINGS = {
    "digits": {
        "source_module": "test_hand_digits",
        "hand_weights": config.HAND_WEIGHTS,
        "target_weights": config.DIGIT_WEIGHTS,
        "imgsz": config.IMGSZ,
        "hand_conf": config.HAND_CONF,
        "target_conf": config.DIGIT_CONF,
        "iou_thres": config.IOU_THRES,
        "max_det": config.MAX_DET,
        "margin": config.MARGIN,
    },
}

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = FastAPI(
    title="Hand Recognition WebRTC Server",
    description="FastAPI WebRTC service for browser camera streaming and mode-switchable hand recognition.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

registry = DetectorRegistry(
    device_name=config.DEVICE,
    jpeg_quality=config.JPEG_QUALITY,
    model_settings=MODEL_SETTINGS,
)
pq_detector = None
pq_detector_error = None
peer_connections: Set[RTCPeerConnection] = set()


def get_pq_detector():
    global pq_detector
    global pq_detector_error
    if pq_detector is not None:
        return pq_detector
    if pq_detector_error is not None:
        raise RuntimeError(pq_detector_error)

    try:
        pq_detector = PQHybridDetector(
            hand_weights=config.HAND_WEIGHTS,
            letters_weights=config.LETTER_WEIGHTS,
            mediapipe_model_path=config.MEDIAPIPE_TASK,
            imgsz=config.IMGSZ,
            hand_conf=config.HAND_CONF,
            letters_conf=config.LETTER_CONF,
            iou_thres=config.IOU_THRES,
            device_name=config.DEVICE,
            max_det=config.MAX_DET,
            margin=config.MARGIN,
            jpeg_quality=config.JPEG_QUALITY,
            pq_exit_grace_seconds=config.PQ_EXIT_GRACE_SECONDS,
            mn_exit_grace_seconds=config.MN_EXIT_GRACE_SECONDS,
            ij_dz_exit_grace_seconds=config.IJ_DZ_EXIT_GRACE_SECONDS,
        )
        return pq_detector
    except Exception as exc:
        pq_detector_error = str(exc)
        raise RuntimeError(pq_detector_error)


def get_detector(mode: str):
    if mode == "letters":
        return get_pq_detector()
    return registry.get("digits")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> Dict[str, object]:
    errors = [registry.get_error(mode) for mode in MODEL_SETTINGS]
    errors = [item for item in errors if item]
    if pq_detector_error:
        errors.append(pq_detector_error)
    if errors:
        return {"status": "error", "detail": errors[0], "connections": len(peer_connections)}
    return {"status": "ok", "detail": "ready", "connections": len(peer_connections)}


@app.post("/webrtc/offer")
async def create_offer(payload: OfferPayload) -> Dict[str, str]:
    pc = RTCPeerConnection()
    session = SessionState(
        pc,
        payload.mode,
        command_recognizer=HandCommandRecognizer(config.MEDIAPIPE_TASK),
    )
    peer_connections.add(pc)
    session.add_track_task(asyncio.create_task(run_inference_loop(session, get_detector)))

    @pc.on("connectionstatechange")
    async def on_connectionstatechange() -> None:
        if pc.connectionState in {"failed", "closed"}:
            peer_connections.discard(pc)
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
        peer_connections.discard(pc)
        await session.close()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def main() -> None:
    uvicorn.run("server.app_webrtc:app", host=config.HOST, port=config.WEBRTC_PORT, reload=False)


if __name__ == "__main__":
    main()
