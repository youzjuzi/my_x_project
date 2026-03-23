import asyncio
import functools
from typing import Callable

from .presenter import build_result_payload
from .session import SessionState


async def run_inference_loop(session: SessionState, get_detector: Callable[[str], object]) -> None:
    try:
        loop = asyncio.get_running_loop()
        while True:
            image = await session.take_latest_frame()
            detector = get_detector(session.mode)
            func = functools.partial(
                detector.process_frame,
                image,
                include_annotated=False,
            )
            result = await loop.run_in_executor(None, func)
            session.mark_processed()
            result["inputFps"] = session.input_fps()
            result["processedFps"] = session.processed_fps()
            payload = build_result_payload(session, result)
            await session.send_json(payload)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        await session.send_json({"type": "error", "message": str(exc)})
