import time
from pathlib import Path

import cv2
import mediapipe as mp


MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")
WINDOW_NAME = "Hand Commands"
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 900

NUM_HANDS = 2
MIN_HAND_DETECTION_CONFIDENCE = 0.35
MIN_HAND_PRESENCE_CONFIDENCE = 0.30
MIN_TRACKING_CONFIDENCE = 0.30

TRIGGER_THRESHOLD = 3
COMMAND_HOLD_FRAMES = 15

COMMAND_CONFIRM = "CONFIRM"
COMMAND_DELETE = "DELETE"
COMMAND_CLEAR = "CLEAR"
COMMAND_ENTER = "ENTER"
COMMAND_SWITCH = "SWITCH"

HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)


def _open_camera(index: int = 0):
    backends = []
    if hasattr(cv2, "CAP_DSHOW"):
        backends.append(cv2.CAP_DSHOW)
    backends.append(cv2.CAP_ANY)

    for backend in backends:
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            return cap
        cap.release()

    raise RuntimeError("Cannot open camera 0 with available OpenCV backends.")


class HandsCommandParser:
    def __init__(self, trigger_threshold: int = TRIGGER_THRESHOLD) -> None:
        self.trigger_threshold = trigger_threshold
        self.confirm_counter = 0
        self.delete_counter = 0
        self.clear_counter = 0
        self.enter_counter = 0
        self.switch_counter = 0

    def _is_open_palm(self, hand_landmarks) -> bool:
        return (
            hand_landmarks[8].y < hand_landmarks[6].y
            and hand_landmarks[12].y < hand_landmarks[10].y
            and hand_landmarks[16].y < hand_landmarks[14].y
            and hand_landmarks[20].y < hand_landmarks[18].y
        )

    def _is_full_open_palm(self, hand_landmarks) -> bool:
        fingers_up = all(
            hand_landmarks[i].y < hand_landmarks[i - 2].y
            for i in [8, 12, 16, 20]
        )
        is_spread = abs(hand_landmarks[8].x - hand_landmarks[20].x) > 0.15
        return fingers_up and is_spread

    def _is_single_index_up(self, hand_landmarks) -> bool:
        index_up = hand_landmarks[8].y < hand_landmarks[6].y - 0.05
        others_fisted = (
            hand_landmarks[12].y > hand_landmarks[10].y
            and hand_landmarks[16].y > hand_landmarks[14].y
            and hand_landmarks[20].y > hand_landmarks[18].y
        )
        is_highest = hand_landmarks[8].y < hand_landmarks[4].y
        return index_up and others_fisted and is_highest

    def _is_single_index_down(self, hand_landmarks) -> bool:
        index_down = hand_landmarks[8].y > hand_landmarks[6].y + 0.05
        others_up = (
            hand_landmarks[12].y < hand_landmarks[8].y - 0.1
            and hand_landmarks[16].y < hand_landmarks[8].y - 0.1
            and hand_landmarks[20].y < hand_landmarks[8].y - 0.1
        )
        return index_down and others_up

    def _is_single_fist(self, hand_landmarks) -> bool:
        return (
            hand_landmarks[8].y > hand_landmarks[5].y + 0.05
            and hand_landmarks[12].y > hand_landmarks[9].y + 0.05
            and hand_landmarks[16].y > hand_landmarks[13].y + 0.05
            and hand_landmarks[20].y > hand_landmarks[17].y + 0.05
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

    def snapshot(self):
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


def _build_landmarker_options():
    base_options = mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH))
    return mp.tasks.vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=NUM_HANDS,
        min_hand_detection_confidence=MIN_HAND_DETECTION_CONFIDENCE,
        min_hand_presence_confidence=MIN_HAND_PRESENCE_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    )


def _draw_hand(frame, landmarks):
    frame_h, frame_w = frame.shape[:2]
    points = []

    for landmark in landmarks:
        x = int(landmark.x * frame_w)
        y = int(landmark.y * frame_h)
        points.append((x, y))

    for start_idx, end_idx in HAND_CONNECTIONS:
        cv2.line(frame, points[start_idx], points[end_idx], (75, 210, 135), 2)

    for x, y in points:
        cv2.circle(frame, (x, y), 4, (20, 110, 255), -1)

    return points


def _draw_centers(frame, points_a, points_b):
    if not points_a or not points_b:
        return
    center_a = points_a[9]
    center_b = points_b[9]
    cv2.line(frame, center_a, center_b, (78, 170, 255), 2)
    cv2.circle(frame, center_a, 8, (78, 170, 255), 2)
    cv2.circle(frame, center_b, 8, (78, 170, 255), 2)


def _draw_header(frame, detected_hands, candidate, counters, triggered):
    counter_text = " ".join(
        f"{name}:{value}/{TRIGGER_THRESHOLD}"
        for name, value in counters.items()
    )
    status_text = triggered or "Waiting for command"
    info_text = f"Hands: {detected_hands}  Candidate: {candidate or '-'}  {counter_text}"

    cv2.rectangle(frame, (16, 16), (1180, 120), (18, 28, 24), -1)
    cv2.putText(
        frame,
        status_text,
        (30, 56),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (244, 250, 247) if triggered else (214, 233, 224),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        info_text,
        (30, 92),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (156, 193, 177),
        2,
        cv2.LINE_AA,
    )


def _draw_banner(frame, text: str):
    frame_w = frame.shape[1]
    center_x = frame_w // 2
    cv2.rectangle(frame, (center_x - 220, 28), (center_x + 220, 104), (92, 148, 232), -1)
    cv2.putText(
        frame,
        text,
        (center_x - 120, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.45,
        (250, 255, 252),
        3,
        cv2.LINE_AA,
    )


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    cap = _open_camera(0)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

    parser = HandsCommandParser()
    hold_frames = 0
    last_command = ""
    start_time = time.monotonic()
    options = _build_landmarker_options()

    with mp.tasks.vision.HandLandmarker.create_from_options(options) as landmarker:
        while True:
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("Camera frame capture failed.")

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int((time.monotonic() - start_time) * 1000)

            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            multi_hand_landmarks = result.hand_landmarks or []

            drawn_points = []
            for hand_landmarks in multi_hand_landmarks:
                drawn_points.append(_draw_hand(frame, hand_landmarks))

            if len(drawn_points) == 2:
                _draw_centers(frame, drawn_points[0], drawn_points[1])

            candidate = parser.detect_candidate(multi_hand_landmarks)
            triggered = parser.detect_command(multi_hand_landmarks)

            if triggered:
                last_command = triggered
                hold_frames = COMMAND_HOLD_FRAMES
            elif hold_frames > 0:
                hold_frames -= 1
            else:
                last_command = ""

            _draw_header(
                frame,
                detected_hands=len(multi_hand_landmarks),
                candidate=candidate,
                counters=parser.snapshot(),
                triggered=last_command,
            )

            if last_command:
                _draw_banner(frame, last_command)

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (220, 230, 225),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
