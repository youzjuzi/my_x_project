import math
import time
from typing import Dict

import cv2
import mediapipe as mp


TRIGGER_THRESHOLD = 15
DISPLAY_HOLD_FRAMES = 12

COMMAND_CONFIRM = "CONFIRM"
COMMAND_DELETE = "DELETE"
COMMAND_CLEAR = "CLEAR"
COMMAND_NEXT = "NEXT"
COMMAND_SUBMIT = "SUBMIT"


class HandsCommandParser:
    def __init__(self, trigger_threshold: int = TRIGGER_THRESHOLD, submit_trigger_threshold: int = 40, confirm_trigger_threshold: int = 35, miss_tolerance: int = 8, switch_tolerance: int = 5) -> None:
        self.trigger_threshold = trigger_threshold
        self.submit_trigger_threshold = submit_trigger_threshold
        self.confirm_trigger_threshold = confirm_trigger_threshold
        # miss_tolerance: 手势「消失/丢失」时，允许连续丢失多少帧才清空进度（用于处理识别掉帧）
        self.miss_tolerance = miss_tolerance
        # switch_tolerance: 手势「切换」时，允许多少帧的过渡缓冲才重置（用于处理换手势时的抖动）
        self.switch_tolerance = switch_tolerance
        self.confirm_counter = 0
        self.delete_counter = 0
        self.clear_counter = 0
        self.next_counter = 0
        self.submit_counter = 0
        self._miss_counter = 0
        self._switch_miss_counter = 0
        self._last_candidate = ""

    def _get_palm_scale(self, hand_landmarks) -> float:
        """计算手腕(0)到中指根部(9)的欧氏距离，作为手掌基准尺度。"""
        wrist = hand_landmarks[0]
        mid_mcp = hand_landmarks[9]
        return math.hypot(mid_mcp.x - wrist.x, mid_mcp.y - wrist.y)

    def _is_full_open_palm(self, hand_landmarks) -> bool:
        palm_scale = self._get_palm_scale(hand_landmarks)
        wrist = hand_landmarks[0]
        
        # 优化1：使用距离替代绝对的 Y 轴坐标，实现旋转不变性 (无论手朝向哪里都能识别)
        fingers_up = all(
            math.hypot(hand_landmarks[i].x - wrist.x, hand_landmarks[i].y - wrist.y) >
            math.hypot(hand_landmarks[i - 2].x - wrist.x, hand_landmarks[i - 2].y - wrist.y)
            for i in [8, 12, 16, 20]
        )
        
        # 优化2：稍微放宽“间距” (spread) 的要求，0.65 对部分用户偏严苛，改为 0.45，手指即便稍微并拢也能识别
        spread_dist = math.hypot(
            hand_landmarks[8].x - hand_landmarks[20].x,
            hand_landmarks[8].y - hand_landmarks[20].y,
        )
        is_spread = spread_dist > 0.45 * palm_scale
        
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
        wrist = hand_landmarks[0]
        
        def dist(idx):
            return math.hypot(hand_landmarks[idx].x - wrist.x, hand_landmarks[idx].y - wrist.y)
            
        # 判断其余四指是否收拢（指尖距离手腕的距离 < 第一指节离手腕的距离，这在任意旋转角度下都成立）
        index_folded = dist(8) < dist(6)
        middle_folded = dist(12) < dist(10)
        ring_folded = dist(16) < dist(14)
        pinky_folded = dist(20) < dist(18)
        
        # 拇指是否伸直
        thumb_extended = dist(4) > dist(3)
        
        # 拇指是否是向上的（拇指尖 y 最小）
        thumb_tip_y = hand_landmarks[4].y
        is_highest = all(thumb_tip_y < hand_landmarks[i].y for i in [8, 12, 16, 20])
        
        return (
            is_highest
            and thumb_extended
            and index_folded
            and middle_folded
            and ring_folded
            and pinky_folded
        )

    def reset(self) -> None:
        self.confirm_counter = 0
        self.delete_counter = 0
        self.clear_counter = 0
        self.next_counter = 0
        self.submit_counter = 0
        self._miss_counter = 0
        self._switch_miss_counter = 0
        self._last_candidate = ""

    def snapshot(self) -> Dict[str, int]:
        return {
            COMMAND_CONFIRM: self.confirm_counter,
            COMMAND_DELETE: self.delete_counter,
            COMMAND_CLEAR: self.clear_counter,
            COMMAND_NEXT: self.next_counter,
            COMMAND_SUBMIT: self.submit_counter,
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
        if self._is_single_index_up(hand1) and self._is_single_index_up(hand2):
            return COMMAND_NEXT
        if self._is_single_thumb_up(hand1) and self._is_single_thumb_up(hand2):
            return COMMAND_SUBMIT
        return ""

    def detect_command(self, multi_hand_landmarks) -> str:
        candidate = self.detect_candidate(multi_hand_landmarks)

        # 情况1：没有检测到任何手势（掉帧/遮挡）
        # 使用较大的 miss_tolerance，不轻易清空已有进度
        if not candidate:
            self._miss_counter += 1
            self._switch_miss_counter = 0
            if self._miss_counter > self.miss_tolerance:
                self.reset()
            return ""

        # 情况2：检测到的手势与上一帧不同（手势切换）
        # 使用较小的 switch_tolerance，切换时较快重置，防止串台
        if self._last_candidate and candidate != self._last_candidate:
            self._switch_miss_counter += 1
            self._miss_counter = 0  # 有手势，不计丢失帧
            if self._switch_miss_counter > self.switch_tolerance:
                # 超过切换容错期，确实在换手势，重置进度
                self.reset()
                self._last_candidate = candidate
                self._switch_miss_counter = 0
            # 在容错期内（单帧识别抖动），暂停输出但不清空进度
            return ""

        # 情况3：手势连续或第一次检测到，正常累加
        self._last_candidate = candidate
        self._miss_counter = 0
        self._switch_miss_counter = 0

        # 进度条累加逻辑
        if candidate == COMMAND_CONFIRM:
            self.confirm_counter += 1
            if self.confirm_counter >= self.confirm_trigger_threshold:
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
        elif candidate == COMMAND_NEXT:
            self.next_counter += 1
            if self.next_counter >= self.trigger_threshold:
                self.next_counter = 0
                return COMMAND_NEXT
        elif candidate == COMMAND_SUBMIT:
            self.submit_counter += 1
            if self.submit_counter >= self.submit_trigger_threshold:
                self.submit_counter = 0
                return COMMAND_SUBMIT

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
        self._last_timestamp_ms = -1
        self._hold_frames = 0
        self._last_command = ""

    def process_frame(self, frame) -> Dict[str, object]:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        # 确保时间戳严格单调递增
        timestamp_ms = int((time.monotonic() - self.start_time) * 1000)
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        
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
            "commandSubmitThreshold": self.parser.submit_trigger_threshold,
            "commandConfirmThreshold": self.parser.confirm_trigger_threshold,
        }

    def reset(self) -> None:
        self.parser.reset()
        self._hold_frames = 0
        self._last_command = ""

    def close(self) -> None:
        self.landmarker.close()
