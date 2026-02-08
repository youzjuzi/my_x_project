package com.diy.sys.entity.challenge;

import lombok.Data;
import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 挑战记录（包含用户信息）DTO
 */
@Data
public class ChallengeWithUser implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private Integer id;
    private String challengeId;
    private Integer userId;
    private String username; // 用户名
    private String mode;
    private Integer questionSetId;
    private Integer timeLimit;
    private Integer timeUsed;
    private Integer score;
    private Integer completedCount;
    private Integer totalCount;
    private Integer status;
    private LocalDateTime createTime;
    private LocalDateTime finishTime;
}

