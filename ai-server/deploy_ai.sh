#!/usr/bin/env bash
set -Eeuo pipefail

# GPU 识别端交互部署脚本
# 功能：拉取代码、检测 NVIDIA 环境、安装/复用 PyTorch 与依赖、检查模型文件、启动服务。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
LOG_DIR="${SCRIPT_DIR}/logs"
DEPLOY_LOG="${LOG_DIR}/deploy-ai.log"
SERVER_LOG="${LOG_DIR}/ai-server.log"

mkdir -p "${LOG_DIR}"
touch "${DEPLOY_LOG}"

exec > >(tee -a "${DEPLOY_LOG}") 2>&1

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [信息] $*"
}

warn() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [警告] $*"
}

fail() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [错误] $*" >&2
  exit 1
}

ask_yes_no() {
  local prompt="$1"
  local default="${2:-y}"
  local suffix
  if [[ "${default}" == "y" ]]; then
    suffix="[Y/n]"
  else
    suffix="[y/N]"
  fi

  local answer
  read -r -p "${prompt} ${suffix} " answer || true
  answer="${answer:-${default}}"
  [[ "${answer}" =~ ^[Yy]$ ]]
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

detect_python() {
  if command_exists python3.10; then
    echo "python3.10"
    return
  fi
  if command_exists python3; then
    echo "python3"
    return
  fi
  if command_exists python; then
    echo "python"
    return
  fi
  fail "未找到 Python，请先安装 Python 3.10/3.11。"
}

ensure_clean_or_confirm() {
  cd "${PROJECT_ROOT}"
  if ! command_exists git || [[ ! -d ".git" ]]; then
    warn "当前目录不是 Git 仓库或未安装 Git，跳过代码拉取。"
    return
  fi

  local dirty
  dirty="$(git status --porcelain)"
  if [[ -n "${dirty}" ]]; then
    warn "检测到本地存在未提交改动："
    echo "${dirty}"
    if ! ask_yes_no "是否跳过 git pull，继续使用当前代码部署？" "y"; then
      fail "为避免覆盖现场，已停止。请先处理本地改动。"
    fi
    return
  fi

  if ask_yes_no "是否先执行 git pull --ff-only 拉取最新代码？" "y"; then
    git pull --ff-only
  else
    warn "已跳过 git pull。"
  fi
}

detect_nvidia() {
  if ! command_exists nvidia-smi; then
    warn "未检测到 nvidia-smi，后续默认按 CPU 环境处理。"
    return
  fi

  log "检测到 NVIDIA 环境："
  nvidia-smi || true
}

driver_version() {
  if ! command_exists nvidia-smi; then
    echo ""
    return
  fi
  nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n 1 | tr -d ' '
}

recommend_torch_choice() {
  local driver="$1"
  local major="${driver%%.*}"

  if [[ -z "${driver}" ]]; then
    echo "cpu"
    return
  fi

  if [[ "${major}" =~ ^[0-9]+$ ]] && (( major >= 550 )); then
    echo "cu124"
    return
  fi

  if [[ "${major}" =~ ^[0-9]+$ ]] && (( major >= 525 )); then
    echo "cu121"
    return
  fi

  echo "cu118"
}

activate_venv() {
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
}

ensure_venv() {
  local py_bin="$1"

  if [[ -d "${VENV_DIR}" ]]; then
    log "检测到已有虚拟环境：${VENV_DIR}"
  else
    log "创建虚拟环境：${VENV_DIR}"
    "${py_bin}" -m venv "${VENV_DIR}"
  fi

  activate_venv
  python -m pip install --upgrade pip
}

torch_status() {
  python - <<'PY'
try:
    import torch
    print(f"torch={torch.__version__}")
    print(f"cuda_available={torch.cuda.is_available()}")
    print(f"torch_cuda={getattr(torch.version, 'cuda', None)}")
    print(f"device={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none'}")
except Exception as exc:
    print(f"missing_or_error={exc}")
PY
}

install_torch() {
  local driver
  local recommended
  driver="$(driver_version)"
  recommended="$(recommend_torch_choice "${driver}")"

  log "当前 PyTorch 状态："
  torch_status || true

  if python - <<'PY'
try:
    import torch
    raise SystemExit(0 if torch.cuda.is_available() else 1)
except Exception:
    raise SystemExit(1)
PY
  then
    if ask_yes_no "已检测到可用 CUDA 版 PyTorch，是否跳过 PyTorch 安装？" "y"; then
      return
    fi
  fi

  echo ""
  log "请选择 PyTorch 安装版本。检测到驱动版本：${driver:-未知}，推荐：${recommended}"
  echo "  1) 推荐版本 (${recommended})"
  echo "  2) cu121 - 适合 535 系驱动 / CUDA 12.1-12.2"
  echo "  3) cu124 - 通常需要 550+ 驱动"
  echo "  4) cu118 - 适合较旧驱动"
  echo "  5) CPU 版本"
  echo "  6) 跳过 PyTorch 安装"

  local choice
  read -r -p "请输入选项 [1-6]，默认 1：" choice || true
  choice="${choice:-1}"

  local target="${recommended}"
  case "${choice}" in
    1) target="${recommended}" ;;
    2) target="cu121" ;;
    3) target="cu124" ;;
    4) target="cu118" ;;
    5) target="cpu" ;;
    6)
      warn "已跳过 PyTorch 安装。"
      return
      ;;
    *) fail "无效选项：${choice}" ;;
  esac

  case "${target}" in
    cu121)
      log "安装 PyTorch CUDA 12.1 版本..."
      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
      ;;
    cu124)
      log "安装 PyTorch CUDA 12.4 版本..."
      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
      ;;
    cu118)
      log "安装 PyTorch CUDA 11.8 版本..."
      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
      ;;
    cpu)
      log "安装 PyTorch CPU 版本..."
      pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
      ;;
    *) fail "未知 PyTorch 目标版本：${target}" ;;
  esac

  log "PyTorch 安装后状态："
  torch_status || true
}

