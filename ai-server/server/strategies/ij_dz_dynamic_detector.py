import math
from collections import Counter, deque

# =========================
# 可调参数 (已针对 YOLO+MediaPipe 联合运行时的低帧率做极大优化)
# =========================
FINGER_STRAIGHT_THRESHOLD = 160
PINKY_STRAIGHT_THRESHOLD = 110  

# I/J 动态参数 (上下晃动)
IJ_TRAJ_WINDOW = 12           # [降低] 帧率较低时，缓存12帧(约0.5-1秒)就足够了
IJ_MIN_TRACK_FRAMES = 4       # [降低] 积累4帧即可开始判断
IJ_TH_MOVE = 0.35             # [降低] 动作幅度要求大幅放宽
IJ_TH_WAVE_CURVE = 1.25       # [降低] 折返阈值放宽，不需要非常完美的来回
IJ_YX_RATIO = 1.2             # [降低] 允许一定程度的斜向误差
IJ_NO_HAND_GRACE = 3          # [降低] 丢失手后尽快重置，减少粘滞延迟
IJ_FAMILY_GRACE = 5           # [降低] 握拳后断开的延迟降低，迅速切回 YOLO
IJ_VOTE_WINDOW = 3            # [降低] 投票窗口缩小，极速响应
IJ_VOTE_MIN = 2               # [降低] 2票即可确认

# D/Z 动态参数 (左右晃动)
DZ_TRAJ_WINDOW = 12           
DZ_MIN_TRACK_FRAMES = 4       
DZ_TH_MOVE = 0.35             
DZ_TH_WAVE_CURVE = 1.25       
DZ_XY_RATIO = 1.2             
DZ_NO_HAND_GRACE = 3
DZ_FAMILY_GRACE = 5           
DZ_VOTE_WINDOW = 3
DZ_VOTE_MIN = 2


def point_xy(lm):
    return (lm.x, lm.y)


