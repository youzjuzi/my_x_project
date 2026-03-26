from itertools import product
from typing import List

try:
    from Pinyin2Hanzi import DefaultDagParams, dag
except ImportError:  # pragma: no cover - dependency may be installed later
    DefaultDagParams = None
    dag = None


VALID_PINYIN_SET = {
    "a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "er", "o", "ou",
    "ba", "bai", "ban", "bang", "bao", "bei", "ben", "beng", "bi", "bian", "biao", "bie", "bin", "bing", "bo", "bu",
    "pa", "pai", "pan", "pang", "pao", "pei", "pen", "peng", "pi", "pian", "piao", "pie", "pin", "ping", "po", "pou", "pu",
    "ma", "mai", "man", "mang", "mao", "me", "mei", "men", "meng", "mi", "mian", "miao", "mie", "min", "ming", "miu", "mo", "mou", "mu",
    "fa", "fan", "fang", "fei", "fen", "feng", "fo", "fou", "fu",
    "da", "dai", "dan", "dang", "dao", "de", "dei", "den", "deng", "di", "dia", "dian", "diao", "die", "ding", "diu", "dong", "dou", "du", "duan", "dui", "dun", "duo",
    "ta", "tai", "tan", "tang", "tao", "te", "tei", "teng", "ti", "tian", "tiao", "tie", "ting", "tong", "tou", "tu", "tuan", "tui", "tun", "tuo",
    "na", "nai", "nan", "nang", "nao", "ne", "nei", "nen", "neng", "ni", "nian", "niang", "niao", "nie", "nin", "ning", "niu", "nong", "nou", "nu", "nuan", "nuo", "nv", "nve",
    "la", "lai", "lan", "lang", "lao", "le", "lei", "leng", "li", "lia", "lian", "liang", "liao", "lie", "lin", "ling", "liu", "lo", "long", "lou", "lu", "luan", "lun", "luo", "lv", "lve",
    "ga", "gai", "gan", "gang", "gao", "ge", "gei", "gen", "geng", "gong", "gou", "gu", "gua", "guai", "guan", "guang", "gui", "gun", "guo",
    "ka", "kai", "kan", "kang", "kao", "ke", "kei", "ken", "keng", "kong", "kou", "ku", "kua", "kuai", "kuan", "kuang", "kui", "kun", "kuo",
    "ha", "hai", "han", "hang", "hao", "he", "hei", "hen", "heng", "hong", "hou", "hu", "hua", "huai", "huan", "huang", "hui", "hun", "huo",
    "ji", "jia", "jian", "jiang", "jiao", "jie", "jin", "jing", "jiong", "jiu", "ju", "juan", "jue", "jun",
    "qi", "qia", "qian", "qiang", "qiao", "qie", "qin", "qing", "qiong", "qiu", "qu", "quan", "que", "qun",
    "xi", "xia", "xian", "xiang", "xiao", "xie", "xin", "xing", "xiong", "xiu", "xu", "xuan", "xue", "xun",
    "za", "zai", "zan", "zang", "zao", "ze", "zei", "zen", "zeng", "zha", "zhai", "zhan", "zhang", "zhao", "zhe", "zhei", "zhen", "zheng", "zhi", "zhong", "zhou", "zhu", "zhua", "zhuai", "zhuan", "zhuang", "zhui", "zhun", "zhuo", "zi", "zong", "zou", "zu", "zuan", "zui", "zun", "zuo",
    "ca", "cai", "can", "cang", "cao", "ce", "cei", "cen", "ceng", "cha", "chai", "chan", "chang", "chao", "che", "chen", "cheng", "chi", "chong", "chou", "chu", "chua", "chuai", "chuan", "chuang", "chui", "chun", "chuo", "ci", "cong", "cou", "cu", "cuan", "cui", "cun", "cuo",
    "sa", "sai", "san", "sang", "sao", "se", "sei", "sen", "seng", "sha", "shai", "shan", "shang", "shao", "she", "shei", "shen", "sheng", "shi", "shou", "shu", "shua", "shuai", "shuan", "shuang", "shui", "shun", "shuo", "si", "song", "sou", "su", "suan", "sui", "sun", "suo",
    "ran", "rang", "rao", "re", "ren", "reng", "ri", "rong", "rou", "ru", "rua", "ruan", "rui", "run", "ruo",
    "ya", "yan", "yang", "yao", "ye", "yi", "yin", "ying", "yo", "yong", "you", "yu", "yuan", "yue", "yun",
    "wa", "wai", "wan", "wang", "wei", "wen", "weng", "wo", "wu",
}

