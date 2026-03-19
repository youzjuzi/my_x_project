import cv2
import time
import math
from collections import deque, Counter
import mediapipe as mp


# =========================
# 可调参数
# =========================
MODEL_PATH = "hand_landmarker.task"
WINDOW_NAME = "D / Z Dynamic Anti-Break"
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

NUM_HANDS = 1

# 为了减少大幅动作时的断触，这里比之前更宽松
MIN_HAND_DETECTION_CONFIDENCE = 0.35
MIN_HAND_PRESENCE_CONFIDENCE = 0.30
MIN_TRACKING_CONFIDENCE = 0.30

# 手指 straight / bent
FINGER_STRAIGHT_THRESHOLD = 160

# Z 动态检测
TRAJ_WINDOW = 24          # 轨迹缓存长度，放大一点更适合画大范围 Z
MIN_TRACK_FRAMES = 8      # 少于这个帧数时，先按 D 看

TH_STILL_PATH = 0.35      # 静止时总路径阈值（掌宽归一化后）
TH_STILL_END = 0.12       # 静止时首尾位移阈值

TH_MOVE = 0.85            # 认为“明显在画 Z”的总路径阈值
TH_HORIZ = 0.18           # 第一/三段横向位移阈值
TH_DIAG_X = 0.12          # 第二段斜线 x 位移阈值
TH_DIAG_Y = 0.12          # 第二段斜线 y 位移阈值
TH_CURVE = 1.20           # 曲线度阈值
TH_OVERALL_DOWN = 0.10    # 整体向下趋势
HORIZ_RATIO = 1.20        # 横向段：|dx| > HORIZ_RATIO * |dy|

# 防断触关键参数
NO_HAND_GRACE = 5         # 手完全丢失后允许保留的帧数
FAMILY_GRACE = 6          # 家族判定失败后允许保留的帧数

# 多帧稳定
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


