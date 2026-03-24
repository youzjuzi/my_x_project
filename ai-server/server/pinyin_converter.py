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


def _normalize_path(path) -> str:
    if isinstance(path, list):
        return "".join(path) if path else ""
    if isinstance(path, str):
        cleaned = path.strip()
        if cleaned.startswith("[") and cleaned.endswith("]"):
            cleaned = cleaned[1:-1].strip("'\"")
        return cleaned
    return str(path)


class PinyinConverter:
    def __init__(self) -> None:
        self.available = DefaultDagParams is not None and dag is not None
        self.dag_params = DefaultDagParams() if self.available else None

    def convert_with_candidates(self, pinyin_str: str, num: int = 5) -> List[str]:
        if not self.available:
            return []

        source = (pinyin_str or "").lower().strip()
        if not source:
            return []

        try:
            pinyin_list = split_pinyin(source)
            if not pinyin_list:
                return []

            result = dag(self.dag_params, pinyin_list, path_num=num)
            candidates = []
            seen = set()

            for item in result:
                text = _normalize_path(item.path)
                if not text or text in seen:
                    continue
                seen.add(text)
                candidates.append(text)

            return candidates
        except Exception:
            return []
