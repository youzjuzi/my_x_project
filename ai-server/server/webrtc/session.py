import asyncio
from collections import Counter, deque
import json
import time
from typing import Deque, Dict, Optional, Set

from aiortc import RTCPeerConnection

from ..pinyin_converter import PinyinConverter, digits_to_candidates


class SessionState:
    def __init__(
        self,
        pc: RTCPeerConnection,
        mode: str,
        process_items_limit: int = 8,
        command_recognizer=None,
        command_mode_timeout_seconds: float = 2.5,
        switch_min_interval_seconds: float = 1.0,
        stable_token_duration_seconds: float = 1.5,
        delete_hold_seconds: float = 1.5,
        clear_hold_seconds: float = 1.5,
        vote_window_frames: int = 20,
        switch_suppression_seconds: float = 2.0,
    ) -> None:
        self.pc = pc
        self.mode = mode if mode in ("digits", "letters") else "digits"
        self.command_recognizer = command_recognizer
        self.command_mode_timeout_seconds = command_mode_timeout_seconds
        self.switch_min_interval_seconds = switch_min_interval_seconds
        self.stable_token_duration_seconds = stable_token_duration_seconds
        self.delete_hold_seconds = delete_hold_seconds
        self.clear_hold_seconds = clear_hold_seconds
        self.switch_suppression_seconds = switch_suppression_seconds

        self.channel = None
        self.track_tasks: Set[asyncio.Task] = set()
        self.latest_frame = None
        self.latest_frame_lock = asyncio.Lock()
        self.frame_ready = asyncio.Event()
        self.input_timestamps: Deque[float] = deque()
        self.processed_timestamps: Deque[float] = deque()

        self.process_items: Deque[str] = deque(maxlen=process_items_limit)
        self._vote_buffer: Deque[str] = deque(maxlen=vote_window_frames)
        self.spelling_buffer = ""
        self.cached_buffer = ""
        self.raw_pinyin_buffer = ""
        self.hanzi_candidate = ""
        self.hanzi_candidates = []
        self.candidate_index = 0
        self.pinyin_converter = PinyinConverter()

        self.pending_stable_text = ""
        self.pending_stable_started_at: Optional[float] = None
        self.last_cached_token = ""
        self.switch_suppression_until: Optional[float] = None

        self.command_mode_active = False
        self.command_mode_started_at: Optional[float] = None
        self.command_mode_last_seen_at: Optional[float] = None
        self.command_mode_last_command_at: Optional[float] = None
        self.command_reentry_requires_release = False

        self.confirm_ready = True
        self.delete_ready = True
        self.clear_ready = True
        self.next_ready = True
        self.submit_ready = True

        self.pending_delete_started_at: Optional[float] = None
        self.pending_clear_started_at: Optional[float] = None

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
            self.reset_display_state(clear_cached=True)
            self.deactivate_command_mode()
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

    def mark_processed(self) -> None:
        self._mark_timestamp(self.processed_timestamps)

    def input_fps(self) -> float:
        return self._calculate_fps(self.input_timestamps)

    def processed_fps(self) -> float:
        return self._calculate_fps(self.processed_timestamps)

    def _is_in_switch_suppression(self) -> bool:
        """模式切换冷却期内返回 True，过期后自动清理时间戳。"""
        if self.switch_suppression_until is None:
            return False
        if time.perf_counter() < self.switch_suppression_until:
            return True
        self.switch_suppression_until = None
        return False

    def _compute_vote_winner(self, min_ratio: float = 0.45) -> str:
        """从最近 N 帧的原始识别结果中投票，返回占比达到 min_ratio 的赢家，否则返回空串。"""
        if not self._vote_buffer:
            return ""
        counts = Counter(c for c in self._vote_buffer if c)
        if not counts:
            return ""
        winner, count = counts.most_common(1)[0]
        if count / len(self._vote_buffer) >= min_ratio:
            return winner
        return ""

    def update_display_state(self, result: Dict[str, object]) -> None:
        is_command_result = result.get("engine") == "mediapipe-command"
        raw_spelling = "" if is_command_result else str(result.get("text") or "").strip()

        if not is_command_result:
            if self._is_in_switch_suppression():
                # 冷却期内：清空 vote_buffer 防止污染，保持空白输出
                self._vote_buffer.clear()
                self.spelling_buffer = ""
                self._refresh_pinyin_state()
                return
            self._vote_buffer.append(raw_spelling)

        # 投票赢家作为所有下游的输入，过滤帧间抖动
        vote_winner = self._compute_vote_winner() if not is_command_result else ""
        self.spelling_buffer = vote_winner

        if not is_command_result:
            self._update_cached_buffer(vote_winner)

        self._refresh_pinyin_state()

        if is_command_result:
            return

        # process_items 只在投票赢家发生变化时追加，不再对每帧原始结果追加
        if vote_winner and (not self.process_items or self.process_items[-1] != vote_winner):
            self.process_items.append(vote_winner)

    def display_snapshot(self) -> Dict[str, object]:
        return {
            "processItems": list(self.process_items),
            "spellingBuffer": self.spelling_buffer,
            "cachedBuffer": self.cached_buffer,
            "hanziCandidate": self.hanzi_candidate,
            "hanziCandidates": list(self.hanzi_candidates),
            "candidateIndex": self.candidate_index,
            "stabilityProgress": self.stability_progress(),
            "stabilityDurationMs": int(self.stable_token_duration_seconds * 1000),
        }

    def reset_display_state(self, clear_cached: bool = False) -> None:
        self.process_items.clear()
        self._vote_buffer.clear()
        self.spelling_buffer = ""
        self.pending_stable_text = ""
        self.pending_stable_started_at = None
        if clear_cached:
            self.cached_buffer = ""
            self.last_cached_token = ""
        self._refresh_pinyin_state()

    def activate_command_mode(self) -> None:
        now = time.perf_counter()
        self.command_mode_active = True
        self.command_mode_started_at = now
        self.command_mode_last_seen_at = now
        self.command_mode_last_command_at = None
        self.confirm_ready = True
        self.delete_ready = True
        self.clear_ready = True
        self.next_ready = True
        self.submit_ready = True
        self.pending_delete_started_at = None
        self.pending_clear_started_at = None
        self.reset_display_state()
        if self.command_recognizer is not None:
            self.command_recognizer.reset()

    def update_command_reentry_gate(self, hand_count: int) -> None:
        if hand_count < 2:
            self.command_reentry_requires_release = False

    def can_activate_command_mode(self, hand_count: int) -> bool:
        self.update_command_reentry_gate(hand_count)
        return hand_count >= 2 and not self.command_reentry_requires_release

    def update_command_mode(self, command_result: Dict[str, object]) -> None:
        if not self.command_mode_active:
            return

        now = time.perf_counter()
        hand_count = int(command_result.get("commandHandCount") or 0)
        command_gesture = str(command_result.get("commandGesture") or "").strip()

        if hand_count >= 2:
            self.command_mode_last_seen_at = now

        if command_gesture:
            self.command_mode_last_command_at = now

        no_two_hands_too_long = (
            self.command_mode_last_seen_at is None
            or now - self.command_mode_last_seen_at >= self.command_mode_timeout_seconds
        )
        no_command_too_long = (
            self.command_mode_last_command_at is None
            and self.command_mode_started_at is not None
            and now - self.command_mode_started_at >= self.command_mode_timeout_seconds
        )
        command_stale = (
            self.command_mode_last_command_at is not None
            and now - self.command_mode_last_command_at >= self.command_mode_timeout_seconds
        )

        if no_two_hands_too_long or no_command_too_long or command_stale:
            self.deactivate_command_mode()

    def deactivate_command_mode(self) -> None:
        self.command_mode_active = False
        self.command_mode_started_at = None
        self.command_mode_last_seen_at = None
        self.command_mode_last_command_at = None
        self.confirm_ready = True
        self.delete_ready = True
        self.clear_ready = True
        self.next_ready = True
        self.submit_ready = True
        self.pending_delete_started_at = None
        self.pending_clear_started_at = None
        if self.command_recognizer is not None:
            self.command_recognizer.reset()

    def apply_command_actions(self, command_result: Dict[str, object]) -> Dict[str, object]:
        metadata: Dict[str, object] = {
            "modeChangedByCommand": False,
            "actionPerformed": False,
            "actionType": "",
            "actionToast": "",
        }
        command_gesture = str(command_result.get("commandGesture") or "").strip()
        command_candidate = str(command_result.get("commandCandidate") or "").strip()
        now = time.perf_counter()

        if command_gesture != "CONFIRM" and command_candidate != "CONFIRM":
            self.confirm_ready = True

        if command_gesture != "DELETE" and command_candidate != "DELETE":
            self.delete_ready = True
            self.pending_delete_started_at = None

        if command_gesture != "CLEAR" and command_candidate != "CLEAR":
            self.clear_ready = True
            self.pending_clear_started_at = None

        if command_gesture != "NEXT" and command_candidate != "NEXT":
            self.next_ready = True

        if command_gesture != "SUBMIT" and command_candidate != "SUBMIT":
            self.submit_ready = True

        # --- CONFIRM: 选中当前高亮候选词 → 放入已接受词语 ---
        if command_gesture == "CONFIRM" and self.confirm_ready:
            self.confirm_ready = False
            confirmed_text = self.hanzi_candidate or self.raw_pinyin_buffer
            print(f"[CONFIRM] hanzi_candidate={self.hanzi_candidate!r}, candidate_index={self.candidate_index}, candidates={self.hanzi_candidates}, confirmed_text={confirmed_text!r}")
            if confirmed_text:
                self.command_reentry_requires_release = True
                self.reset_display_state(clear_cached=True)
                self.deactivate_command_mode()
                metadata["actionPerformed"] = True
                metadata["actionType"] = "CONFIRM"
                metadata["actionToast"] = confirmed_text
                return metadata

        # --- DELETE: 删掉 cached_buffer 最后一个字母 ---
        if command_candidate == "DELETE" and self.delete_ready:
            if self.pending_delete_started_at is None:
                self.pending_delete_started_at = now

            if now - self.pending_delete_started_at >= self.delete_hold_seconds:
                self.delete_ready = False
                self.pending_delete_started_at = None
                self.command_reentry_requires_release = True
                if self.cached_buffer:
                    self.cached_buffer = self.cached_buffer[:-1]
                self.last_cached_token = ""
                self.reset_display_state()
                self.deactivate_command_mode()
                metadata["actionPerformed"] = True
                metadata["actionType"] = "DELETE"
                metadata["actionToast"] = "Deleted"
                return metadata

        # --- CLEAR: 清空所有缓存 ---
        if command_candidate == "CLEAR" and self.clear_ready:
            if self.pending_clear_started_at is None:
                self.pending_clear_started_at = now

            if now - self.pending_clear_started_at >= self.clear_hold_seconds:
                self.clear_ready = False
                self.pending_clear_started_at = None
                self.command_reentry_requires_release = True
                self.reset_display_state(clear_cached=True)
                self.deactivate_command_mode()
                metadata["actionPerformed"] = True
                metadata["actionType"] = "CLEAR"
                metadata["actionToast"] = "Cleared"
                return metadata

        # --- NEXT: 切换到下一个候选词 ---
        if command_gesture == "NEXT" and self.next_ready:
            self.next_ready = False
            if self.hanzi_candidates and len(self.hanzi_candidates) > 1:
                self.candidate_index = (self.candidate_index + 1) % len(self.hanzi_candidates)
                self.hanzi_candidate = self.hanzi_candidates[self.candidate_index]
                metadata["actionPerformed"] = True
                metadata["actionType"] = "NEXT"
                metadata["actionToast"] = self.hanzi_candidate
                print(f"[NEXT] candidate_index={self.candidate_index}, hanzi_candidate={self.hanzi_candidate!r}")
            return metadata

        # --- SUBMIT: 提交整句到后端 AI 润色 ---
        if command_gesture == "SUBMIT" and self.submit_ready:
            self.submit_ready = False
            self.command_reentry_requires_release = True
            self.deactivate_command_mode()
            metadata["actionPerformed"] = True
            metadata["actionType"] = "SUBMIT"
            metadata["actionToast"] = ""
            return metadata

        return metadata

    def _command_candidate_progress(self, command_candidate: str, command_result: Dict) -> float:
        """计算当前候选手势的完成进度 [0.0, 1.0]。
        DELETE/CLEAR 为时间 hold 进度；CONFIRM/NEXT/SUBMIT 为帧计数/触发阈值比。
        """
        if not command_candidate:
            return 0.0
        now = time.perf_counter()
        if command_candidate == "DELETE":
            if self.pending_delete_started_at is None:
                return 0.0
            return min(1.0, (now - self.pending_delete_started_at) / max(self.delete_hold_seconds, 0.001))
        if command_candidate == "CLEAR":
            if self.pending_clear_started_at is None:
                return 0.0
            return min(1.0, (now - self.pending_clear_started_at) / max(self.clear_hold_seconds, 0.001))
        counters = dict(command_result.get("commandCounters") or {})
        if command_candidate == "SUBMIT":
            threshold = int(command_result.get("commandSubmitThreshold") or 0)
        else:
            threshold = int(command_result.get("commandThreshold") or 0)
        if threshold > 0:
            count = int(counters.get(command_candidate) or 0)
            # counter 归零说明刚触发，返回 1.0 避免进度条瞬间消失
            if count == 0 and str(command_result.get("commandGesture") or "") == command_candidate:
                return 1.0
            return min(1.0, count / threshold)
        return 0.0

    def build_command_result(
        self,
        command_result: Dict[str, object],
        image_shape,
        metadata: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        metadata = metadata or {}
        command_gesture = str(command_result.get("commandGesture") or "").strip()
        command_candidate = str(command_result.get("commandCandidate") or "").strip()
        display_text = command_gesture or command_candidate
        mode_changed = bool(metadata.get("modeChangedByCommand"))
        action_performed = bool(metadata.get("actionPerformed"))
        action_type = str(metadata.get("actionType") or "")

        if mode_changed or action_performed:
            display_text = ""

        # NEXT 只切换候选词高亮，不清空任何显示状态，
        # 否则 reset_display_state → _refresh_pinyin_state 会把
        # apply_command_actions 刚设好的 candidate_index 强制归零。
        is_next_action = action_type == "NEXT"
        should_reset = (mode_changed or action_performed) and not is_next_action
        should_suppress = mode_changed or action_performed

        return {
            "type": "result",
            "mode": self.mode,
            "engine": "mediapipe-command",
            "latencyMs": 0.0,
            "imageWidth": int(image_shape[1]),
            "imageHeight": int(image_shape[0]),
            "handCount": int(command_result.get("commandHandCount") or 0),
            "text": display_text,
            "hands": [],
            "commandModeActive": self.command_mode_active,
            "commandGesture": command_gesture,
            "commandHandCount": int(command_result.get("commandHandCount") or 0),
            "commandCandidate": command_candidate,
            "commandCounters": dict(command_result.get("commandCounters") or {}),
            "commandThreshold": int(command_result.get("commandThreshold") or 0),
            "commandCandidateProgress": self._command_candidate_progress(command_candidate, command_result),
            "modeChangedByCommand": mode_changed,
            "actionPerformed": action_performed,
            "actionType": action_type,
            "actionToast": str(metadata.get("actionToast") or ""),
            "resetDisplayState": should_reset,
            "suppressDisplayStateUpdate": should_suppress,
        }

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
        self.reset_display_state(clear_cached=True)
        if self.command_recognizer is not None:
            self.command_recognizer.close()
            self.command_recognizer = None
        if self.channel is not None and self.channel.readyState != "closed":
            self.channel.close()
        if self.pc.connectionState != "closed":
            await self.pc.close()

    def _update_cached_buffer(self, spelling_text: str) -> None:
        if not spelling_text:
            self.pending_stable_text = ""
            self.pending_stable_started_at = None
            self.last_cached_token = ""
            return

        now = time.perf_counter()

        if spelling_text != self.pending_stable_text:
            self.pending_stable_text = spelling_text
            self.pending_stable_started_at = now
            return

        if self.pending_stable_started_at is None:
            self.pending_stable_started_at = now
            return

        if self.last_cached_token == spelling_text:
            return

        if now - self.pending_stable_started_at < self.stable_token_duration_seconds:
            return

        self.cached_buffer += spelling_text
        self.last_cached_token = spelling_text

    def stability_progress(self) -> float:
        if not self.pending_stable_text or self.pending_stable_started_at is None:
            return 0.0
        elapsed = time.perf_counter() - self.pending_stable_started_at
        if self.stable_token_duration_seconds <= 0:
            return 1.0
        return round(min(1.0, max(0.0, elapsed / self.stable_token_duration_seconds)), 3)

    def _current_pinyin_buffer(self) -> str:
        current = self.cached_buffer
        if self.spelling_buffer and self.spelling_buffer != self.last_cached_token:
            current += self.spelling_buffer
        return current.lower()

    def _refresh_pinyin_state(self) -> None:
        self.raw_pinyin_buffer = self._current_pinyin_buffer()

        if not self.raw_pinyin_buffer:
            self.hanzi_candidate = ""
            self.hanzi_candidates = []
            self.candidate_index = 0
            return

        if self.mode == "digits":
            candidates = digits_to_candidates(self.raw_pinyin_buffer)
        else:
            candidates = self.pinyin_converter.convert_with_candidates(self.raw_pinyin_buffer, num=9)

        # 候选列表没有变化时（相同拼音 buffer 反复刷新），保留用户已切换的 candidate_index，
        # 避免每帧 update_display_state → _refresh_pinyin_state 把手动切换的高亮归零。
        # 只有候选列表真正改变（拼音变了）时才重置为 0。
        changed = candidates != self.hanzi_candidates
        if changed:
            print(f"[REFRESH] candidates CHANGED: old={self.hanzi_candidates}, new={candidates}, resetting index 0")
            self.hanzi_candidates = candidates
            self.candidate_index = 0
        else:
            # 列表不变：确保 index 没有越界
            if self.candidate_index >= len(candidates):
                self.candidate_index = 0

        self.hanzi_candidate = candidates[self.candidate_index] if candidates else ""
