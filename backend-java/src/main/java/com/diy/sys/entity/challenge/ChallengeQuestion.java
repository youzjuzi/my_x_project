package com.diy.sys.entity.challenge;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * <p>
 * 挑战题目关联实体
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Data
@TableName("x_challenge_question")
@AllArgsConstructor
@NoArgsConstructor
public class ChallengeQuestion implements Serializable {
    private static final long serialVersionUID = 1L;
    
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;
    
    private String challengeId; // 挑战ID
    
    private Integer questionId; // 题目ID
    
    private Integer questionOrder; // 题目顺序（从0开始）
    
    private Integer completed; // 是否完成：0-未完成，1-已完成
    
    private Integer timeSpent; // 花费时间（秒）
    
    private Integer score; // 该题得分
    
    private LocalDateTime createTime; // 创建时间
}
