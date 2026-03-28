import time
from pathlib import Path

import cv2
import mediapipe as mp


MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")
WINDOW_NAME = "Hand Landmarks Viewer"
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 900

NUM_HANDS = 2
MIN_HAND_DETECTION_CONFIDENCE = 0.35
MIN_HAND_PRESENCE_CONFIDENCE = 0.30
MIN_TRACKING_CONFIDENCE = 0.30

HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)

KEY_POINT_LABELS = {
    0: "0 wrist",
    4: "4 thumb_tip",
    5: "5 index_mcp",
    8: "8 index_tip",
    9: "9 middle_mcp",
    12: "12 middle_tip",
    13: "13 ring_mcp",
    16: "16 ring_tip",
    17: "17 pinky_mcp",
    20: "20 pinky_tip",
}


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


def _to_pixel_point(landmark, frame_w: int, frame_h: int):
    x = int(landmark.x * frame_w)
    y = int(landmark.y * frame_h)
    return x, y


def _draw_hand(frame, landmarks, handedness_text: str, hand_index: int):
    frame_h, frame_w = frame.shape[:2]
    points = [_to_pixel_point(landmark, frame_w, frame_h) for landmark in landmarks]

    for start_idx, end_idx in HAND_CONNECTIONS:
        cv2.line(frame, points[start_idx], points[end_idx], (90, 220, 150), 2)

    for idx, (x, y) in enumerate(points):
        is_key_point = idx in KEY_POINT_LABELS
        point_color = (30, 110, 255) if is_key_point else (235, 220, 70)
        radius = 6 if is_key_point else 4

        cv2.circle(frame, (x, y), radius, point_color, -1)
        cv2.circle(frame, (x, y), radius + 2, (20, 20, 20), 1)

        label = KEY_POINT_LABELS.get(idx, str(idx))
        label_x = min(x + 10, frame_w - 170)
        label_y = max(y - 10, 24)

        cv2.putText(
            frame,
            label,
            (label_x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            label,
            (label_x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (20, 20, 20),
            1,
            cv2.LINE_AA,
        )

    wrist_x, wrist_y = points[0]
    title_y = max(wrist_y - 28, 30 + hand_index * 26)
    cv2.putText(
        frame,
        f"Hand {hand_index + 1}: {handedness_text}",
        (max(wrist_x - 20, 20), title_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (250, 250, 250),
        2,
        cv2.LINE_AA,
    )


def _draw_header(frame, detected_hands: int):
    cv2.rectangle(frame, (16, 16), (780, 124), (18, 26, 30), -1)
    cv2.putText(
        frame,
        f"Hands detected: {detected_hands}",
        (28, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (244, 248, 250),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        "All 21 landmarks are numbered. Key points are highlighted with larger orange dots.",
        (28, 82),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (184, 209, 220),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        "Key ids: 0 wrist, 4/8/12/16/20 fingertips, 5/9/13/17 finger bases",
        (28, 106),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (184, 209, 220),
        1,
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

    start_time = time.monotonic()
    last_timestamp_ms = -1
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
            if timestamp_ms <= last_timestamp_ms:
                timestamp_ms = last_timestamp_ms + 1
            last_timestamp_ms = timestamp_ms

            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            multi_hand_landmarks = result.hand_landmarks or []
            multi_handedness = result.handedness or []

            for hand_index, hand_landmarks in enumerate(multi_hand_landmarks):
                handedness_text = "Unknown"
                if hand_index < len(multi_handedness) and multi_handedness[hand_index]:
                    handedness_text = multi_handedness[hand_index][0].category_name
                _draw_hand(frame, hand_landmarks, handedness_text, hand_index)

            _draw_header(frame, len(multi_hand_landmarks))

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (230, 236, 240),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q")):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
