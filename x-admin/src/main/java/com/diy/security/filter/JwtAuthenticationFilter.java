package com.diy.security.filter;

import com.diy.common.utils.JwtUtil;
import com.diy.security.service.CustomUserDetailsService;
import com.diy.sys.service.UserAndRole.IAuthCacheService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

/**
 * JWT 认证过滤器
 * 
 * 功能：
 * 1. 从请求头中提取 JWT Token
 * 2. 验证 Token 有效性
 * 3. 加载用户信息和权限
 * 4. 设置 Spring Security 上下文
 * 
 * @author youzi
 * @since 2024
 */
@Slf4j
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    @Lazy // 延迟加载，打破循环依赖
    private CustomUserDetailsService userDetailsService;

    @Autowired
    private IAuthCacheService authCacheService;

    private static final String TOKEN_HEADER = "X-Token";
    private static final String TOKEN_PREFIX = ""; // JWT Token 没有前缀

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {

        String requestPath = request.getRequestURI();

        // 提取 Token
        String token = extractTokenFromRequest(request);

        if (token != null) {
            try {
                // 解析 Token，获取用户信息
                Integer userId = extractUserIdFromToken(token);

                if (userId != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                    // 验证 Redis 中的 Token 是否有效
                    if (!authCacheService.validateToken(userId, token)) {
                        log.debug("Redis Token 验证失败 - 用户ID: {}, 路径: {}", userId, requestPath);
                        // Token 在 Redis 中不存在或不匹配，拒绝访问
                        filterChain.doFilter(request, response);
                        return;
                    }

                    // Token 验证通过，自动续签
                    authCacheService.refreshToken(userId);

                    // 加载用户详情（包含角色和权限）
                    UserDetails userDetails = userDetailsService.loadUserByUserId(userId);

                    if (userDetails != null) {
                        // 创建认证对象
                        UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                                userDetails,
                                null,
                                userDetails.getAuthorities());

                        authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));

                        // 设置到 Spring Security 上下文
                        SecurityContextHolder.getContext().setAuthentication(authentication);

                        log.debug("JWT 认证成功 - 用户ID: {}, 路径: {}, Token 已续签", userId, requestPath);
                    }
                }
            } catch (Exception e) {
                log.error("JWT 认证失败 - 路径: {}, 错误: {}", requestPath, e.getMessage());
                // 认证失败，继续过滤器链，由 Spring Security 处理
            }
        } else {
            log.debug("请求未包含 Token - 路径: {}", requestPath);
        }

        // 继续过滤器链
        filterChain.doFilter(request, response);
    }

    /**
     * 从请求中提取 Token
     */
    private String extractTokenFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader(TOKEN_HEADER);

        if (StringUtils.hasText(bearerToken)) {
            // 如果 Token 有前缀（如 "Bearer "），则移除
            if (bearerToken.startsWith(TOKEN_PREFIX)) {
                return bearerToken.substring(TOKEN_PREFIX.length());
            }
            return bearerToken;
        }

        return null;
    }

    /**
     * 从 Token 中提取用户ID
     */
    private Integer extractUserIdFromToken(String token) {
        try {
            // 解析 Token，获取用户对象
            com.diy.sys.entity.UserAndRole.User user = jwtUtil.parseToken(token,
                    com.diy.sys.entity.UserAndRole.User.class);
            if (user != null && user.getId() != null) {
                return user.getId();
            }
        } catch (Exception e) {
            log.debug("Token 解析失败: {}", e.getMessage());
        }
        return null;
    }
}