def palm_scale(hand):
    """
    用掌宽归一化：5(食指根) 到 17(小指根)
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


def path_length(points):
    if len(points) < 2:
        return 0.0

    total = 0.0
    for i in range(1, len(points)):
        total += dist_xy(points[i - 1], points[i])
    return total


def smooth_points(points, window=3):
    """
    简单滑动平均去抖
    """
    if len(points) == 0:
        return []

    radius = window // 2
    smoothed = []

    for i in range(len(points)):
        left = max(0, i - radius)
        right = min(len(points), i + radius + 1)

        xs = [points[j][0] for j in range(left, right)]
        ys = [points[j][1] for j in range(left, right)]

        smoothed.append((sum(xs) / len(xs), sum(ys) / len(ys)))

    return smoothed


def cumulative_lengths(points):
    """
    累积路径长度
    """
    if len(points) == 0:
        return [0.0]

    cum = [0.0]
    for i in range(1, len(points)):
        cum.append(cum[-1] + dist_xy(points[i - 1], points[i]))
    return cum


def point_at_fraction(points, frac):
    """
    按“路径长度比例”取点，比按帧数分段更稳
    frac: 0~1
    """
    if len(points) == 0:
        return (0.0, 0.0)
    if len(points) == 1:
        return points[0]

    frac = max(0.0, min(1.0, frac))
    cum = cumulative_lengths(points)
    total = cum[-1]

    if total == 0:
        return points[0]

    target = frac * total

    for i in range(1, len(points)):
        if cum[i] >= target:
            prev_len = cum[i - 1]
            seg_len = cum[i] - prev_len

            if seg_len == 0:
                return points[i]

            t = (target - prev_len) / seg_len
            x = points[i - 1][0] + t * (points[i][0] - points[i - 1][0])
            y = points[i - 1][1] + t * (points[i][1] - points[i - 1][1])
            return (x, y)

    return points[-1]


# =========================
# 手指 straight / bent 判断
# =========================
def is_finger_straight(hand, mcp_id, pip_id, dip_id, tip_id, threshold=160):
    angle1 = angle_3points(hand[mcp_id], hand[pip_id], hand[dip_id])
    angle2 = angle_3points(hand[pip_id], hand[dip_id], hand[tip_id])
    ok = (angle1 > threshold) and (angle2 > threshold)
    return ok, angle1, angle2


# =========================
# D / Z 家族判定
# =========================
def is_dz_family(index_ok, middle_ok, ring_ok, pinky_ok):
    """
    D / Z 共用静态家族：
    食指伸直，其他三指弯曲
    """
    return index_ok and (not middle_ok) and (not ring_ok) and (not pinky_ok)


def is_dz_family_keep(index_ok, middle_ok, ring_ok, pinky_ok):
    """
    跟踪已经开始后，续判更宽松一些，减少断触
    """
    return index_ok and ((not ring_ok) or (not pinky_ok))


# =========================
# D / Z 动态分类
# =========================
def classify_dz_dynamic(
    samples,
    min_track_frames=8,
    th_still_path=0.35,
    th_still_end=0.12,
    th_move=0.85,
    th_horiz=0.18,
    th_diag_x=0.12,
    th_diag_y=0.12,
    th_curve=1.20,
    th_overall_down=0.10,
    horiz_ratio=1.20,
):
    """
    samples: [(x, y, scale), ...]
    x/y 是整张图里的归一化坐标，不是相对 wrist 的坐标

    逻辑：
    - 静止 / 几乎不动 -> D
    - 轨迹满足“横 -> 斜下反向 -> 横” -> Z
    - 否则 -> uncertain
    """
    if len(samples) == 0:
        return "not_dz", {}

    points = [(s[0], s[1]) for s in samples]
    scales = [s[2] for s in samples]
    mean_scale = max(sum(scales) / len(scales), 1e-6)

    smoothed = smooth_points(points, window=3)

    # 平移归一化：以起点为原点
    x0, y0 = smoothed[0]
    traj = [((x - x0) / mean_scale, (y - y0) / mean_scale) for x, y in smoothed]

    total_len = path_length(traj)
    end_disp = dist_xy(traj[0], traj[-1])
    curve_ratio = total_len / max(end_disp, 1e-6)

    # 用路径比例取三段关键点
    p0 = traj[0]
    p1 = point_at_fraction(traj, 1 / 3)
    p2 = point_at_fraction(traj, 2 / 3)
    p3 = traj[-1]

    # 三段位移
    s1x, s1y = p1[0] - p0[0], p1[1] - p0[1]
    s2x, s2y = p2[0] - p1[0], p2[1] - p1[1]
    s3x, s3y = p3[0] - p2[0], p3[1] - p2[1]

    not_enough_frames = len(traj) < min_track_frames

    still_enough = (total_len < th_still_path) and (end_disp < th_still_end)
    moved_enough = total_len > th_move

    # 第一段：横向
    horiz1 = (abs(s1x) > th_horiz) and (abs(s1x) > horiz_ratio * abs(s1y))

    # 第二段：斜向下，且 x/y 都要有明显分量
    diag2 = (
        abs(s2x) > th_diag_x and
        s2y > th_diag_y and
        abs(s2x) > 0.40 * abs(s2y) and
        abs(s2x) < 3.00 * abs(s2y)
    )

    # 第三段：横向
    horiz3 = (abs(s3x) > th_horiz) and (abs(s3x) > horiz_ratio * abs(s3y))

    # Z 形方向关系：
    # 第一段和第三段横向方向一致
    # 第二段横向方向与它们相反
    zigzag_dir = (s1x * s3x > 0) and (s1x * s2x < 0)

    # 整体应有一点向下趋势
    overall_down = (p3[1] - p0[1]) > th_overall_down

    if not_enough_frames:
        cls = "D"
    elif still_enough:
        cls = "D"
    elif moved_enough and horiz1 and diag2 and horiz3 and zigzag_dir and overall_down and (curve_ratio > th_curve):
        cls = "Z"
    elif total_len < (th_move * 0.55):
        cls = "D"
    else:
        cls = "uncertain"

    # 方便画图
    disp_p1 = point_at_fraction(smoothed, 1 / 3)
    disp_p2 = point_at_fraction(smoothed, 2 / 3)

    return cls, {
        "num_points": len(traj),
        "total_len": total_len,
        "end_disp": end_disp,
        "curve_ratio": curve_ratio,

        "s1x": s1x, "s1y": s1y,
        "s2x": s2x, "s2y": s2y,
        "s3x": s3x, "s3y": s3y,

        "horiz1": horiz1,
        "diag2": diag2,
        "horiz3": horiz3,
        "zigzag_dir": zigzag_dir,
        "overall_down": overall_down,
        "still_enough": still_enough,
        "moved_enough": moved_enough,

        "disp_p1": disp_p1,
        "disp_p2": disp_p2,
    }


# =========================
# 多帧稳定
# =========================
def stabilize_cls(history, vote_min=3):
    if len(history) == 0:
        return "none"

    valid = [c for c in history if c in ["D", "Z"]]
    if len(valid) == 0:
        return history[-1]

    top_cls, top_count = Counter(valid).most_common(1)[0]
    if top_count >= vote_min:
        return top_cls

    return valid[-1]


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

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

traj_buffer = deque(maxlen=TRAJ_WINDOW)   # 存 (x, y, scale)
cls_history = deque(maxlen=VOTE_WINDOW)

family_miss_count = 0
no_hand_miss_count = 0
tracking_active = False
last_raw_cls = "not_dz"
last_stable_cls = "not_dz"

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

        raw_cls = last_raw_cls
        stable_cls = last_stable_cls
        info = {}
        handed_label = "Unknown"

        if result.hand_landmarks:
            no_hand_miss_count = 0
            hand = result.hand_landmarks[0]

            if result.handedness:
                handed_label = result.handedness[0][0].category_name

            # ===== 四指状态 =====
            index_ok, ia1, ia2 = is_finger_straight(hand, 5, 6, 7, 8, FINGER_STRAIGHT_THRESHOLD)
            middle_ok, ma1, ma2 = is_finger_straight(hand, 9, 10, 11, 12, FINGER_STRAIGHT_THRESHOLD)
            ring_ok, ra1, ra2 = is_finger_straight(hand, 13, 14, 15, 16, FINGER_STRAIGHT_THRESHOLD)
            pinky_ok, pa1, pa2 = is_finger_straight(hand, 17, 18, 19, 20, FINGER_STRAIGHT_THRESHOLD)

            dz_family_start = is_dz_family(index_ok, middle_ok, ring_ok, pinky_ok)
            dz_family_keep = is_dz_family_keep(index_ok, middle_ok, ring_ok, pinky_ok)

            # 当前帧食指尖
            px = hand[8].x
            py = hand[8].y
            scale = palm_scale(hand)

            if dz_family_start:
                tracking_active = True
                family_miss_count = 0
                traj_buffer.append((px, py, scale))

            else:
                if tracking_active:
                    if dz_family_keep:
                        family_miss_count = 0
                        traj_buffer.append((px, py, scale))
                    else:
                        family_miss_count += 1
                        if family_miss_count <= FAMILY_GRACE:
                            traj_buffer.append((px, py, scale))
                        else:
                            tracking_active = False
                            family_miss_count = 0
                            traj_buffer.clear()
                            cls_history.clear()
                            raw_cls = "not_dz"
                            stable_cls = "not_dz"
                else:
                    raw_cls = "not_dz"
                    stable_cls = "not_dz"

            # 只要 tracking_active，就继续判 D/Z
            if tracking_active and len(traj_buffer) > 0:
                raw_cls, info = classify_dz_dynamic(
                    list(traj_buffer),
                    min_track_frames=MIN_TRACK_FRAMES,
                    th_still_path=TH_STILL_PATH,
                    th_still_end=TH_STILL_END,
                    th_move=TH_MOVE,
                    th_horiz=TH_HORIZ,
                    th_diag_x=TH_DIAG_X,
                    th_diag_y=TH_DIAG_Y,
                    th_curve=TH_CURVE,
                    th_overall_down=TH_OVERALL_DOWN,
                    horiz_ratio=HORIZ_RATIO,
                )

                cls_history.append(raw_cls)
                stable_cls = stabilize_cls(cls_history, vote_min=VOTE_MIN)

                last_raw_cls = raw_cls
                last_stable_cls = stable_cls

            # ===== 画所有关键点 =====
            for i, lm in enumerate(hand):
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

                if i in [8, 12, 16, 20]:
                    cv2.putText(
                        frame, str(i), (x + 6, y - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2
                    )

            # 高亮食指尖 8
            x8 = int(hand[8].x * w)
            y8 = int(hand[8].y * h)
            cv2.circle(frame, (x8, y8), 7, (0, 255, 255), 2)

            # ===== 画轨迹 =====
            traj_px = [(int(x * w), int(y * h)) for x, y, _ in traj_buffer]
            for i in range(1, len(traj_px)):
                cv2.line(frame, traj_px[i - 1], traj_px[i], (255, 0, 0), 2)

            if len(traj_px) > 0:
                cv2.circle(frame, traj_px[0], 5, (0, 255, 0), -1)
                cv2.circle(frame, traj_px[-1], 5, (0, 0, 255), -1)

            # 画 1/3 和 2/3 分段点
            if info:
                disp_p1 = info.get("disp_p1", None)
                disp_p2 = info.get("disp_p2", None)
                if disp_p1 is not None:
                    p1 = (int(disp_p1[0] * w), int(disp_p1[1] * h))
                    cv2.circle(frame, p1, 5, (255, 255, 0), -1)
                if disp_p2 is not None:
                    p2 = (int(disp_p2[0] * w), int(disp_p2[1] * h))
                    cv2.circle(frame, p2, 5, (255, 128, 0), -1)

            # ===== 标题信息 =====
            cls_color = (0, 0, 255) if stable_cls == "Z" else (0, 255, 255) if stable_cls == "D" else (200, 200, 200)

            cv2.putText(
                frame,
                f"{handed_label} raw={raw_cls} stable={stable_cls}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                cls_color,
                2
            )

            cv2.putText(
                frame,
                f"tracking={tracking_active} family_start={dz_family_start} family_keep={dz_family_keep}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"index={'S' if index_ok else 'B'} middle={'S' if middle_ok else 'B'} ring={'S' if ring_ok else 'B'} pinky={'S' if pinky_ok else 'B'}",
                (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.56,
                (255, 255, 255),
                2
            )

            if info:
                total_len = info.get("total_len", -1)
                end_disp = info.get("end_disp", -1)
                curve_ratio = info.get("curve_ratio", -1)

                s1x = info.get("s1x", 0)
                s1y = info.get("s1y", 0)
                s2x = info.get("s2x", 0)
                s2y = info.get("s2y", 0)
                s3x = info.get("s3x", 0)
                s3y = info.get("s3y", 0)

                horiz1 = info.get("horiz1", False)
                diag2 = info.get("diag2", False)
                horiz3 = info.get("horiz3", False)
                zigzag_dir = info.get("zigzag_dir", False)
                overall_down = info.get("overall_down", False)
                still_enough = info.get("still_enough", False)
                moved_enough = info.get("moved_enough", False)

                cv2.putText(
                    frame,
                    f"path={total_len:.3f} end={end_disp:.3f} curve={curve_ratio:.3f}",
                    (20, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.56,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"s1=({s1x:.2f},{s1y:.2f}) s2=({s2x:.2f},{s2y:.2f}) s3=({s3x:.2f},{s3y:.2f})",
                    (20, 155),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.53,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"h1={horiz1} d2={diag2} h3={horiz3} zigzag={zigzag_dir} down={overall_down}",
                    (20, 185),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.53,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"still={still_enough} move={moved_enough} miss_family={family_miss_count} miss_hand={no_hand_miss_count}",
                    (20, 215),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.52,
                    (255, 255, 255),
                    2
                )

        else:
            # 当前帧没检测到手
            no_hand_miss_count += 1

            if tracking_active and no_hand_miss_count <= NO_HAND_GRACE:
                raw_cls = last_raw_cls
                stable_cls = last_stable_cls
            else:
                tracking_active = False
                family_miss_count = 0
                no_hand_miss_count = 0
                traj_buffer.clear()
                cls_history.clear()
                raw_cls = "not_dz"
                stable_cls = "not_dz"
                info = {}

        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()
