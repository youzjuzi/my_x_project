import os
import torch
from pathlib import Path
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
AI_ROOT = ROOT.parent

# 自动从 ai-server/.env 读取环境变量
load_dotenv(AI_ROOT / ".env")

HOST = "127.0.0.1"
PORT = 8001
WEBRTC_PORT = 8002

DEVICE = "0" if torch.cuda.is_available() else "cpu"  # 有 CUDA GPU 自动用 GPU，否则回退到 CPU
_EXT = ".onnx" if DEVICE == "cpu" else ".pt"

# 智能读取环境变量并支持 `.pt` 回退到 `.onnx`
def _get_model_path(env_key: str, default_rel_path: str) -> str:
    # 优先从 .env 读取配置的路径，未配置则使用默认路径
    path_str = os.environ.get(env_key, default_rel_path)
    # 如果定义的是相对路径，则拼接到 AI_ROOT
    if not os.path.isabs(path_str):
        path_str = str(AI_ROOT / path_str)
    
    # 智能后缀替换：如果环境配置写的是.pt但当前无GPU，则尝试加载更快已转换好的.onnx
    if path_str.endswith(".pt") and _EXT == ".onnx":
        onnx_path = path_str.replace(".pt", ".onnx")
        if os.path.exists(onnx_path):
            return onnx_path
    return path_str

HAND_WEIGHTS = _get_model_path("HAND_WEIGHTS", "runs/hand_detect_yolov5s_b32/weights/best.pt")
DIGIT_WEIGHTS = _get_model_path("DIGIT_WEIGHTS", "runs/digits_detect_yolov5b64/weights/best.pt")
LETTER_WEIGHTS = _get_model_path("LETTER_WEIGHTS", "runs/letters_detect_yolov5m_v12/weights/best.pt")
MEDIAPIPE_TASK = _get_model_path("MEDIAPIPE_TASK", "mediapipe/hand_landmarker.task")
IMGSZ = 640
HAND_CONF = 0.30
DIGIT_CONF = 0.25
LETTER_CONF = 0.25
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
