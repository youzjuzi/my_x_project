package com.diy.sys.entity.Question;

import com.alibaba.fastjson2.annotation.JSONField;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * <p>
 * 题库-题目关联实体
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Data
@TableName("x_question_set")
@NoArgsConstructor
@AllArgsConstructor
public class QuestionSetQuestion implements Serializable {
    private static final long serialVersionUID = 1L;
    
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    @JSONField(name = "set_id")
    private Integer questionSetId; // 题库ID

    @JSONField(name = "question_id")
    private Integer questionId; // 题目ID
}

