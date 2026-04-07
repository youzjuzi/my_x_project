import base64
import math
import time
from collections import Counter, deque
from typing import Any, Deque, Dict, List, Optional, Tuple

import mediapipe as mp
import numpy as np

from .ij_dz_dynamic_detector import DynamicLetterSession
# 注意这里：根据你之前提供的代码，文件名如果是 mn_hybrid_detector.py，导入函数就是 classify_mnt_only
from .mn_hybrid_detector import classify_mnt_only 
from ..yolo_stage import YOLOStage, clamp_box, cv2, draw_box, select_device


FINGER_STRAIGHT_THRESHOLD = 160
TH_P_SEG = 0.22
TH_P_T_MIN = -0.05
TH_P_T_MAX = 1.05
TH_Q_OPEN = 0.45
TH_Q_TIP_Y_DIFF = 0.40
TH_INDEX_DOWN_RATIO = 0.80
TH_THUMB_DOWN_RATIO = 0.50
VOTE_WINDOW = 5
VOTE_MIN = 3


def point_xy(lm):
    return (lm.x, lm.y)


def dist_xy(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx * dx + dy * dy)


def midpoint_xy(a, b):
    return ((a.x + b.x) / 2, (a.y + b.y) / 2)


def palm_scale(hand):
    scale = dist_xy(point_xy(hand[5]), point_xy(hand[17]))
    return max(scale, 1e-6)


def angle_3points(a, b, c):
    abx = a.x - b.x
    aby = a.y - b.y
    cbx = c.x - b.x
    cby = c.y - b.y

    dot = abx * cbx + aby * cby
    norm_ab = math.sqrt(abx * abx + aby * aby)
    norm_cb = math.sqrt(cbx * cbx + cby * cby)
    if norm_ab == 0 or norm_cb == 0:
        return 0.0

    cos_value = dot / (norm_ab * norm_cb)
    cos_value = max(-1.0, min(1.0, cos_value))
    return math.degrees(math.acos(cos_value))


def dot2(a, b):
    return a[0] * b[0] + a[1] * b[1]


def point_to_segment_distance_and_t(p, a, b):
    ab = (b[0] - a[0], b[1] - a[1])
    ap = (p[0] - a[0], p[1] - a[1])
    ab2 = dot2(ab, ab)
    if ab2 == 0:
        return dist_xy(p, a), 0.0

    t = dot2(ap, ab) / ab2
    t_clamped = max(0.0, min(1.0, t))
    proj = (a[0] + t_clamped * ab[0], a[1] + t_clamped * ab[1])
    dist = dist_xy(p, proj)
    return dist, t


def is_finger_straight(hand, mcp_id, pip_id, dip_id, tip_id, threshold=160):
    angle1 = angle_3points(hand[mcp_id], hand[pip_id], hand[dip_id])
    angle2 = angle_3points(hand[pip_id], hand[dip_id], hand[tip_id])
    ok = (angle1 > threshold) and (angle2 > threshold)
    return ok, angle1, angle2


