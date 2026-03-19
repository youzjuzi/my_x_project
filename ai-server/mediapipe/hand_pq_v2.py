import cv2
import time
import math
from collections import deque, Counter
import mediapipe as mp


# =========================
# 可调参数
# =========================
MODEL_PATH = "hand_landmarker.task"

NUM_HANDS = 1
MIN_HAND_DETECTION_CONFIDENCE = 0.5
MIN_HAND_PRESENCE_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

FINGER_STRAIGHT_THRESHOLD = 160   # 四指 straight/bent 判断阈值

# P 的约束：严格一点
TH_P_SEG = 0.22
TH_P_T_MIN = -0.05
TH_P_T_MAX = 1.05

# Q 的约束：按“门型 / 反U型”宽判
TH_Q_OPEN = 0.38          # d(4,8) 要大于这个，表示拇指没藏 inside
TH_Q_TIP_Y_DIFF = 0.55    # 两个指尖高度差不要太大
TH_INDEX_DOWN_RATIO = 0.60
TH_THUMB_DOWN_RATIO = 0.35

VOTE_WINDOW = 5
VOTE_MIN = 3


# =========================
# 基础几何函数
# =========================
def point_xy(lm):
    return (lm.x, lm.y)


def dist_xy(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx * dx + dy * dy)


def midpoint_xy(a, b):
    return ((a.x + b.x) / 2, (a.y + b.y) / 2)


def palm_scale(hand):
    """
    用掌宽归一化
    """
    scale = dist_xy(point_xy(hand[5]), point_xy(hand[17]))
    return max(scale, 1e-6)


def angle_3points(a, b, c):
    """
    计算 ∠ABC，单位：度
    """
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
    """
    p: 点
    a, b: 线段两端点
    返回:
      dist: 点到线段的最短距离
      t: 投影参数
         t < 0   在线段 a 外侧
         0~1     在线段内部
         t > 1   在线段 b 外侧
    """
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


# =========================
# 手指 straight/bent 判断
# =========================
def is_finger_straight(hand, mcp_id, pip_id, dip_id, tip_id, threshold=160):
    angle1 = angle_3points(hand[mcp_id], hand[pip_id], hand[dip_id])
    angle2 = angle_3points(hand[pip_id], hand[dip_id], hand[tip_id])
    ok = (angle1 > threshold) and (angle2 > threshold)
    return ok, angle1, angle2


