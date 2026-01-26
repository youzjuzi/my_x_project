package com.diy.sys.entity.UserAndRole;

import lombok.Data;
import java.util.Map;

/**
 * 登录请求DTO
 * 
 * @author youzi
 * @since 2024
 */
@Data
public class LoginRequest {
    private String username;
    private String password;
    private String captchaId;
    private Map<String, Object> captchaData;
}

