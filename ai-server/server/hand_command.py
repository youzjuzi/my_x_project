import math
import time
from typing import Dict

import cv2
import mediapipe as mp


TRIGGER_THRESHOLD = 3
PROXIMITY_THRESHOLD = 0.25
DISPLAY_HOLD_FRAMES = 12

COMMAND_ENTER = "ENTER"
COMMAND_CONFIRM = "CONFIRM"
COMMAND_DELETE = "DELETE"
COMMAND_CLEAR = "CLEAR"
COMMAND_SWITCH = "SWITCH"


class HandsCommandParser:
    def __init__(self, trigger_threshold: int = TRIGGER_THRESHOLD) -> None:
        self.trigger_threshold = trigger_threshold
        self.confirm_counter = 0
        self.enter_counter = 0
        self.backspace_counter = 0
        self.clear_counter = 0
        self.switch_mode_counter = 0

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

    def _is_full_open_palm(self, hand_landmarks) -> bool:
        thumb_is_up = hand_landmarks[4].y < hand_landmarks[3].y
        index_is_up = hand_landmarks[8].y < hand_landmarks[6].y
        middle_is_up = hand_landmarks[12].y < hand_landmarks[10].y
        ring_is_up = hand_landmarks[16].y < hand_landmarks[14].y
        pinky_is_up = hand_landmarks[20].y < hand_landmarks[18].y
        is_spread = abs(hand_landmarks[8].x - hand_landmarks[20].x) > 0.1
        return (
            thumb_is_up
            and index_is_up
            and middle_is_up
            and ring_is_up
            and pinky_is_up
            and is_spread
        )

    def _is_single_index_down(self, hand_landmarks) -> bool:
        index_is_down = (
            hand_landmarks[8].y > hand_landmarks[6].y
            and hand_landmarks[6].y > hand_landmarks[5].y
        )
        others_are_higher = (
            hand_landmarks[12].y < hand_landmarks[8].y - 0.05
            and hand_landmarks[16].y < hand_landmarks[8].y - 0.05
            and hand_landmarks[20].y < hand_landmarks[8].y - 0.05
        )
        return index_is_down and others_are_higher

    def _is_single_fist(self, hand_landmarks) -> bool:
        # 增加一个偏移量 0.05，确保手指是彻底折叠的
        index_is_folded = hand_landmarks[8].y > hand_landmarks[5].y + 0.05
        middle_is_folded = hand_landmarks[12].y > hand_landmarks[9].y + 0.05
        ring_is_folded = hand_landmarks[16].y > hand_landmarks[13].y + 0.05
        pinky_is_folded = hand_landmarks[20].y > hand_landmarks[17].y + 0.05
        # 拇指也需要更严格的判定
        thumb_is_folded = hand_landmarks[4].x > hand_landmarks[2].x # 假设是右手
        return index_is_folded and middle_is_folded and ring_is_folded and pinky_is_folded

    def _is_open_palm(self, hand_landmarks) -> bool:
        index_is_up = hand_landmarks[8].y < hand_landmarks[6].y
        middle_is_up = hand_landmarks[12].y < hand_landmarks[10].y
        ring_is_up = hand_landmarks[16].y < hand_landmarks[14].y
        pinky_is_up = hand_landmarks[20].y < hand_landmarks[18].y
        return index_is_up and middle_is_up and ring_is_up and pinky_is_up

    def _get_hand_orientation(self, hand_landmarks) -> str:
        dx = hand_landmarks[12].x - hand_landmarks[0].x
        dy = hand_landmarks[12].y - hand_landmarks[0].y

        if abs(dx) < 1e-6:
            dx = 1e-6
        if abs(dy) < 1e-6:
            dy = 1e-6

        if abs(dy) / abs(dx) > 1.5:
            return "vertical"
        if abs(dx) / abs(dy) > 1.5:
            return "horizontal"
        return "unknown"

    def check_enter_command(self, multi_hand_landmarks) -> bool:
        if not multi_hand_landmarks or len(multi_hand_landmarks) != 2:
            self.enter_counter = 0
            return False

        hand1 = multi_hand_landmarks[0]
        hand2 = multi_hand_landmarks[1]
        if self._is_single_thumb_up(hand1) and self._is_single_thumb_up(hand2):
            self.enter_counter += 1
            if self.enter_counter >= self.trigger_threshold:
                self.enter_counter = 0
                return True
        else:
            self.enter_counter = 0
        return False

    def check_confirm_command(self, multi_hand_landmarks) -> bool:
        if not multi_hand_landmarks or len(multi_hand_landmarks) != 2:
            self.confirm_counter = 0
            return False

        hand1 = multi_hand_landmarks[0]
        hand2 = multi_hand_landmarks[1]
        if self._is_full_open_palm(hand1) and self._is_full_open_palm(hand2):
            self.confirm_counter += 1
            if self.confirm_counter >= self.trigger_threshold:
                self.confirm_counter = 0
                return True
        else:
            self.confirm_counter = 0
        return False

    def check_backspace_command(self, multi_hand_landmarks) -> bool:
        if not multi_hand_landmarks or len(multi_hand_landmarks) != 2:
            self.backspace_counter = 0
            return False

        hand1 = multi_hand_landmarks[0]
        hand2 = multi_hand_landmarks[1]
        if self._is_single_index_down(hand1) and self._is_single_index_down(hand2):
            self.backspace_counter += 1
            if self.backspace_counter >= self.trigger_threshold:
                self.backspace_counter = 0
                return True
        else:
            self.backspace_counter = 0
        return False

    def check_clear_all_command(self, multi_hand_landmarks) -> bool:
        if not multi_hand_landmarks or len(multi_hand_landmarks) != 2:
            self.clear_counter = 0
            return False

        hand1 = multi_hand_landmarks[0]
        hand2 = multi_hand_landmarks[1]
        if self._is_single_fist(hand1) and self._is_single_fist(hand2):
            self.clear_counter += 1
            if self.clear_counter >= self.trigger_threshold:
                self.clear_counter = 0
                return True
        else:
            self.clear_counter = 0
        return False

    def check_switch_mode_command(self, multi_hand_landmarks) -> bool:
        if not multi_hand_landmarks or len(multi_hand_landmarks) != 2:
            self.switch_mode_counter = 0
            return False

        hand1 = multi_hand_landmarks[0]
        hand2 = multi_hand_landmarks[1]
        if not (self._is_open_palm(hand1) and self._is_open_palm(hand2)):
            self.switch_mode_counter = 0
            return False

        ori1 = self._get_hand_orientation(hand1)
        ori2 = self._get_hand_orientation(hand2)
        is_t_shape = (
            (ori1 == "vertical" and ori2 == "horizontal")
            or (ori1 == "horizontal" and ori2 == "vertical")
        )

        if is_t_shape:
            center_dx = hand1[9].x - hand2[9].x
            center_dy = hand1[9].y - hand2[9].y
            distance = math.hypot(center_dx, center_dy)
            if distance < PROXIMITY_THRESHOLD:
                self.switch_mode_counter += 1
                if self.switch_mode_counter >= self.trigger_threshold:
                    self.switch_mode_counter = 0
                    return True
            else:
                self.switch_mode_counter = 0
        else:
            self.switch_mode_counter = 0
        return False

    def reset(self) -> None:
        self.confirm_counter = 0
        self.enter_counter = 0
        self.backspace_counter = 0
        self.clear_counter = 0
        self.switch_mode_counter = 0

    def snapshot(self) -> Dict[str, int]:
        return {
            "CONFIRM": self.confirm_counter,
            "ENTER": self.enter_counter,
            "DELETE": self.backspace_counter,
            "CLEAR": self.clear_counter,
            "SWITCH": self.switch_mode_counter,
        }


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

        candidate = self._detect_candidate(multi_hand_landmarks)
        command = self._detect_command(multi_hand_landmarks)
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

    def _detect_candidate(self, multi_hand_landmarks) -> str:
        if not multi_hand_landmarks or len(multi_hand_landmarks) != 2:
            return ""

        hand1 = multi_hand_landmarks[0]
        hand2 = multi_hand_landmarks[1]

        if self.parser._is_full_open_palm(hand1) and self.parser._is_full_open_palm(hand2):
            return COMMAND_CONFIRM

        if self.parser._is_single_index_down(hand1) and self.parser._is_single_index_down(hand2):
            return COMMAND_DELETE

        if self.parser._is_single_fist(hand1) and self.parser._is_single_fist(hand2):
            return COMMAND_CLEAR

        if self.parser._is_single_thumb_up(hand1) and self.parser._is_single_thumb_up(hand2):
            return COMMAND_ENTER

        if self.parser._is_open_palm(hand1) and self.parser._is_open_palm(hand2):
            ori1 = self.parser._get_hand_orientation(hand1)
            ori2 = self.parser._get_hand_orientation(hand2)
            is_t_shape = (
                (ori1 == "vertical" and ori2 == "horizontal")
                or (ori1 == "horizontal" and ori2 == "vertical")
            )
            if is_t_shape:
                center_dx = hand1[9].x - hand2[9].x
                center_dy = hand1[9].y - hand2[9].y
                if math.hypot(center_dx, center_dy) < PROXIMITY_THRESHOLD:
                    return COMMAND_SWITCH

        return ""

    def reset(self) -> None:
        self.parser.reset()
        self._hold_frames = 0
        self._last_command = ""

    def _detect_command(self, multi_hand_landmarks) -> str:
        if self.parser.check_confirm_command(multi_hand_landmarks):
            return COMMAND_CONFIRM
        if self.parser.check_enter_command(multi_hand_landmarks):
            return COMMAND_ENTER
        if self.parser.check_backspace_command(multi_hand_landmarks):
            return COMMAND_DELETE
        if self.parser.check_clear_all_command(multi_hand_landmarks):
            return COMMAND_CLEAR
        if self.parser.check_switch_mode_command(multi_hand_landmarks):
            return COMMAND_SWITCH
        return ""

    def close(self) -> None:
        self.landmarker.close()
