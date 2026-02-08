package com.diy.security.example;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Spring Security 使用示例
 * 
 * 展示如何在 Controller 中使用 Spring Security 进行权限控制
 * 
 * @author youzi
 * @since 2024
 */
@RestController
@RequestMapping("/example")
public class SecurityUsageExample {

    /**
     * 示例1：基于角色的访问控制
     * 只有 ADMIN 角色可以访问
     */
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/admin-only")
    public String adminOnly() {
        return "只有管理员可以访问";
    }

    /**
     * 示例2：多个角色都可以访问
     */
    @PreAuthorize("hasAnyRole('ADMIN', 'USER')")
    @GetMapping("/admin-or-user")
    public String adminOrUser() {
        return "管理员或普通用户都可以访问";
    }

    /**
     * 示例3：基于菜单权限的访问控制
     * 只有拥有 /sys/user 菜单权限的用户可以访问
     */
    @PreAuthorize("hasPermission('/sys/user', 'MENU')")
    @GetMapping("/menu-permission")
    public String menuPermission() {
        return "只有拥有该菜单权限的用户可以访问";
    }

    /**
     * 示例4：组合条件
     * 需要 ADMIN 角色 且 拥有菜单权限
     */
    @PreAuthorize("hasRole('ADMIN') and hasPermission('/sys/user', 'MENU')")
    @GetMapping("/combined")
    public String combined() {
        return "需要 ADMIN 角色且拥有菜单权限";
    }

    /**
     * 示例5：获取当前认证用户信息
     * 方式1：从 SecurityContext 获取
     */
    @GetMapping("/current-user-1")
    public String getCurrentUser1() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth != null && auth.isAuthenticated()) {
            return "当前用户: " + auth.getName() + ", 权限: " + auth.getAuthorities();
        }
        return "未认证";
    }

    /**
     * 示例6：获取当前认证用户信息
     * 方式2：从方法参数注入
     */
    @GetMapping("/current-user-2")
    public String getCurrentUser2(@AuthenticationPrincipal UserDetails userDetails) {
        if (userDetails != null) {
            return "当前用户: " + userDetails.getUsername() + ", 权限: " + userDetails.getAuthorities();
        }
        return "未认证";
    }

    /**
     * 示例7：获取当前认证用户信息
     * 方式3：直接注入 Authentication
     */
    @GetMapping("/current-user-3")
    public String getCurrentUser3(Authentication authentication) {
        if (authentication != null && authentication.isAuthenticated()) {
            return "当前用户: " + authentication.getName() + ", 权限: " + authentication.getAuthorities();
        }
        return "未认证";
    }
}

