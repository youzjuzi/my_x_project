import os
import torch
from pathlib import Path
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
AI_ROOT = ROOT.parent

# 自动从 ai-server/.env 读取环境变量
load_dotenv(AI_ROOT / ".env")

# 允许局域网其他设备访问（0.0.0.0 代替 127.0.0.1）
HOST = "0.0.0.0"
PORT = 8001
WEBRTC_PORT = 8002

DEVICE = "0" if torch.cuda.is_available() else "cpu"  # 有 CUDA GPU 自动用 GPU，否则回退到 CPU
_EXT = ".onnx" if DEVICE == "cpu" else ".pt"

# 智能读取环境变量：自动区分 GPU 专用模型 (.pt) 与 CPU 专用模型 (.onnx)
def _get_model_path(env_key: str, default_rel_path: str) -> str:
    # 1. 如果当前环境是 CPU（要求加载 ONNX），优先寻找带 _ONNX 后缀的终极优化配置
    if _EXT == ".onnx":
        onnx_env_key = f"{env_key}_ONNX"
        if onnx_env_key in os.environ:
            path_str = os.environ[onnx_env_key]
            if not os.path.isabs(path_str):
                path_str = str(AI_ROOT / path_str)
            if os.path.exists(path_str):
                return path_str

    # 2. 如果没找到专属配置，或者当前是 GPU 环境，读取基础配置
    path_str = os.environ.get(env_key, default_rel_path)
    if not os.path.isabs(path_str):
        path_str = str(AI_ROOT / path_str)
    
    # 3. 智能老本降级：如果只有 .pt，但必须跑 CPU，偷偷去找有没有同名的 .onnx
    if path_str.endswith(".pt") and _EXT == ".onnx":
        fallback_onnx = path_str.replace(".pt", ".onnx")
        if os.path.exists(fallback_onnx):
            return fallback_onnx
            
    return path_str

HAND_WEIGHTS = _get_model_path("HAND_WEIGHTS", "runs/hand_detect_yolov5s_b32/weights/best.pt")
DIGIT_WEIGHTS = _get_model_path("DIGIT_WEIGHTS", "runs/digits_detect_yolov5b64/weights/best.pt")
LETTER_WEIGHTS = _get_model_path("LETTER_WEIGHTS", "runs/letters_detect_yolov5m_v12/weights/best.pt")
MEDIAPIPE_TASK = _get_model_path("MEDIAPIPE_TASK", "mediapipe/hand_landmarker.task")
IMGSZ = 640
HAND_CONF = 0.40
DIGIT_CONF = 0.25
LETTER_CONF = 0.40
# Q 在 .pt 推理引擎下极易误报，给它设定更高的专属置信度门槛
LETTER_Q_CONF = 0.65
IOU_THRES = 0.45
MAX_DET = 100
MARGIN = 10
PQ_EXIT_GRACE_SECONDS = 3.0
MN_EXIT_GRACE_SECONDS = 2.4
IJ_DZ_EXIT_GRACE_SECONDS = 2.4

JPEG_QUALITY = 80

# 大语言模型接口配置 (DeepSeek等)
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
