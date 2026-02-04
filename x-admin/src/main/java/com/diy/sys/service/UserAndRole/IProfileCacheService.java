package com.diy.sys.service.UserAndRole;

/**
 * 个人资料缓存服务接口
 * 
 * 封装 Redis 操作，管理用户个人资料信息缓存
 * 
 * @author youzi
 * @since 2024
 */
public interface IProfileCacheService {

    /**
     * 存储 Profile 信息到 Redis
     * 
     * @param userId      用户ID
     * @param profileInfo Profile 信息（Map 格式）
     */
    void saveProfileInfo(Integer userId, Object profileInfo);

    /**
     * 从 Redis 获取 Profile 信息
     * 
     * @param userId 用户ID
     * @return Profile 信息，不存在则返回 null
     */
    Object getProfileInfo(Integer userId);

    /**
     * 删除 Profile 信息缓存
     * 
     * @param userId 用户ID
     */
    void removeProfileInfo(Integer userId);
}