# =========================
# P/Q 分类
# =========================
def classify_pq_robust(
    hand,
    index_ok, middle_ok, ring_ok, pinky_ok,
    th_p_seg=0.22,
    th_p_t_min=-0.05, th_p_t_max=1.05,
    th_q_open=0.38,
    th_q_tip_y_diff=0.55,
    th_index_down_ratio=0.60,
    th_thumb_down_ratio=0.35,
):
    """
    当前按你的定义：
    P = 食指/中指伸直，拇指夹在中间
    Q = 食指向下，拇指也伸出来且不藏 inside，像门型/反U型
    """

    # 基础家族：食指必须直；无名指、小指必须弯
    pq_family = index_ok and (not ring_ok) and (not pinky_ok)
    if not pq_family:
        return "not_pq", {}

    scale = palm_scale(hand)
    thumb_tip = point_xy(hand[4])

    # -------------------------
    # P 通道：拇指位于食指-中指之间
    # -------------------------
    p_top = midpoint_xy(hand[8], hand[12])
    p_bottom = midpoint_xy(hand[6], hand[10])

    p_seg_dist, p_t = point_to_segment_distance_and_t(thumb_tip, p_top, p_bottom)
    p_seg_dist /= scale

    # -------------------------
    # 辅助距离
    # -------------------------
    d48 = dist_xy(point_xy(hand[4]), point_xy(hand[8])) / scale
    d412 = dist_xy(point_xy(hand[4]), point_xy(hand[12])) / scale

    # -------------------------
    # 食指方向：向下
    # 5 -> 8
    # 图像里 y 变大表示向下
    # -------------------------
    dx_i = hand[8].x - hand[5].x
    dy_i = hand[8].y - hand[5].y
    index_down = (dy_i > 0) and (abs(dy_i) > th_index_down_ratio * abs(dx_i))

    # -------------------------
    # 拇指方向：也向下 / 外伸
    # 2 -> 4
    # -------------------------
    dx_t = hand[4].x - hand[2].x
    dy_t = hand[4].y - hand[2].y
    thumb_down = (dy_t > 0) and (abs(dy_t) > th_thumb_down_ratio * abs(dx_t))

    # -------------------------
    # 门型特征
    # 1) 拇指不能藏 inside，要张开
    # 2) 两个指尖高度差不要太大
    # -------------------------
    thumb_open = d48 > th_q_open

    # 这里直接用归一化坐标的y差，再除以掌宽做尺度统一
    tip_y_diff = abs(hand[4].y - hand[8].y) / scale
    tips_same_level = tip_y_diff < th_q_tip_y_diff

    # -------------------------
    # P：严判
    # -------------------------
    p_like = (
        middle_ok and
        (p_seg_dist < th_p_seg) and
        (th_p_t_min <= p_t <= th_p_t_max)
    )

    # -------------------------
    # Q：门型 / 反U型宽判
    # -------------------------
    q_like = (
        (not middle_ok) and
        index_down and
        thumb_down and
        thumb_open and
        tips_same_level
    )

    if p_like and not q_like:
        cls = "P"
    elif q_like and not p_like:
        cls = "Q"
    elif p_like and q_like:
        # 冲突时优先 P，因为 P 条件更强
        cls = "P"
    else:
        cls = "uncertain"

    return cls, {
        "pq_family": pq_family,

        "p_top": p_top,
        "p_bottom": p_bottom,
        "p_seg_dist": p_seg_dist,
        "p_t": p_t,

        "d48": d48,
        "d412": d412,

        "dx_i": dx_i,
        "dy_i": dy_i,
        "dx_t": dx_t,
        "dy_t": dy_t,

        "index_down": index_down,
        "thumb_down": thumb_down,
        "thumb_open": thumb_open,
        "tip_y_diff": tip_y_diff,
        "tips_same_level": tips_same_level,

        "p_like": p_like,
        "q_like": q_like,
    }


# =========================
# 多帧稳定
# =========================
def stabilize_cls(history, vote_min=3):
    if len(history) == 0:
        return "none"

    top_cls, top_count = Counter(history).most_common(1)[0]
    if top_count >= vote_min:
        return top_cls
    return history[-1]


# =========================
# MediaPipe 初始化
# =========================
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=NUM_HANDS,
    min_hand_detection_confidence=MIN_HAND_DETECTION_CONFIDENCE,
    min_hand_presence_confidence=MIN_HAND_PRESENCE_CONFIDENCE,
    min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("无法打开摄像头")
    raise SystemExit

tip_ids = [4, 8, 12, 16, 20]
root_ids = [5, 9, 13, 17]

cls_history = deque(maxlen=VOTE_WINDOW)
start_time = time.monotonic()

