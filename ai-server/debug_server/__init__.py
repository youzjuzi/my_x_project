# -*- coding: utf-8 -*-
"""
手语识别调试服务模块
==================

目录结构:
    debug_server/
    ├── __init__.py      # 模块入口
    ├── config.py        # 配置管理
    ├── server.py        # WebSocket 服务
    ├── models/          # 数据模型
    │   └── __init__.py  # PinyinState
    └── services/        # 业务服务
        ├── __init__.py
        └── time_voter.py  # TimeVoter 投票箱
"""

from .config import Config
from .models import PinyinState
from .services import TimeVoter

__all__ = ['Config', 'PinyinState', 'TimeVoter']
