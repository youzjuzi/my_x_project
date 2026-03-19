const wsUrlInput = document.getElementById("wsUrl");
const fpsInput = document.getElementById("fpsInput");
const qualityInput = document.getElementById("qualityInput");
const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const cameraBtn = document.getElementById("cameraBtn");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const clearLogBtn = document.getElementById("clearLogBtn");
const modeButtons = document.querySelectorAll(".mode-btn");

const socketStatus = document.getElementById("socketStatus");
const cameraStatus = document.getElementById("cameraStatus");
const streamStatus = document.getElementById("streamStatus");
const modeStatus = document.getElementById("modeStatus");
const sentMeta = document.getElementById("sentMeta");
const latencyMeta = document.getElementById("latencyMeta");

const video = document.getElementById("video");
const captureCanvas = document.getElementById("captureCanvas");
const resultImage = document.getElementById("resultImage");
const resultText = document.getElementById("resultText");
const modeText = document.getElementById("modeText");
const handCountText = document.getElementById("handCountText");
const jsonOutput = document.getElementById("jsonOutput");
const logOutput = document.getElementById("logOutput");

let socket = null;
let mediaStream = null;
let sendTimer = null;
let frameInFlight = false;
let sentFrames = 0;
let currentMode = "digits";

function setPill(element, state, text) {
  element.className = `pill ${state}`;
  element.textContent = text;
}

function log(message) {
  const item = document.createElement("div");
  item.className = "log-item";
  item.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  logOutput.prepend(item);
}

function summarizeResultPayload(data) {
  return {
    type: data.type,
    mode: data.mode,
    latencyMs: data.latencyMs,
    imageWidth: data.imageWidth,
    imageHeight: data.imageHeight,
    handCount: data.handCount,
    text: data.text,
    hands: data.hands
  };
}

function updateModeUi(nextMode) {
  currentMode = nextMode;
  modeText.textContent = nextMode;
  setPill(modeStatus, "warn", `当前模式 ${nextMode}`);
  modeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === nextMode);
  });
}

function setConnected(connected) {
  connectBtn.disabled = connected;
  disconnectBtn.disabled = !connected;
  startBtn.disabled = !connected || !mediaStream;
  stopBtn.disabled = !sendTimer;
}

async function openCamera() {
  if (mediaStream) {
    return;
  }

  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: "user" },
      audio: false
    });
    video.srcObject = mediaStream;
    setPill(cameraStatus, "ok", "摄像头已启动");
    setConnected(Boolean(socket));
    log("摄像头已打开");
  } catch (error) {
    setPill(cameraStatus, "error", "摄像头失败");
    log(`打开摄像头失败: ${error.message}`);
  }
}

function connectSocket() {
  const url = wsUrlInput.value.trim();
  if (!url) {
    log("请先输入 WebSocket 地址");
    return;
  }

  socket = new WebSocket(url);
  setPill(socketStatus, "warn", "连接中");
  log(`连接 ${url}`);

  socket.onopen = () => {
    setPill(socketStatus, "ok", "已连接");
    setConnected(true);
    socket.send(`mode:${currentMode}`);
    log("WebSocket 已连接");
  };

  socket.onclose = () => {
    socket = null;
    stopStreaming();
    setPill(socketStatus, "idle", "未连接");
    setConnected(false);
    log("WebSocket 已断开");
  };

  socket.onerror = () => {
    setPill(socketStatus, "error", "连接异常");
    log("WebSocket 出现错误");
  };

  socket.onmessage = (event) => {
    frameInFlight = false;
    const data = JSON.parse(event.data);

    if (data.type === "ready") {
      updateModeUi(data.defaultMode || currentMode);
      log(data.message);
      return;
    }
    if (data.type === "pong") {
      log("收到 pong");
      return;
    }
    if (data.type === "mode_changed") {
      updateModeUi(data.mode);
      log(`后端已切换到 ${data.mode}`);
      return;
    }
    if (data.type === "error") {
      log(`服务端错误: ${data.message}`);
      return;
    }
    if (data.type === "info") {
      log(data.message);
      return;
    }
    if (data.type === "result") {
      updateModeUi(data.mode || currentMode);
      latencyMeta.textContent = `延迟 ${data.latencyMs} ms`;
      resultText.textContent = data.text || "-";
      handCountText.textContent = String(data.handCount ?? 0);
      resultImage.src = data.annotatedFrame || "";
      jsonOutput.textContent = JSON.stringify(summarizeResultPayload(data), null, 2);
    }
  };
}

function disconnectSocket() {
  if (socket) {
    socket.close();
  }
}

function captureAndSend() {
  if (!socket || socket.readyState !== WebSocket.OPEN || !mediaStream || frameInFlight) {
    return;
  }
  if (!video.videoWidth || !video.videoHeight) {
    return;
  }

  frameInFlight = true;
  captureCanvas.width = video.videoWidth;
  captureCanvas.height = video.videoHeight;
  const ctx = captureCanvas.getContext("2d");
  ctx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);

  const quality = Math.max(0.3, Math.min(1, Number(qualityInput.value) || 0.7));
  captureCanvas.toBlob(async (blob) => {
    if (!blob) {
      frameInFlight = false;
      return;
    }
    try {
      const arrayBuffer = await blob.arrayBuffer();
      socket.send(arrayBuffer);
      sentFrames += 1;
      sentMeta.textContent = `${sentFrames} 帧`;
    } catch (error) {
      frameInFlight = false;
      log(`发送帧失败: ${error.message}`);
    }
  }, "image/jpeg", quality);
}

function startStreaming() {
  if (!socket || socket.readyState !== WebSocket.OPEN || !mediaStream || sendTimer) {
    return;
  }
  const fps = Math.max(1, Math.min(20, Number(fpsInput.value) || 3));
  const interval = Math.round(1000 / fps);
  sendTimer = window.setInterval(captureAndSend, interval);
  setPill(streamStatus, "ok", "推流中");
  setConnected(true);
  stopBtn.disabled = false;
  log(`开始推流，目标 FPS=${fps}`);
}

function stopStreaming() {
  if (sendTimer) {
    window.clearInterval(sendTimer);
    sendTimer = null;
  }
  frameInFlight = false;
  setPill(streamStatus, "idle", "未推流");
  stopBtn.disabled = true;
  setConnected(Boolean(socket));
}

function changeMode(nextMode) {
  updateModeUi(nextMode);
  resultText.textContent = "-";
  handCountText.textContent = "0";
  jsonOutput.textContent = "";
  resultImage.removeAttribute("src");
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(`mode:${nextMode}`);
    log(`请求切换模式为 ${nextMode}`);
  }
}

connectBtn.addEventListener("click", connectSocket);
disconnectBtn.addEventListener("click", disconnectSocket);
cameraBtn.addEventListener("click", openCamera);
startBtn.addEventListener("click", startStreaming);
stopBtn.addEventListener("click", stopStreaming);
clearLogBtn.addEventListener("click", () => {
  logOutput.innerHTML = "";
});
modeButtons.forEach((button) => {
  button.addEventListener("click", () => changeMode(button.dataset.mode));
});

setPill(socketStatus, "idle", "未连接");
setPill(cameraStatus, "idle", "摄像头未启动");
setPill(streamStatus, "idle", "未推流");
updateModeUi("digits");
setConnected(false);
