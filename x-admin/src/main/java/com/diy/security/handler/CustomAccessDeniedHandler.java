package com.diy.security.handler;

import com.alibaba.fastjson2.JSON;
import com.diy.common.vo.Result;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * 自定义访问拒绝处理器
 * 
 * 处理已认证但权限不足的请求
 * 
 * @author youzi
 * @since 2024
 */
@Slf4j
@Component
public class CustomAccessDeniedHandler implements AccessDeniedHandler {

    @Override
    public void handle(
            HttpServletRequest request,
            HttpServletResponse response,
            AccessDeniedException accessDeniedException
    ) throws IOException, ServletException {
        
        log.warn("权限不足 - 路径: {}, 用户: {}, 错误: {}", 
                request.getRequestURI(), 
                request.getUserPrincipal() != null ? request.getUserPrincipal().getName() : "未知",
                accessDeniedException.getMessage());
        
        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpServletResponse.SC_FORBIDDEN);
        
        Result<Object> result = Result.fail(20004, "权限不足，无法访问该资源");
        response.getWriter().write(JSON.toJSONString(result));
    }
}

