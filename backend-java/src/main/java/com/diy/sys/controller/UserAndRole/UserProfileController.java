package com.diy.sys.controller.UserAndRole;

import com.diy.common.utils.SecurityUtils;
import com.diy.common.vo.Result;
import com.diy.sys.service.File.IFileUploadService;
import com.diy.sys.service.UserAndRole.IUserProfileService;
import com.diy.sys.service.UserAndRole.IUserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

/**
 * 个人信息控制器
 * 
 * 处理用户个人信息的查看和修改，用户只能修改自己的信息
 * 
 * @author youzi
 * @since 2024
 */
@Tag(name = "个人信息接口")
@RestController
@RequestMapping("/profile")
@PreAuthorize("isAuthenticated()")
public class UserProfileController {

    @Autowired
    private IUserProfileService userProfileService;
    @Autowired
    private IUserService userService;
    @Autowired
    private IFileUploadService fileUploadService;

    /**
     * 获取用户个人信息
     * @return 用户信息
     */
    @Operation(summary = "获取用户个人信息")
    @GetMapping("/getInfo")
    public Result<Map<String,Object>> getUserInfo(){
        Integer userId = SecurityUtils.getCurrentUserId();
        if (userId == null) {
            return Result.fail(20003, "无法获取用户信息，请重新登录");
        }
        
        // 根据当前用户ID获取用户信息
        Map<String,Object> data = userProfileService.getUserInfoByUserId(userId);
        if (data != null){
            return Result.success(data, "获取用户信息成功");
        }
        return Result.fail(20003, "获取用户信息失败");
    }

    @Operation(summary = "检测账号是否已经存在")
    @GetMapping("/checkUsername")
    public Result<Boolean> check(@RequestParam("username") String username){
        return Result.success(userService.check(username));
    }

    @Operation(summary = "更改密码")
    @PostMapping("/changePassword")
    public Result<Boolean> changePassword(@RequestBody Map<String,String> password){
        try {
            Integer userId = SecurityUtils.getCurrentUserId();
            if (userId == null) {
                return Result.fail(20003, "无法获取用户信息，请重新登录");
            }
            
            // 将当前用户ID添加到 password Map 中
            password.put("userId", String.valueOf(userId));
            Boolean success = userService.changePassword(password);
            if (success) {
                return Result.success(true, "密码修改成功");
            } else {
                return Result.fail(20004, "密码修改失败");
            }
        } catch (RuntimeException e) {
            return Result.fail(20004, e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail(20004, "密码修改失败，请稍后重试");
        }
    }

    @Operation(summary = "更新手机号")
    @PostMapping("/updatePhone")
    public Result<Boolean> updatePhone(@RequestBody Map<String,String> phoneMap){
        try {
            Integer userId = SecurityUtils.getCurrentUserId();
            if (userId == null) {
                return Result.fail(20003, "无法获取用户信息，请重新登录");
            }
            
            phoneMap.put("userId", String.valueOf(userId));
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
    public Result<Boolean> updateEmail(@RequestBody Map<String,String> emailMap){
        try {
            Integer userId = SecurityUtils.getCurrentUserId();
            if (userId == null) {
                return Result.fail(20003, "无法获取用户信息，请重新登录");
            }
            
            emailMap.put("userId", String.valueOf(userId));
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
    public Result<Map<String, String>> uploadAvatar(@RequestParam("file") MultipartFile file) {
        try {
            Integer userId = SecurityUtils.getCurrentUserId();
            if (userId == null) {
                return Result.fail(20003, "无法获取用户信息，请重新登录");
            }

            // 上传文件到 Cloudflare R2
            String fileUrl = fileUploadService.uploadFile(file, "avatar/");

            // 更新用户头像
            Map<String, String> avatarMap = new HashMap<>();
            avatarMap.put("userId", String.valueOf(userId));
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
