package com.diy.sys.service.UserAndRole.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.diy.common.utils.JwtUtil;
import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.entity.UserAndRole.UserActivityTime;
import com.diy.sys.mapper.UserAndRole.UserMapper;
import com.diy.sys.service.UserAndRole.IUserActivityTimeService;
import com.diy.sys.service.TokenService;
import com.diy.sys.service.UserAndRole.IUserProfileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class UserProfileServiceImpl extends ServiceImpl<UserMapper, User> implements IUserProfileService {
    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private IUserActivityTimeService userActivityTimeService;

    @Autowired
    private TokenService tokenService;

    /**
     * 根据token获取用户完整信息
     * 
     * @param token JWT token
     * @return 用户信息Map
     */
    @Override
    public Map<String, Object> getUserInfo(String token) {
        // 1. 解析token获取用户基本信息
        User loginUser = null;
        try {
            loginUser = jwtUtil.parseToken(token, User.class);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }

        if (loginUser == null || loginUser.getId() == null) {
            return null;
        }

        // 2. 从数据库获取完整的用户信息
        User dbUser = this.getById(loginUser.getId());
        if (dbUser == null) {
            return null;
        }

        // 3. 获取用户角色
        List<String> roleList = this.baseMapper.getRoleNameByUserId(dbUser.getId());

        // 4. 获取注册时间（首次活动时间）
        LocalDateTime createTime = getFirstActivityTime(dbUser.getId());

        // 5. 获取最后登录时间（最近一次活动时间）
        LocalDateTime lastLoginTime = getLastActivityTime(dbUser.getId());

        // 6. 构建返回数据
        Map<String, Object> data = new HashMap<>();
        data.put("id", dbUser.getId());
        data.put("name", dbUser.getUsername());
        data.put("avatar", dbUser.getAvatar() != null ? dbUser.getAvatar() : "");
        data.put("email", dbUser.getEmail() != null ? dbUser.getEmail() : "");
        data.put("phone", dbUser.getPhone() != null ? dbUser.getPhone() : "");
        data.put("roles", roleList);
        data.put("role", roleList != null && !roleList.isEmpty() ? roleList.get(0) : "普通用户");

        // 格式化时间
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        if (createTime != null) {
            data.put("createTime", createTime.format(formatter));
        } else {
            data.put("createTime", "");
        }

        if (lastLoginTime != null) {
            data.put("lastLoginTime", lastLoginTime.format(formatter));
        } else {
            data.put("lastLoginTime", "");
        }

        return data;
    }

    /**
     * 根据用户ID获取用户完整信息
     * 
     * @param userId 用户ID
     * @return 用户信息Map
     */
    @Override
    @SuppressWarnings("unchecked")
    public Map<String, Object> getUserInfoByUserId(Integer userId) {
        if (userId == null) {
            return null;
        }

        // 优先从 Redis 缓存获取
        Object cached = tokenService.getProfileInfo(userId);
        if (cached != null && cached instanceof Map) {
            System.out.println("从 Redis 缓存获取 Profile 信息");
            return (Map<String, Object>) cached;
        }

        System.out.println("从数据库查询 Profile 信息");
        // 从数据库获取完整的用户信息
        User dbUser = this.getById(userId);
        if (dbUser == null) {
            return null;
        }

        // 获取用户角色
        List<String> roleList = this.baseMapper.getRoleNameByUserId(dbUser.getId());

        // 获取注册时间（首次活动时间）
        LocalDateTime createTime = getFirstActivityTime(dbUser.getId());

        // 获取最后登录时间（最近一次活动时间）
        LocalDateTime lastLoginTime = getLastActivityTime(dbUser.getId());

        // 构建返回数据
        Map<String, Object> data = new HashMap<>();
        data.put("id", dbUser.getId());
        data.put("name", dbUser.getUsername());
        data.put("avatar", dbUser.getAvatar() != null ? dbUser.getAvatar() : "");
        data.put("email", dbUser.getEmail() != null ? dbUser.getEmail() : "");
        data.put("phone", dbUser.getPhone() != null ? dbUser.getPhone() : "");
        data.put("roles", roleList);
        data.put("role", roleList != null && !roleList.isEmpty() ? roleList.get(0) : "普通用户");

        // 格式化时间
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        if (createTime != null) {
            data.put("createTime", createTime.format(formatter));
        } else {
            data.put("createTime", "");
        }

        if (lastLoginTime != null) {
            data.put("lastLoginTime", lastLoginTime.format(formatter));
        } else {
            data.put("lastLoginTime", "");
        }

        // 存入 Redis 缓存
        tokenService.saveProfileInfo(userId, data);

        return data;
    }

    /**
     * 获取用户首次活动时间（注册时间）
     * 
     * @param userId 用户ID
     * @return 首次活动时间
     */
    private LocalDateTime getFirstActivityTime(Integer userId) {
        LambdaQueryWrapper<UserActivityTime> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserActivityTime::getUserId, userId)
                .orderByAsc(UserActivityTime::getActivityTime)
                .last("LIMIT 1");
        UserActivityTime firstActivity = userActivityTimeService.getOne(wrapper);
        return firstActivity != null ? firstActivity.getActivityTime() : null;
    }

    /**
     * 获取用户最后登录时间（最近一次活动时间）
     * 
     * @param userId 用户ID
     * @return 最后登录时间
     */
    private LocalDateTime getLastActivityTime(Integer userId) {
        LambdaQueryWrapper<UserActivityTime> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserActivityTime::getUserId, userId)
                .orderByDesc(UserActivityTime::getActivityTime)
                .last("LIMIT 1");
        UserActivityTime lastActivity = userActivityTimeService.getOne(wrapper);
        return lastActivity != null ? lastActivity.getActivityTime() : null;
    }
}
