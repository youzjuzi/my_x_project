package com.diy.sys.service.UserAndRole.impl;

import com.diy.sys.service.UserAndRole.IAuthCacheService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

/**
 * 认证缓存服务实现类
 * 
 * 封装 Redis 操作，管理用户登录 Token 和用户权限信息缓存：
 * - 存储 Token（登录时）
 * - 验证 Token（请求验证时）
 * - 刷新 Token TTL（自动续签）
 * - 删除 Token（登出时）
 * - 用户权限信息缓存
 * 
 * Key 格式:
 * - Token: login:token:{userId}
 * - UserInfo: auth:info:{userId}
 * 
 * TTL: 30 分钟
 * 
 * @author youzi
 * @since 2024
 */
@Slf4j
@Service
public class AuthCacheServiceImpl implements IAuthCacheService {

    private static final String TOKEN_PREFIX = "login:token:";
    private static final String USER_INFO_PREFIX = "auth:info:";
    private static final long TOKEN_EXPIRE_TIME = 30; // 30 分钟
    private static final TimeUnit TOKEN_EXPIRE_UNIT = TimeUnit.MINUTES;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    // ==================== Token 管理 ====================

    private String getTokenKey(Integer userId) {
        return TOKEN_PREFIX + userId;
    }

    @Override
    public void saveToken(Integer userId, String token) {
        String key = getTokenKey(userId);
        redisTemplate.opsForValue().set(key, token, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
        log.debug("Token 已存储 - userId: {}, TTL: {}分钟", userId, TOKEN_EXPIRE_TIME);
    }

    @Override
    public String getToken(Integer userId) {
        String key = getTokenKey(userId);
        Object token = redisTemplate.opsForValue().get(key);
        return token != null ? token.toString() : null;
    }

    @Override
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

    @Override
    public void refreshToken(Integer userId) {
        String key = getTokenKey(userId);
        Boolean success = redisTemplate.expire(key, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
        if (Boolean.TRUE.equals(success)) {
            log.debug("Token 已续签 - userId: {}, TTL: {}分钟", userId, TOKEN_EXPIRE_TIME);
        }
    }

    @Override
    public void removeToken(Integer userId) {
        String key = getTokenKey(userId);
        Boolean deleted = redisTemplate.delete(key);
        if (Boolean.TRUE.equals(deleted)) {
            log.debug("Token 已删除 - userId: {}", userId);
        }
    }

    @Override
    public boolean hasToken(Integer userId) {
        String key = getTokenKey(userId);
        return Boolean.TRUE.equals(redisTemplate.hasKey(key));
    }

    // ==================== 用户信息缓存 ====================

    private String getUserInfoKey(Integer userId) {
        return USER_INFO_PREFIX + userId;
    }

    @Override
    public void saveUserInfo(Integer userId, Object userInfo) {
        String key = getUserInfoKey(userId);
        redisTemplate.opsForValue().set(key, userInfo, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
        log.debug("用户信息已缓存 - userId: {}, TTL: {}分钟", userId, TOKEN_EXPIRE_TIME);
    }

    @Override
    public Object getUserInfo(Integer userId) {
        String key = getUserInfoKey(userId);
        return redisTemplate.opsForValue().get(key);
    }

    @Override
    public void removeUserInfo(Integer userId) {
        String key = getUserInfoKey(userId);
        Boolean deleted = redisTemplate.delete(key);
        if (Boolean.TRUE.equals(deleted)) {
            log.debug("用户信息缓存已删除 - userId: {}", userId);
        }
    }

    @Override
    public void refreshUserInfo(Integer userId) {
        String key = getUserInfoKey(userId);
        redisTemplate.expire(key, TOKEN_EXPIRE_TIME, TOKEN_EXPIRE_UNIT);
    }
}
