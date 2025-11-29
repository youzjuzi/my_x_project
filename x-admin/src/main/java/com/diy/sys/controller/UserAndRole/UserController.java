package com.diy.sys.controller.UserAndRole;

import com.diy.common.vo.Result;
import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.entity.UserAndRole.UserActivityTime;
import com.diy.sys.service.UserAndRole.IUserActivityTimeService;
import com.diy.sys.service.UserAndRole.IUserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 用户管理控制器
 * 
 * 处理用户管理的增删改查等操作，需要管理员权限
 * 
 * @author youzi
 * @since 2023-09-02
 */
@Tag(name = "用户管理接口")
@RestController
@RequestMapping("/user")
@PreAuthorize("hasPermission('/sys/user', 'MENU')")
public class UserController {

    @Autowired
    private IUserService userService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private IUserActivityTimeService userActivityTimeService;

    @Operation(summary = "用户列表")
    @GetMapping("/list")
    public Result<Map<String, Object>> getUserList(
            @RequestParam(value = "username", required = false) String username,
            @RequestParam(value = "phone", required = false) String phone,
            @RequestParam(value = "email", required = false) String email,
            @RequestParam("pageNo") Long pageNo,
            @RequestParam("pageSize") Long pageSize) {
        Map<String, Object> data = userService.getUserList(username, phone, email, pageNo, pageSize);
        return Result.success(data);
    }

    @Operation(summary = "获取所有用户")
    @GetMapping("/all")
    public Result<List<User>> getAllUser() {
        List<User> list = userService.list();
        return Result.success(list, "查询成功");
    }

    @Operation(summary = "获取用户活动时间")
    @GetMapping("/time")
    public Result<List<UserActivityTime>> getAllActivityTime() {
        List<UserActivityTime> list = userActivityTimeService.list();
        return Result.success(list, "查询成功");
    }

    @Operation(summary = "检测账号是否已经存在")
    @GetMapping("/checkUsername")
    public Result<Boolean> check(@RequestParam("username") String username) {
        return Result.success(userService.check(username));
    }

    @Operation(summary = "新增用户")
    @PostMapping
    public Result<?> addUser(@RequestBody User user) {
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        userService.addUser(user);
        return Result.success("新增用户成功");
    }

    @Operation(summary = "修改用户")
    @PutMapping
    public Result<?> updateUser(@RequestBody User user) {
        userService.updateUser(user);
        return Result.success("修改用户成功");
    }

    @Operation(summary = "获取用户")
    @GetMapping("/{id}")
    public Result<User> getUserById(@PathVariable("id") Integer id) {
        User user = userService.getUserById(id);
        return Result.success(user);
    }

    @Operation(summary = "删除用户")
    @DeleteMapping("/{id}")
    public Result<User> deleteUserById(@PathVariable("id") Integer id) {
        userService.deleteUserById(id);
        return Result.success("删除用户成功");
    }
}
