import asyncio
from collections import Counter, deque
import json
import time
from typing import Deque, Dict, Optional, Set

from aiortc import RTCPeerConnection


class BaseSession:
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
        action_suppression_seconds: float = 1.5,
    ) -> None:
        self.pc = pc
        self.mode = mode if mode in ("digits", "letters") else "letters"
        self.command_recognizer = command_recognizer
        self.command_mode_timeout_seconds = command_mode_timeout_seconds
        self.switch_min_interval_seconds = switch_min_interval_seconds
        self.stable_token_duration_seconds = stable_token_duration_seconds
        self.delete_hold_seconds = delete_hold_seconds
        self.clear_hold_seconds = clear_hold_seconds
        self.action_suppression_seconds = action_suppression_seconds

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

        self.pending_stable_text = ""
        self.pending_stable_started_at: Optional[float] = None
        self.last_cached_token = ""
        self.action_suppression_until: Optional[float] = None

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

    def _is_in_action_suppression(self) -> bool:
        if self.action_suppression_until is None:
            return False
        if time.perf_counter() < self.action_suppression_until:
            return True
        self.action_suppression_until = None
        return False

    def _start_action_suppression(self) -> None:
        self.action_suppression_until = time.perf_counter() + self.action_suppression_seconds

    def _compute_vote_winner(self, min_ratio: float = 0.45) -> str:
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
        raise NotImplementedError

    def display_snapshot(self) -> Dict[str, object]:
        raise NotImplementedError

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
        raise NotImplementedError

    def _command_candidate_progress(self, command_candidate: str, command_result: Dict) -> float:
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
        elif command_candidate == "CONFIRM":
            threshold = int(command_result.get("commandConfirmThreshold") or 0)
        else:
            threshold = int(command_result.get("commandThreshold") or 0)
        if threshold > 0:
            count = int(counters.get(command_candidate) or 0)
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
        raise NotImplementedError
