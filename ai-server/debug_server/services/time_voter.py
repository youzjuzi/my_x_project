# -*- coding: utf-8 -*-
"""
TimeVoter 投票箱服务
====================

功能说明:
    维护一个"投票箱"来收集连续输入的字符，通过投票机制
    确定最终锁定的字符。当输入静默超过阈值时，自动锁定
    票数最多的字符。

工作流程:
    1. 收到字符 -> 加入投票箱 -> 返回当前票数最高的候选字符
    2. 后台定时检查是否超时
    3. 超时后 -> 获取最终获胜者 -> 清空投票箱

使用示例:
    voter = TimeVoter(timeout=1.0)
    
    # 连续收到输入
    candidate = voter.add('A')  # 返回 'A'
    candidate = voter.add('A')  # 返回 'A'
    candidate = voter.add('B')  # 返回 'A' (A票数更多)
    
    # 检查是否超时
    if voter.should_commit():
        winner = voter.get_final_winner()  # 返回 'A'，并清空投票箱
"""

import time
from collections import Counter
from typing import Optional, List, Tuple
from dataclasses import dataclass, field


@dataclass
class TimeVoter:
    """
    投票箱服务类
    
    通过收集一段时间内的输入字符，使用投票机制确定最终结果。
    这样可以有效过滤识别过程中的抖动和误识别。
    
    Attributes:
        timeout: 静默超时阈值（秒），超过此时间没有新输入则自动锁定
        bucket: 投票箱，存储最近接收到的字符
        last_input_time: 最后一次输入的时间戳
    
    Example:
        >>> voter = TimeVoter(timeout=1.0)
        >>> voter.add('A')
        'A'
        >>> voter.add('A')
        'A'
        >>> voter.add('B')
        'A'
        >>> time.sleep(1.1)
        >>> voter.should_commit()
        True
        >>> voter.get_final_winner()
        'A'
    """
    
    timeout: float = 1.0
    bucket: List[str] = field(default_factory=list)
    last_input_time: float = field(default_factory=time.time)
    
    def add(self, char: str) -> str:
        """
        添加字符到投票箱
        
        Args:
            char: 输入的字符（字母/数字/功能键）
            
        Returns:
            当前票数最高的候选字符
            
        Note:
            每次添加都会更新 last_input_time
        """
        self.last_input_time = time.time()
        self.bucket.append(char)
        
        # 返回当前票数最高的字符
        return self._get_top_candidate()
    
    def should_commit(self) -> bool:
        """
        判断是否应该锁定字符
        
        Returns:
            True: 超时且投票箱不为空，应该锁定
            False: 未超时或投票箱为空
            
        Note:
            超时条件: (当前时间 - 最后输入时间) > timeout
        """
        if not self.bucket:
            return False
        
        elapsed = time.time() - self.last_input_time
        return elapsed > self.timeout
    
    def get_final_winner(self) -> Tuple[Optional[str], int]:
        """
        获取最终获胜者并清空投票箱
        
        Returns:
            (winner, count) 元组:
                winner: 票数最多的字符，如果投票箱为空则返回 None
                count: 获胜字符的票数
            
        Note:
            调用此方法后，投票箱会被清空
        """
        if not self.bucket:
            return None, 0
        
        counter = Counter(self.bucket)
        winner, count = counter.most_common(1)[0]
        self.bucket.clear()
        return winner, count
    
    def _get_top_candidate(self) -> str:
        """
        获取当前票数最高的候选字符
        
        Returns:
            票数最多的字符
        """
        if not self.bucket:
            return ""
        
        counter = Counter(self.bucket)
        # most_common(1) 返回 [(char, count)]
        return counter.most_common(1)[0][0]
    
    def get_current_candidate(self) -> Optional[str]:
        """
        获取当前候选字符（不清空投票箱）
        
        Returns:
            当前票数最高的字符，如果投票箱为空则返回 None
        """
        if not self.bucket:
            return None
        return self._get_top_candidate()
    
    def clear(self) -> None:
        """清空投票箱"""
        self.bucket.clear()
    
    def __repr__(self) -> str:
        """调试用的字符串表示"""
        candidate = self._get_top_candidate() if self.bucket else "None"
        return f"TimeVoter(bucket={self.bucket}, candidate={candidate})"
