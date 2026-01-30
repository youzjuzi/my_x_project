package com.diy.security.config;

import com.diy.security.evaluator.MenuPermissionEvaluator;
import com.diy.security.filter.JwtAuthenticationFilter;
import com.diy.security.handler.CustomAccessDeniedHandler;
import com.diy.security.handler.CustomAuthenticationEntryPoint;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.access.expression.method.DefaultMethodSecurityExpressionHandler;
import org.springframework.security.access.expression.method.MethodSecurityExpressionHandler;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;

/**
 * Spring Security 配置类
 * 
 * 安全策略：
 * 1. 基于 JWT 的无状态认证
 * 2. 基于角色的访问控制（RBAC）
 * 3. 基于菜单路径的权限控制
 * 
 * @author youzi
 * @since 2024
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true, // 启用 @PreAuthorize 和 @PostAuthorize
        securedEnabled = true, // 启用 @Secured
        jsr250Enabled = true // 启用 @RolesAllowed
)
public class SecurityConfig {

    @Autowired
    private JwtAuthenticationFilter jwtAuthenticationFilter;

    @Autowired
    private CustomAuthenticationEntryPoint authenticationEntryPoint;

    @Autowired
    private CustomAccessDeniedHandler accessDeniedHandler;

    @Autowired
    private MenuPermissionEvaluator menuPermissionEvaluator;

    /**
     * 安全过滤器链配置
     * 
     * 策略：
     * - 禁用默认的登录表单和基本认证
     * - 使用 JWT 认证过滤器
     * - 配置 CORS
     * - 配置异常处理
     */
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                // 禁用 CSRF（因为使用 JWT，不需要 CSRF 保护）
                .csrf(AbstractHttpConfigurer::disable)

                // 配置 CORS
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))

                // 配置会话管理（无状态，使用 JWT）
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))

                // 配置请求授权
                .authorizeHttpRequests(auth -> auth
                        // 公开访问的接口（不需要认证）
                        .requestMatchers(
                                "/auth/login",
                                "/auth/register",
                                "/auth/info",
                                "/captcha",
                                "/error",
                                "/swagger-ui.html",
                                "/swagger-ui/**",
                                "/swagger-resources/**",
                                "/v3/api-docs/**",
                                "/v3/**",
                                "/doc.html",
                                "/webjars/**")
                        .permitAll()

                        // 需要认证的接口（具体权限由方法级安全注解控制）
                        // 注意：这里只做基本的认证检查，具体权限由菜单权限系统控制
                        // 注意：路径匹配顺序很重要，更具体的路径应该放在前面
                        .requestMatchers(
                                "/challenge/admin/**", // 管理员挑战接口
                                "/challenge/**", // 普通挑战接口（放在 admin 后面，避免冲突）
                                "/user/**", // 用户管理接口（需要管理员权限）
                                "/role/**",
                                "/menu/**",
                                "/questionSet/**",
                                "/question/**",
                                "/profile/**" // 个人信息接口（需要登录，用户只能修改自己的信息）
                        ).authenticated() // 需要认证，具体权限由方法级注解或菜单权限控制

                        // 其他所有请求需要认证
                        .anyRequest().authenticated())

                // 添加 JWT 认证过滤器（在 UsernamePasswordAuthenticationFilter 之前）
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)

                // 配置异常处理
                .exceptionHandling(exceptions -> exceptions
                        .authenticationEntryPoint(authenticationEntryPoint) // 未认证时的处理
                        .accessDeniedHandler(accessDeniedHandler) // 权限不足时的处理
                );

        return http.build();
    }

    /**
     * CORS 配置
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();

        // 允许的源
        configuration.setAllowedOrigins(Arrays.asList(
                "http://localhost",
                "http://localhost:8888",
                "http://localhost:8001",
                "http://localhost:5173",
                "http://4.194.131.190:9999",
                "http://4.194.131.190",
                "http://4.194.131.190:8888",
                "http://admin.youzilite.app:8888",
                "http://admin.youzilite.app:9999",
                "http://admin.youzilite.app",
                "https://admin.youzilite.app:9999",
                "https://admin.youzilite.app:443",
                "https://admin.youzilite.app",
                "https://admin.youzilite.app:443",
                "https://admin.youzilite.app:8888",
                // Tauri 应用的 origin
                "tauri://localhost",
                "http://tauri.localhost"));

        // 允许的请求方法
        configuration.setAllowedMethods(Arrays.asList(
                "GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"));

        // 允许的请求头
        configuration.setAllowedHeaders(Arrays.asList("*"));

        // 允许携带凭证
        configuration.setAllowCredentials(true);

        // 预检请求的缓存时间
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);

        return source;
    }

    /**
     * 密码编码器
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /**
     * 方法级安全表达式处理器
     * 用于支持自定义权限评估器
     */
    @Bean
    public MethodSecurityExpressionHandler methodSecurityExpressionHandler() {
        DefaultMethodSecurityExpressionHandler handler = new DefaultMethodSecurityExpressionHandler();
        handler.setPermissionEvaluator(menuPermissionEvaluator);
        return handler;
    }
}