with HandLandmarker.create_from_options(options) as landmarker:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("读取摄像头画面失败")
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = int((time.monotonic() - start_time) * 1000)
        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        h, w = frame.shape[:2]

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]

            # ===== 四指状态 =====
            index_ok, ia1, ia2 = is_finger_straight(hand, 5, 6, 7, 8, FINGER_STRAIGHT_THRESHOLD)
            middle_ok, ma1, ma2 = is_finger_straight(hand, 9, 10, 11, 12, FINGER_STRAIGHT_THRESHOLD)
            ring_ok, ra1, ra2 = is_finger_straight(hand, 13, 14, 15, 16, FINGER_STRAIGHT_THRESHOLD)
            pinky_ok, pa1, pa2 = is_finger_straight(hand, 17, 18, 19, 20, FINGER_STRAIGHT_THRESHOLD)

            # ===== P/Q 分类 =====
            raw_cls, info = classify_pq_robust(
                hand,
                index_ok, middle_ok, ring_ok, pinky_ok,
                th_p_seg=TH_P_SEG,
                th_p_t_min=TH_P_T_MIN,
                th_p_t_max=TH_P_T_MAX,
                th_q_open=TH_Q_OPEN,
                th_q_tip_y_diff=TH_Q_TIP_Y_DIFF,
                th_index_down_ratio=TH_INDEX_DOWN_RATIO,
                th_thumb_down_ratio=TH_THUMB_DOWN_RATIO,
            )

            cls_history.append(raw_cls)
            stable_cls = stabilize_cls(cls_history, vote_min=VOTE_MIN)

            # ===== 画所有关键点 =====
            for lm in hand:
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            # ===== 特别标注 =====
            for i in tip_ids:
                lm = hand[i]
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 7, (0, 255, 255), 2)
                cv2.putText(
                    frame, str(i), (x + 6, y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2
                )

            for i in root_ids:
                lm = hand[i]
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 7, (255, 0, 255), 2)
                cv2.putText(
                    frame, str(i), (x + 6, y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2
                )

            # ===== 画 P 通道 =====
            if info:
                p_top = info.get("p_top", None)
                p_bottom = info.get("p_bottom", None)

                if p_top is not None and p_bottom is not None:
                    x1, y1 = int(p_top[0] * w), int(p_top[1] * h)
                    x2, y2 = int(p_bottom[0] * w), int(p_bottom[1] * h)
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 128, 255), 2)
                    cv2.putText(
                        frame, "P-gap", (x1 + 8, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 128, 255), 2
                    )

            # ===== handedness =====
            if result.handedness:
                label = result.handedness[0][0].category_name
                score = result.handedness[0][0].score
                cv2.putText(
                    frame,
                    f"{label} {score:.2f}",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

            # ===== 调试信息 =====
            cls_color = (0, 0, 255) if stable_cls in ["P", "Q"] else (200, 200, 200)

            cv2.putText(
                frame,
                f"raw={raw_cls} stable={stable_cls}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                cls_color,
                2
            )

            cv2.putText(
                frame,
                f"index={'S' if index_ok else 'B'} middle={'S' if middle_ok else 'B'} ring={'S' if ring_ok else 'B'} pinky={'S' if pinky_ok else 'B'}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2
            )

            if info:
                p_seg_dist = info.get("p_seg_dist", -1)
                p_t = info.get("p_t", -1)

                d48 = info.get("d48", -1)
                d412 = info.get("d412", -1)

                index_down = info.get("index_down", False)
                thumb_down = info.get("thumb_down", False)
                thumb_open = info.get("thumb_open", False)
                tip_y_diff = info.get("tip_y_diff", -1)
                tips_same_level = info.get("tips_same_level", False)

                p_like = info.get("p_like", False)
                q_like = info.get("q_like", False)

                cv2.putText(
                    frame,
                    f"P: seg={p_seg_dist:.3f} t={p_t:.3f} like={p_like}",
                    (20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Q: idx_down={index_down} th_down={thumb_down} like={q_like}",
                    (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"thumb_open={thumb_open} tips_same={tips_same_level}",
                    (20, 190),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"d(4,8)={d48:.3f} d(4,12)={d412:.3f} ydiff={tip_y_diff:.3f}",
                    (20, 220),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"P_seg={TH_P_SEG:.2f} Q_open>{TH_Q_OPEN:.2f} Q_ydiff<{TH_Q_TIP_Y_DIFF:.2f}",
                    (20, 250),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2
                )

        cv2.imshow("PQ Robust Full", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:   # ESC
            break

cap.release()
cv2.destroyAllWindows()