import asyncio
from collections import deque
import functools
import json
from pathlib import Path
import time
from typing import Deque, Dict, Set

from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from . import config
from .detector import DetectorRegistry
from .pq_hybrid_detector import PQHybridDetector


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
ANNOTATED_FRAME_INTERVAL = 4

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


class OfferPayload(BaseModel):
    sdp: str
    type: str
    mode: str = "digits"


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


async def wait_for_ice_gathering(pc: RTCPeerConnection) -> None:
    if pc.iceGatheringState == "complete":
        return

    completed = asyncio.Event()

    @pc.on("icegatheringstatechange")
    async def on_ice_gathering_state_change() -> None:
        if pc.iceGatheringState == "complete":
            completed.set()

    await completed.wait()


class SessionState:
    def __init__(self, pc: RTCPeerConnection, mode: str) -> None:
        self.pc = pc
        self.mode = mode if mode in ("digits", "letters") else "digits"
        self.channel = None
        self.track_tasks: Set[asyncio.Task] = set()
        self.latest_frame = None
        self.latest_frame_lock = asyncio.Lock()
        self.frame_ready = asyncio.Event()
        self.result_counter = 0
        self.input_timestamps: Deque[float] = deque()
        self.processed_timestamps: Deque[float] = deque()

    async def send_json(self, payload: Dict[str, object]) -> None:
        if self.channel is None or self.channel.readyState != "open":
            return
        if getattr(self.channel, "bufferedAmount", 0) > 1_000_000:
            return
        self.channel.send(json.dumps(payload, ensure_ascii=False))

    async def send_ready(self) -> None:
        await self.send_json(
            {
                "type": "ready",
                "transport": "webrtc",
                "message": "WebRTC connected. Browser media track is streaming.",
                "modes": ["digits", "letters"],
                "defaultMode": self.mode,
            }
        )

    async def handle_channel_message(self, message: object) -> None:
        if not isinstance(message, str):
            return

        text = message.strip()
        if text == "ping":
            await self.send_json({"type": "pong"})
            return
        if text.startswith("mode:"):
            requested_mode = text.split(":", 1)[1].strip()
            if requested_mode not in ("digits", "letters"):
                await self.send_json({"type": "error", "message": f"Unsupported mode: {requested_mode}"})
                return
            self.mode = requested_mode
            await self.send_json({"type": "mode_changed", "mode": self.mode})
            return

        await self.send_json({"type": "info", "message": "Send mode:<digits|letters> or ping on the data channel."})

    def attach_channel(self, channel) -> None:
        self.channel = channel

        @channel.on("open")
        def on_open() -> None:
            asyncio.create_task(self.send_ready())

        @channel.on("message")
        def on_message(message: object) -> None:
            asyncio.create_task(self.handle_channel_message(message))

    def add_track_task(self, task: asyncio.Task) -> None:
        self.track_tasks.add(task)
        task.add_done_callback(lambda finished: self.track_tasks.discard(finished))

    async def publish_frame(self, frame) -> None:
        self._mark_timestamp(self.input_timestamps)
        image = frame.to_ndarray(format="bgr24")
        async with self.latest_frame_lock:
            self.latest_frame = image
            self.frame_ready.set()

    async def take_latest_frame(self):
        while True:
            await self.frame_ready.wait()
            async with self.latest_frame_lock:
                image = self.latest_frame
                self.latest_frame = None
                self.frame_ready.clear()
            if image is not None:
                return image

    def should_include_annotated(self) -> bool:
        self.result_counter += 1
        return self.result_counter % ANNOTATED_FRAME_INTERVAL == 1

    def mark_processed(self) -> None:
        self._mark_timestamp(self.processed_timestamps)

    def input_fps(self) -> float:
        return self._calculate_fps(self.input_timestamps)

    def processed_fps(self) -> float:
        return self._calculate_fps(self.processed_timestamps)

    def _mark_timestamp(self, bucket: Deque[float]) -> None:
        now = time.perf_counter()
        bucket.append(now)
        cutoff = now - 1.0
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

    def _calculate_fps(self, bucket: Deque[float]) -> float:
        cutoff = time.perf_counter() - 1.0
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) <= 1:
            return float(len(bucket))
        duration = bucket[-1] - bucket[0]
        if duration <= 0:
            return float(len(bucket))
        return round(len(bucket) / duration, 2)

    async def close(self) -> None:
        for task in list(self.track_tasks):
            task.cancel()
        self.track_tasks.clear()
        self.frame_ready.set()
        if self.channel is not None and self.channel.readyState != "closed":
            self.channel.close()
        if self.pc.connectionState != "closed":
            await self.pc.close()


async def receive_video_track(track, session: SessionState) -> None:
    try:
        while True:
            frame = await track.recv()
            await session.publish_frame(frame)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        await session.send_json({"type": "error", "message": str(exc)})


async def run_inference_loop(session: SessionState) -> None:
    try:
        loop = asyncio.get_running_loop()
        while True:
            image = await session.take_latest_frame()
            detector = get_detector(session.mode)
            include_annotated = session.should_include_annotated()
            func = functools.partial(
                detector.process_frame,
                image,
                include_annotated=include_annotated,
            )
            result = await loop.run_in_executor(None, func)
            session.mark_processed()
            result["inputFps"] = session.input_fps()
            result["processedFps"] = session.processed_fps()
            await session.send_json(result)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        await session.send_json({"type": "error", "message": str(exc)})


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
    session = SessionState(pc, payload.mode)
    peer_connections.add(pc)
    session.add_track_task(asyncio.create_task(run_inference_loop(session)))

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
