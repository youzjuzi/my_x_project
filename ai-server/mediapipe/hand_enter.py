import time
from pathlib import Path

import cv2
import mediapipe as mp


MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")
WINDOW_NAME = "Hand Enter"
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 900

NUM_HANDS = 2
MIN_HAND_DETECTION_CONFIDENCE = 0.35
MIN_HAND_PRESENCE_CONFIDENCE = 0.30
MIN_TRACKING_CONFIDENCE = 0.30

TRIGGER_THRESHOLD = 3
ENTER_HOLD_FRAMES = 15
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)


class HandsCommandParser:
    def __init__(self, trigger_threshold: int = TRIGGER_THRESHOLD):
        self.enter_counter = 0
        self.trigger_threshold = trigger_threshold

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
        cv2.line(frame, points[start_idx], points[end_idx], (70, 220, 120), 2)

    for x, y in points:
        cv2.circle(frame, (x, y), 4, (28, 115, 255), -1)


def _draw_header(frame, detected_hands: int, counter: int, triggered: bool):
    status_text = "ENTER triggered" if triggered else "Waiting for double thumbs up"
    info_text = f"Hands: {detected_hands}  Counter: {counter}/{TRIGGER_THRESHOLD}"

    cv2.rectangle(frame, (16, 16), (540, 120), (18, 28, 24), -1)
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
        0.72,
        (156, 193, 177),
        2,
        cv2.LINE_AA,
    )


def _draw_enter_banner(frame):
    frame_h, frame_w = frame.shape[:2]
    center_x = frame_w // 2
    cv2.rectangle(
        frame,
        (center_x - 190, 28),
        (center_x + 190, 104),
        (64, 170, 88),
        -1,
    )
    cv2.putText(
        frame,
        "ENTER",
        (center_x - 115, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.6,
        (250, 255, 252),
        3,
        cv2.LINE_AA,
    )


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera 0.")

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

    parser = HandsCommandParser()
    enter_hold = 0
    start_time = time.monotonic()
    options = _build_landmarker_options()

    with mp.tasks.vision.HandLandmarker.create_from_options(options) as landmarker:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int((time.monotonic() - start_time) * 1000)

            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            multi_hand_landmarks = result.hand_landmarks or []

            for hand_landmarks in multi_hand_landmarks:
                _draw_hand(frame, hand_landmarks)

            triggered = parser.check_enter_command(multi_hand_landmarks)
            if triggered:
                enter_hold = ENTER_HOLD_FRAMES
            elif enter_hold > 0:
                enter_hold -= 1

            _draw_header(
                frame,
                detected_hands=len(multi_hand_landmarks),
                counter=parser.enter_counter,
                triggered=enter_hold > 0,
            )

            if enter_hold > 0:
                _draw_enter_banner(frame)

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
