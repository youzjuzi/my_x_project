import asyncio
from pathlib import Path
from typing import Dict, Set

from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from openai import AsyncOpenAI

from . import config
from .detector import DetectorRegistry
from .hand_command import HandCommandRecognizer
from .pq_hybrid_detector import PQHybridDetector
from .webrtc import OfferPayload, SessionState, receive_video_track, run_inference_loop, wait_for_ice_gathering


MODEL_SETTINGS = {
    "digits": {
        "source_module": "server.yolo_stage",
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


class PolishRequest(BaseModel):
    content: str


@app.post("/webrtc/polish")
async def polish_sentence(payload: PolishRequest) -> Dict[str, str]:
    if not payload.content.strip():
        return {"polishedText": ""}
        
    if not config.LLM_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="AI 润色未配置 LLM_API_KEY，请在 ai-server/.env 中配置相关参数并重启服务。"
        )

    try:
        client = AsyncOpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL
        )

        system_prompt = """
你是一个专业的手语翻译润色助手。

# Task
我会给你一组手语识别系统输出的零碎词汇（Gloss），请你将它们组合、润色成一句符合中文日常表达习惯的流畅句子。

# Rules
1. 保持原意：不要随意添加无关的细节或过度联想。
2. 纠正语序：手语常使用倒装或宾语前置，请调整为主谓宾结构。
3. 补充虚词：适当补充“的、了、是、在”等助词，使句子连贯。
4. 极简输出：只输出润色后的最终句子，**绝对不要**包含任何解释、问候语或标点符号的多余前缀。

# Example
输入：我 昨天 医院 去 看病
输出：我昨天去医院看病了。

输入：你 叫 名字 什么
输出：你叫什么名字？
"""
        response = await client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": f"输入：{payload.content.strip()}"}
            ],
            temperature=0.3, # 稍微降低温度，追求稳定性
        )
        
        polished_text = response.choices[0].message.content.strip()
        # 清理可能生成的以"输出："开头的内容
        if polished_text.startswith("输出："):
            polished_text = polished_text[3:]
            
        return {"polishedText": polished_text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI 服务调用失败: {str(exc)}") from exc



def main() -> None:
    uvicorn.run("server.app_webrtc:app", host=config.HOST, port=config.WEBRTC_PORT, reload=False)


if __name__ == "__main__":
    main()
