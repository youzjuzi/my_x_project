# -*- coding: utf-8 -*-
"""
AI Server 主入口
================

统一的服务启动入口，管理所有子服务的启动。

使用方式:
    # 启动调试服务
    python main.py debug
    
    # 启动检测服务（原 app.py）
    python main.py detect
    
    # 显示帮助信息
    python main.py --help

依赖:
    pip install fastapi uvicorn websockets

作者: AI Assistant
日期: 2026-02-09
"""

import sys
import argparse


def start_debug_server():
    """
    启动手语识别调试服务
    
    端口: 8000
    WebSocket 地址: ws://localhost:8000/ws
    """
    print("🚀 正在启动调试服务...")
    from debug_server.server import app, Config
    import uvicorn
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    手语识别调试服务                              ║
╠══════════════════════════════════════════════════════════════╣
║  WebSocket 地址: ws://{Config.HOST}:{Config.PORT}/ws                      ║
║  健康检查地址:   http://{Config.HOST}:{Config.PORT}/                       ║
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


def start_detect_server():
    """
    启动手语检测服务（原 app.py）
    
    端口: 5000
    使用 Flask-SocketIO
    """
    print("🚀 正在启动检测服务...")
    from app import socketio, app
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    手语识别检测服务                              ║
╠══════════════════════════════════════════════════════════════╣
║  HTTP 地址:      http://localhost:5000                       ║
║  SocketIO 地址:  ws://localhost:5000                         ║
║                                                              ║
║  等待客户端连接...                                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    socketio.run(
        app, 
        debug=True, 
        host="localhost", 
        port=5000, 
        allow_unsafe_werkzeug=True
    )


def main():
    """
    主入口函数
    
    解析命令行参数并启动对应的服务
    """
    parser = argparse.ArgumentParser(
        description="AI Server - 手语识别服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py debug     启动调试服务 (端口 8000)
  python main.py detect    启动检测服务 (端口 5000)
        """
    )
    
    parser.add_argument(
        "service",
        choices=["debug", "detect"],
        nargs="?",
        default="debug",
        help="要启动的服务类型 (默认: debug)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用的服务"
    )
    
    args = parser.parse_args()
    
    # 显示可用服务列表
    if args.list:
        print("""
可用服务:
  debug   - 手语识别调试服务 (端口 8000, WebSocket)
            用于前端 SignDebug 页面的模拟输入测试
            
  detect  - 手语识别检测服务 (端口 5000, Flask-SocketIO)
            用于真实摄像头手语识别
        """)
        return
    
    # 启动对应服务
    if args.service == "debug":
        start_debug_server()
    elif args.service == "detect":
        start_detect_server()


if __name__ == "__main__":
    main()
