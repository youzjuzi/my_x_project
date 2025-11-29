package com.diy.common.utils;

import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.service.UserAndRole.IUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

/**
 * Spring Security 工具类
 * 用于从 SecurityContext 获取当前登录用户信息
 * 
 * @author youzi
 * @since 2024
 */
@Component
public class SecurityUtils {

    private static IUserService userService;

    @Autowired
    public void setUserService(IUserService userService) {
        SecurityUtils.userService = userService;
    }

    /**
     * 获取当前登录用户的ID
     * 
     * @return 用户ID，如果未登录则返回 null
     */
    public static Integer getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return null;
        }

        Object principal = authentication.getPrincipal();
        if (principal instanceof UserDetails) {
            UserDetails userDetails = (UserDetails) principal;
            String username = userDetails.getUsername();
            if (userService != null) {
                User user = userService.getByUsername(username);
                return user != null ? user.getId() : null;
            }
        }

        return null;
    }

    /**
     * 获取当前登录用户的用户名
     * 
     * @return 用户名，如果未登录则返回 null
     */
    public static String getCurrentUsername() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return null;
        }

        Object principal = authentication.getPrincipal();
        if (principal instanceof UserDetails) {
            UserDetails userDetails = (UserDetails) principal;
            return userDetails.getUsername();
        }

        return null;
    }

    /**
     * 获取当前登录用户对象
     * 
     * @return 用户对象，如果未登录则返回 null
     */
    public static User getCurrentUser() {
        Integer userId = getCurrentUserId();
        if (userId != null && userService != null) {
            return userService.getUserById(userId);
        }
        return null;
    }
}

