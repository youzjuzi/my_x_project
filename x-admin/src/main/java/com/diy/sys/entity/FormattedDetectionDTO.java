package com.diy.sys.entity;


import lombok.Data;

@Data
public class FormattedDetectionDTO {
    private String timestamp;
    private String source;
    private Double confidence;
    private String sessionId;
    private String className;
    private String userId;
}
