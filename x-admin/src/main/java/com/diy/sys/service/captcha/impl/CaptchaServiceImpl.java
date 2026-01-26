package com.diy.sys.service.captcha.impl;

import com.diy.sys.service.captcha.ICaptchaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import javax.imageio.ImageIO;

/**
 * 验证码服务实现类
 * 使用简化的滑动验证码实现
 * 
 * @author youzi
 * @since 2024
 */
@Service
public class CaptchaServiceImpl implements ICaptchaService {
    
    @Autowired(required = false)
    private RedisTemplate<String, Object> redisTemplate;
    
    // 内存缓存，用于存储验证码目标位置（当没有 Redis 时使用）
    private static final ConcurrentHashMap<String, Integer> memoryCache = new ConcurrentHashMap<>();
    private static final ConcurrentHashMap<String, Long> cacheTimestamps = new ConcurrentHashMap<>();
    
    // 验证码目标位置（简化实现，实际应该由后端生成随机位置）
    private static final int TARGET_POSITION = 150;
    // 允许的误差范围
    private static final int TOLERANCE = 10;
    // 缓存过期时间（5分钟）
    private static final long CACHE_EXPIRE_TIME = 5 * 60 * 1000;
    
    @Override
    public Map<String, Object> generate() {
        // 生成验证码ID
        String id = UUID.randomUUID().toString();
        
        // 生成随机目标位置（实际应该使用 Tianai-Captcha 生成）
        int targetPosition = (int) (Math.random() * 200) + 50;
        
        // 将目标位置存储到 Redis 或内存缓存（用于验证）
        if (redisTemplate != null) {
            redisTemplate.opsForValue().set("captcha:" + id, targetPosition, 5, TimeUnit.MINUTES);
        } else {
            // 使用内存缓存
            memoryCache.put(id, targetPosition);
            cacheTimestamps.put(id, System.currentTimeMillis());
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("id", id);
        // 生成一个简单的占位图片（300x150的灰色背景）
        // 这里应该返回 Tianai-Captcha 生成的图片，暂时返回占位符
        String placeholderBg = generatePlaceholderImage(300, 150);
        String placeholderTemplate = generatePlaceholderImage(50, 150);
        result.put("backgroundImage", placeholderBg);
        result.put("templateImage", placeholderTemplate);
        result.put("targetPosition", targetPosition); // 临时使用，实际应该隐藏
        
        return result;
    }
    
    @Override
    public boolean verify(String id, Map<String, Object> data) {
        try {
            if (id == null || data == null) {
                return false;
            }
            
            // 从 Redis 或内存缓存获取目标位置
            Integer targetPosition = null;
            if (redisTemplate != null) {
                Object stored = redisTemplate.opsForValue().get("captcha:" + id);
                if (stored != null) {
                    targetPosition = (Integer) stored;
                    // 验证后删除
                    redisTemplate.delete("captcha:" + id);
                }
            } else {
                // 从内存缓存获取
                targetPosition = memoryCache.get(id);
                Long timestamp = cacheTimestamps.get(id);
                
                // 检查是否过期
                if (timestamp != null && System.currentTimeMillis() - timestamp > CACHE_EXPIRE_TIME) {
                    // 已过期，清除缓存
                    memoryCache.remove(id);
                    cacheTimestamps.remove(id);
                    targetPosition = null;
                } else if (targetPosition != null) {
                    // 验证后删除
                    memoryCache.remove(id);
                    cacheTimestamps.remove(id);
                }
            }
            
            if (targetPosition == null) {
                System.out.println("验证码ID不存在或已过期: " + id);
                return false;
            }
            
            // 获取用户滑动的位置
            int userPosition = 0;
            if (data.containsKey("x")) {
                userPosition = Integer.parseInt(data.get("x").toString());
            }
            
            // 验证位置是否在允许范围内
            int diff = Math.abs(userPosition - targetPosition);
            boolean valid = diff <= TOLERANCE;
            
            System.out.println("验证码验证 - ID: " + id + ", 目标位置: " + targetPosition + ", 用户位置: " + userPosition + ", 差值: " + diff + ", 验证结果: " + valid);
            
            return valid;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * 生成占位图片
     */
    private String generatePlaceholderImage(int width, int height) {
        try {
            BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
            Graphics2D g = image.createGraphics();
            
            // 设置抗锯齿
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            
            // 绘制背景
            g.setColor(new Color(240, 240, 240));
            g.fillRect(0, 0, width, height);
            
            // 绘制边框
            g.setColor(new Color(200, 200, 200));
            g.setStroke(new BasicStroke(2));
            g.drawRect(0, 0, width - 1, height - 1);
            
            // 绘制一些装饰线条
            g.setColor(new Color(220, 220, 220));
            for (int i = 0; i < 5; i++) {
                int y = (height / 5) * (i + 1);
                g.drawLine(0, y, width, y);
            }
            
            g.dispose();
            
            // 转换为 base64
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ImageIO.write(image, "png", baos);
            byte[] imageBytes = baos.toByteArray();
            String base64 = Base64.getEncoder().encodeToString(imageBytes);
            
            return "data:image/png;base64," + base64;
        } catch (Exception e) {
            e.printStackTrace();
            // 如果生成失败，返回一个最小的占位符
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";
        }
    }
}