def classify_pq_robust(
    hand,
    index_ok,
    middle_ok,
    ring_ok,
    pinky_ok,
    th_p_seg=TH_P_SEG,
    th_p_t_min=TH_P_T_MIN,
    th_p_t_max=TH_P_T_MAX,
    th_q_open=TH_Q_OPEN,
    th_q_tip_y_diff=TH_Q_TIP_Y_DIFF,
    th_index_down_ratio=TH_INDEX_DOWN_RATIO,
    th_thumb_down_ratio=TH_THUMB_DOWN_RATIO,
):
    pq_family = index_ok and (not ring_ok) and (not pinky_ok)
    if not pq_family:
        return "not_pq", {}

    scale = palm_scale(hand)
    thumb_tip = point_xy(hand[4])

    p_top = midpoint_xy(hand[8], hand[12])
    p_bottom = midpoint_xy(hand[6], hand[10])
    p_seg_dist, p_t = point_to_segment_distance_and_t(thumb_tip, p_top, p_bottom)
    p_seg_dist /= scale

    d48 = dist_xy(point_xy(hand[4]), point_xy(hand[8])) / scale
    d412 = dist_xy(point_xy(hand[4]), point_xy(hand[12])) / scale

    dx_i = hand[8].x - hand[5].x
    dy_i = hand[8].y - hand[5].y
    index_down = (dy_i > 0) and (abs(dy_i) > th_index_down_ratio * abs(dx_i))

    dx_t = hand[4].x - hand[2].x
    dy_t = hand[4].y - hand[2].y
    thumb_down = (dy_t > 0) and (abs(dy_t) > th_thumb_down_ratio * abs(dx_t))

    thumb_open = d48 > th_q_open
    tip_y_diff = abs(hand[4].y - hand[8].y) / scale
    tips_same_level = tip_y_diff < th_q_tip_y_diff

    p_like = middle_ok and (p_seg_dist < th_p_seg) and (th_p_t_min <= p_t <= th_p_t_max)
    q_like = (not middle_ok) and index_down and thumb_down and thumb_open and tips_same_level

    if p_like and not q_like:
        cls = "P"
    elif q_like and not p_like:
        cls = "Q"
    elif p_like and q_like:
        cls = "P"
    else:
        cls = "uncertain"

    return cls, {
        "p_seg_dist": p_seg_dist,
        "p_t": p_t,
        "d48": d48,
        "d412": d412,
        "index_down": index_down,
        "thumb_down": thumb_down,
        "thumb_open": thumb_open,
        "tip_y_diff": tip_y_diff,
        "tips_same_level": tips_same_level,
        "p_like": p_like,
        "q_like": q_like,
    }


def classify_f_only(hand):
    scale = palm_scale(hand)
    thumb_tip = point_xy(hand[4])
    index_tip = point_xy(hand[8])
    
    # 距离需要相对于手掌大小
    dist_thumb_index = dist_xy(thumb_tip, index_tip) / scale
    
    # 后三指必须伸立
    middle_ok, _, _ = is_finger_straight(hand, 9, 10, 11, 12, FINGER_STRAIGHT_THRESHOLD)
    ring_ok, _, _ = is_finger_straight(hand, 13, 14, 15, 16, FINGER_STRAIGHT_THRESHOLD)
    pinky_ok, _, _ = is_finger_straight(hand, 17, 18, 19, 20, FINGER_STRAIGHT_THRESHOLD)
    
    # 判定捏合的容差。考虑到透视，可以放宽到 0.25
    touching = dist_thumb_index < 0.25
    
    info = {
        "dist_ti": dist_thumb_index,
        "touching": touching,
        "middle_ok": middle_ok,
        "ring_ok": ring_ok,
        "pinky_ok": pinky_ok
    }
    
    if touching and middle_ok and ring_ok and pinky_ok:
        return "F", info
    return "not_f", info


def stabilize_cls(history, vote_min=VOTE_MIN):
    if len(history) == 0:
        return "none"
    top_cls, top_count = Counter(history).most_common(1)[0]
    if top_count >= vote_min:
        return top_cls
    return "uncertain"


