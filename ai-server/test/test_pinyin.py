# -*- coding: utf-8 -*-
"""
测试 Pinyin2Hanzi 库的正确用法
"""

from Pinyin2Hanzi import DefaultDagParams, dag

# 初始化
dagParams = DefaultDagParams()

# 测试1: 单个拼音
print("=== 测试单个拼音 ===")
try:
    result = dag(dagParams, ['ni'], path_num=1)
    if result:
        print(f"输入: ['ni']")
        print(f"结果类型: {type(result[0])}")
        print(f"结果: {result[0]}")
        print(f"path 属性: {result[0].path}")
        print(f"path 类型: {type(result[0].path)}")
except Exception as e:
    print(f"错误: {e}")

# 测试2: 多个拼音
print("\n=== 测试多个拼音 ===")
try:
    result = dag(dagParams, ['ni', 'hao'], path_num=1)
    if result:
        print(f"输入: ['ni', 'hao']")
        print(f"结果: {result[0]}")
        print(f"path 属性: {result[0].path}")
except Exception as e:
    print(f"错误: {e}")

# 测试3: 单字符
print("\n=== 测试单字符 ===")
try:
    result = dag(dagParams, ['n'], path_num=1)
    if result:
        print(f"输入: ['n']")
        print(f"path 属性: {result[0].path}")
except Exception as e:
    print(f"错误: {e}")
