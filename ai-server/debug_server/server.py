# -*- coding: utf-8 -*-
"""
手语识别调试服务 - WebSocket 服务器
=============================================

功能说明:
    接收前端 SignDebug.vue 发来的模拟输入消息,
    使用 TimeVoter 投票机制过滤抖动，并在终端清晰显示。

消息格式:

    前端发送:
    {
        "type": "mock",
        "label": "A",
        "timestamp": 1707000000000
    }

    后端响应 - 状态更新:
    {
        "type": "state_update",
        "candidate": "A",       # 当前候选字符（灰色显示）
        "buffer": "nihao",      # 拼音缓冲区
        "sentence": "你好"       # 已生成句子
    }

运行方式:
    cd ai-server
    python main.py debug

作者: AI Assistant
日期: 2026-02-09
"""

import json
import asyncio
import requests
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入模块
from .config import Config
from .models import PinyinState
from .services import TimeVoter, PinyinConverter


# =============================================================================
# WebSocket 连接管理
# =============================================================================

class ConnectionManager:
    """
    WebSocket 连接管理器
    
    管理所有活跃的 WebSocket 连接。
    每个连接都有独立的 PinyinState 和 TimeVoter。
    """
    
    def __init__(self):
        # 活跃连接列表
        self.active_connections: list[WebSocket] = []
        # 每个连接的状态 (使用 id 作为 key)
        self.states: Dict[int, PinyinState] = {}
        # 每个连接的投票器
        self.voters: Dict[int, TimeVoter] = {}
        # 每个连接的拼音转换器
        self.converters: Dict[int, PinyinConverter] = {}
        # 每个连接的用户ID
        self.user_ids: Dict[int, str] = {}
        # 后台任务
        self.tasks: Dict[int, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # 为新连接创建状态、投票器和转换器
        conn_id = id(websocket)
        self.states[conn_id] = PinyinState()
        self.voters[conn_id] = TimeVoter(timeout=Config.VOTER_TIMEOUT)
        self.converters[conn_id] = PinyinConverter()
        self.user_ids[conn_id] = user_id
        
        self._log_event("连接", f"新客户端连接 (用户: {user_id}), 当前连接数: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket) -> None:
        """处理 WebSocket 断开连接"""
        conn_id = id(websocket)
        user_id = self.user_ids.get(conn_id, "Unknown")
        
        # 取消后台任务
        if conn_id in self.tasks:
            self.tasks[conn_id].cancel()
            del self.tasks[conn_id]
            
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        # 清理状态
        if conn_id in self.states:
            del self.states[conn_id]
        if conn_id in self.voters:
            del self.voters[conn_id]
        if conn_id in self.converters:
            del self.converters[conn_id]
        if conn_id in self.user_ids:
            del self.user_ids[conn_id]
            
        self._log_event("断开", f"客户端断开 (用户: {user_id}), 当前连接数: {len(self.active_connections)}")
        
    def get_state(self, websocket: WebSocket) -> PinyinState:
        """获取连接对应的状态"""
        return self.states.get(id(websocket), PinyinState())
    
    def get_voter(self, websocket: WebSocket) -> TimeVoter:
        """获取连接对应的投票器"""
        return self.voters.get(id(websocket), TimeVoter())
    
    def get_converter(self, websocket: WebSocket) -> PinyinConverter:
        """获取连接对应的拼音转换器"""
        return self.converters.get(id(websocket), PinyinConverter())
    
    async def send_response(self, websocket: WebSocket, data: dict) -> None:
        """向指定客户端发送响应"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            self._log_event("错误", f"发送消息失败: {e}")
            
    def _log_event(self, event_type: str, message: str) -> None:
        """打印带时间戳的日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{event_type}] {message}")


# =============================================================================
# FastAPI 应用
# =============================================================================

app = FastAPI(
    title="手语识别调试服务",
    description="接收前端模拟输入, 使用投票机制处理",
    version="2.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 连接管理器实例
manager = ConnectionManager()


# =============================================================================
# 后台定时任务
# =============================================================================

async def timer_task(websocket: WebSocket):
    """
    后台定时任务 - 检查投票超时
    
    每隔 VOTER_CHECK_INTERVAL 秒检查一次:
    - 如果超时且投票箱不为空，锁定字符并通知前端
    
    Args:
        websocket: 对应的 WebSocket 连接
    """
    try:
        while True:
            await asyncio.sleep(Config.VOTER_CHECK_INTERVAL)
            
            voter = manager.get_voter(websocket)
            state = manager.get_state(websocket)
            converter = manager.get_converter(websocket)
            
            # 检查是否超时
            if voter.should_commit():
                winner, count = voter.get_final_winner()
                
                if winner:
                    # 打印锁定信息
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f"\n{'='*60}")
                    print(f"[{timestamp}] ⏰ 超时锁定!")
                    print(f"{'='*60}")
                    print(f"🔒 锁定字符: {winner} (票数: {count})")
                    
                    # 处理锁定的字符
                    if winner == "Backspace":
                        state.backspace()
                        state.update_hanzi_candidate(converter)
                        print(f"⬅️  执行删除")
                    elif winner == "Space":
                        if count >= 2 and state.hanzi_candidates:
                            # 双击 Space → 切换候选词
                            state.cycle_candidate()
                            print(f"🔄 切换候选词 -> {state.hanzi_candidate} ({state.candidate_index + 1}/{len(state.hanzi_candidates)})")
                        else:
                            # 单击 Space → 确认候选词
                            state.confirm_pinyin()
                            print(f"✅ 确认拼音 -> 汉字: {state.sentence}")
                    elif winner == "Enter":
                        submitted = state.submit_sentence()
                        print(f"📤 提交句子: {submitted}")
                        
                        # 获取用户 ID
                        user_id = manager.user_ids.get(id(websocket), "Anonymous")
                        
                        # 发送到 Java 后端
                        if user_id != "Anonymous":
                            try:
                                url = f"http://{Config.JAVA_BACKEND_HOST}:{Config.JAVA_BACKEND_PORT}/sign/submit"
                                payload = {"userId": user_id, "content": submitted}
                                
                                # 在线程池中异步执行请求，避免阻塞主循环
                                loop = asyncio.get_event_loop()
                                await loop.run_in_executor(None, lambda: requests.post(url, json=payload))
                                print(f"✅ 已推送到 Java 后端 (User: {user_id})")
                            except Exception as e:
                                print(f"❌ 推送失败: {e}")
                    elif winner == "Null":
                        print(f"⏸️  空操作")
                    elif winner.isalnum():
                        state.add_char(winner)
                        state.update_hanzi_candidate(converter)
                        print(f"➕ 添加字符: {winner}")
                    
                    print(f"\n📊 当前状态:")
                    print(f"   拼音缓冲区: '{state.buffer}'")
                    print(f"   汉字候选:   '{state.hanzi_candidate}' ({state.candidate_index + 1}/{len(state.hanzi_candidates) if state.hanzi_candidates else 0})")
                    print(f"   句子:       '{state.sentence}'")
                    print(f"{'='*60}\n")
                    
                    # 向前端推送状态更新（清空候选字符）
                    response = {
                        "type": "state_update",
                        "candidate": "",  # 清空候选
                        "buffer": state.buffer,
                        "hanzi_candidate": state.hanzi_candidate,
                        "hanzi_candidates": state.hanzi_candidates,
                        "candidate_index": state.candidate_index,
                        "sentence": state.sentence
                    }
                    
                    if 'submitted' in locals() and submitted:
                         response["submitted"] = submitted
                         submitted = None # 重置

                    await manager.send_response(websocket, response)
                    
    except asyncio.CancelledError:
        # 任务被取消，正常退出
        pass


# =============================================================================
# WebSocket 端点
# =============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, userId: str = Query(None)):
    """
    WebSocket 主端点
    
    处理逻辑:
    1. 收到字符 -> 加入投票箱 -> 返回候选字符给前端（灰色显示）
    2. 后台任务检测超时 -> 锁定字符 -> 更新状态 -> 通知前端
    """
    if userId is None:
        userId = "Anonymous"
        
    await manager.connect(websocket, userId)
    
    # 启动后台定时任务
    task = asyncio.create_task(timer_task(websocket))
    manager.tasks[id(websocket)] = task
    
    state = manager.get_state(websocket)
    voter = manager.get_voter(websocket)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            # ========== 在终端显示收到的 JSON ==========
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"\n{'='*60}")
            print(f"[{timestamp}] 📥 收到前端消息:")
            print(f"{'='*60}")
            
            try:
                # 解析 JSON
                message = json.loads(data)
                print(json.dumps(message, indent=2, ensure_ascii=False))
                
                # 提取关键信息
                msg_type = message.get("type", "unknown")
                label = message.get("label", "")
                
                print(f"\n📌 消息类型: {msg_type}")
                print(f"📌 输入标签: {label}")
                
                # ========== 处理消息逻辑 ==========
                if msg_type == "mock" and label:
                    # 加入投票箱，获取当前候选
                    candidate = voter.add(label)
                    
                    print(f"🗳️  投票箱状态: {voter.bucket}")
                    print(f"👆 当前候选: {candidate}")
                    print(f"{'='*60}\n")
                    
                    # 立即向前端回传候选字符（灰色显示）
                    response = {
                        "type": "state_update",
                        "candidate": candidate,  # 当前候选（未锁定）
                        "buffer": state.buffer,
                        "hanzi_candidate": state.hanzi_candidate,
                        "hanzi_candidates": state.hanzi_candidates,
                        "candidate_index": state.candidate_index,
                        "sentence": state.sentence
                    }
                    await manager.send_response(websocket, response)
                else:
                    print(f"⚠️  未处理的消息类型: {msg_type}")
                    print(f"{'='*60}\n")
                
            except json.JSONDecodeError:
                print(f"⚠️  无法解析 JSON: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# =============================================================================
# HTTP 端点 (用于健康检查)
# =============================================================================

@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "running",
        "service": "手语识别调试服务 v2.0",
        "websocket": f"ws://{Config.HOST}:{Config.PORT}/ws",
        "features": ["TimeVoter 投票机制", "后台超时检测"]
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "connections": len(manager.active_connections)
    }


