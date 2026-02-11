package com.diy.common.exception;

import lombok.Getter;

/**
 * 自定义业务异常
 * 用于在 Service 层抛出可控的业务错误，由 GlobalExceptionHandler 统一处理
 */
@Getter
public class BusinessException extends RuntimeException {

    private final Integer code;

    public BusinessException(String message) {
        super(message);
        this.code = 20001; // 默认错误码
    }

    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }
}
