# AI Server Windows 一键启动脚本。
#
# 用法：
#   .\start-ai.ps1
#   .\start-ai.ps1 --s
#   .\start-ai.ps1 --env ai --port 8080
#
# 参数：
#   -s, --s, --skip-check      跳过启动前检测，直接启动。
#   -e, --env <name>           Conda 环境名。默认：ai
#   -p, --port <port>          AI WebRTC/FastAPI 端口。默认：8080
#   --host <host>              监听地址。默认：0.0.0.0
#   --help                     显示帮助。

$ErrorActionPreference = "Stop"

$SkipCheck = $false
$CondaEnv = "ai"
$AiHost = "0.0.0.0"
$AiPort = 8080

function Show-Usage {
    Write-Host ""
    Write-Host "用法："
    Write-Host "  .\start-ai.ps1"
    Write-Host "  .\start-ai.ps1 --s"
    Write-Host "  .\start-ai.ps1 --env ai --port 8080"
    Write-Host ""
    Write-Host "参数："
    Write-Host "  -s, --s, --skip-check      跳过启动前检测，直接启动。"
    Write-Host "  -e, --env <name>           Conda 环境名。默认：ai"
    Write-Host "  -p, --port <port>          AI WebRTC/FastAPI 端口。默认：8080"
    Write-Host "  --host <host>              监听地址。默认：0.0.0.0"
    Write-Host "  --help                     显示帮助。"
    Write-Host ""
}

function Read-NextArg {
    param(
        [string[]]$Values,
        [int]$Index,
        [string]$Name
    )

    if ($Index + 1 -ge $Values.Count) {
        throw "参数 $Name 缺少取值。"
    }

    return $Values[$Index + 1]
}

$RawArgs = @($args)
for ($i = 0; $i -lt $RawArgs.Count; $i++) {
    switch ($RawArgs[$i]) {
        "-s" { $SkipCheck = $true; continue }
        "--s" { $SkipCheck = $true; continue }
        "--skip-check" { $SkipCheck = $true; continue }
        "--skip-checks" { $SkipCheck = $true; continue }
        "-e" {
            $CondaEnv = Read-NextArg -Values $RawArgs -Index $i -Name $RawArgs[$i]
            $i++
            continue
        }
        "--env" {
            $CondaEnv = Read-NextArg -Values $RawArgs -Index $i -Name $RawArgs[$i]
            $i++
            continue
        }
        "-p" {
            $AiPort = [int](Read-NextArg -Values $RawArgs -Index $i -Name $RawArgs[$i])
            $i++
            continue
        }
        "--port" {
            $AiPort = [int](Read-NextArg -Values $RawArgs -Index $i -Name $RawArgs[$i])
            $i++
            continue
        }
        "--host" {
            $AiHost = Read-NextArg -Values $RawArgs -Index $i -Name $RawArgs[$i]
            $i++
            continue
        }
        "--help" {
            Show-Usage
            exit 0
        }
        default {
            throw "未知参数：$($RawArgs[$i])。使用 --help 查看用法。"
        }
    }
}

function Write-Step {
    param([string]$Message)
    Write-Host "[信息] $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[通过] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[警告] $Message" -ForegroundColor Yellow
}

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "未找到命令：$Name"
    }
    Write-Ok "命令可用：$Name"
}

function Assert-Path {
    param(
        [string]$Path,
        [string]$Label
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "未找到 $Label：$Path"
    }
    Write-Ok "$Label 存在：$Path"
}

function Test-PortFree {
    param([int]$Port)

    if (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue) {
        $listeners = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
        if ($listeners.Count -gt 0) {
            $processInfo = $listeners |
                Select-Object -ExpandProperty OwningProcess -Unique |
                ForEach-Object {
                    $pidValue = $_
                    $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
                    if ($proc) {
                        "$pidValue ($($proc.ProcessName))"
                    } else {
                        "$pidValue"
                    }
                }
            throw "端口 $Port 已被占用，占用进程：$($processInfo -join ', ')"
        }
    }

    Write-Ok "端口 $Port 未被占用。"
}

function Test-CondaEnv {
    param([string]$EnvName)

    Write-Step "检查 Conda 环境：$EnvName"
    & conda run -n $EnvName python --version
    if ($LASTEXITCODE -ne 0) {
        throw "Conda 环境 '$EnvName' 不可用。请确认环境已创建。"
    }
    Write-Ok "Conda 环境可用：$EnvName"
}

function Test-PythonImports {
    param([string]$EnvName)

    Write-Step "检查 Python 依赖模块..."
    $code = @"
import importlib
import sys

modules = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("aiortc", "aiortc"),
    ("dotenv", "python-dotenv"),
    ("torch", "torch"),
    ("cv2", "opencv-python"),
    ("mediapipe", "mediapipe"),
]

missing = []
for module, package in modules:
    try:
        importlib.import_module(module)
    except Exception as exc:
        missing.append(f"{package}: {exc}")

if missing:
    print("缺少或不可用的 Python 模块：")
    for item in missing:
        print(" - " + item)
    sys.exit(1)

print("Python 依赖模块检查通过。")
"@

    & conda run -n $EnvName python -c $code
    if ($LASTEXITCODE -ne 0) {
        throw "Python 依赖检查失败。可执行：conda run -n $EnvName pip install -r requirements.txt"
    }
    Write-Ok "Python 依赖模块可用。"
}

