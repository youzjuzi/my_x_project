package com.diy.sys.service.MenuAndRole.impl;

import com.diy.sys.entity.MenuAndRole.Menu;
import com.diy.sys.service.MenuAndRole.IMenuCacheService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Set;
import java.util.concurrent.TimeUnit;

/**
 * 菜单缓存服务实现类
 * 
 * 封装 Redis 操作，管理用户菜单树缓存
 * 
 * Key 格式: user:menu_tree:{userId}
 * TTL: 7 天
 * 
 * @author youzi
 * @since 2024
 */
@Slf4j
@Service
public class MenuCacheServiceImpl implements IMenuCacheService {

    private static final String MENU_TREE_PREFIX = "user:menu_tree:";
    private static final long CACHE_EXPIRE_TIME = 7; // 7 天
    private static final TimeUnit CACHE_EXPIRE_UNIT = TimeUnit.DAYS;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private String getMenuTreeKey(Integer userId) {
        return MENU_TREE_PREFIX + userId;
    }

    @Override
    public void saveMenuTree(Integer userId, List<Menu> menuList) {
        String key = getMenuTreeKey(userId);
        redisTemplate.opsForValue().set(key, menuList, CACHE_EXPIRE_TIME, CACHE_EXPIRE_UNIT);
        log.debug("菜单树已缓存 - userId: {}, TTL: {}天", userId, CACHE_EXPIRE_TIME);
    }

    @Override
    @SuppressWarnings("unchecked")
    public List<Menu> getMenuTree(Integer userId) {
        String key = getMenuTreeKey(userId);
        Object cached = redisTemplate.opsForValue().get(key);
        if (cached != null && cached instanceof List) {
            return (List<Menu>) cached;
        }
        return null;
    }

    @Override
    public void removeMenuTree(Integer userId) {
        String key = getMenuTreeKey(userId);
        Boolean deleted = redisTemplate.delete(key);
        if (Boolean.TRUE.equals(deleted)) {
            log.debug("菜单树缓存已删除 - userId: {}", userId);
        }
    }

    @Override
    public void removeAllMenuTreeCache() {
        // 使用 keys 命令匹配所有用户的菜单缓存
        Set<String> keys = redisTemplate.keys(MENU_TREE_PREFIX + "*");
        if (keys != null && !keys.isEmpty()) {
            redisTemplate.delete(keys);
            log.debug("已删除所有菜单树缓存 - 共 {} 个", keys.size());
        }
    }
}
