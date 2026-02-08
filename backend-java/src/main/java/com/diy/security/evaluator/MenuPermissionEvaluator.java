package com.diy.security.evaluator;

import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.PermissionEvaluator;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.stereotype.Component;

import java.io.Serializable;

/**
 * 菜单权限评估器
 * 
 * 用于方法级安全注解中评估菜单权限
 * 例如：@PreAuthorize("hasPermission('/sys/user', 'MENU')")
 * 
 * @author youzi
 * @since 2024
 */
@Slf4j
@Component
public class MenuPermissionEvaluator implements PermissionEvaluator {

    @Override
    public boolean hasPermission(
            Authentication authentication,
            Object targetDomainObject,
            Object permission
    ) {
        // 如果用户未认证，返回 false
        if (authentication == null || !authentication.isAuthenticated()) {
            return false;
        }

        // 如果目标对象不是字符串（菜单路径），返回 false
        if (!(targetDomainObject instanceof String)) {
            return false;
        }

        String menuPath = (String) targetDomainObject;
        String permissionType = permission != null ? permission.toString() : "MENU";

        // 只处理 MENU 类型的权限
        if (!"MENU".equals(permissionType)) {
            return false;
        }

        // 规范化菜单路径（确保以 / 开头）
        if (!menuPath.startsWith("/")) {
            menuPath = "/" + menuPath;
        }

        // 构建权限标识
        String requiredPermission = "MENU_" + menuPath;

        for (GrantedAuthority authority : authentication.getAuthorities()) {
            String authorityString = authority.getAuthority();
            
            if (requiredPermission.equals(authorityString)) {
                return true;
            }
            
            if (authorityString.endsWith("/*")) {
                String prefix = authorityString.substring(0, authorityString.length() - 2);
                if (requiredPermission.startsWith(prefix)) {
                    return true;
                }
            }
            
            if (authorityString.startsWith("MENU_") && requiredPermission.startsWith(authorityString + "/")) {
                return true;
            }
        }

        return false;
    }

    @Override
    public boolean hasPermission(
            Authentication authentication,
            Serializable targetId,
            String targetType,
            Object permission
    ) {
        // 这个方法可以用于基于ID的权限检查
        // 目前不需要，返回 false
        return false;
    }
}

