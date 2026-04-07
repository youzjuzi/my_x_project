import asyncio
import functools
import traceback
from typing import Callable

from .presenter import build_result_payload
from ..scenes import BaseSession
from .. import cpu_perf  # CPU 性能优化配置


def _build_command_practice_result(session: BaseSession, command_result, image_shape) -> dict:
    command_gesture = str(command_result.get("commandGesture") or "").strip()
    command_candidate = str(command_result.get("commandCandidate") or "").strip()
    display_text = command_gesture or command_candidate

    return {
        "type": "result",
        "mode": session.mode,
        "engine": "mediapipe-command",
        "latencyMs": 0.0,
        "imageWidth": int(image_shape[1]),
        "imageHeight": int(image_shape[0]),
        "handCount": int(command_result.get("commandHandCount") or 0),
        "text": display_text,
        "hands": [],
        "commandModeActive": True,
        "commandGesture": command_gesture,
        "commandHandCount": int(command_result.get("commandHandCount") or 0),
        "commandCandidate": command_candidate,
        "commandCounters": dict(command_result.get("commandCounters") or {}),
        "commandThreshold": int(command_result.get("commandThreshold") or 0),
        "commandCandidateProgress": session._command_candidate_progress(command_candidate, command_result),
        "actionPerformed": False,
        "actionType": "",
        "actionToast": "",
    }


async def run_inference_loop(session: BaseSession, get_detector: Callable[[str], object]) -> None:
    try:
        loop = asyncio.get_running_loop()
        _frame_counter = 0  # 用于 CPU 限帧计数
        while True:
            image = await session.take_latest_frame()

            # ② CPU 限帧：非采样帧直接跳过，不送入模型
            _frame_counter += 1
            if cpu_perf.ENABLED and (_frame_counter % cpu_perf.INFERENCE_EVERY_N != 0):
                continue

            # ③ CPU 降分辨率：推理前按比例缩小图像
            infer_image = cpu_perf.maybe_downsample(image)

            if session.mode == "commands" and session.command_recognizer is not None:
                command_result = await loop.run_in_executor(
                    None,
                    session.command_recognizer.process_frame,
                    image,
                )
                result = _build_command_practice_result(session, command_result, image.shape)
            elif session.command_mode_active and session.allows_detector_command_mode():
                command_result = await loop.run_in_executor(
                    None,
                    session.command_recognizer.process_frame,
                    image,  # ⚠️ 修正：MediaPipe 需要输入原始分辨率，缩小会导致它的特征追踪断代而巨卡
                )
                command_metadata = session.apply_command_actions(command_result)
                session.update_command_mode(command_result)
                if session.command_mode_active:
                    result = session.build_command_result(command_result, image.shape, command_metadata)
                elif command_metadata.get("modeChangedByCommand") or command_metadata.get("actionPerformed"):
                    result = session.build_command_result(command_result, image.shape, command_metadata)
                else:
                    detector = await loop.run_in_executor(None, get_detector, session.mode)
                    func = functools.partial(
                        detector.process_frame,
                        infer_image,
                        include_annotated=False,
                    )
                    result = await loop.run_in_executor(None, func)
            else:
                detector = await loop.run_in_executor(None, get_detector, session.mode)
                func = functools.partial(
                    detector.process_frame,
                    infer_image,
                    include_annotated=False,
                )
                result = await loop.run_in_executor(None, func)
                hand_count = int(result.get("handCount") or 0)

                # 双手在画面中时，YOLOv5 的字符识别不可靠（常误识别为 Q），
                # 清空 text 防止污染 vote_buffer
                if hand_count >= 2:
                    result["text"] = ""

                # action_suppression 期间，无论 handCount 多少，都清空文本
                # 防止命令退出后用户收手时 YOLO 识别出的字符污染显示状态
                if session._is_in_action_suppression():
                    result["text"] = ""

                if session.allows_detector_command_mode():
                    session.update_command_reentry_gate(hand_count)
                if session.allows_detector_command_mode() and session.can_activate_command_mode(hand_count):
                    session.activate_command_mode()
                    command_result = await loop.run_in_executor(
                        None,
                        session.command_recognizer.process_frame,
                        image,  # ⚠️ 修正：MediaPipe 需要原始分辨率来保持手部追踪器的持续工作而不触发报错
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
