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

HAND_WEIGHTS = str(AI_ROOT / "runs/hand_detect_yolov5s_b32/weights/best.pt")
DIGIT_WEIGHTS = str(AI_ROOT / "runs/digits_detect_yolov5b64/weights/best.pt")
LETTER_WEIGHTS = str(AI_ROOT / "runs/letters_detect_yolov5m_v12/weights/best.pt")
MEDIAPIPE_TASK = str(AI_ROOT / "mediapipe/hand_landmarker.task")
IMGSZ = 640
HAND_CONF = 0.30
DIGIT_CONF = 0.25
LETTER_CONF = 0.25
IOU_THRES = 0.45
DEVICE = "0" if torch.cuda.is_available() else "cpu"  # 有 CUDA GPU 自动用 GPU，否则回退到 CPU
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