@app.post("/notify/ai_result")
async def notify_ai_result(payload: dict):
    """
    接收 Java 后端推送的 AI 润色结果，并通过 WebSocket 转发给前端
    Payload: { "userId": "1", "result": "..." }
    """
    user_id = payload.get("userId")
    ai_result = payload.get("result")
    
    if not user_id or not ai_result:
        return {"status": "error", "message": "Missing userId or result"}
        
    print(f"📩 收到 AI 结果推送 (User: {user_id}): {ai_result}")
    
    # 查找对应用户的 WebSocket 连接
    target_ws = None
    for ws, uid in manager.user_ids.items():
        if str(uid) == str(user_id):
            # manager.user_ids key is id(ws), value is userId
            # Need to find the ws object from active_connections
            for conn in manager.active_connections:
                if id(conn) == ws:
                    target_ws = conn
                    break
            if target_ws:
                break
    
    if target_ws:
        response = {
            "type": "ai_result",
            "content": ai_result
        }
        await manager.send_response(target_ws, response)
        print(f"✅ 已转发 AI 结果给前端 (User: {user_id})")
        return {"status": "success", "message": "Notification sent"}
    else:
        print(f"⚠️  未找到用户 {user_id} 的 WebSocket 连接，无法推送")
        return {"status": "warning", "message": "User not connected"}


# =============================================================================
# 主入口 (仅用于直接运行)
# =============================================================================

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                手语识别调试服务 v2.0                            ║
╠══════════════════════════════════════════════════════════════╣
║  WebSocket 地址: ws://{Config.HOST}:{Config.PORT}/ws                      ║
║  健康检查地址:   http://{Config.HOST}:{Config.PORT}/                       ║
║                                                              ║
║  新功能:                                                      ║
║  - TimeVoter 投票机制                                         ║
║  - 后台超时检测 ({Config.VOTER_TIMEOUT}s)                                  ║
║                                                              ║
║  等待前端连接...                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info" if Config.DEBUG else "warning"
    )
