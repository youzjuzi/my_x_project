# -*- coding: utf-8 -*-
"""
数据模型模块
===========

定义消息和状态的数据结构。
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class PinyinState:
    """
    拼音状态管理
    
    Attributes:
        buffer: 当前拼音缓冲区 (如: "nihao")
        sentence: 已确认的句子 (如: "你好世界")
        hanzi_candidate: 当前显示的汉字候选词 (如: "你好")
        hanzi_candidates: 所有汉字候选词列表
        candidate_index: 当前候选词索引
    """
    buffer: str = ""
    sentence: str = ""
    hanzi_candidate: str = ""
    hanzi_candidates: List[str] = field(default_factory=list)
    candidate_index: int = 0
    
    def add_char(self, char: str) -> None:
        """添加字符到缓冲区"""
        self.buffer += char.lower()
        
    def backspace(self) -> None:
        """删除缓冲区最后一个字符"""
        if self.buffer:
            self.buffer = self.buffer[:-1]
    
    def update_hanzi_candidate(self, converter) -> None:
        """
        根据当前 buffer 更新所有汉字候选词
        
        Args:
            converter: PinyinConverter 实例
        """
        if self.buffer:
            self.hanzi_candidates = converter.convert_with_candidates(self.buffer, num=5)
            self.candidate_index = 0
            self.hanzi_candidate = self.hanzi_candidates[0] if self.hanzi_candidates else ""
        else:
            self.hanzi_candidate = ""
            self.hanzi_candidates = []
            self.candidate_index = 0
    
    def cycle_candidate(self) -> None:
        """切换到下一个候选词（循环）"""
        if self.hanzi_candidates:
            self.candidate_index = (self.candidate_index + 1) % len(self.hanzi_candidates)
            self.hanzi_candidate = self.hanzi_candidates[self.candidate_index]
            
    def confirm_pinyin(self) -> None:
        """
        确认当前拼音 (Space 键)
        将汉字候选词添加到句子中, 然后清空缓冲区和候选词
        每个确认的词/字用方括号包裹，方便后续 AI 润色
        """
        if self.hanzi_candidate:
            self.sentence += f"[{self.hanzi_candidate}]"
            self.buffer = ""
            self.hanzi_candidate = ""
            self.hanzi_candidates = []
            self.candidate_index = 0
        elif self.buffer:
            # 如果没有汉字候选词，直接添加拼音
            self.sentence += f"[{self.buffer}]"
            self.buffer = ""
            
    def submit_sentence(self) -> str:
        """
        提交整句 (Enter 键)
        返回完整句子并清空状态
        """
        # 如果还有未确认的汉字候选词，先添加到句子
        if self.hanzi_candidate:
            self.sentence += f"[{self.hanzi_candidate}]"
        elif self.buffer:
            self.sentence += f"[{self.buffer}]"
        
        full_sentence = self.sentence
        self.buffer = ""
        self.sentence = ""
        self.hanzi_candidate = ""
        self.hanzi_candidates = []
        self.candidate_index = 0
        return full_sentence
    
    def clear(self) -> None:
        """清空所有状态"""
        self.buffer = ""
        self.sentence = ""
        self.hanzi_candidate = ""
        self.hanzi_candidates = []
        self.candidate_index = 0
        
    def to_dict(self) -> dict:
        """转换为响应字典"""
        return {
            "buffer": self.buffer,
            "sentence": self.sentence,
            "hanzi_candidate": self.hanzi_candidate,
            "hanzi_candidates": self.hanzi_candidates,
            "candidate_index": self.candidate_index
        }

