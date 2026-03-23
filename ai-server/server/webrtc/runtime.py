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
            if session.command_mode_active and session.command_recognizer is not None:
                command_result = await loop.run_in_executor(
                    None,
                    session.command_recognizer.process_frame,
                    image,
                )
                command_metadata = session.apply_command_actions(command_result)
                session.update_command_mode(command_result)
                if session.command_mode_active:
                    result = session.build_command_result(command_result, image.shape, command_metadata)
                elif command_metadata.get("modeChangedByCommand"):
                    result = session.build_command_result(command_result, image.shape, command_metadata)
                else:
                    detector = get_detector(session.mode)
                    func = functools.partial(
                        detector.process_frame,
                        image,
                        include_annotated=False,
                    )
                    result = await loop.run_in_executor(None, func)
            else:
                detector = get_detector(session.mode)
                func = functools.partial(
                    detector.process_frame,
                    image,
                    include_annotated=False,
                )
                result = await loop.run_in_executor(None, func)
                if (
                    session.command_recognizer is not None
                    and int(result.get("handCount") or 0) == 2
                ):
                    session.activate_command_mode()
                    command_result = await loop.run_in_executor(
                        None,
                        session.command_recognizer.process_frame,
                        image,
                    )
                    command_metadata = session.apply_command_actions(command_result)
                    session.update_command_mode(command_result)
                    if session.command_mode_active:
                        result = session.build_command_result(command_result, image.shape, command_metadata)
                    elif command_metadata.get("modeChangedByCommand"):
                        result = session.build_command_result(command_result, image.shape, command_metadata)

            session.mark_processed()
            result["inputFps"] = session.input_fps()
            result["processedFps"] = session.processed_fps()
            payload = build_result_payload(session, result)
            await session.send_json(payload)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        await session.send_json({"type": "error", "message": str(exc)})
