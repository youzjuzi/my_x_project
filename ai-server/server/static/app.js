const wsUrlInput = document.getElementById("wsUrl");
const webrtcUrlInput = document.getElementById("webrtcUrl");
const fpsInput = document.getElementById("fpsInput");
const qualityInput = document.getElementById("qualityInput");
const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const cameraBtn = document.getElementById("cameraBtn");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const clearLogBtn = document.getElementById("clearLogBtn");
const modeButtons = document.querySelectorAll(".mode-btn");
const transportButtons = document.querySelectorAll(".transport-btn");

const socketStatus = document.getElementById("socketStatus");
const transportStatus = document.getElementById("transportStatus");
const cameraStatus = document.getElementById("cameraStatus");
const streamStatus = document.getElementById("streamStatus");
const modeStatus = document.getElementById("modeStatus");
const sentMeta = document.getElementById("sentMeta");
const latencyMeta = document.getElementById("latencyMeta");

const video = document.getElementById("video");
const captureCanvas = document.getElementById("captureCanvas");
const resultImage = document.getElementById("resultImage");
const resultPlaceholder = document.getElementById("resultPlaceholder");
const resultText = document.getElementById("resultText");
const modeText = document.getElementById("modeText");
const handCountText = document.getElementById("handCountText");
const inputFpsText = document.getElementById("inputFpsText");
const processedFpsText = document.getElementById("processedFpsText");
const jsonOutput = document.getElementById("jsonOutput");
const logOutput = document.getElementById("logOutput");

let socket = null;
let mediaStream = null;
let sendTimer = null;
let frameInFlight = false;
let sentFrames = 0;
let currentMode = "digits";
let currentTransport = "ws";
let peerConnection = null;
let dataChannel = null;

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

function resetResultView() {
  resultText.textContent = "-";
  handCountText.textContent = "0";
  inputFpsText.textContent = "-";
  processedFpsText.textContent = "-";
  resultImage.removeAttribute("src");
  resultPlaceholder.hidden = false;
  jsonOutput.textContent = "";
  latencyMeta.textContent = "Latency -";
}

function updateModeUi(nextMode) {
  currentMode = nextMode;
  modeText.textContent = nextMode;
  setPill(modeStatus, "warn", `Mode ${nextMode}`);
  modeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === nextMode);
  });
}

function updateTransportUi(nextTransport) {
  currentTransport = nextTransport;
  transportButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.transport === nextTransport);
  });
  setPill(transportStatus, "warn", `Transport ${nextTransport === "ws" ? "WebSocket" : "WebRTC"}`);
  updateControls();
}

function updateControls() {
  const hasCamera = Boolean(mediaStream);
  const wsConnected = Boolean(socket);
  const webrtcConnected = Boolean(peerConnection);

  if (currentTransport === "ws") {
    connectBtn.textContent = "Connect WebSocket";
    disconnectBtn.textContent = "Disconnect";
    connectBtn.disabled = wsConnected;
    disconnectBtn.disabled = !wsConnected;
    startBtn.disabled = !wsConnected || !hasCamera;
    stopBtn.disabled = !sendTimer;
    fpsInput.disabled = false;
    qualityInput.disabled = false;
  } else {
    connectBtn.textContent = "Connect WebRTC";
    disconnectBtn.textContent = "Disconnect";
    connectBtn.disabled = webrtcConnected;
    disconnectBtn.disabled = !webrtcConnected;
    startBtn.disabled = true;
    stopBtn.disabled = true;
    fpsInput.disabled = true;
    qualityInput.disabled = true;
  }
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
    setPill(cameraStatus, "ok", "Camera Online");
    log("Camera opened");
  } catch (error) {
    setPill(cameraStatus, "error", "Camera Failed");
    log(`Camera error: ${error.message}`);
  }
  updateControls();
}

function closeCamera() {
  if (!mediaStream) {
    return;
  }
  mediaStream.getTracks().forEach((track) => track.stop());
  mediaStream = null;
  video.srcObject = null;
  setPill(cameraStatus, "idle", "Camera Offline");
  updateControls();
}

