# -*- coding: utf-8 -*-
"""
配置管理模块
===========

集中管理所有服务配置项。
"""


class Config:
    """
    服务配置类
    
    Attributes:
        HOST: 服务监听地址
        PORT: 服务端口
        DEBUG: 是否开启调试模式
        VOTER_TIMEOUT: 投票超时时间（秒）
        VOTER_CHECK_INTERVAL: 超时检查间隔（秒）
    """
    # 服务配置
    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True
    
    # TimeVoter 配置
    VOTER_TIMEOUT: float = 1.0     # 静默超时阈值（秒）
    VOTER_CHECK_INTERVAL: float = 0.1  # 超时检查间隔（秒）
    
    # Java 后端配置
    JAVA_BACKEND_HOST: str = "localhost"
    JAVA_BACKEND_PORT: int = 9999
