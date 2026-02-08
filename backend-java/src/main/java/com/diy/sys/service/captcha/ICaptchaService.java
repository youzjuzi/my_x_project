package com.diy.sys.service.captcha;

import java.util.Map;

/**
 * 验证码服务接口
 * 
 * @author youzi
 * @since 2024
 */
public interface ICaptchaService {
    
    /**
     * 生成验证码
     * @return 验证码数据，包含 id、backgroundImage、templateImage 等
     */
    Map<String, Object> generate();
    
    /**
     * 验证验证码
     * @param id 验证码ID
     * @param data 验证数据（包含滑动轨迹等）
     * @return 验证是否通过
     */
    boolean verify(String id, Map<String, Object> data);
}