function handleServerMessage(data) {
  if (data.type === "ready") {
    updateModeUi(data.defaultMode || currentMode);
    log(data.message || "Connection ready");
    return;
  }
  if (data.type === "pong") {
    log("Received pong");
    return;
  }
  if (data.type === "mode_changed") {
    updateModeUi(data.mode);
    log(`Mode changed to ${data.mode}`);
    return;
  }
  if (data.type === "error") {
    log(`Server error: ${data.message}`);
    return;
  }
  if (data.type === "info") {
    log(data.message);
    return;
  }
  if (data.type === "result") {
    updateModeUi(data.mode || currentMode);
    latencyMeta.textContent = `Latency ${data.latencyMs} ms`;
    resultText.textContent = data.text || "-";
    handCountText.textContent = String(data.handCount ?? 0);
    inputFpsText.textContent = data.inputFps ?? "-";
    processedFpsText.textContent = data.processedFps ?? "-";
    if (data.annotatedFrame) {
      resultImage.src = data.annotatedFrame;
      resultPlaceholder.hidden = true;
    }
    jsonOutput.textContent = JSON.stringify(summarizeResultPayload(data), null, 2);
  }
}

function stopStreaming() {
  if (sendTimer) {
    window.clearInterval(sendTimer);
    sendTimer = null;
  }
  frameInFlight = false;
  setPill(streamStatus, "idle", "Idle");
  updateControls();
}

function disconnectSocket() {
  if (socket) {
    socket.close();
    socket = null;
  }
  stopStreaming();
  setPill(socketStatus, "idle", "Disconnected");
  updateControls();
}

function connectSocket() {
  if (peerConnection) {
    disconnectWebRtc();
  }

  const url = wsUrlInput.value.trim();
  if (!url) {
    log("WebSocket URL is required");
    return;
  }

  socket = new WebSocket(url);
  setPill(socketStatus, "warn", "WebSocket Connecting");
  log(`Connecting to ${url}`);
  updateControls();

  socket.onopen = () => {
    setPill(socketStatus, "ok", "WebSocket Connected");
    socket.send(`mode:${currentMode}`);
    log("WebSocket connected");
    updateControls();
  };

  socket.onclose = () => {
    socket = null;
    stopStreaming();
    setPill(socketStatus, "idle", "Disconnected");
    log("WebSocket closed");
    updateControls();
  };

  socket.onerror = () => {
    setPill(socketStatus, "error", "WebSocket Error");
    log("WebSocket error");
  };

  socket.onmessage = (event) => {
    frameInFlight = false;
    handleServerMessage(JSON.parse(event.data));
  };
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
      sentMeta.textContent = `${sentFrames} frames`;
    } catch (error) {
      frameInFlight = false;
      log(`Frame send failed: ${error.message}`);
    }
  }, "image/jpeg", quality);
}

function startStreaming() {
  if (currentTransport !== "ws") {
    return;
  }
  if (!socket || socket.readyState !== WebSocket.OPEN || !mediaStream || sendTimer) {
    return;
  }

  const fps = Math.max(1, Math.min(20, Number(fpsInput.value) || 3));
  const interval = Math.round(1000 / fps);
  sendTimer = window.setInterval(captureAndSend, interval);
  setPill(streamStatus, "ok", "WebSocket Streaming");
  log(`Streaming JPEG frames at ${fps} FPS`);
  updateControls();
}

function setupDataChannel(channel) {
  dataChannel = channel;

  dataChannel.onopen = () => {
    setPill(socketStatus, "ok", "WebRTC Connected");
    setPill(streamStatus, "ok", "WebRTC Streaming");
    log("WebRTC data channel opened");
    dataChannel.send(`mode:${currentMode}`);
    updateControls();
  };

  dataChannel.onclose = () => {
    log("WebRTC data channel closed");
  };

  dataChannel.onerror = (error) => {
    const message = error && error.message ? error.message : "unknown";
    log(`WebRTC data channel error: ${message}`);
  };

  dataChannel.onmessage = (event) => {
    handleServerMessage(JSON.parse(event.data));
  };
}

async function waitForIceGatheringComplete(pc) {
  if (pc.iceGatheringState === "complete") {
    return;
  }
  await new Promise((resolve) => {
    const timeoutId = window.setTimeout(() => {
      pc.removeEventListener("icegatheringstatechange", onStateChange);
      resolve();
    }, 1500);

    function onStateChange() {
      if (pc.iceGatheringState === "complete") {
        window.clearTimeout(timeoutId);
        pc.removeEventListener("icegatheringstatechange", onStateChange);
        resolve();
      }
    }
    pc.addEventListener("icegatheringstatechange", onStateChange);
  });
}