function Test-ModelFiles {
    Write-Step "检查 AI 模型和资源文件..."

    $modelGroups = @(
        @{
            Name = "手部检测模型"
            Paths = @(
                "runs\hand_detect_yolov5s_b32\weights\best.pt",
                "runs\hand_detect_yolov5s_b32\weights\best.onnx",
                "runs\hand_detect_yolov5s_b32\weights\best_int8.onnx"
            )
        },
        @{
            Name = "数字识别模型"
            Paths = @(
                "runs\digits_detect_yolov5b64\weights\best.pt",
                "runs\digits_detect_yolov5b64\weights\best.onnx",
                "runs\digits_detect_yolov5b64\weights\best_int8.onnx"
            )
        },
        @{
            Name = "字母识别模型"
            Paths = @(
                "runs\letters_detect_yolov5m_v12\weights\best.pt",
                "runs\letters_detect_yolov5m_v12\weights\best.onnx",
                "runs\letters_detect_yolov5m_v12\weights\best_int8.onnx"
            )
        }
    )

    foreach ($group in $modelGroups) {
        $found = $false
        foreach ($path in $group["Paths"]) {
            if (Test-Path -LiteralPath $path) {
                $found = $true
                Write-Ok "$($group["Name"]): $path"
                break
            }
        }

        if (-not $found) {
            Write-Warn "$($group["Name"]) 未找到。已检查：$($group["Paths"] -join ', ')"
        }
    }

    if (Test-Path -LiteralPath "mediapipe\hand_landmarker.task") {
        Write-Ok "MediaPipe 手部模型存在：mediapipe\hand_landmarker.task"
    } else {
        Write-Warn "MediaPipe 手部模型未找到：mediapipe\hand_landmarker.task"
    }
}

function Get-LocalIPv4Addresses {
    $addresses = @()

    if (Get-Command Get-NetIPAddress -ErrorAction SilentlyContinue) {
        $addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
            Where-Object {
                $_.IPAddress -ne "127.0.0.1" -and
                $_.IPAddress -notlike "169.254.*" -and
                $_.PrefixOrigin -ne "WellKnown"
            } |
            Sort-Object -Property InterfaceAlias, IPAddress |
            Select-Object -ExpandProperty IPAddress -Unique
    }

    if (-not $addresses -or $addresses.Count -eq 0) {
        $addresses = [System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) |
            Where-Object {
                $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork -and
                $_.IPAddressToString -ne "127.0.0.1" -and
                $_.IPAddressToString -notlike "169.254.*"
            } |
            ForEach-Object { $_.IPAddressToString } |
            Select-Object -Unique
    }

    return @($addresses)
}

function Show-AccessAddresses {
    param([int]$Port)

    Write-Host ""
    Write-Host "可用于前端配置的 AI 服务地址：" -ForegroundColor Magenta
    Write-Host "  本机访问：http://127.0.0.1:$Port"

    $localIps = Get-LocalIPv4Addresses
    if ($localIps.Count -gt 0) {
        foreach ($ip in $localIps) {
            Write-Host "  局域网访问：http://$ip`:$Port"
        }
    } else {
        Write-Warn "没有自动识别到局域网 IPv4 地址。可手动执行 ipconfig 查看。"
    }

    Write-Host ""
}

function Start-AiServer {
    param(
        [string]$EnvName,
        [string]$HostName,
        [int]$Port
    )

    $env:AI_SERVER_HOST = $HostName
    $env:AI_SERVER_PORT = [string]$Port
    $env:AI_WEBRTC_PORT = [string]$Port
    $env:PYTHONUNBUFFERED = "1"

    Write-Step "正在启动 AI 服务..."
    Write-Host "  Conda 环境：$EnvName"
    Write-Host "  监听地址 ：http://$HostName`:$Port"
    Write-Host "  健康检查 ：http://127.0.0.1:$Port/health"
    Show-AccessAddresses -Port $Port
    Write-Host ""
    Write-Host "按 Ctrl+C 停止服务。" -ForegroundColor Yellow
    Write-Host ""

    try {
        & conda run --no-capture-output -n $EnvName python main.py
        $exitCode = $LASTEXITCODE
    } finally {
        Write-Host ""
        Write-Step "AI 服务已退出，当前机器 IP 地址如下："
        Show-AccessAddresses -Port $Port
    }

    exit $exitCode
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ScriptDir

Write-Host ""
Write-Host "=== AI Server Windows 一键启动 ===" -ForegroundColor Magenta
Write-Host "工作目录：$ScriptDir"
Write-Host ""

if (-not $SkipCheck) {
    Write-Step "开始启动前检测..."
    Assert-Path -Path "main.py" -Label "AI 入口文件"
    Assert-Path -Path "requirements.txt" -Label "Python 依赖清单"
    if (-not (Test-Path -LiteralPath ".env")) {
        Write-Warn "未找到 .env。服务仍可启动，但 LLM 或模型路径覆盖配置可能缺失。"
        Write-Warn "可复制 .env.example 为 .env，再填写密钥和自定义配置。"
    } else {
        Write-Ok ".env 存在。"
    }

    Assert-Command -Name "conda"
    Test-CondaEnv -EnvName $CondaEnv
    Test-PythonImports -EnvName $CondaEnv
    Test-ModelFiles
    Test-PortFree -Port $AiPort
    Write-Ok "启动前检测完成。"
} else {
    Write-Warn "已启用跳过检测模式，将直接启动。"
}

Start-AiServer -EnvName $CondaEnv -HostName $AiHost -Port $AiPort