install_requirements() {
  cd "${SCRIPT_DIR}"
  log "安装/更新 ai-server Python 依赖..."
  pip install -r requirements.txt
}

check_runtime_files() {
  cd "${SCRIPT_DIR}"

  if [[ ! -f ".env" ]]; then
    warn "未找到 ai-server/.env。润色接口会缺少 LLM_API_KEY，模型路径也只能使用默认值。"
    warn "可复制模板后编辑：cp .env.example .env"
  fi

  local missing=0
  local files=(
    "runs/hand_detect_yolov5s_b32/weights/best.pt"
    "runs/digits_detect_yolov5b64/weights/best.pt"
    "runs/letters_detect_yolov5m_v12/weights/best.pt"
    "mediapipe/hand_landmarker.task"
  )

  for file in "${files[@]}"; do
    if [[ -f "${file}" ]]; then
      log "模型/资源存在：${file}"
    else
      warn "缺少模型/资源：${file}"
      missing=1
    fi
  done

  if [[ "${missing}" == "1" ]]; then
    warn "存在缺失模型文件。如果这些文件没有随 Git 上传，请用 Xftp/SCP 手动放到对应路径。"
  fi
}

verify_imports() {
  log "检查关键依赖导入与 CUDA 状态..."
  python - <<'PY'
import importlib

modules = [
    ("torch", "torch"),
    ("cv2", "opencv"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("aiortc", "aiortc"),
    ("mediapipe", "mediapipe"),
    ("openai", "openai"),
    ("dotenv", "python-dotenv"),
    ("ultralytics", "ultralytics"),
    ("psutil", "psutil"),
]

failed = []
for module, name in modules:
    try:
        importlib.import_module(module)
        print(f"[OK] {name}")
    except Exception as exc:
        failed.append((name, str(exc)))
        print(f"[FAIL] {name}: {exc}")

try:
    import torch
    print(f"[CUDA] available={torch.cuda.is_available()} version={getattr(torch.version, 'cuda', None)}")
    if torch.cuda.is_available():
        print(f"[CUDA] device={torch.cuda.get_device_name(0)}")
except Exception as exc:
    failed.append(("torch cuda check", str(exc)))

if failed:
    raise SystemExit(1)
PY
}

stop_existing_background() {
  local pid_file="${SCRIPT_DIR}/logs/ai-server.pid"
  if [[ ! -f "${pid_file}" ]]; then
    return
  fi

  local old_pid
  old_pid="$(cat "${pid_file}" || true)"
  if [[ -n "${old_pid}" ]] && kill -0 "${old_pid}" >/dev/null 2>&1; then
    warn "检测到旧后台进程 PID=${old_pid}"
    if ask_yes_no "是否停止旧进程后重新启动？" "y"; then
      kill "${old_pid}" || true
      sleep 2
    fi
  fi
}

run_server() {
  cd "${SCRIPT_DIR}"

  echo ""
  echo "  1) 前台运行（适合首次调试，Ctrl+C 停止）"
  echo "  2) 后台运行（写入 logs/ai-server.log）"
  echo "  3) 暂不启动"

  local choice
  read -r -p "请选择启动方式 [1-3]，默认 1：" choice || true
  choice="${choice:-1}"

  case "${choice}" in
    1)
      log "前台启动 AI 识别服务..."
      python main.py
      ;;
    2)
      stop_existing_background
      log "后台启动 AI 识别服务，日志：${SERVER_LOG}"
      nohup python main.py >> "${SERVER_LOG}" 2>&1 &
      echo "$!" > "${SCRIPT_DIR}/logs/ai-server.pid"
      log "已启动，PID=$(cat "${SCRIPT_DIR}/logs/ai-server.pid")"
      log "查看日志：tail -f ${SERVER_LOG}"
      ;;
    3)
      warn "已选择暂不启动。"
      ;;
    *) fail "无效选项：${choice}" ;;
  esac
}

main() {
  log "开始部署 AI 识别端，目录：${SCRIPT_DIR}"
  ensure_clean_or_confirm

  local py_bin
  py_bin="$(detect_python)"
  log "使用 Python：$(${py_bin} --version 2>&1)"

  detect_nvidia
  ensure_venv "${py_bin}"
  install_torch
  install_requirements
  verify_imports
  check_runtime_files
  run_server

  log "AI 识别端部署流程结束。"
}

main "$@"
