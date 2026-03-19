from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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


app = FastAPI(
    title="Hand Recognition WebSocket Server",
    description="FastAPI websocket service for browser camera streaming and mode-switchable hand recognition.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registry = DetectorRegistry(
    device_name=config.DEVICE,
    jpeg_quality=config.JPEG_QUALITY,
    model_settings=MODEL_SETTINGS,
)
pq_detector = None
pq_detector_error = None

app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(config.STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> Dict[str, str]:
    errors = [registry.get_error(mode) for mode in MODEL_SETTINGS]
    errors = [item for item in errors if item]
    if pq_detector_error:
        errors.append(pq_detector_error)
    if errors:
        return {"status": "error", "detail": errors[0]}
    return {"status": "ok", "detail": "ready"}


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


@app.websocket("/ws/hand-digits")
async def hand_digits_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    current_mode = "digits"
    await websocket.send_json(
        {
            "type": "ready",
            "message": "WebSocket connected. Send JPEG binary frames.",
            "modes": ["digits", "letters"],
            "defaultMode": current_mode,
        }
    )

    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break

            if message.get("bytes") is not None:
                try:
                    if current_mode == "letters":
                        detector = get_pq_detector()
                    else:
                        detector = registry.get(current_mode)
                    result = detector.process_jpeg_bytes(message["bytes"])
                    await websocket.send_json(result)
                except Exception as exc:
                    await websocket.send_json({"type": "error", "message": str(exc)})
                continue

            if message.get("text") is not None:
                text = message["text"].strip()
                if text == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue
                if text.startswith("mode:"):
                    requested_mode = text.split(":", 1)[1].strip()
                    if requested_mode not in ("digits", "letters"):
                        await websocket.send_json({"type": "error", "message": "Unsupported mode: {0}".format(requested_mode)})
                    else:
                        current_mode = requested_mode
                        await websocket.send_json({"type": "mode_changed", "mode": current_mode})
                    continue
                await websocket.send_json({"type": "info", "message": "Send JPEG binary frames to run detection."})
    except WebSocketDisconnect:
        return


def main() -> None:
    uvicorn.run("server.app:app", host=config.HOST, port=config.PORT, reload=False)


if __name__ == "__main__":
    main()
