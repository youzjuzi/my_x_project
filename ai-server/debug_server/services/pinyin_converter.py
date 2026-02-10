# -*- coding: utf-8 -*-
"""
拼音转汉字服务
=============

使用 Pinyin2Hanzi 库将拼音转换为汉字候选词。
"""

from Pinyin2Hanzi import DefaultDagParams, dag
from typing import List, Optional


# 所有有效的拼音音节（按长度排序，优先匹配长音节）
VALID_PINYIN_SET = {
    # 单音节
    'a', 'ai', 'an', 'ang', 'ao', 'e', 'ei', 'en', 'eng', 'er', 'o', 'ou',
    # b 系列
    'ba', 'bai', 'ban', 'bang', 'bao', 'bei', 'ben', 'beng', 'bi', 'bian', 'biao', 'bie', 'bin', 'bing', 'bo', 'bu',
    # p 系列
    'pa', 'pai', 'pan', 'pang', 'pao', 'pei', 'pen', 'peng', 'pi', 'pian', 'piao', 'pie', 'pin', 'ping', 'po', 'pou', 'pu',
    # m 系列
    'ma', 'mai', 'man', 'mang', 'mao', 'me', 'mei', 'men', 'meng', 'mi', 'mian', 'miao', 'mie', 'min', 'ming', 'miu', 'mo', 'mou', 'mu',
    # f 系列
    'fa', 'fan', 'fang', 'fei', 'fen', 'feng', 'fo', 'fou', 'fu',
    # d 系列
    'da', 'dai', 'dan', 'dang', 'dao', 'de', 'dei', 'den', 'deng', 'di', 'dia', 'dian', 'diao', 'die', 'ding', 'diu', 'dong', 'dou', 'du', 'duan', 'dui', 'dun', 'duo',
    # t 系列
    'ta', 'tai', 'tan', 'tang', 'tao', 'te', 'tei', 'teng', 'ti', 'tian', 'tiao', 'tie', 'ting', 'tong', 'tou', 'tu', 'tuan', 'tui', 'tun', 'tuo',
    # n 系列
    'na', 'nai', 'nan', 'nang', 'nao', 'ne', 'nei', 'nen', 'neng', 'ni', 'nian', 'niang', 'niao', 'nie', 'nin', 'ning', 'niu', 'nong', 'nou', 'nu', 'nuan', 'nuo', 'nv', 'nve',
    # l 系列
    'la', 'lai', 'lan', 'lang', 'lao', 'le', 'lei', 'leng', 'li', 'lia', 'lian', 'liang', 'liao', 'lie', 'lin', 'ling', 'liu', 'lo', 'long', 'lou', 'lu', 'luan', 'lun', 'luo', 'lv', 'lve',
    # g 系列
    'ga', 'gai', 'gan', 'gang', 'gao', 'ge', 'gei', 'gen', 'geng', 'gong', 'gou', 'gu', 'gua', 'guai', 'guan', 'guang', 'gui', 'gun', 'guo',
    # k 系列
    'ka', 'kai', 'kan', 'kang', 'kao', 'ke', 'kei', 'ken', 'keng', 'kong', 'kou', 'ku', 'kua', 'kuai', 'kuan', 'kuang', 'kui', 'kun', 'kuo',
    # h 系列
    'ha', 'hai', 'han', 'hang', 'hao', 'he', 'hei', 'hen', 'heng', 'hong', 'hou', 'hu', 'hua', 'huai', 'huan', 'huang', 'hui', 'hun', 'huo',
    # j 系列
    'ji', 'jia', 'jian', 'jiang', 'jiao', 'jie', 'jin', 'jing', 'jiong', 'jiu', 'ju', 'juan', 'jue', 'jun',
    # q 系列
    'qi', 'qia', 'qian', 'qiang', 'qiao', 'qie', 'qin', 'qing', 'qiong', 'qiu', 'qu', 'quan', 'que', 'qun',
    # x 系列
    'xi', 'xia', 'xian', 'xiang', 'xiao', 'xie', 'xin', 'xing', 'xiong', 'xiu', 'xu', 'xuan', 'xue', 'xun',
    # z 系列
    'za', 'zai', 'zan', 'zang', 'zao', 'ze', 'zei', 'zen', 'zeng', 'zha', 'zhai', 'zhan', 'zhang', 'zhao', 'zhe', 'zhei', 'zhen', 'zheng', 'zhi', 'zhong', 'zhou', 'zhu', 'zhua', 'zhuai', 'zhuan', 'zhuang', 'zhui', 'zhun', 'zhuo', 'zi', 'zong', 'zou', 'zu', 'zuan', 'zui', 'zun', 'zuo',
    # c 系列
    'ca', 'cai', 'can', 'cang', 'cao', 'ce', 'cei', 'cen', 'ceng', 'cha', 'chai', 'chan', 'chang', 'chao', 'che', 'chen', 'cheng', 'chi', 'chong', 'chou', 'chu', 'chua', 'chuai', 'chuan', 'chuang', 'chui', 'chun', 'chuo', 'ci', 'cong', 'cou', 'cu', 'cuan', 'cui', 'cun', 'cuo',
    # s 系列
    'sa', 'sai', 'san', 'sang', 'sao', 'se', 'sei', 'sen', 'seng', 'sha', 'shai', 'shan', 'shang', 'shao', 'she', 'shei', 'shen', 'sheng', 'shi', 'shou', 'shu', 'shua', 'shuai', 'shuan', 'shuang', 'shui', 'shun', 'shuo', 'si', 'song', 'sou', 'su', 'suan', 'sui', 'sun', 'suo',
    # r 系列
    'ran', 'rang', 'rao', 're', 'ren', 'reng', 'ri', 'rong', 'rou', 'ru', 'rua', 'ruan', 'rui', 'run', 'ruo',
    # y 系列
    'ya', 'yan', 'yang', 'yao', 'ye', 'yi', 'yin', 'ying', 'yo', 'yong', 'you', 'yu', 'yuan', 'yue', 'yun',
    # w 系列
    'wa', 'wai', 'wan', 'wang', 'wei', 'wen', 'weng', 'wo', 'wu',
}