# 声母集合（用于缩写匹配）
INITIALS = {
    "b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h",
    "j", "q", "x", "z", "c", "s", "r", "y", "w",
    "zh", "ch", "sh",
}

# 按声母分组的拼音查找表：initial -> [该声母的所有完整拼音]
_INITIAL_TO_FINALS: dict = {}


def _build_initial_map() -> None:
    """构建声母 -> 拼音列表 的映射表（启动时执行一次）。"""
    if _INITIAL_TO_FINALS:
        return
    # 按长度降序排列声母，确保先匹配 zh/ch/sh
    sorted_initials = sorted(INITIALS, key=len, reverse=True)
    for py in VALID_PINYIN_SET:
        for ini in sorted_initials:
            if py.startswith(ini):
                _INITIAL_TO_FINALS.setdefault(ini, []).append(py)
                break
        else:
            # 零声母韵母（a, o, e, ai, ...）自身就是 "声母"
            _INITIAL_TO_FINALS.setdefault(py, []).append(py)


_build_initial_map()


# ============================================================================
# 精确拼音分割（原有逻辑，保留不动）
# ============================================================================

def split_pinyin(pinyin_str: str) -> List[str]:
    result = []
    index = 0
    source = (pinyin_str or "").lower()

    while index < len(source):
        matched = False
        for length in range(min(6, len(source) - index), 0, -1):
            segment = source[index:index + length]
            if segment in VALID_PINYIN_SET:
                result.append(segment)
                index += length
                matched = True
                break
        if not matched:
            index += 1

    return result


# ============================================================================
# 模糊拼音分割（新增：支持声母缩写）
# ============================================================================

def _split_fuzzy(pinyin_str: str) -> List[List[str]]:
    """将输入拆分成一组"槽位"，每个槽位是该位置所有可能的拼音列表。

    算法：贪心优先匹配完整拼音，无法匹配时尝试声母展开。

    示例:
        "nh"   -> [["na","nai",...], ["ha","hai",...]]        (纯声母)
        "nihao" -> [["ni"], ["hao"]]                          (完整拼音)
        "nih"  -> [["ni"], ["ha","hai",...]]                   (混合)
    """
    slots: List[List[str]] = []
    index = 0
    source = (pinyin_str or "").lower()

    while index < len(source):
        # 1) 先尝试精确匹配完整拼音（贪心：最长优先）
        matched = False
        for length in range(min(6, len(source) - index), 0, -1):
            segment = source[index:index + length]
            if segment in VALID_PINYIN_SET:
                slots.append([segment])
                index += length
                matched = True
                break

        if matched:
            continue

        # 2) 尝试匹配声母（zh/ch/sh 优先于单字母）
        initial_matched = False
        for ini_len in (2, 1):
            if index + ini_len > len(source):
                continue
            candidate = source[index:index + ini_len]
            if candidate in INITIALS:
                expansions = _INITIAL_TO_FINALS.get(candidate, [])
                if expansions:
                    slots.append(list(expansions))
                    index += ini_len
                    initial_matched = True
                    break

        if initial_matched:
            continue

        # 3) 单个零声母韵母字母（a, e, o 等）
        ch = source[index]
        if ch in _INITIAL_TO_FINALS:
            slots.append(list(_INITIAL_TO_FINALS[ch]))
            index += 1
        else:
            # 无法识别的字符，跳过
            index += 1

    return slots


# ============================================================================
# 工具函数
# ============================================================================

def _normalize_path(path) -> str:
    if isinstance(path, list):
        return "".join(path) if path else ""
    if isinstance(path, str):
        cleaned = path.strip()
        if cleaned.startswith("[") and cleaned.endswith("]"):
            cleaned = cleaned[1:-1].strip("'\"")
        return cleaned
    return str(path)


# ============================================================================
# 数字转中文
# ============================================================================

