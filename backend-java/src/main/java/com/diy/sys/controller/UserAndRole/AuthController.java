package com.diy.sys.controller.UserAndRole;

import com.diy.common.vo.Result;
import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.service.UserAndRole.IUserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Map;

/**
 * 认证控制器
 * 处理用户登录、注册、登出等认证相关接口
 * 
 * @author youzi
 * @since 2024
 */
@Tag(name = "认证接口")
@RestController
@RequestMapping("/auth")
public class AuthController {

    @Autowired
    private IUserService userService;

    @Operation(summary = "用户登录")
    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody User user) {
        Map<String, Object> data = userService.login(user);
        if (data != null) {
            User loggedInUser = userService.getByUsername(user.getUsername());
            data.put("userId", loggedInUser.getId());
            return Result.success(data, "登录成功");
        }
        return Result.fail(20002, "用户名或密码错误");
    }

    @Operation(summary = "用户注册")
    @PostMapping("/register")
    public Result<?> register(@RequestBody User user, HttpServletRequest request) {
        Map<String, Object> data = userService.register(user);
        if (data != null) {
            return Result.success(data, "注册成功");
        }
        return Result.fail(20001, "注册失败");
    }

    @Operation(summary = "获取用户信息")
    @GetMapping("/info")
    public Result<Map<String, Object>> getUserInfo(@RequestParam("token") String token) {
        Map<String, Object> data = userService.getUserInfo(token);
        if (data != null) {
            User user = userService.getByUsername((String) data.get("name"));
            data.put("userId", user.getId());
            return Result.success(data);
        }
        return Result.fail(20003, "登录信息无效，请重新登录");
    }

    @Operation(summary = "用户登出")
    @PostMapping("/logout")
    @PreAuthorize("isAuthenticated()")
    public Result<?> logout(@RequestHeader("X-Token") String token) {
        userService.logout(token);
        return Result.success("注销成功");
    }
}

