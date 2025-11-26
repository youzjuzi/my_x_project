package com.diy.sys.controller;


import com.diy.common.vo.Result;
import com.diy.sys.service.IFileUploadService;
import com.diy.sys.service.IUserProfileService;
import com.diy.sys.service.IUserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;


@Tag(name = "个人信息接口")
@RestController
@RequestMapping("/profile")
public class UserProfileController {

    @Autowired
    private IUserProfileService userProfileService;
    @Autowired
    private IUserService userService;
    @Autowired
    private IFileUploadService fileUploadService;

    /**
     * 获取用户个人信息
     * @param token JWT token（从请求头获取）
     * @return 用户信息
     */
    @Operation(summary = "获取用户个人信息")
    @GetMapping("/getInfo")
    public Result<Map<String,Object>> getUserInfo(@RequestHeader("X-Token") String token){
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

    @Operation(summary = "检测账号是否已经存在")
    @GetMapping("/checkUsername")
    public Result<Boolean> check(@RequestParam("username") String username){
        return Result.success(userService.check(username));
    }

    @Operation(summary = "更改密码")
    @PostMapping("/changePassword")
    public Result<Boolean> changePassword(
            @RequestHeader("X-Token") String token,
            @RequestBody Map<String,String> password){
        try {
            // 将 token 添加到 password Map 中
            password.put("token", token);
            Boolean success = userService.changePassword(password);
            if (success) {
                return Result.success(true, "密码修改成功");
            } else {
                return Result.fail(20004, "密码修改失败");
            }
        } catch (RuntimeException e) {
            // 捕获业务异常，返回错误信息
            return Result.fail(20004, e.getMessage());
        } catch (Exception e) {
            // 捕获其他异常
            e.printStackTrace();
            return Result.fail(20004, "密码修改失败，请稍后重试");
        }
    }

    @Operation(summary = "更新手机号")
    @PostMapping("/updatePhone")
    public Result<Boolean> updatePhone(
            @RequestHeader("X-Token") String token,
            @RequestBody Map<String,String> phoneMap){
        try {
            phoneMap.put("token", token);
            Boolean success = userService.updatePhone(phoneMap);
            if (success) {
                return Result.success(true, "手机号更新成功");
            } else {
                return Result.fail(20005, "手机号更新失败");
            }
        } catch (RuntimeException e) {
            return Result.fail(20005, e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail(20005, "手机号更新失败，请稍后重试");
        }
    }

    @Operation(summary = "更新邮箱")
    @PostMapping("/updateEmail")
    public Result<Boolean> updateEmail(
            @RequestHeader("X-Token") String token,
            @RequestBody Map<String,String> emailMap){
        try {
            emailMap.put("token", token);
            Boolean success = userService.updateEmail(emailMap);
            if (success) {
                return Result.success(true, "邮箱更新成功");
            } else {
                return Result.fail(20006, "邮箱更新失败");
            }
        } catch (RuntimeException e) {
            return Result.fail(20006, e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail(20006, "邮箱更新失败，请稍后重试");
        }
    }

    @Operation(summary = "上传头像")
    @PostMapping("/uploadAvatar")
    public Result<Map<String, String>> uploadAvatar(
            @RequestHeader("X-Token") String token,
            @RequestParam("file") MultipartFile file) {
        try {
            if (token == null || token.isEmpty()) {
                return Result.fail(20003, "缺少认证token");
            }

            // 上传文件到 Cloudflare R2
            String fileUrl = fileUploadService.uploadFile(file, "avatar/");

            // 更新用户头像
            Map<String, String> avatarMap = new HashMap<>();
            avatarMap.put("token", token);
            avatarMap.put("avatar", fileUrl);
            Boolean success = userService.updateAvatar(avatarMap);

            if (success) {
                Map<String, String> result = new HashMap<>();
                result.put("url", fileUrl);
                return Result.success(result, "头像上传成功");
            } else {
                return Result.fail(20007, "头像更新失败");
            }
        } catch (RuntimeException e) {
            return Result.fail(20007, e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail(20007, "头像上传失败，请稍后重试");
        }
    }

}
