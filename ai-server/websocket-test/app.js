const wsUrlInput = document.getElementById("wsUrl");
const clientNameInput = document.getElementById("clientName");
const messageInput = document.getElementById("messageInput");
const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const clearLogBtn = document.getElementById("clearLogBtn");
const sendTextBtn = document.getElementById("sendTextBtn");
const sendJsonBtn = document.getElementById("sendJsonBtn");
const useTemplateBtn = document.getElementById("useTemplateBtn");
const logOutput = document.getElementById("logOutput");
const statusBadge = document.getElementById("statusBadge");
const messageCount = document.getElementById("messageCount");

let socket = null;
let logCounter = 0;

const templates = {
  ping: {
    type: "ping",
    client: "mediapipe-debug-client",
    timestamp: new Date().toISOString()
  },
  start: {
    type: "start_detection",
    source: "websocket-test-page",
    model: "hand_landmarker",
    timestamp: new Date().toISOString()
  },
  frame: {
    type: "frame_meta",
    frameId: 1,
    width: 1280,
    height: 720,
    timestamp: new Date().toISOString()
  }
};

function setStatus(state, text) {
  statusBadge.className = `badge ${state}`;
  statusBadge.textContent = text;
}

function setControlsConnected(connected) {
  connectBtn.disabled = connected;
  disconnectBtn.disabled = !connected;
  sendTextBtn.disabled = !connected;
  sendJsonBtn.disabled = !connected;
}

function formatPayload(payload) {
  if (typeof payload === "string") {
    return payload;
  }
  try {
    return JSON.stringify(payload, null, 2);
  } catch (error) {
    return String(payload);
  }
}

function addLog(kind, label, payload) {
  logCounter += 1;
  messageCount.textContent = `${logCounter} 条`;

  const item = document.createElement("article");
  item.className = `log-entry ${kind}`;

  const time = document.createElement("span");
  time.className = "log-time";
  time.textContent = new Date().toLocaleTimeString();

  const content = document.createElement("div");
  content.className = "log-content";
  content.innerHTML = `<span class="log-label">${label}</span>${escapeHtml(formatPayload(payload))}`;

  item.appendChild(time);
  item.appendChild(content);
  logOutput.prepend(item);
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function connect() {
  const url = wsUrlInput.value.trim();
  if (!url) {
    addLog("error", "ERROR", "请先输入 WebSocket 地址");
    return;
  }

  try {
    socket = new WebSocket(url);
    setStatus("idle", "连接中");
    addLog("system", "SYSTEM", `尝试连接 ${url}`);
  } catch (error) {
    setStatus("error", "连接失败");
    addLog("error", "ERROR", error.message || String(error));
    return;
  }

  socket.addEventListener("open", () => {
    setStatus("connected", "已连接");
    setControlsConnected(true);
    const hello = {
      type: "hello",
      client: clientNameInput.value.trim() || "websocket-test-client",
      timestamp: new Date().toISOString()
    };
    socket.send(JSON.stringify(hello));
    addLog("system", "OPEN", "连接已建立");
    addLog("outgoing", "SEND", hello);
  });

  socket.addEventListener("message", (event) => {
    addLog("incoming", "RECV", event.data);
  });

  socket.addEventListener("error", () => {
    setStatus("error", "连接异常");
    addLog("error", "ERROR", "WebSocket 发生错误");
  });

  socket.addEventListener("close", (event) => {
    setStatus("idle", "未连接");
    setControlsConnected(false);
    addLog("system", "CLOSE", `连接关闭 code=${event.code} reason=${event.reason || "none"}`);
    socket = null;
  });
}

function disconnect() {
  if (!socket) {
    return;
  }
  socket.close(1000, "client disconnect");
}

function sendRaw(text) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    addLog("error", "ERROR", "连接尚未建立");
    return;
  }
  socket.send(text);
  addLog("outgoing", "SEND", text);
}

function sendJson() {
  const raw = messageInput.value.trim();
  if (!raw) {
    addLog("error", "ERROR", "消息内容为空");
    return;
  }
  try {
    const parsed = JSON.parse(raw);
    socket.send(JSON.stringify(parsed));
    addLog("outgoing", "SEND", parsed);
  } catch (error) {
    addLog("error", "ERROR", `JSON 格式不合法: ${error.message}`);
  }
}

function fillTemplate(name) {
  const next = { ...templates[name], timestamp: new Date().toISOString() };
  if (next.client) {
    next.client = clientNameInput.value.trim() || next.client;
  }
  messageInput.value = JSON.stringify(next, null, 2);
}

connectBtn.addEventListener("click", connect);
disconnectBtn.addEventListener("click", disconnect);
clearLogBtn.addEventListener("click", () => {
  logOutput.innerHTML = "";
  logCounter = 0;
  messageCount.textContent = "0 条";
});
sendTextBtn.addEventListener("click", () => sendRaw(messageInput.value));
sendJsonBtn.addEventListener("click", sendJson);
useTemplateBtn.addEventListener("click", () => fillTemplate("ping"));

document.querySelectorAll("[data-template]").forEach((button) => {
  button.addEventListener("click", () => fillTemplate(button.dataset.template));
});

fillTemplate("ping");
setStatus("idle", "未连接");
setControlsConnected(false);
