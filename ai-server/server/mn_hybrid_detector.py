import math

FINGER_STRAIGHT_THRESHOLD = 160
TH_GAP = 0.60
TH_E = 0.45
TH_SEG = 0.20
TH_Z = 0.15


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
        sum(p[1] for p in points) / len(points),
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


def is_finger_straight(hand, mcp_id, pip_id, dip_id, tip_id, threshold=FINGER_STRAIGHT_THRESHOLD):
    angle1 = angle_3points(hand[mcp_id], hand[pip_id], hand[dip_id])
    angle2 = angle_3points(hand[pip_id], hand[dip_id], hand[tip_id])
    ok = (angle1 > threshold) and (angle2 > threshold)
    return ok, angle1, angle2


def is_fist_family(index_ok, middle_ok, ring_ok, pinky_ok):
    bent_count = int(not index_ok) + int(not middle_ok) + int(not ring_ok) + int(not pinky_ok)
    return bent_count >= 3, bent_count


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


def classify_mnt_robust(hand, fist_family, th_gap=TH_GAP, th_e=TH_E, th_seg=TH_SEG, th_z=TH_Z):
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
        # 越过无名指，是 M
        best_name = "M"
    elif t_thumb > t_middle - 0.05:
        # 在中指和无名指之间，是 N
        best_name = "N"
    elif t_thumb > -0.15:
        # 在食指（投影起点为0）和中指之间，预留 -0.15 容差，是 T
        best_name = "T"
    else:
        # 放在了食指外围太远的地方，直接拦截
        base_info["best"] = "Out_of_bounds"
        return "not_mnt", base_info

    # 获取缝隙坐标，用于后续深度校验
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
    base_info["dT_raw"] = d_t_raw
    base_info["dN_raw"] = d_n_raw
    base_info["dM_raw"] = d_m_raw

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


def classify_mnt_only(hand):
    index_ok, _, _ = is_finger_straight(hand, 5, 6, 7, 8)
    middle_ok, _, _ = is_finger_straight(hand, 9, 10, 11, 12)
    ring_ok, _, _ = is_finger_straight(hand, 13, 14, 15, 16)
    pinky_ok, _, _ = is_finger_straight(hand, 17, 18, 19, 20)
    fist_family, _ = is_fist_family(index_ok, middle_ok, ring_ok, pinky_ok)

    cls, info = classify_mnt_robust(hand, fist_family)
    
    if cls not in ("M", "N", "T"):
        cls = "not_mnt"
        
    info.update(
        {
            "index_ok": index_ok,
            "middle_ok": middle_ok,
            "ring_ok": ring_ok,
            "pinky_ok": pinky_ok,
            "fist_family": fist_family,
        }
    )
    return cls, info