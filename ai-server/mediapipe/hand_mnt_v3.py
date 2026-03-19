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
MIN_HAND_DETECTION_CONFIDENCE = 0.35
MIN_HAND_PRESENCE_CONFIDENCE = 0.30
MIN_TRACKING_CONFIDENCE = 0.30

FINGER_STRAIGHT_THRESHOLD = 160
TH_GAP = 0.55
TH_E = 0.45
TH_SEG = 0.18
TH_Z = 0.10

TH_GAP_KEEP = 0.72
TH_SEG_KEEP = 0.28
TH_Z_KEEP = 0.18

NO_HAND_GRACE = 5
FIST_GRACE = 8

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

def avg_xy(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def avg_multi_xy(points):
    return (
        sum(p[0] for p in points) / len(points),
        sum(p[1] for p in points) / len(points)
    )

def avg_z(hand, ids):
    return sum(hand[i].z for i in ids) / len(ids)

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


# =========================
# 四指状态判断
# =========================
def is_finger_straight(hand, mcp_id, pip_id, dip_id, tip_id, threshold=160):
    angle1 = angle_3points(hand[mcp_id], hand[pip_id], hand[dip_id])
    angle2 = angle_3points(hand[pip_id], hand[dip_id], hand[tip_id])
    ok = (angle1 > threshold) and (angle2 > threshold)
    return ok, angle1, angle2

def is_fist_family(index_ok, middle_ok, ring_ok, pinky_ok):
    bent_count = int(not index_ok) + int(not middle_ok) + int(not ring_ok) + int(not pinky_ok)
    return bent_count >= 3, bent_count

def is_fist_family_keep(index_ok, middle_ok, ring_ok, pinky_ok):
    bent_count = int(not index_ok) + int(not middle_ok) + int(not ring_ok) + int(not pinky_ok)
    return bent_count >= 2, bent_count


# =========================
# M/N/T gap 定义
# =========================
def gap_segment(hand, mcp_a, mcp_b, pip_a, pip_b):
    top = midpoint_xy(hand[pip_a], hand[pip_b])
    bottom = midpoint_xy(hand[mcp_a], hand[mcp_b])
    return top, bottom

def gap_center(hand, mcp_a, mcp_b, pip_a, pip_b):
    root_mid = midpoint_xy(hand[mcp_a], hand[mcp_b])
    pip_mid = midpoint_xy(hand[pip_a], hand[pip_b])
    return avg_xy(root_mid, pip_mid)

def get_gap_ids(best_name):
    if best_name == "T":
        return [5, 6, 9, 10]
    if best_name == "N":
        return [9, 10, 13, 14]
    if best_name == "M":
        return [13, 14, 17, 18]
    return []


# =========================
# M/N/T 分类（拓扑硬边界 + 深度锁死）
# =========================
def classify_mnt_robust(hand, fist_family, th_gap=0.55, th_e=0.45, th_seg=0.18, th_z=0.10):
    if not fist_family:
        return "not_fist", {}

    thumb_tip = point_xy(hand[4])
    scale = palm_scale(hand)

    # 1. 构建手掌横向参考系 (食指根部 5 -> 小指根部 17)
    p5 = point_xy(hand[5])
    p17 = point_xy(hand[17])
    palm_vec = (p17[0] - p5[0], p17[1] - p5[1])
    palm_len2 = dot2(palm_vec, palm_vec)

    if palm_len2 < 1e-6:
        return "uncertain", {}

    # 投影辅助函数：计算拇指横向相对比例
    def get_proj_t(p):
        vec = (p[0] - p5[0], p[1] - p5[1])
        return dot2(vec, palm_vec) / palm_len2

    t_thumb = get_proj_t(thumb_tip)
    t_middle = get_proj_t(point_xy(hand[9]))  # 中指根部边界
    t_ring = get_proj_t(point_xy(hand[13]))   # 无名指根部边界

    base_info = {
        "t_thumb": t_thumb, "t_middle": t_middle, "t_ring": t_ring,
        "best": None, "seg_dist": None, "seg_t": None,
        "thumb_z": None, "gap_z": None, "z_diff": None,
        "inserted_xy": False, "inserted_z": False,
        "gap_t": None, "gap_n": None, "gap_m": None,
        "seg_top": None, "seg_bottom": None
    }

    # --- 核心优化 1：三区域硬边界防线 ---
    if t_thumb > t_ring - 0.02:
        best_name = "M"
    elif t_thumb > t_middle - 0.05:
        best_name = "N"
    elif t_thumb > -0.15:
        best_name = "T"
    else:
        base_info["best"] = "Out_of_bounds"
        return "not_mnt", base_info

    # 获取缝隙坐标，用于后续深度校验和画图
    gap_t = gap_center(hand, 5, 9, 6, 10)
    gap_n = gap_center(hand, 9, 13, 10, 14)
    gap_m = gap_center(hand, 13, 17, 14, 18)
    base_info["gap_t"] = gap_t
    base_info["gap_n"] = gap_n
    base_info["gap_m"] = gap_m

    d_t_raw = dist_xy(thumb_tip, gap_t) / scale
    d_n_raw = dist_xy(thumb_tip, gap_n) / scale
    d_m_raw = dist_xy(thumb_tip, gap_m) / scale

    if best_name == "M":
        raw_best_d = d_m_raw
    elif best_name == "N":
        raw_best_d = d_n_raw
    else:
        raw_best_d = d_t_raw

    # 基础校验：大拇指是否收拢
    tips_center = avg_multi_xy([
        point_xy(hand[8]), point_xy(hand[12]),
        point_xy(hand[16]), point_xy(hand[20])
    ])
    d_e = dist_xy(thumb_tip, tips_center) / scale
    base_info["dE"] = d_e

    if d_e < th_e:
        return "not_mnt", base_info

    if raw_best_d > th_gap * 1.2:
        return "uncertain", base_info

    # --- 核心优化 2：深度锁死 ---
    if best_name == "T":
        seg_top, seg_bottom = gap_segment(hand, 5, 9, 6, 10)
    elif best_name == "N":
        seg_top, seg_bottom = gap_segment(hand, 9, 13, 10, 14)
    else:
        seg_top, seg_bottom = gap_segment(hand, 13, 17, 14, 18)

    seg_dist, t = point_to_segment_distance_and_t(thumb_tip, seg_top, seg_bottom)
    seg_dist_norm = seg_dist / scale

    # 逼迫大拇指必须“深插”到根部缝隙中 (-0.2 到 0.65)
    inserted_xy = (seg_dist_norm < th_seg) and (-0.2 <= t <= 0.65)

    gap_ids = get_gap_ids(best_name)
    gap_z = avg_z(hand, gap_ids)
    thumb_z = hand[4].z
    z_diff = abs(thumb_z - gap_z)
    inserted_z = (z_diff < th_z)
    
    inserted = inserted_xy and inserted_z
    cls = best_name if inserted else "not_mnt"

    base_info.update({
        "best": best_name,
        "seg_dist": seg_dist_norm,
        "seg_t": t,
        "thumb_z": thumb_z,
        "gap_z": gap_z,
        "z_diff": z_diff,
        "inserted_xy": inserted_xy,
        "inserted_z": inserted_z,
        "seg_top": seg_top,
        "seg_bottom": seg_bottom
    })
    return cls, base_info


def to_mnt_or_yolo(cls):
    return cls if cls in ["M", "N", "T"] else "yolo"


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
# MediaPipe 初始化与主循环
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
tracking_active = False
fist_miss_count = 0
no_hand_miss_count = 0
last_raw_cls = "yolo"
last_stable_cls = "yolo"
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
            no_hand_miss_count = 0
            hand = result.hand_landmarks[0]

            index_ok, _, _ = is_finger_straight(hand, 5, 6, 7, 8, FINGER_STRAIGHT_THRESHOLD)
            middle_ok, _, _ = is_finger_straight(hand, 9, 10, 11, 12, FINGER_STRAIGHT_THRESHOLD)
            ring_ok, _, _ = is_finger_straight(hand, 13, 14, 15, 16, FINGER_STRAIGHT_THRESHOLD)
            pinky_ok, _, _ = is_finger_straight(hand, 17, 18, 19, 20, FINGER_STRAIGHT_THRESHOLD)

            fist_family_start, bent_count = is_fist_family(index_ok, middle_ok, ring_ok, pinky_ok)
            fist_family_keep, bent_count_keep = is_fist_family_keep(index_ok, middle_ok, ring_ok, pinky_ok)

            raw_cls = last_raw_cls
            stable_cls = last_stable_cls
            raw_cls_base = "not_fist"
            info = {}

            if fist_family_start:
                tracking_active = True
                fist_miss_count = 0
            elif tracking_active and fist_family_keep:
                fist_miss_count = 0
            elif tracking_active:
                fist_miss_count += 1
                if fist_miss_count > FIST_GRACE:
                    tracking_active = False
                    fist_miss_count = 0
                    cls_history.clear()
                    last_raw_cls = "yolo"
                    last_stable_cls = "yolo"
                    raw_cls = "yolo"
                    stable_cls = "yolo"
            else:
                raw_cls = "yolo"
                stable_cls = "yolo"

            if tracking_active:
                use_keep_thresholds = not fist_family_start

                # 调用更新后的 MNT 识别逻辑
                raw_cls_base, info = classify_mnt_robust(
                    hand,
                    True,
                    th_gap=TH_GAP_KEEP if use_keep_thresholds else TH_GAP,
                    th_e=TH_E,
                    th_seg=TH_SEG_KEEP if use_keep_thresholds else TH_SEG,
                    th_z=TH_Z_KEEP if use_keep_thresholds else TH_Z
                )

                candidate_raw = to_mnt_or_yolo(raw_cls_base)

                if candidate_raw in ["M", "N", "T"]:
                    raw_cls = candidate_raw
                    cls_history.append(raw_cls)
                    stable_cls = stabilize_cls(cls_history, vote_min=VOTE_MIN)
                    last_raw_cls = raw_cls
                    last_stable_cls = stable_cls
                elif fist_miss_count <= FIST_GRACE and len(cls_history) > 0:
                    raw_cls = last_raw_cls
                    stable_cls = last_stable_cls
                else:
                    raw_cls = "yolo"
                    cls_history.append(raw_cls)
                    stable_cls = stabilize_cls(cls_history, vote_min=VOTE_MIN)
                    last_raw_cls = raw_cls
                    last_stable_cls = stable_cls

            # ---------------- 绘制部分 ----------------
            for lm in hand:
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            for i in tip_ids:
                lm = hand[i]
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 7, (0, 255, 255), 2)
                cv2.putText(frame, str(i), (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            for i in root_ids:
                lm = hand[i]
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 7, (255, 0, 255), 2)
                cv2.putText(frame, str(i), (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

            if info:
                # 绘制 T/N/M 的 gap 辅助点
                for name, gap in [("T", info.get("gap_t")), ("N", info.get("gap_n")), ("M", info.get("gap_m"))]:
                    if gap is None:
                        continue
                    gx = int(gap[0] * w)
                    gy = int(gap[1] * h)
                    cv2.circle(frame, (gx, gy), 6, (255, 255, 0), 2)
                    cv2.putText(frame, name, (gx + 6, gy - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            if info and info.get("seg_top") is not None and info.get("seg_bottom") is not None:
                seg_top = info["seg_top"]
                seg_bottom = info["seg_bottom"]
                x1, y1 = int(seg_top[0] * w), int(seg_top[1] * h)
                x2, y2 = int(seg_bottom[0] * w), int(seg_bottom[1] * h)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 128, 255), 2)

            if result.handedness:
                label = result.handedness[0][0].category_name
                score = result.handedness[0][0].score
                cv2.putText(frame, f"{label} {score:.2f}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            cls_color = (0, 0, 255) if stable_cls in ["M", "N", "T"] else (200, 200, 200)

            cv2.putText(frame, f"raw={raw_cls} stable={stable_cls}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, cls_color, 2)
            cv2.putText(frame, f"base_raw={raw_cls_base}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            cv2.putText(frame, f"fist_start={fist_family_start} fist_keep={fist_family_keep} bent={bent_count}/{bent_count_keep}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            cv2.putText(
                frame,
                f"index={'S' if index_ok else 'B'} middle={'S' if middle_ok else 'B'} ring={'S' if ring_ok else 'B'} pinky={'S' if pinky_ok else 'B'}",
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2
            )

            if info:
                t_thumb = info.get("t_thumb", -1)
                t_middle = info.get("t_middle", -1)
                t_ring = info.get("t_ring", -1)
                d_e = info.get("dE", -1)
                best = info.get("best")
                seg_dist = info.get("seg_dist")
                seg_t = info.get("seg_t")
                thumb_z = info.get("thumb_z")
                gap_z = info.get("gap_z")
                z_diff = info.get("z_diff")
                inserted_xy = info.get("inserted_xy", False)
                inserted_z = info.get("inserted_z", False)

                # 更新显示为新的拓扑特征指标
                cv2.putText(frame, f"thumb={t_thumb:.2f} mid(N)={t_middle:.2f} ring(M)={t_ring:.2f} dE={d_e:.2f}", (20, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)
                cv2.putText(frame, f"best_zone={best}", (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)

                if seg_dist is not None and seg_t is not None:
                    cv2.putText(frame, f"seg_dist={seg_dist:.3f} seg_t={seg_t:.3f} (must < 0.65)", (20, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)

                if thumb_z is not None and gap_z is not None and z_diff is not None:
                    cv2.putText(frame, f"thumb_z={thumb_z:.3f} gap_z={gap_z:.3f} z_diff={z_diff:.3f}", (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)

                cv2.putText(frame, f"xy_ok={inserted_xy} z_ok={inserted_z}", (20, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)

                cv2.putText(
                    frame,
                    f"tracking={tracking_active} miss_fist={fist_miss_count} miss_hand={no_hand_miss_count}",
                    (20, 340),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2
                )
                cv2.putText(
                    frame,
                    f"TH_GAP={TH_GAP:.2f} TH_SEG={TH_SEG:.2f} TH_Z={TH_Z:.2f}",
                    (20, 370),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (255, 255, 255),
                    2
                )

        else:
            no_hand_miss_count += 1
            if tracking_active and no_hand_miss_count <= NO_HAND_GRACE:
                raw_cls = last_raw_cls
                stable_cls = last_stable_cls
                cls_color = (0, 0, 255) if stable_cls in ["M", "N", "T"] else (200, 200, 200)
                cv2.putText(frame, f"raw={raw_cls} stable={stable_cls}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, cls_color, 2)
                cv2.putText(frame, f"tracking={tracking_active} miss_fist={fist_miss_count} miss_hand={no_hand_miss_count}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            else:
                tracking_active = False
                fist_miss_count = 0
                cls_history.clear()
                last_raw_cls = "yolo"
                last_stable_cls = "yolo"

        cv2.imshow("MNT Vision Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()