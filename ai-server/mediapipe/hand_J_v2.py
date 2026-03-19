import cv2
import time
import math
from collections import deque, Counter
import mediapipe as mp


# =========================
# 可调参数
# =========================
MODEL_PATH = "hand_landmarker.task"
WINDOW_NAME = "I / J Dynamic Anti-Break"
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

NUM_HANDS = 1

# 为减少大幅动作时断触，设得更宽松
MIN_HAND_DETECTION_CONFIDENCE = 0.35
MIN_HAND_PRESENCE_CONFIDENCE = 0.30
MIN_TRACKING_CONFIDENCE = 0.30

# 四指 straight / bent 判断
FINGER_STRAIGHT_THRESHOLD = 160
# 专门为小拇指放宽阈值，允许手腕转动时产生的 2D 角度形变
PINKY_STRAIGHT_THRESHOLD = 110 

# J 动态检测 (上下晃动)
TRAJ_WINDOW = 24          # 轨迹缓存长度
MIN_TRACK_FRAMES = 8      # 少于这个帧数时，先按 I 看

# 移除了静止阈值对分类的限制，I 现在是默认状态
TH_MOVE = 0.60            # 明显有动作的总路径阈值
TH_WAVE_CURVE = 1.5       # 判断“来回晃动”的折返阈值 (路径总长/首尾距离)
YX_RATIO = 1.5            # Y轴运动量是X轴的多少倍才算“上下”

# 防断触关键参数
NO_HAND_GRACE = 5         # 手完全丢失后允许保留的帧数
FAMILY_GRACE = 10         # 家族判定失败后允许保留的帧数（握拳后约等待10帧消失）

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
    用掌宽做归一化：5(食指根) 到 17(小指根)
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


# =========================
# 手指 straight / bent 判断
# =========================
def is_finger_straight(hand, mcp_id, pip_id, dip_id, tip_id, threshold=160):
    angle1 = angle_3points(hand[mcp_id], hand[pip_id], hand[dip_id])
    angle2 = angle_3points(hand[pip_id], hand[dip_id], hand[tip_id])
    ok = (angle1 > threshold) and (angle2 > threshold)
    return ok, angle1, angle2


# =========================
# I / J 家族判定
# =========================
def is_ij_family(index_ok, middle_ok, ring_ok, pinky_ok):
    """
    I / J 共用静态家族：
    小拇指伸直，其他三指弯曲
    """
    return pinky_ok and (not index_ok) and (not middle_ok) and (not ring_ok)


def is_ij_family_keep(index_ok, middle_ok, ring_ok, pinky_ok):
    """
    跟踪开始后，续判放宽一些，减少断触。
    【核心修复】：小拇指必须是伸直的，握拳绝对不行！
    其余三指（食、中、无名）只要有两个以上弯曲即可（允许一个误判）。
    """
    other_bent_count = (not index_ok) + (not middle_ok) + (not ring_ok)
    return pinky_ok and (other_bent_count >= 2)


# =========================
# I / J 动态分类 (I为绝对保底版)
# =========================
def classify_ij_dynamic(
    samples,
    min_track_frames=8,
    th_move=0.60,
    th_wave_curve=1.5,
    yx_ratio=1.5
):
    """
    极简版动态分类：
    1) 只要不满足 J，怎么动默认都是 I
    2) 上下明显晃动 -> J
    """
    if len(samples) == 0:
        return "not_ij", {}

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

    not_enough_frames = len(traj) < min_track_frames

    # 计算 X 和 Y 方向的累计绝对位移
    sum_dx = 0.0
    sum_dy = 0.0
    for i in range(1, len(traj)):
        sum_dx += abs(traj[i][0] - traj[i-1][0])
        sum_dy += abs(traj[i][1] - traj[i-1][1])

    # J的三个条件
    moved_enough = total_len > th_move
    is_vertical = sum_dy > (sum_dx * yx_ratio)
    is_waving = curve_ratio > th_wave_curve

    if not_enough_frames:
        cls = "I"
    elif moved_enough and is_vertical and is_waving:
        cls = "J"
    else:
        cls = "I"  # 无论你是在移动、还是静止，只要姿势还在，统统都是 I

    return cls, {
        "num_points": len(traj),
        "total_len": total_len,
        "end_disp": end_disp,
        "curve_ratio": curve_ratio,
        "sum_dx": sum_dx,
        "sum_dy": sum_dy,
        "moved_enough": moved_enough,
        "is_vertical": is_vertical,
        "is_waving": is_waving,
    }


