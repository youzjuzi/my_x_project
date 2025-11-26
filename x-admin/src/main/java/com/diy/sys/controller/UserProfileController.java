package com.diy.sys.controller;


import com.diy.common.vo.Result;
import com.diy.sys.service.IUserProfileService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;


@Tag(name = "个人信息接口")
@RestController
@RequestMapping("/profile")
public class UserProfileController {

    @Autowired
    private IUserProfileService userProfileService;

    /**
     * 获取用户个人信息
     * @param token JWT token（从请求头获取）
     * @return 用户信息
     */
    @Operation(summary = "获取用户个人信息")
    @GetMapping("/getInfo")
    public Result<Map<String,Object>> getUserInfo(@RequestParam("token") String token){
        // 如果请求头没有token，尝试从参数获取（兼容旧版本）
        if (token == null || token.isEmpty()) {
            return Result.fail(20003, "缺少认证token");
        }
        
        // 根据token获取用户信息
        Map<String,Object> data = userProfileService.getUserInfo(token);
        if (data != null){
            return Result.success(data, "获取用户信息成功");
        }
        return Result.fail(20003, "登录信息无效，请重新登录");
    }
}