class PQHybridDetector:
    def __init__(
        self,
        hand_weights,
        letters_weights,
        mediapipe_model_path,
        imgsz,
        hand_conf,
        letters_conf,
        iou_thres,
        device_name,
        max_det,
        margin,
        jpeg_quality,
        pq_exit_grace_seconds,
        mn_exit_grace_seconds,
        ij_dz_exit_grace_seconds,
    ):
        self.device = select_device(device_name)
        self.hand_stage = YOLOStage(hand_weights, self.device, imgsz)
        self.letters_stage = YOLOStage(letters_weights, self.device, imgsz)
        self.hand_conf = hand_conf
        self.letters_conf = letters_conf
        self.iou_thres = iou_thres
        self.max_det = max_det
        self.margin = margin
        self.jpeg_quality = jpeg_quality
        self.pq_exit_grace_seconds = pq_exit_grace_seconds
        self.mn_exit_grace_seconds = mn_exit_grace_seconds
        self.ij_dz_exit_grace_seconds = ij_dz_exit_grace_seconds

        base_options = mp.tasks.BaseOptions(model_asset_path=mediapipe_model_path)
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.start_time = time.monotonic()

        self.mp_active = False
        self.expected_label = None  # type: Optional[str]
        self.mismatch_started_at = None  # type: Optional[float]
        self.cls_history = deque(maxlen=VOTE_WINDOW)  # type: Deque[str]
        self._last_timestamp_ms = -1
        self.ij_session = DynamicLetterSession("I")
        self.dz_session = DynamicLetterSession("D")
        self.last_yolo_payload = {
            "handCount": 0,
            "hands": [],
            "text": "",
        }

    def process_jpeg_bytes(self, payload, include_annotated=True):
        frame = self._decode_jpeg(payload)
        return self.process_frame(frame, include_annotated=include_annotated)

    def process_frame(self, frame, include_annotated=True):
        started = time.perf_counter()
        output = frame.copy()
        yolo_payload = self.last_yolo_payload
        yolo_text = yolo_payload["text"]

        if not self.mp_active:
            yolo_payload = self._run_yolo_letters(frame, output)
            self.last_yolo_payload = yolo_payload
            yolo_text = yolo_payload["text"]
            special_candidate = self._pick_special_candidate(yolo_payload["hands"])
            # 修改点 1：把 F 加入到可以激活 MediaPipe 的候选列表中
            # 双手出现时禁止激活单手字母检测，避免误触发
            if special_candidate in ("P", "Q", "M", "N", "T", "I", "D", "F") and yolo_payload["handCount"] <= 1:
                self._activate_mediapipe(special_candidate)

        mp_payload = None
        if self.mp_active:
            mp_payload = self._run_mediapipe(frame, output)
            if mp_payload.get("handCount", 0) == 0:
                self._deactivate_mediapipe()
                mp_payload["deactivated"] = True
            elif mp_payload.get("handCount", 0) > 1:
                # 双手出现时立即退出单手检测模式，将控制权交还给双手功能手势
                self._deactivate_mediapipe()
                mp_payload["deactivated"] = True
            else:
                self._update_mp_state(mp_payload["stable"])

        final_text = yolo_text
        engine = "yolo"
        if self.mp_active and mp_payload is not None:
            engine = "mediapipe"
            if self.expected_label in ("P", "Q") and mp_payload["stable"] in ("P", "Q"):
                final_text = mp_payload["stable"]
            # 修改点 2：将 T 加入到 M/N 的预期和稳定判断中
            elif self.expected_label in ("M", "N", "T") and mp_payload["stable"] in ("M", "N", "T"):
                final_text = mp_payload["stable"]
            elif self.expected_label in ("I", "D") and mp_payload["stable"] in ("I", "J", "D", "Z"):
                final_text = mp_payload["stable"]
            # 修改点 3：在 fallback 中加入 T
            elif self.expected_label in ("P", "Q", "M", "N", "T"):
                final_text = self.expected_label

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        result = {
            "type": "result",
            "mode": "letters",
            "engine": engine,
            "latencyMs": latency_ms,
            "imageWidth": int(frame.shape[1]),
            "imageHeight": int(frame.shape[0]),
            "handCount": yolo_payload["handCount"] if engine == "yolo" else mp_payload.get("handCount", 0),
            "text": final_text,
            "expectedLabel": self.expected_label or "",
            "mediapipeActive": self.mp_active,
            "mediapipeGraceRemaining": self._grace_remaining(),
            "hands": yolo_payload["hands"] if engine == "yolo" else (mp_payload.get("hands", []) if mp_payload else []),
            "mediapipe": mp_payload or {},
        }
        if include_annotated:
            result["annotatedFrame"] = "data:image/jpeg;base64,{0}".format(self._encode_jpeg(output))
        return result

    def _run_yolo_letters(self, frame, output):
        hand_det = self.hand_stage.infer(frame, self.hand_conf, self.iou_thres, self.max_det)
        hands = []
        hand_texts = []

        for hand_index, (*hand_xyxy, hand_conf, _) in enumerate(hand_det.tolist(), start=1):
            hx1, hy1, hx2, hy2 = map(int, hand_xyxy)
            hx1 -= self.margin
            hy1 -= self.margin
            hx2 += self.margin
            hy2 += self.margin
            hx1, hy1, hx2, hy2 = clamp_box(hx1, hy1, hx2, hy2, frame.shape[1], frame.shape[0])
            if hx2 <= hx1 or hy2 <= hy1:
                continue

            hand_roi = frame[hy1:hy2, hx1:hx2]
            letter_det = self.letters_stage.infer(hand_roi, self.letters_conf, self.iou_thres, self.max_det)
            draw_box(output, (hx1, hy1, hx2, hy2), "hand {0:.2f}".format(hand_conf), (0, 255, 0), thickness=2)

            ordered_labels = []
            detections = []
            best_label = None
            best_conf = 0.0
            for *letter_xyxy, letter_conf, letter_cls in letter_det.tolist():
                dx1, dy1, dx2, dy2 = map(int, letter_xyxy)
                gx1, gy1 = hx1 + dx1, hy1 + dy1
                gx2, gy2 = hx1 + dx2, hy1 + dy2
                letter_name = str(self.letters_stage.names[int(letter_cls)])
                detections.append(
                    {
                        "label": letter_name,
                        "confidence": round(float(letter_conf), 4),
                        "box": [gx1, gy1, gx2, gy2],
                    }
                )
                # 跟踪置信度最高的检测结果
                if letter_conf > best_conf:
                    best_conf = letter_conf
                    best_label = letter_name
                draw_box(
                    output,
                    (gx1, gy1, gx2, gy2),
                    "{0} {1:.2f}".format(letter_name, letter_conf),
                    (0, 165, 255),
                    thickness=2,
                )

            hand_text = ""
            # 单手只保留最高置信度的字母，避免拼接出 "HQ" 这样的噪声
            if best_label:
                hand_text = best_label
                hand_texts.append(hand_text)
                cv2.putText(
                    output,
                    "letters: {0}".format(hand_text),
                    (hx1, min(frame.shape[0] - 10, hy2 + 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2,
                )

            hands.append(
                {
                    "handIndex": hand_index,
                    "confidence": round(float(hand_conf), 4),
                    "box": [hx1, hy1, hx2, hy2],
                    "text": hand_text,
                    "detections": detections,
                }
            )

        return {
            "handCount": len(hands),
            "hands": hands,
            "text": " | ".join(item for item in hand_texts if item),
        }

    def _run_mediapipe(self, frame, output):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        # 确保时间戳严格单调递增
        timestamp_ms = int((time.monotonic() - self.start_time) * 1000)
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        raw_cls = "not_active"
        stable_cls = "not_active"
        handed_label = "Unknown"
        hand_count = 0

        if result.hand_landmarks:
            hand_count = len(result.hand_landmarks)
            hand = result.hand_landmarks[0]
            if result.handedness:
                handed_label = result.handedness[0][0].category_name

            info = {}
            if self.expected_label in ("P", "Q"):
                index_ok, _, _ = is_finger_straight(hand, 5, 6, 7, 8, FINGER_STRAIGHT_THRESHOLD)
                middle_ok, _, _ = is_finger_straight(hand, 9, 10, 11, 12, FINGER_STRAIGHT_THRESHOLD)
                ring_ok, _, _ = is_finger_straight(hand, 13, 14, 15, 16, FINGER_STRAIGHT_THRESHOLD)
                pinky_ok, _, _ = is_finger_straight(hand, 17, 18, 19, 20, FINGER_STRAIGHT_THRESHOLD)
                raw_cls, info = classify_pq_robust(hand, index_ok, middle_ok, ring_ok, pinky_ok)
                self.cls_history.append(raw_cls)
                stable_cls = stabilize_cls(self.cls_history, vote_min=VOTE_MIN)
            # 修改点 4：将 T 加入到路由判断，并调用我们更新过的新函数名 classify_mnt_only
            elif self.expected_label in ("M", "N", "T"):
                raw_cls, info = classify_mnt_only(hand)
                self.cls_history.append(raw_cls)
                stable_cls = stabilize_cls(self.cls_history, vote_min=VOTE_MIN)
            elif self.expected_label == "F":
                raw_cls, info = classify_f_only(hand)
                self.cls_history.append(raw_cls)
                stable_cls = stabilize_cls(self.cls_history, vote_min=VOTE_MIN)
            elif self.expected_label == "I":
                dynamic_result = self.ij_session.update(hand)
                raw_cls = dynamic_result["raw"]
                stable_cls = dynamic_result["stable"]
                info = dynamic_result["info"]
            elif self.expected_label == "D":
                dynamic_result = self.dz_session.update(hand)
                raw_cls = dynamic_result["raw"]
                stable_cls = dynamic_result["stable"]
                info = dynamic_result["info"]

            height, width = frame.shape[:2]
            for lm in hand:
                x = int(lm.x * width)
                y = int(lm.y * height)
                cv2.circle(output, (x, y), 3, (0, 255, 0), -1)

            cls_color = (0, 0, 255) if stable_cls in ("P", "Q") else (200, 200, 200)
            cv2.putText(
                output,
                "MP {0} raw={1} stable={2}".format(handed_label, raw_cls, stable_cls),
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                cls_color,
                2,
            )
            cv2.putText(
                output,
                "expect={0} active={1}".format(self.expected_label or "-", self.mp_active),
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                output,
                "raw_info p={0} q={1} fist={2}".format(info.get("p_like", False), info.get("q_like", False), info.get("fist_family", False)),
                (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )
            if self.expected_label == "F":
                cv2.putText(
                    output,
                    "F_info dist={0:.2f} touch={1} ms={2}".format(
                        info.get("dist_ti", -1.0),
                        info.get("touching", False),
                        info.get("middle_ok", False)
                    ),
                    (20, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (255, 255, 255),
                    2,
                )
            # 修改点 5：修改这里让 M, N, T 的相关辅助信息正确展示
            if self.expected_label in ("M", "N", "T"):
                cv2.putText(
                    output,
                    "M/N/T t_thumb={0:.2f} t_mid={1:.2f} t_ring={2:.2f} best={3}".format(
                        info.get("t_thumb", -1),
                        info.get("t_middle", -1),
                        info.get("t_ring", -1),
                        info.get("best", "-")
                    ),
                    (20, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (255, 255, 255),
                    2,
                )
            if self.expected_label in ("I", "D"):
                cv2.putText(
                    output,
                    "dynamic still={0} move={1} curve={2:.3f}".format(
                        info.get("still_enough", False),
                        info.get("moved_enough", False),
                        info.get("curve_ratio", -1.0),
                    ),
                    (20, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (255, 255, 255),
                    2,
                )
        else:
            if self.expected_label == "I":
                dynamic_result = self.ij_session.update(None)
                raw_cls = dynamic_result["raw"]
                stable_cls = dynamic_result["stable"]
            elif self.expected_label == "D":
                dynamic_result = self.dz_session.update(None)
                raw_cls = dynamic_result["raw"]
                stable_cls = dynamic_result["stable"]
            cv2.putText(
                output,
                "MP no hand",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (180, 180, 180),
                2,
            )

        # 从骨骼关键点计算手部边界框，让前端统一画框
        mp_hands = []
        if result.hand_landmarks:
            height, width = frame.shape[:2]
            for hi, hand_lm in enumerate(result.hand_landmarks):
                xs = [lm.x * width for lm in hand_lm]
                ys = [lm.y * height for lm in hand_lm]
                margin_px = 20
                bx1 = max(0, int(min(xs)) - margin_px)
                by1 = max(0, int(min(ys)) - margin_px)
                bx2 = min(width, int(max(xs)) + margin_px)
                by2 = min(height, int(max(ys)) + margin_px)
                
                # 过滤内部不确定的标签，提升用户体验
                if stable_cls in ("not_active", "none", "uncertain", "not_mnt", "not_pq", "not_fist"):
                    display_text = "Analyzing..."
                    label_text = raw_cls if raw_cls not in ("not_active", "none", "uncertain", "not_mnt", "not_pq", "not_fist") else ""
                else:
                    display_text = f"MP: {stable_cls}"
                    label_text = stable_cls

                mp_hands.append({
                    "handIndex": hi + 1,
                    "confidence": 1.0,
                    "box": [bx1, by1, bx2, by2],
                    "text": label_text,
                    "detections": [{
                        "label": display_text,
                        "confidence": 1.0,
                        "box": [bx1, by1, bx2, by2],
                    }],
                })
                # 同时在 annotated frame 上画框
                cv2.rectangle(output, (bx1, by1), (bx2, by2), (180, 105, 255), 2)
                cv2.putText(
                    output,
                    display_text,
                    (bx1, max(15, by1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (180, 105, 255),
                    2,
                )

        return {
            "raw": raw_cls,
            "stable": stable_cls,
            "handCount": hand_count,
            "hands": mp_hands,
        }

    def _pick_special_candidate(self, hands):
        for hand in hands:
            text = hand.get("text", "")
            # 确保 F 能被选中作为特殊候选者
            if text in ("P", "Q", "M", "N", "T", "I", "D", "F"):
                return text
        return None

    def _activate_mediapipe(self, label):
        self.mp_active = True
        self.expected_label = label
        self.mismatch_started_at = None
        self.cls_history.clear()
        if label == "I":
            self.ij_session.reset()
        if label == "D":
            self.dz_session.reset()

    def _deactivate_mediapipe(self):
        self.mp_active = False
        self.expected_label = None
        self.mismatch_started_at = None
        self.cls_history.clear()

    def _update_mp_state(self, stable_label):
        if not self.mp_active:
            return
        now = time.monotonic()
        if stable_label == self.expected_label:
            self.mismatch_started_at = None
            return

        if self.mismatch_started_at is None:
            self.mismatch_started_at = now
            return

        if now - self.mismatch_started_at >= self._current_grace_seconds():
            self._deactivate_mediapipe()

    def _grace_remaining(self):
        if self.mismatch_started_at is None:
            return self._current_grace_seconds() if self.mp_active else 0.0
        remaining = self._current_grace_seconds() - (time.monotonic() - self.mismatch_started_at)
        return round(max(0.0, remaining), 2)

    def _current_grace_seconds(self):
        # 修改点 7：把 T 的退出宽限时间加入
        if self.expected_label in ("M", "N", "T"):
            return self.mn_exit_grace_seconds
        if self.expected_label in ("I", "D"):
            return self.ij_dz_exit_grace_seconds
        return self.pq_exit_grace_seconds

    def _decode_jpeg(self, payload):
        array = np.frombuffer(payload, dtype=np.uint8)
        frame = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Unable to decode JPEG frame")
        return frame

    def _encode_jpeg(self, frame):
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
        if not ok:
            raise ValueError("Unable to encode annotated frame")
        return base64.b64encode(encoded.tobytes()).decode("ascii")
