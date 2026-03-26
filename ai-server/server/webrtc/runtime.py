import asyncio
import functools
import traceback
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
                elif command_metadata.get("modeChangedByCommand") or command_metadata.get("actionPerformed"):
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
                hand_count = int(result.get("handCount") or 0)

                # 双手在画面中时，YOLOv5 的字符识别不可靠（常误识别为 Q），
                # 清空 text 防止污染 vote_buffer
                if hand_count >= 2:
                    result["text"] = ""

                if session.command_recognizer is not None:
                    session.update_command_reentry_gate(hand_count)
                if (
                    session.command_recognizer is not None
                    and session.can_activate_command_mode(hand_count)
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
                    elif command_metadata.get("modeChangedByCommand") or command_metadata.get("actionPerformed"):
                        result = session.build_command_result(command_result, image.shape, command_metadata)

            session.mark_processed()
            result["inputFps"] = session.input_fps()
            result["processedFps"] = session.processed_fps()
            payload = build_result_payload(session, result)
            await session.send_json(payload)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        traceback.print_exc()
        await session.send_json({"type": "error", "message": str(exc)})
