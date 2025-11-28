package com.diy.common.utils;

import net.sourceforge.pinyin4j.PinyinHelper;
import net.sourceforge.pinyin4j.format.HanyuPinyinCaseType;
import net.sourceforge.pinyin4j.format.HanyuPinyinOutputFormat;
import net.sourceforge.pinyin4j.format.HanyuPinyinToneType;
import net.sourceforge.pinyin4j.format.exception.BadHanyuPinyinOutputFormatCombination;
import org.springframework.stereotype.Component;

/**
 * 拼音工具类
 * 用于将中文转换为拼音
 *
 * @author youzi
 */
@Component
public class PinyinUtil {

    /**
     * 将中文转换为不带音调的大写拼音
     * 例如："你好" -> "NIHAO"
     *
     * @param chinese 中文字符串
     * @return 大写拼音字符串（无空格）
     */
    public static String toPinyin(String chinese) {
        if (chinese == null || chinese.trim().isEmpty()) {
            return "";
        }

        HanyuPinyinOutputFormat format = new HanyuPinyinOutputFormat();
        format.setCaseType(HanyuPinyinCaseType.UPPERCASE); // 大写
        format.setToneType(HanyuPinyinToneType.WITHOUT_TONE); // 不带音调

        StringBuilder pinyin = new StringBuilder();
        char[] chars = chinese.toCharArray();

        for (char c : chars) {
            if (Character.toString(c).matches("[\\u4E00-\\u9FA5]+")) {
                // 是中文字符
                try {
                    String[] pinyinArray = PinyinHelper.toHanyuPinyinStringArray(c, format);
                    if (pinyinArray != null && pinyinArray.length > 0) {
                        pinyin.append(pinyinArray[0]);
                    }
                } catch (BadHanyuPinyinOutputFormatCombination e) {
                    // 转换失败，保留原字符
                    pinyin.append(c);
                }
            } else {
                // 非中文字符（字母、数字等）直接保留
                pinyin.append(c);
            }
        }

        return pinyin.toString();
    }

    /**
     * 将中文转换为带空格分隔的拼音
     * 例如："你好" -> "NI HAO"
     *
     * @param chinese 中文字符串
     * @return 大写拼音字符串（带空格）
     */
    public static String toPinyinWithSpace(String chinese) {
        if (chinese == null || chinese.trim().isEmpty()) {
            return "";
        }

        HanyuPinyinOutputFormat format = new HanyuPinyinOutputFormat();
        format.setCaseType(HanyuPinyinCaseType.UPPERCASE);
        format.setToneType(HanyuPinyinToneType.WITHOUT_TONE);

        StringBuilder pinyin = new StringBuilder();
        char[] chars = chinese.toCharArray();

        for (int i = 0; i < chars.length; i++) {
            char c = chars[i];
            if (Character.toString(c).matches("[\\u4E00-\\u9FA5]+")) {
                try {
                    String[] pinyinArray = PinyinHelper.toHanyuPinyinStringArray(c, format);
                    if (pinyinArray != null && pinyinArray.length > 0) {
                        if (i > 0 && pinyin.length() > 0) {
                            pinyin.append(" ");
                        }
                        pinyin.append(pinyinArray[0]);
                    }
                } catch (BadHanyuPinyinOutputFormatCombination e) {
                    if (i > 0 && pinyin.length() > 0) {
                        pinyin.append(" ");
                    }
                    pinyin.append(c);
                }
            } else {
                if (i > 0 && pinyin.length() > 0 && !Character.isWhitespace(c)) {
                    pinyin.append(" ");
                }
                pinyin.append(c);
            }
        }

        return pinyin.toString();
    }
}

