# -*- coding: utf-8 -*-
"""
AI Server 主入口
================

统一的服务启动入口，运行该脚本将启动 WebRTC 手语检测服务。

使用方式:
    python main.py
"""

import uvicorn
from server import config

def main():
    print("🚀 正在启动 WebRTC 检测服务...")
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    手语识别 WebRTC 检测服务                      ║
╠══════════════════════════════════════════════════════════════╣
║  接口服务运行在:  http://{config.HOST}:{config.WEBRTC_PORT}                      ║
║  请在前端点击“开启识别”连接到大屏幕                               ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 启动 FastAPI WebRTC 服务，相当于 python -m server.app_webrtc
    uvicorn.run(
        "server.app_webrtc:app",
        host=config.HOST,
        port=config.WEBRTC_PORT,
        reload=False
    )

if __name__ == "__main__":
    main()
