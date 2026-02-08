package com.diy.sys.entity.UserAndRole;


import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.time.LocalDateTime;

@TableName("x_user_activity")
@Data
public class UserActivityTime {
    private Integer id;
    @JsonProperty("user_id")
    private Integer userId;
    @JsonProperty("activity_time")
    private LocalDateTime ActivityTime;
}