_DIGIT_LOWER = {"0": "零", "1": "一", "2": "二", "3": "三", "4": "四",
                "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}
_DIGIT_UPPER = {"0": "零", "1": "壹", "2": "贰", "3": "叁", "4": "肆",
                "5": "伍", "6": "陆", "7": "柒", "8": "捌", "9": "玖"}


def digits_to_candidates(digit_str: str) -> List[str]:
    """将纯数字字符串转为候选列表: [原数字, 中文小写, 中文大写]。"""
    if not digit_str or not all(c.isdigit() for c in digit_str):
        return []
    lower = "".join(_DIGIT_LOWER.get(c, c) for c in digit_str)
    upper = "".join(_DIGIT_UPPER.get(c, c) for c in digit_str)
    candidates = [digit_str]
    if lower != digit_str:
        candidates.append(lower)
    if upper != lower:
        candidates.append(upper)
    return candidates


# ============================================================================
# PinyinConverter（改造：支持精确 + 模糊两种模式）
# ============================================================================

# 模糊匹配时，最多允许展开多少种组合（防止爆炸）
_MAX_FUZZY_COMBOS = 200


class PinyinConverter:
    def __init__(self) -> None:
        self.available = DefaultDagParams is not None and dag is not None
        self.dag_params = DefaultDagParams() if self.available else None

    def convert_with_candidates(self, pinyin_str: str, num: int = 5) -> List[str]:
        """精确 + 模糊拼音转汉字，返回去重候选词列表。

        优先级：
        1. 完整拼音精确匹配的结果排在前面
        2. 模糊展开的结果补充在后面
        """
        if not self.available:
            return []

        source = (pinyin_str or "").lower().strip()
        if not source:
            return []

        seen: set = set()
        candidates: List[str] = []

        # --- 阶段 1: 精确拼音匹配 ---
        exact_list = split_pinyin(source)
        if exact_list:
            try:
                result = dag(self.dag_params, exact_list, path_num=num)
                for item in result:
                    text = _normalize_path(item.path)
                    if text and text not in seen:
                        seen.add(text)
                        candidates.append(text)
            except Exception:
                pass

        # --- 阶段 2: 模糊拼音匹配 ---
        slots = _split_fuzzy(source)
        if slots and self._has_expansion(slots):
            fuzzy_candidates = self._dag_fuzzy(slots, num=max(num, 8))
            for text in fuzzy_candidates:
                if text not in seen:
                    seen.add(text)
                    candidates.append(text)

        return candidates[:num]

    def _has_expansion(self, slots: List[List[str]]) -> bool:
        """判断 slots 中是否有任何一个槽位包含多个选项（即存在模糊展开）。"""
        return any(len(s) > 1 for s in slots)

    def _dag_fuzzy(self, slots: List[List[str]], num: int = 8) -> List[str]:
        """对模糊槽位进行笛卡尔积展开，每种组合跑 DAG，汇总后按得分排序取 top-k。"""
        if not self.available or not slots:
            return []

        # 计算总组合数，超限时截断每个槽位的展开数量
        total = 1
        for s in slots:
            total *= len(s)
            if total > _MAX_FUZZY_COMBOS:
                break

        if total > _MAX_FUZZY_COMBOS:
            # 截断：每个槽位只保留常用拼音（按字母序前 N 个）
            max_per_slot = max(2, int(_MAX_FUZZY_COMBOS ** (1.0 / len(slots))))
            truncated = [sorted(s)[:max_per_slot] for s in slots]
        else:
            truncated = slots

        scored: List[tuple] = []  # [(score, text), ...]

        for combo in product(*truncated):
            pinyin_list = list(combo)
            try:
                result = dag(self.dag_params, pinyin_list, path_num=2)
                for item in result:
                    text = _normalize_path(item.path)
                    score = getattr(item, "score", 0.0) or 0.0
                    if text:
                        scored.append((score, text))
            except Exception:
                continue

        # 去重并按得分降序排列
        scored.sort(key=lambda x: x[0], reverse=True)
        seen: set = set()
        out: List[str] = []
        for _score, text in scored:
            if text not in seen:
                seen.add(text)
                out.append(text)
            if len(out) >= num:
                break
        return out