async function connectWebRtc() {
  if (socket) {
    disconnectSocket();
  }
  if (!mediaStream) {
    log("Open the camera before starting WebRTC");
    return;
  }

  const url = webrtcUrlInput.value.trim();
  if (!url) {
    log("WebRTC Offer URL is required");
    return;
  }

  try {
    peerConnection = new RTCPeerConnection();
    setupDataChannel(peerConnection.createDataChannel("results"));
    log("WebRTC peer connection created");

    peerConnection.onconnectionstatechange = () => {
      if (!peerConnection) {
        return;
      }
      const state = peerConnection.connectionState;
      if (state === "connecting") {
        setPill(socketStatus, "warn", "WebRTC Connecting");
      } else if (state === "connected") {
        setPill(socketStatus, "ok", "WebRTC Connected");
      } else if (state === "failed") {
        setPill(socketStatus, "error", "WebRTC Failed");
      } else if (state === "closed") {
        setPill(socketStatus, "idle", "Disconnected");
      }
    };

    mediaStream.getTracks().forEach((track) => {
      peerConnection.addTrack(track, mediaStream);
    });

    const offer = await peerConnection.createOffer();
    log("WebRTC offer created");
    await peerConnection.setLocalDescription(offer);
    log("Waiting for ICE gathering");
    await waitForIceGatheringComplete(peerConnection);
    log(`ICE gathering state: ${peerConnection.iceGatheringState}`);

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sdp: peerConnection.localDescription.sdp,
        type: peerConnection.localDescription.type,
        mode: currentMode
      })
    });
    log(`Offer posted to ${url}`);

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `HTTP ${response.status}`);
    }

    const answer = await response.json();
    await peerConnection.setRemoteDescription(answer);
    setPill(socketStatus, "warn", "WebRTC Negotiated");
    setPill(streamStatus, "warn", "Waiting for DataChannel");
    log(`WebRTC offer sent to ${url}`);
  } catch (error) {
    log(`WebRTC connection failed: ${error.message}`);
    disconnectWebRtc();
  }
  updateControls();
}

function disconnectWebRtc() {
  if (dataChannel) {
    dataChannel.close();
    dataChannel = null;
  }
  if (peerConnection) {
    peerConnection.close();
    peerConnection = null;
  }
  setPill(socketStatus, "idle", "Disconnected");
  setPill(streamStatus, "idle", "Idle");
  updateControls();
}

function changeMode(nextMode) {
  updateModeUi(nextMode);
  resetResultView();
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(`mode:${nextMode}`);
    log(`Requested mode ${nextMode} over WebSocket`);
  }
  if (dataChannel && dataChannel.readyState === "open") {
    dataChannel.send(`mode:${nextMode}`);
    log(`Requested mode ${nextMode} over WebRTC`);
  }
}

function changeTransport(nextTransport) {
  if (nextTransport === currentTransport) {
    return;
  }

  if (socket) {
    disconnectSocket();
  }
  if (peerConnection) {
    disconnectWebRtc();
  }

  resetResultView();
  updateTransportUi(nextTransport);
  setPill(streamStatus, "idle", nextTransport === "ws" ? "Idle" : "Waiting for WebRTC");
}

function connectActiveTransport() {
  if (currentTransport === "ws") {
    connectSocket();
  } else {
    connectWebRtc();
  }
}

function disconnectActiveTransport() {
  if (currentTransport === "ws") {
    disconnectSocket();
  } else {
    disconnectWebRtc();
  }
}

connectBtn.addEventListener("click", connectActiveTransport);
disconnectBtn.addEventListener("click", disconnectActiveTransport);
cameraBtn.addEventListener("click", openCamera);
startBtn.addEventListener("click", startStreaming);
stopBtn.addEventListener("click", stopStreaming);
clearLogBtn.addEventListener("click", () => {
  logOutput.innerHTML = "";
});

modeButtons.forEach((button) => {
  button.addEventListener("click", () => changeMode(button.dataset.mode));
});

transportButtons.forEach((button) => {
  button.addEventListener("click", () => changeTransport(button.dataset.transport));
});

window.addEventListener("beforeunload", () => {
  disconnectSocket();
  disconnectWebRtc();
  closeCamera();
});

setPill(socketStatus, "idle", "Disconnected");
setPill(cameraStatus, "idle", "Camera Offline");
setPill(streamStatus, "idle", "Idle");
updateModeUi("digits");
updateTransportUi("ws");
resetResultView();
sentMeta.textContent = "0 frames";
