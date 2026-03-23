import asyncio
from collections import deque
import json
import time
from typing import Deque, Dict, Optional, Set

from aiortc import RTCPeerConnection


class SessionState:
    def __init__(
        self,
        pc: RTCPeerConnection,
        mode: str,
        process_items_limit: int = 8,
        command_recognizer=None,
        command_mode_timeout_seconds: float = 2.5,
    ) -> None:
        self.pc = pc
        self.mode = mode if mode in ("digits", "letters") else "digits"
        self.command_recognizer = command_recognizer
        self.command_mode_timeout_seconds = command_mode_timeout_seconds
        self.channel = None
        self.track_tasks: Set[asyncio.Task] = set()
        self.latest_frame = None
        self.latest_frame_lock = asyncio.Lock()
        self.frame_ready = asyncio.Event()
        self.input_timestamps: Deque[float] = deque()
        self.processed_timestamps: Deque[float] = deque()
        self.process_items: Deque[str] = deque(maxlen=process_items_limit)
        self.spelling_buffer = ""
        self.command_mode_active = False
        self.command_mode_started_at: Optional[float] = None
        self.command_mode_last_seen_at: Optional[float] = None
        self.command_mode_last_command_at: Optional[float] = None

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
            self.reset_display_state()
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

    def update_display_state(self, result: Dict[str, object]) -> None:
        spelling_text = str(result.get("text") or "").strip()
        self.spelling_buffer = spelling_text

        hand_texts = []
        for hand in result.get("hands", []):
            if not isinstance(hand, dict):
                continue
            hand_text = str(hand.get("text") or "").strip()
            if hand_text:
                hand_texts.append(hand_text)

        if not hand_texts and spelling_text:
            hand_texts.append(spelling_text)

        for item in hand_texts:
            if not self.process_items or self.process_items[-1] != item:
                self.process_items.append(item)

    def display_snapshot(self) -> Dict[str, object]:
        return {
            "processItems": list(self.process_items),
            "spellingBuffer": self.spelling_buffer,
        }

    def reset_display_state(self) -> None:
        self.process_items.clear()
        self.spelling_buffer = ""

    def activate_command_mode(self) -> None:
        now = time.perf_counter()
        self.command_mode_active = True
        self.command_mode_started_at = now
        self.command_mode_last_seen_at = now
        self.command_mode_last_command_at = None
        self.reset_display_state()
        if self.command_recognizer is not None:
            self.command_recognizer.reset()

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
        if self.command_recognizer is not None:
            self.command_recognizer.reset()

    def build_command_result(self, command_result: Dict[str, object], image_shape) -> Dict[str, object]:
        return {
            "type": "result",
            "mode": self.mode,
            "engine": "mediapipe-command",
            "latencyMs": 0.0,
            "imageWidth": int(image_shape[1]),
            "imageHeight": int(image_shape[0]),
            "handCount": int(command_result.get("commandHandCount") or 0),
            "text": "",
            "hands": [],
            "commandModeActive": self.command_mode_active,
            "commandGesture": str(command_result.get("commandGesture") or ""),
            "commandHandCount": int(command_result.get("commandHandCount") or 0),
            "commandCandidate": str(command_result.get("commandCandidate") or ""),
            "commandCounters": dict(command_result.get("commandCounters") or {}),
            "commandThreshold": int(command_result.get("commandThreshold") or 0),
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
        self.reset_display_state()
        if self.command_recognizer is not None:
            self.command_recognizer.close()
            self.command_recognizer = None
        if self.channel is not None and self.channel.readyState != "closed":
            self.channel.close()
        if self.pc.connectionState != "closed":
            await self.pc.close()