# =========================
# 多帧稳定
# =========================
def stabilize_cls(history, vote_min=3):
    if len(history) == 0:
        return "none"

    valid = [c for c in history if c in ["I", "J"]]
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
last_raw_cls = "not_ij"
last_stable_cls = "not_ij"

start_time = time.monotonic()

with HandLandmarker.create_from_options(options) as landmarker:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("读取摄像头画面失败")
            break
            
        # 镜像反转画面（操作更直观）
        frame = cv2.flip(frame, 1)

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
            pinky_ok, pa1, pa2 = is_finger_straight(hand, 17, 18, 19, 20, PINKY_STRAIGHT_THRESHOLD)

            ij_family_start = is_ij_family(index_ok, middle_ok, ring_ok, pinky_ok)
            ij_family_keep = is_ij_family_keep(index_ok, middle_ok, ring_ok, pinky_ok)

            # 当前帧小拇指尖 (20)
            px = hand[20].x
            py = hand[20].y
            scale = palm_scale(hand)

            # 控制跟踪生命周期
            if ij_family_start:
                tracking_active = True
                family_miss_count = 0
                traj_buffer.append((px, py, scale))
            else:
                if tracking_active:
                    if ij_family_keep:
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
                            raw_cls = "not_ij"
                            stable_cls = "not_ij"
                else:
                    raw_cls = "not_ij"
                    stable_cls = "not_ij"

            # 只要 tracking_active，就继续判 I/J
            if tracking_active and len(traj_buffer) > 0:
                raw_cls, info = classify_ij_dynamic(
                    list(traj_buffer),
                    min_track_frames=MIN_TRACK_FRAMES,
                    th_move=TH_MOVE,
                    th_wave_curve=TH_WAVE_CURVE,
                    yx_ratio=YX_RATIO,
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

            # 高亮小拇指尖 20
            x20 = int(hand[20].x * w)
            y20 = int(hand[20].y * h)
            cv2.circle(frame, (x20, y20), 7, (0, 255, 255), 2)

            # ===== 画轨迹 =====
            traj_px = [(int(x * w), int(y * h)) for x, y, _ in traj_buffer]
            for i in range(1, len(traj_px)):
                cv2.line(frame, traj_px[i - 1], traj_px[i], (255, 0, 0), 2)

            if len(traj_px) > 0:
                cv2.circle(frame, traj_px[0], 5, (0, 255, 0), -1)
                cv2.circle(frame, traj_px[-1], 5, (0, 0, 255), -1)

            # ===== 标题信息 =====
            cls_color = (0, 0, 255) if stable_cls == "J" else (0, 255, 255) if stable_cls == "I" else (200, 200, 200)

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
                f"tracking={tracking_active} family_start={ij_family_start} family_keep={ij_family_keep}",
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

                sum_dx = info.get("sum_dx", 0)
                sum_dy = info.get("sum_dy", 0)

                moved_enough = info.get("moved_enough", False)
                is_vertical = info.get("is_vertical", False)
                is_waving = info.get("is_waving", False)

                # 第一行数据：路径与折返率
                cv2.putText(
                    frame,
                    f"path={total_len:.3f} end={end_disp:.3f} curve={curve_ratio:.3f}",
                    (20, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.56,
                    (255, 255, 255),
                    2
                )

                # 第二行数据：方向位移与判定标志
                cv2.putText(
                    frame,
                    f"dx={sum_dx:.2f} dy={sum_dy:.2f} vertical={is_vertical} waving={is_waving}",
                    (20, 155),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.53,
                    (255, 255, 255),
                    2
                )

                # 第三行数据：综合状态
                cv2.putText(
                    frame,
                    f"move={moved_enough} miss_family={family_miss_count} miss_hand={no_hand_miss_count}",
                    (20, 185),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.53,
                    (255, 255, 255),
                    2
                )

        else:
            # 当前帧完全没检测到手
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
                raw_cls = "not_ij"
                stable_cls = "not_ij"
                info = {}

        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()