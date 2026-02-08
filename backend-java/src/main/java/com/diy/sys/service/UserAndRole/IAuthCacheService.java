package com.diy.sys.service.UserAndRole;

/**
 * 认证缓存服务接口
 * 
 * 封装 Redis 操作，管理用户登录 Token 和用户权限信息缓存
 * 
 * @author youzi
 * @since 2024
 */
public interface IAuthCacheService {

    // ==================== Token 管理 ====================

    /**
     * 存储 Token 到 Redis
     * 
     * @param userId 用户ID
     * @param token  JWT Token
     */
    void saveToken(Integer userId, String token);

    /**
     * 从 Redis 获取 Token
     * 
     * @param userId 用户ID
     * @return Token 字符串，不存在则返回 null
     */
    String getToken(Integer userId);

    /**
     * 验证 Token 是否有效
     * 
     * @param userId 用户ID
     * @param token  前端传入的 Token
     * @return true 如果 Token 存在且匹配
     */
    boolean validateToken(Integer userId, String token);

    /**
     * 刷新 Token TTL（自动续签）
     * 
     * @param userId 用户ID
     */
    void refreshToken(Integer userId);

    /**
     * 删除 Token（登出时调用）
     * 
     * @param userId 用户ID
     */
    void removeToken(Integer userId);

    /**
     * 检查 Token 是否存在
     * 
     * @param userId 用户ID
     * @return true 如果 Token 存在
     */
    boolean hasToken(Integer userId);

    // ==================== 用户信息缓存 ====================

    /**
     * 存储用户信息到 Redis
     * 
     * @param userId   用户ID
     * @param userInfo 用户信息（Map 格式）
     */
    void saveUserInfo(Integer userId, Object userInfo);

    /**
     * 从 Redis 获取用户信息
     * 
     * @param userId 用户ID
     * @return 用户信息，不存在则返回 null
     */
    Object getUserInfo(Integer userId);

    /**
     * 删除用户信息缓存
     * 
     * @param userId 用户ID
     */
    void removeUserInfo(Integer userId);

    /**
     * 刷新用户信息缓存 TTL
     * 
     * @param userId 用户ID
     */
    void refreshUserInfo(Integer userId);
}