def dist_xy(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.sqrt(dx * dx + dy * dy)


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


def path_length(points):
    if len(points) < 2:
        return 0.0
    total = 0.0
    for i in range(1, len(points)):
        total += dist_xy(points[i - 1], points[i])
    return total


def smooth_points(points, window=3):
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


def is_finger_straight(hand, mcp_id, pip_id, dip_id, tip_id, threshold=FINGER_STRAIGHT_THRESHOLD):
    angle1 = angle_3points(hand[mcp_id], hand[pip_id], hand[dip_id])
    angle2 = angle_3points(hand[pip_id], hand[dip_id], hand[tip_id])
    ok = (angle1 > threshold) and (angle2 > threshold)
    return ok, angle1, angle2


# =========================
# I / J 逻辑
# =========================
def is_ij_family(index_ok, middle_ok, ring_ok, pinky_ok):
    return pinky_ok and (not index_ok) and (not middle_ok) and (not ring_ok)


def is_ij_family_keep(index_ok, middle_ok, ring_ok, pinky_ok):
    other_bent_count = (not index_ok) + (not middle_ok) + (not ring_ok)
    return pinky_ok and (other_bent_count >= 2)


def classify_ij_dynamic(samples):
    if len(samples) == 0:
        return "not_ij", {}

    points = [(s[0], s[1]) for s in samples]
    scales = [s[2] for s in samples]
    mean_scale = max(sum(scales) / len(scales), 1e-6)
    smoothed = smooth_points(points, window=3)

    x0, y0 = smoothed[0]
    traj = [((x - x0) / mean_scale, (y - y0) / mean_scale) for x, y in smoothed]

    total_len = path_length(traj)
    end_disp = dist_xy(traj[0], traj[-1])
    curve_ratio = total_len / max(end_disp, 1e-6)

    not_enough_frames = len(traj) < IJ_MIN_TRACK_FRAMES

    sum_dx = 0.0
    sum_dy = 0.0
    for i in range(1, len(traj)):
        sum_dx += abs(traj[i][0] - traj[i-1][0])
        sum_dy += abs(traj[i][1] - traj[i-1][1])

    moved_enough = total_len > IJ_TH_MOVE
    is_vertical = sum_dy > (sum_dx * IJ_YX_RATIO)
    is_waving = curve_ratio > IJ_TH_WAVE_CURVE

    if not_enough_frames:
        cls = "I"
    elif moved_enough and is_vertical and is_waving:
        cls = "J"
    else:
        cls = "I" 

    return cls, {}


# =========================
# D / Z 逻辑
# =========================
def is_dz_family(index_ok, middle_ok, ring_ok, pinky_ok):
    return index_ok and (not middle_ok) and (not ring_ok) and (not pinky_ok)


def is_dz_family_keep(index_ok, middle_ok, ring_ok, pinky_ok):
    other_bent_count = (not middle_ok) + (not ring_ok) + (not pinky_ok)
    return index_ok and (other_bent_count >= 2)


def classify_dz_dynamic(samples):
    if len(samples) == 0:
        return "not_dz", {}

    points = [(s[0], s[1]) for s in samples]
    scales = [s[2] for s in samples]
    mean_scale = max(sum(scales) / len(scales), 1e-6)
    smoothed = smooth_points(points, window=3)

    x0, y0 = smoothed[0]
    traj = [((x - x0) / mean_scale, (y - y0) / mean_scale) for x, y in smoothed]

    total_len = path_length(traj)
    end_disp = dist_xy(traj[0], traj[-1])
    curve_ratio = total_len / max(end_disp, 1e-6)

    not_enough_frames = len(traj) < DZ_MIN_TRACK_FRAMES

    sum_dx = 0.0
    sum_dy = 0.0
    for i in range(1, len(traj)):
        sum_dx += abs(traj[i][0] - traj[i-1][0])
        sum_dy += abs(traj[i][1] - traj[i-1][1])

    moved_enough = total_len > DZ_TH_MOVE
    is_horizontal = sum_dx > (sum_dy * DZ_XY_RATIO)
    is_waving = curve_ratio > DZ_TH_WAVE_CURVE

    if not_enough_frames:
        cls = "D"
    elif moved_enough and is_horizontal and is_waving:
        cls = "Z"
    else:
        cls = "D" 

    return cls, {}


# =========================
# 核心 Session 状态机
# =========================
def stabilize_family(history, valid_labels, vote_min):
    if len(history) == 0:
        return "none"
    valid = [c for c in history if c in valid_labels]
    if len(valid) == 0:
        return history[-1]
    top_cls, top_count = Counter(valid).most_common(1)[0]
    if top_count >= vote_min:
        return top_cls
    return valid[-1]


class DynamicLetterSession:
    def __init__(self, base_label):
        self.base_label = base_label
        if base_label == "I":
            self.point_index = 20
            self.traj_window = IJ_TRAJ_WINDOW
            self.no_hand_grace = IJ_NO_HAND_GRACE
            self.family_grace = IJ_FAMILY_GRACE
            self.valid_labels = ("I", "J")
            self.vote_min = IJ_VOTE_MIN
        else:
            self.point_index = 8
            self.traj_window = DZ_TRAJ_WINDOW
            self.no_hand_grace = DZ_NO_HAND_GRACE
            self.family_grace = DZ_FAMILY_GRACE
            self.valid_labels = ("D", "Z")
            self.vote_min = DZ_VOTE_MIN

        self.reset()

    def reset(self):
        self.traj_buffer = deque(maxlen=self.traj_window)
        self.cls_history = deque(maxlen=self.vote_min + 2)
        self.family_miss_count = 0
        self.no_hand_miss_count = 0
        self.tracking_active = False
        self.last_raw_cls = self.base_label
        self.last_stable_cls = self.base_label

    def update(self, hand):
        info = {}
        if hand is None:
            self.no_hand_miss_count += 1
            if self.tracking_active and self.no_hand_miss_count <= self.no_hand_grace:
                return {"raw": self.last_raw_cls, "stable": self.last_stable_cls, "info": info}
            self.reset()
            return {"raw": "not_dynamic", "stable": "not_dynamic", "info": info}

        self.no_hand_miss_count = 0

        index_ok, _, _ = is_finger_straight(hand, 5, 6, 7, 8)
        middle_ok, _, _ = is_finger_straight(hand, 9, 10, 11, 12)
        ring_ok, _, _ = is_finger_straight(hand, 13, 14, 15, 16)
        pinky_threshold = PINKY_STRAIGHT_THRESHOLD if self.base_label == "I" else FINGER_STRAIGHT_THRESHOLD
        pinky_ok, _, _ = is_finger_straight(hand, 17, 18, 19, 20, pinky_threshold)

        if self.base_label == "I":
            family_start = is_ij_family(index_ok, middle_ok, ring_ok, pinky_ok)
            family_keep = is_ij_family_keep(index_ok, middle_ok, ring_ok, pinky_ok)
            classifier = classify_ij_dynamic
        else:
            family_start = is_dz_family(index_ok, middle_ok, ring_ok, pinky_ok)
            family_keep = is_dz_family_keep(index_ok, middle_ok, ring_ok, pinky_ok)
            classifier = classify_dz_dynamic

        px = hand[self.point_index].x
        py = hand[self.point_index].y
        scale = palm_scale(hand)

        if family_start:
            self.tracking_active = True
            self.family_miss_count = 0
            self.traj_buffer.append((px, py, scale))
        elif self.tracking_active:
            if family_keep:
                self.family_miss_count = 0
                self.traj_buffer.append((px, py, scale))
            else:
                self.family_miss_count += 1
                if self.family_miss_count <= self.family_grace:
                    self.traj_buffer.append((px, py, scale))
                else:
                    self.reset()
                    return {"raw": "not_dynamic", "stable": "not_dynamic", "info": info}
        else:
            return {"raw": "not_dynamic", "stable": "not_dynamic", "info": info}

        if self.tracking_active and len(self.traj_buffer) > 0:
            raw_cls, info = classifier(list(self.traj_buffer))
            self.cls_history.append(raw_cls)
            stable_cls = stabilize_family(self.cls_history, self.valid_labels, self.vote_min)
            self.last_raw_cls = raw_cls
            self.last_stable_cls = stable_cls

        return {"raw": self.last_raw_cls, "stable": self.last_stable_cls, "info": info}