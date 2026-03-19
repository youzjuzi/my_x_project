import math


FINGER_STRAIGHT_THRESHOLD = 160
TH_GAP = 0.55
TH_MARGIN = 0.08
TH_E = 0.45
TH_SEG = 0.18
TH_Z = 0.10


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


def classify_mnt_robust(hand, fist_family, th_gap=TH_GAP, th_margin=TH_MARGIN, th_e=TH_E, th_seg=TH_SEG, th_z=TH_Z):
    if not fist_family:
        return "not_fist", {}

    thumb_tip = point_xy(hand[4])
    scale = palm_scale(hand)

    gap_t = gap_center(hand, 5, 9, 6, 10)
    gap_n = gap_center(hand, 9, 13, 10, 14)
    gap_m = gap_center(hand, 13, 17, 14, 18)

    d_t = dist_xy(thumb_tip, gap_t) / scale
    d_n = dist_xy(thumb_tip, gap_n) / scale
    d_m = dist_xy(thumb_tip, gap_m) / scale

    tips_center = avg_multi_xy([point_xy(hand[8]), point_xy(hand[12]), point_xy(hand[16]), point_xy(hand[20])])
    d_e = dist_xy(thumb_tip, tips_center) / scale

    if d_e < th_e:
        return "not_mnt", {"dT": d_t, "dN": d_n, "dM": d_m, "dE": d_e}

    ranked = sorted([("T", d_t), ("N", d_n), ("M", d_m)], key=lambda x: x[1])
    best_name, best_d = ranked[0]
    second_name, second_d = ranked[1]
    margin = second_d - best_d

    if not (best_d < th_gap and margin > th_margin):
        return "uncertain", {
            "dT": d_t,
            "dN": d_n,
            "dM": d_m,
            "dE": d_e,
            "best": best_name,
            "margin": margin,
        }

    if best_name == "T":
        seg_top, seg_bottom = gap_segment(hand, 5, 9, 6, 10)
    elif best_name == "N":
        seg_top, seg_bottom = gap_segment(hand, 9, 13, 10, 14)
    else:
        seg_top, seg_bottom = gap_segment(hand, 13, 17, 14, 18)

    seg_dist, t = point_to_segment_distance_and_t(thumb_tip, seg_top, seg_bottom)
    seg_dist_norm = seg_dist / scale
    inserted_xy = (seg_dist_norm < th_seg) and (0.05 <= t <= 1.05)

    gap_ids = get_gap_ids(best_name)
    gap_z = avg_z(hand, gap_ids)
    thumb_z = hand[4].z
    z_diff = abs(thumb_z - gap_z)
    inserted_z = z_diff < th_z
    inserted = inserted_xy and inserted_z

    if inserted:
        cls = best_name
    elif best_name == "T":
        cls = "S_or_other"
    else:
        cls = "not_mnt"

    return cls, {
        "dT": d_t,
        "dN": d_n,
        "dM": d_m,
        "dE": d_e,
        "best": best_name,
        "best_d": best_d,
        "second": second_name,
        "second_d": second_d,
        "margin": margin,
        "seg_dist": seg_dist_norm,
        "seg_t": t,
        "thumb_z": thumb_z,
        "gap_z": gap_z,
        "z_diff": z_diff,
        "inserted_xy": inserted_xy,
        "inserted_z": inserted_z,
    }


def classify_mn_only(hand):
    index_ok, _, _ = is_finger_straight(hand, 5, 6, 7, 8)
    middle_ok, _, _ = is_finger_straight(hand, 9, 10, 11, 12)
    ring_ok, _, _ = is_finger_straight(hand, 13, 14, 15, 16)
    pinky_ok, _, _ = is_finger_straight(hand, 17, 18, 19, 20)
    fist_family, _ = is_fist_family(index_ok, middle_ok, ring_ok, pinky_ok)

    cls, info = classify_mnt_robust(hand, fist_family)
    if cls not in ("M", "N"):
        cls = "not_mn"
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
