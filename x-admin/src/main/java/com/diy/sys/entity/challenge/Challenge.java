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
 * 挑战记录实体
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Data
@TableName("x_challenge")
@AllArgsConstructor
@NoArgsConstructor
public class Challenge implements Serializable {
    private static final long serialVersionUID = 1L;
    
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;
    
    private String challengeId; // 挑战ID（UUID）
    
    private Integer userId; // 用户ID
    
    private String mode; // 挑战模式：random/questionSet
    
    private Integer questionSetId; // 题库ID（题库模式时使用）
    
    private Integer timeLimit; // 时间限制（秒）
    
    private Integer timeUsed; // 实际使用时间（秒）
    
    private Integer score; // 得分
    
    private Integer completedCount; // 完成题目数
    
    private Integer totalCount; // 总题目数
    
    private Integer status; // 状态：0-进行中，1-已完成，2-已放弃
    
    private LocalDateTime createTime; // 创建时间
    
    private LocalDateTime finishTime; // 完成时间
}
