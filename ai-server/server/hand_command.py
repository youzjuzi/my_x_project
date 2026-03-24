import math
import time
from typing import Dict

import cv2
import mediapipe as mp


TRIGGER_THRESHOLD = 5
DISPLAY_HOLD_FRAMES = 12

COMMAND_CONFIRM = "CONFIRM"
COMMAND_DELETE = "DELETE"
COMMAND_CLEAR = "CLEAR"
COMMAND_ENTER = "ENTER"
COMMAND_SWITCH = "SWITCH"


class HandsCommandParser:
    def __init__(self, trigger_threshold: int = TRIGGER_THRESHOLD) -> None:
        self.trigger_threshold = trigger_threshold
        self.confirm_counter = 0
        self.delete_counter = 0
        self.clear_counter = 0
        self.enter_counter = 0
        self.switch_counter = 0

    def _get_palm_scale(self, hand_landmarks) -> float:
        """计算手腕(0)到中指根部(9)的欧氏距离，作为手掌基准尺度。"""
        wrist = hand_landmarks[0]
        mid_mcp = hand_landmarks[9]
        return math.hypot(mid_mcp.x - wrist.x, mid_mcp.y - wrist.y)

    def _is_full_open_palm(self, hand_landmarks) -> bool:
        palm_scale = self._get_palm_scale(hand_landmarks)
        fingers_up = all(
            hand_landmarks[i].y < hand_landmarks[i - 2].y
            for i in [8, 12, 16, 20]
        )
        is_spread = abs(hand_landmarks[8].x - hand_landmarks[20].x) > 0.75 * palm_scale
        return fingers_up and is_spread

    def _is_single_index_up(self, hand_landmarks) -> bool:
        palm_scale = self._get_palm_scale(hand_landmarks)
        index_up = hand_landmarks[8].y < hand_landmarks[6].y - 0.25 * palm_scale
        others_fisted = (
            hand_landmarks[12].y > hand_landmarks[10].y
            and hand_landmarks[16].y > hand_landmarks[14].y
            and hand_landmarks[20].y > hand_landmarks[18].y
        )
        is_highest = hand_landmarks[8].y < hand_landmarks[4].y
        return index_up and others_fisted and is_highest

    def _is_single_index_down(self, hand_landmarks) -> bool:
        palm_scale = self._get_palm_scale(hand_landmarks)
        index_down = hand_landmarks[8].y > hand_landmarks[6].y + 0.25 * palm_scale
        others_up = (
            hand_landmarks[12].y < hand_landmarks[8].y - 0.5 * palm_scale
            and hand_landmarks[16].y < hand_landmarks[8].y - 0.5 * palm_scale
            and hand_landmarks[20].y < hand_landmarks[8].y - 0.5 * palm_scale
        )
        return index_down and others_up

    def _is_single_fist(self, hand_landmarks) -> bool:
        palm_scale = self._get_palm_scale(hand_landmarks)
        return (
            hand_landmarks[8].y > hand_landmarks[5].y + 0.25 * palm_scale
            and hand_landmarks[12].y > hand_landmarks[9].y + 0.25 * palm_scale
            and hand_landmarks[16].y > hand_landmarks[13].y + 0.25 * palm_scale
            and hand_landmarks[20].y > hand_landmarks[17].y + 0.25 * palm_scale
        )

    def _is_single_thumb_up(self, hand_landmarks) -> bool:
        thumb_is_up = (
            hand_landmarks[4].y < hand_landmarks[3].y
            and hand_landmarks[4].y < hand_landmarks[5].y
        )
        index_is_folded = hand_landmarks[8].y > hand_landmarks[6].y
        middle_is_folded = hand_landmarks[12].y > hand_landmarks[10].y
        ring_is_folded = hand_landmarks[16].y > hand_landmarks[14].y
        pinky_is_folded = hand_landmarks[20].y > hand_landmarks[18].y
        return (
            thumb_is_up
            and index_is_folded
            and middle_is_folded
            and ring_is_folded
            and pinky_is_folded
        )

    def reset(self) -> None:
        self.confirm_counter = 0
        self.delete_counter = 0
        self.clear_counter = 0
        self.enter_counter = 0
        self.switch_counter = 0

    def snapshot(self) -> Dict[str, int]:
        return {
            COMMAND_CONFIRM: self.confirm_counter,
            COMMAND_DELETE: self.delete_counter,
            COMMAND_CLEAR: self.clear_counter,
            COMMAND_ENTER: self.enter_counter,
            COMMAND_SWITCH: self.switch_counter,
        }

    def detect_candidate(self, multi_hand_landmarks) -> str:
        if len(multi_hand_landmarks) != 2:
            return ""

        hand1, hand2 = multi_hand_landmarks[0], multi_hand_landmarks[1]

        if self._is_full_open_palm(hand1) and self._is_full_open_palm(hand2):
            return COMMAND_CONFIRM
        if self._is_single_index_down(hand1) and self._is_single_index_down(hand2):
            return COMMAND_DELETE
        if self._is_single_fist(hand1) and self._is_single_fist(hand2):
            return COMMAND_CLEAR
        if self._is_single_thumb_up(hand1) and self._is_single_thumb_up(hand2):
            return COMMAND_ENTER
        if self._is_single_index_up(hand1) and self._is_single_index_up(hand2):
            return COMMAND_SWITCH
        return ""

    def detect_command(self, multi_hand_landmarks) -> str:
        candidate = self.detect_candidate(multi_hand_landmarks)
        if not candidate:
            self.reset()
            return ""

        if candidate == COMMAND_CONFIRM:
            self.confirm_counter += 1
            if self.confirm_counter >= self.trigger_threshold:
                self.confirm_counter = 0
                return COMMAND_CONFIRM
        elif candidate == COMMAND_DELETE:
            self.delete_counter += 1
            if self.delete_counter >= self.trigger_threshold:
                self.delete_counter = 0
                return COMMAND_DELETE
        elif candidate == COMMAND_CLEAR:
            self.clear_counter += 1
            if self.clear_counter >= self.trigger_threshold:
                self.clear_counter = 0
                return COMMAND_CLEAR
        elif candidate == COMMAND_ENTER:
            self.enter_counter += 1
            if self.enter_counter >= self.trigger_threshold:
                self.enter_counter = 0
                return COMMAND_ENTER
        elif candidate == COMMAND_SWITCH:
            self.switch_counter += 1
            if self.switch_counter >= self.trigger_threshold:
                self.switch_counter = 0
                return COMMAND_SWITCH

        for name in self.snapshot():
            if name != candidate:
                if name == COMMAND_CONFIRM:
                    self.confirm_counter = 0
                elif name == COMMAND_DELETE:
                    self.delete_counter = 0
                elif name == COMMAND_CLEAR:
                    self.clear_counter = 0
                elif name == COMMAND_ENTER:
                    self.enter_counter = 0
                elif name == COMMAND_SWITCH:
                    self.switch_counter = 0
        return ""


class HandCommandRecognizer:
    def __init__(self, model_path: str) -> None:
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.35,
            min_hand_presence_confidence=0.30,
            min_tracking_confidence=0.30,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.parser = HandsCommandParser()
        self.start_time = time.monotonic()
        self._hold_frames = 0
        self._last_command = ""

    def process_frame(self, frame) -> Dict[str, object]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.monotonic() - self.start_time) * 1000)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        multi_hand_landmarks = result.hand_landmarks or []

        candidate = self.parser.detect_candidate(multi_hand_landmarks)
        command = self.parser.detect_command(multi_hand_landmarks)
        if command:
            self._last_command = command
            self._hold_frames = DISPLAY_HOLD_FRAMES
        elif self._hold_frames > 0:
            self._hold_frames -= 1
        else:
            self._last_command = ""

        return {
            "commandGesture": self._last_command,
            "commandHandCount": len(multi_hand_landmarks),
            "commandCandidate": candidate,
            "commandCounters": self.parser.snapshot(),
            "commandThreshold": self.parser.trigger_threshold,
        }

    def reset(self) -> None:
        self.parser.reset()
        self._hold_frames = 0
        self._last_command = ""

    def close(self) -> None:
        self.landmarker.close()
