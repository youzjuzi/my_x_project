package com.diy.sys.service.UserAndRole.impl;

import com.diy.sys.service.UserAndRole.IProfileCacheService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

/**
 * 个人资料缓存服务实现类
 * 
 * 封装 Redis 操作，管理用户个人资料信息缓存
 * 
 * Key 格式: profile:getinfo:{userId}
 * TTL: 30 分钟
 * 
 * @author youzi
 * @since 2024
 */
@Slf4j
@Service
public class ProfileCacheServiceImpl implements IProfileCacheService {

    private static final String PROFILE_INFO_PREFIX = "profile:getinfo:";
    private static final long CACHE_EXPIRE_TIME = 30; // 30 分钟
    private static final TimeUnit CACHE_EXPIRE_UNIT = TimeUnit.MINUTES;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private String getProfileInfoKey(Integer userId) {
        return PROFILE_INFO_PREFIX + userId;
    }

    @Override
    public void saveProfileInfo(Integer userId, Object profileInfo) {
        String key = getProfileInfoKey(userId);
        redisTemplate.opsForValue().set(key, profileInfo, CACHE_EXPIRE_TIME, CACHE_EXPIRE_UNIT);
        log.debug("Profile 信息已缓存 - userId: {}, TTL: {}分钟", userId, CACHE_EXPIRE_TIME);
    }

    @Override
    public Object getProfileInfo(Integer userId) {
        String key = getProfileInfoKey(userId);
        return redisTemplate.opsForValue().get(key);
    }

    @Override
    public void removeProfileInfo(Integer userId) {
        String key = getProfileInfoKey(userId);
        Boolean deleted = redisTemplate.delete(key);
        if (Boolean.TRUE.equals(deleted)) {
            log.debug("Profile 信息缓存已删除 - userId: {}", userId);
        }
    }
}
