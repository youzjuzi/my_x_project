package com.diy.sys.service.captcha.impl;

import com.diy.sys.service.captcha.ICaptchaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * 验证码服务实现类
 * 简单滑块验证码 (Redis Token 模式)
 * 
 * @author youzi
 * @since 2024
 */
@Service
public class CaptchaServiceImpl implements ICaptchaService {

    @Autowired
    private StringRedisTemplate redisTemplate;

    private static final String CAPTCHA_KEY_PREFIX = "captcha:token:";
    private static final long CAPTCHA_TTL = 120; // 2分钟有效期

    @Override
    public Map<String, Object> generate() {
        try {
            // 生成唯一ID
            String id = UUID.randomUUID().toString();
            String key = CAPTCHA_KEY_PREFIX + id;

            System.out.println("CaptchaService: 生成验证码 ID=" + id + ", Key=" + key);

            // 存入 Redis，Value 为 "1" (代表有效)
            redisTemplate.opsForValue().set(key, "1", CAPTCHA_TTL, TimeUnit.SECONDS);

            Map<String, Object> result = new HashMap<>();
            result.put("id", id);
            // 前端不再需要图片数据，但为了兼容旧接口结构，可以返回空或特定标志
            result.put("type", "slider");

            return result;
        } catch (Exception e) {
            System.err.println("CaptchaService: 生成验证码异常: " + e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("生成验证码失败: " + e.getMessage());
        }
    }

    @Override
    public boolean verify(String id, Map<String, Object> data) {
        System.out.println("CaptchaService: 开始验证 ID=" + id);

        if (id == null) {
            System.out.println("CaptchaService: ID 为空，验证失败");
            return false;
        }

        String key = CAPTCHA_KEY_PREFIX + id;

        // 检查 Key 是否存在
        Boolean exists = redisTemplate.hasKey(key);
        System.out.println("CaptchaService: 检查 Redis Key=" + key + ", Exists=" + exists);

        if (Boolean.TRUE.equals(exists)) {
            // 验证成功后立即删除，防止重放
            redisTemplate.delete(key);
            System.out.println("CaptchaService: 验证成功，删除 Key");
            return true;
        }

        System.out.println("CaptchaService: 验证失败，Key 不存在或已过期");
        return false;
    }
}