def split_pinyin(pinyin_str: str) -> List[str]:
    """
    将拼音字符串分割成拼音音节列表（贪心算法）
    
    Args:
        pinyin_str: 拼音字符串，如 "nihao"
        
    Returns:
        拼音音节列表，如 ['ni', 'hao']
    """
    result = []
    i = 0
    pinyin_str = pinyin_str.lower()
    
    while i < len(pinyin_str):
        matched = False
        # 尝试最长匹配（从6个字符开始尝试，递减到1个字符）
        for length in range(min(6, len(pinyin_str) - i), 0, -1):
            segment = pinyin_str[i:i+length]
            if segment in VALID_PINYIN_SET:
                result.append(segment)
                i += length
                matched = True
                break
        
        if not matched:
            # 无法匹配，跳过当前字符
            i += 1
    
    return result


class PinyinConverter:
    """
    拼音转汉字转换器
    
    使用 DAG 算法找到最优的拼音到汉字转换路径。
    
    Example:
        >>> converter = PinyinConverter()
        >>> converter.convert("nihao")
        '你好'
        >>> converter.convert("ni")
        '你'
    """
    
    def __init__(self):
        """初始化 DAG 参数"""
        self.dag_params = DefaultDagParams()
    
    def convert(self, pinyin_str: str) -> str:
        """
        拼音转汉字，返回第一个候选词
        
        Args:
            pinyin_str: 拼音字符串，如 "nihao"
            
        Returns:
            汉字候选词，如 "你好"
            如果无法转换则返回空字符串
        """
        if not pinyin_str:
            return ""
        
        # 转换为小写
        pinyin_str = pinyin_str.lower().strip()
        
        if not pinyin_str:
            return ""
        
        try:
            # 使用自定义分割函数将拼音字符串分割成拼音列表
            pinyin_list = split_pinyin(pinyin_str)
            
            if not pinyin_list:
                return ""
            
            # 使用 DAG 算法获取候选结果
            result = dag(self.dag_params, pinyin_list, path_num=1)
            
            if result and len(result) > 0:
                # 获取第一个候选词的 path
                path = result[0].path
                
                # 处理返回值格式
                if isinstance(path, list):
                    # 如果是列表，连接成字符串
                    return ''.join(path) if path else ""
                elif isinstance(path, str):
                    # 如果是字符串，去除可能的方括号和引号
                    cleaned = path.strip()
                    if cleaned.startswith('[') and cleaned.endswith(']'):
                        # 去除方括号
                        cleaned = cleaned[1:-1]
                        # 去除引号
                        cleaned = cleaned.strip("'\"")
                    return cleaned
                else:
                    return str(path)
            else:
                # 无法转换，返回空字符串
                return ""
                
        except Exception as e:
            # 转换失败，返回空字符串
            print(f"⚠️ 拼音转换失败: {pinyin_str} -> {e}")
            return ""
    
    def convert_with_candidates(self, pinyin_str: str, num: int = 5) -> List[str]:
        """
        拼音转汉字，返回多个候选词
        
        Args:
            pinyin_str: 拼音字符串
            num: 返回的候选词数量
            
        Returns:
            汉字候选词列表
        """
        if not pinyin_str:
            return []
        
        pinyin_str = pinyin_str.lower().strip()
        
        if not pinyin_str:
            return []
        
        try:
            # 使用自定义分割函数
            pinyin_list = split_pinyin(pinyin_str)
            
            if not pinyin_list:
                return []
            
            result = dag(self.dag_params, pinyin_list, path_num=num)
            
            # 处理每个结果
            candidates = []
            for item in result:
                path = item.path
                if isinstance(path, list):
                    candidates.append(''.join(path) if path else "")
                elif isinstance(path, str):
                    cleaned = path.strip()
                    if cleaned.startswith('[') and cleaned.endswith(']'):
                        cleaned = cleaned[1:-1].strip("'\"")
                    candidates.append(cleaned)
                else:
                    candidates.append(str(path))
            
            return candidates
            
        except Exception as e:
            print(f"⚠️ 拼音转换失败: {pinyin_str} -> {e}")
            return []
