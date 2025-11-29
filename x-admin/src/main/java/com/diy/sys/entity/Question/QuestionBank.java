package com.diy.sys.entity.Question;


import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@TableName("x_question_bank")
@AllArgsConstructor
@NoArgsConstructor
public class QuestionBank {
    private static final long serialVersionUID = 1L;
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;
    private String content;
    private int type; // 1:单词 2:数字 3:词语
    private int difficulty; // 1:简单 2:中等 3:困难
    private String pinyin; // 如果是词语，则保存拼音
    @JsonProperty("img_url")
    private String imgUrl;
    @JsonProperty("level_group")
    private String levelGroup;
    private int status;

}
