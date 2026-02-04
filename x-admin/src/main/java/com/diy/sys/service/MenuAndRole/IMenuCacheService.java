package com.diy.sys.service.MenuAndRole;

import com.diy.sys.entity.MenuAndRole.Menu;

import java.util.List;

/**
 * 菜单缓存服务接口
 * 
 * 封装 Redis 操作，管理用户菜单树缓存
 * 
 * Key 格式: user:menu_tree:{userId}
 * TTL: 7 天
 * 
 * @author youzi
 * @since 2024
 */
public interface IMenuCacheService {

    /**
     * 存储用户菜单树到 Redis
     * 
     * @param userId   用户ID
     * @param menuList 菜单树列表
     */
    void saveMenuTree(Integer userId, List<Menu> menuList);

    /**
     * 从 Redis 获取用户菜单树
     * 
     * @param userId 用户ID
     * @return 菜单树列表，不存在则返回 null
     */
    List<Menu> getMenuTree(Integer userId);

    /**
     * 删除用户菜单树缓存
     * 
     * @param userId 用户ID
     */
    void removeMenuTree(Integer userId);

    /**
     * 删除所有用户的菜单树缓存（当管理员修改菜单时调用）
     */
    void removeAllMenuTreeCache();
}
