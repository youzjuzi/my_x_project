"""
CPU 推理性能优化配置
====================================
当检测到没有 CUDA GPU（config.DEVICE == "cpu"）时自动激活，无需手动修改。

优化策略：
  ② 限帧   - 每隔 INFERENCE_EVERY_N 帧才推一次（空帧直接跳过，不送入模型）
  ③ 降分辨  - 推理前将图像缩小到 INFERENCE_IMGSZ，减少模型计算量

参数可在 ai-server/.env 中覆盖：
  CPU_PERF_FRAME_SKIP=2      # 每 N 帧推理一次（1=不跳帧, 2=每隔一帧, 3=每隔两帧）
  CPU_PERF_IMGSZ=416         # 推理前缩放分辨率（0=不缩放, 推荐 320 或 416）
"""

import os
import cv2
from . import config

# ===== 是否启用（自动检测，无需改代码）=====
ENABLED: bool = (config.DEVICE == "cpu")

# ===== ② 限帧：每隔 N 帧推理一次 =====
# 从 .env 读取，默认 2（30fps 摄像头 → 推理约 15fps，用户几乎无感知）
INFERENCE_EVERY_N: int = max(1, int(os.environ.get("CPU_PERF_FRAME_SKIP", "2")))

# ===== ③ 降分辨率：推理前缩放到此边长 =====
# 从 .env 读取，默认 416（从 640 降到 416，推理速度约提升 2 倍，精度损失极小）
# 设为 0 则不缩放
_IMGSZ_ENV = int(os.environ.get("CPU_PERF_IMGSZ", "416"))
INFERENCE_IMGSZ: int = _IMGSZ_ENV if _IMGSZ_ENV > 0 else 0


def maybe_downsample(image):
    """
    如果 CPU 性能模式已启用且配置了目标分辨率，
    按比例缩小图像用于推理（不修改原图）。

    YOLO 内部坐标已按输入图像归一化，
    返回的 bbox 在前端会映射到 imageWidth/imageHeight，
    因此缩小后的 bbox 坐标仍然可以正确显示在画面上。
    """
    if not ENABLED or INFERENCE_IMGSZ <= 0:
        return image

    h, w = image.shape[:2]
    if max(w, h) <= INFERENCE_IMGSZ:
        return image  # 已经不大于目标尺寸，无需缩放

    scale = INFERENCE_IMGSZ / max(w, h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)


def log_status() -> None:
    """启动时打印 CPU 性能模式的配置，方便排查效果。"""
    if not ENABLED:
        print("[cpu_perf] GPU detected — CPU performance mode DISABLED")
        return
    print(
        f"[cpu_perf] CPU mode detected — performance optimizations ENABLED\n"
        f"           ② Frame skip  : every {INFERENCE_EVERY_N} frame(s)\n"
        f"           ③ Infer imgsz : {INFERENCE_IMGSZ if INFERENCE_IMGSZ > 0 else 'no downscale'}"
    )
