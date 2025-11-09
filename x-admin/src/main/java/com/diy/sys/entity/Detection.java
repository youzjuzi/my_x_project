package com.diy.sys.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.time.LocalDateTime;


@TableName("x_detections")
@Data
public class Detection {
    @TableId(type = IdType.AUTO)
    @JsonProperty("session_id")
    private String sessionId;
    private String timestamp;
    @JsonProperty("class_name")
    private String className;
    private String source;
    private Double confidence;
    @JsonProperty("user_id")
    private String userId;
}
