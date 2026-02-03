package com.diy.sys.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

/**
 * Token 服务类
 * 
 * 封装 Redis 操作，管理用户登录 Token：
 * - 存储 Token（登录时）
 * - 验证 Token（请求验证时）
 * - 刷新 Token TTL（自动续签）
 * - 删除 Token（登出时）
 * 
 * Key 格式: login:token:{userId}
 * TTL: 30 分钟
 * 
 * @author youzi
 * @since 2024
 */
@Slf4j
@Service
public class TokenService {

    private static final String TOKEN_PREFIX = "login:token:";
    private static final long TOKEN_EXPIRE_TIME = 30; // 30 分钟
    private static final TimeUnit TOKEN_EXPIRE_UNIT = TimeUnit.MINUTES;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    /**
     * 生成 Redis Key
     */
    private String getTokenKey(Integer userId) {
        return TOKEN_PREFIX + userId;
    }

    /**
     * 存储 Token 到 Redis
     * 
     * @param userId 用户ID
     * @param token  JWT Token
     */
    public void saveToken(Integer userId, String token) {
        String key = getTokenKey(userId);
        redisTemplate.opsForValue().set(key, token, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
        log.debug("Token 已存储 - userId: {}, TTL: {}分钟", userId, TOKEN_EXPIRE_TIME);
    }

    /**
     * 从 Redis 获取 Token
     * 
     * @param userId 用户ID
     * @return Token 字符串，不存在则返回 null
     */
    public String getToken(Integer userId) {
        String key = getTokenKey(userId);
        Object token = redisTemplate.opsForValue().get(key);
        return token != null ? token.toString() : null;
    }

    /**
     * 验证 Token 是否有效
     * 
     * @param userId 用户ID
     * @param token  前端传入的 Token
     * @return true 如果 Token 存在且匹配
     */
    public boolean validateToken(Integer userId, String token) {
        String storedToken = getToken(userId);
        if (storedToken == null) {
            log.debug("Token 验证失败 - userId: {}, 原因: Redis 中不存在", userId);
            return false;
        }
        boolean valid = storedToken.equals(token);
        if (!valid) {
            log.debug("Token 验证失败 - userId: {}, 原因: Token 不匹配", userId);
        }
        return valid;
    }

    /**
     * 刷新 Token TTL（自动续签）
     * 
     * @param userId 用户ID
     */
    public void refreshToken(Integer userId) {
        String key = getTokenKey(userId);
        Boolean success = redisTemplate.expire(key, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
        if (Boolean.TRUE.equals(success)) {
            log.debug("Token 已续签 - userId: {}, TTL: {}分钟", userId, TOKEN_EXPIRE_TIME);
        }
    }

    /**
     * 删除 Token（登出时调用）
     * 
     * @param userId 用户ID
     */
    public void removeToken(Integer userId) {
        String key = getTokenKey(userId);
        Boolean deleted = redisTemplate.delete(key);
        if (Boolean.TRUE.equals(deleted)) {
            log.debug("Token 已删除 - userId: {}", userId);
        }
    }

    /**
     * 检查 Token 是否存在
     * 
     * @param userId 用户ID
     * @return true 如果 Token 存在
     */
    public boolean hasToken(Integer userId) {
        String key = getTokenKey(userId);
        return Boolean.TRUE.equals(redisTemplate.hasKey(key));
    }

    // ==================== 用户信息缓存 ====================

    private static final String USER_INFO_PREFIX = "auth:info:";

    /**
     * 生成用户信息 Redis Key
     */
    private String getUserInfoKey(Integer userId) {
        return USER_INFO_PREFIX + userId;
    }

    /**
     * 存储用户信息到 Redis
     * 
     * @param userId   用户ID
     * @param userInfo 用户信息（Map 格式）
     */
    public void saveUserInfo(Integer userId, Object userInfo) {
        String key = getUserInfoKey(userId);
        redisTemplate.opsForValue().set(key, userInfo, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
        log.debug("用户信息已缓存 - userId: {}, TTL: {}分钟", userId, TOKEN_EXPIRE_TIME);
    }

    /**
     * 从 Redis 获取用户信息
     * 
     * @param userId 用户ID
     * @return 用户信息，不存在则返回 null
     */
    public Object getUserInfo(Integer userId) {
        String key = getUserInfoKey(userId);
        return redisTemplate.opsForValue().get(key);
    }

    /**
     * 删除用户信息缓存
     * 
     * @param userId 用户ID
     */
    public void removeUserInfo(Integer userId) {
        String key = getUserInfoKey(userId);
        Boolean deleted = redisTemplate.delete(key);
        if (Boolean.TRUE.equals(deleted)) {
            log.debug("用户信息缓存已删除 - userId: {}", userId);
        }
    }

    /**
     * 刷新用户信息缓存 TTL
     * 
     * @param userId 用户ID
     */
    public void refreshUserInfo(Integer userId) {
        String key = getUserInfoKey(userId);
        redisTemplate.expire(key, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
    }

    // ==================== Profile 信息缓存 ====================

    private static final String PROFILE_INFO_PREFIX = "profile:getinfo:";

    /**
     * 生成 Profile 信息 Redis Key
     */
    private String getProfileInfoKey(Integer userId) {
        return PROFILE_INFO_PREFIX + userId;
    }

    /**
     * 存储 Profile 信息到 Redis
     * 
     * @param userId      用户ID
     * @param profileInfo Profile 信息（Map 格式）
     */
    public void saveProfileInfo(Integer userId, Object profileInfo) {
        String key = getProfileInfoKey(userId);
        redisTemplate.opsForValue().set(key, profileInfo, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
        log.debug("Profile 信息已缓存 - userId: {}, TTL: {}分钟", userId, TOKEN_EXPIRE_TIME);
    }

    /**
     * 从 Redis 获取 Profile 信息
     * 
     * @param userId 用户ID
     * @return Profile 信息，不存在则返回 null
     */
    public Object getProfileInfo(Integer userId) {
        String key = getProfileInfoKey(userId);
        return redisTemplate.opsForValue().get(key);
    }

    /**
     * 删除 Profile 信息缓存
     * 
     * @param userId 用户ID
     */
    public void removeProfileInfo(Integer userId) {
        String key = getProfileInfoKey(userId);
        Boolean deleted = redisTemplate.delete(key);
        if (Boolean.TRUE.equals(deleted)) {
            log.debug("Profile 信息缓存已删除 - userId: {}", userId);
        }
    }
}
