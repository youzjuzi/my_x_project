package com.diy.sys.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.diy.common.vo.Result;
import com.diy.config.CaptureConfig;
import com.diy.sys.entity.User;
import com.diy.sys.entity.UserActivityTime;
import com.diy.sys.service.IUserActivityTimeService;
import com.diy.sys.service.IUserService;
import com.wf.captcha.utils.CaptchaUtil;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.repository.query.Param;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;
import org.springframework.stereotype.Controller;

import jakarta.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * <p>
 *  前端控制器
 * </p>
 *
 * @author youzi
 * @since 2023-09-02
 */
@Tag(name = "用户接口列表")
@RestController
@RequestMapping("/user")
public class UserController {
    @Autowired
    private IUserService userService;
    @Autowired
    private PasswordEncoder passwordEncoder;
    @Autowired
    private IUserActivityTimeService userActivityTimeService;


    @GetMapping("/time")
    public Result<List<UserActivityTime>> getAllActivityTime() {
        List<UserActivityTime> list = userActivityTimeService.list();
        return Result.success(list,"查询成功");
    }
    @GetMapping("/all")
    public Result<List<User>> getAllUser() {
        List<User> list = userService.list();
        return Result.success(list, "查询成功");
    }
    @Operation(summary = "用户登录")
    @PostMapping("/login")
    public Result<Map<String,Object>> login(@RequestBody User user){

//        System.out.println("codeKey:" + user.getCodeKey());
//        System.out.println("code:" + user.getCaptcha());
//        // 判断验证码是否正确
//        if (!user.getCaptcha().toLowerCase().equals(CaptureConfig.CAPTURE_MAP.get(user.getCodeKey()))) {
//            //验证码错误
//            CaptureConfig.CAPTURE_MAP.clear();
//            return Result.fail(20004,"验证码错误");
//        }
        Map<String,Object> data = userService.login(user);
        if (data != null){
            User loggedInUser = userService.getByUsername(user.getUsername());
            data.put("userId", loggedInUser.getId());
            return Result.success(data,"登录成功");
        }
        return Result.fail(20002,"用户名或密码错误");
    }

    @Operation(summary = "用户注册")
    @PostMapping("/register")
    public Result<?> register(@RequestBody User user,HttpServletRequest request){
//        if (!user.getCaptcha().toLowerCase().equals(CaptureConfig.CAPTURE_MAP.get(user.getCodeKey()))) {
//            //验证码错误
//            CaptureConfig.CAPTURE_MAP.clear();
//            return Result.fail(20004,"验证码错误");
//        }
        //检测用户名是否已经存在
        Map<String,Object> data = userService.register(user);
        if (data != null){
//            //成功，清除验证码
//            CaptureConfig.CAPTURE_MAP.clear();
            return Result.success(data,"注册成功");
        }
        return Result.fail(20001,"注册失败");
    }

    @Operation(summary = "info")
    @GetMapping("/info")
    public Result<Map<String,Object>> getUserInfo(@RequestParam("token") String token){
        //根据token获取用户信息，redis
        Map<String,Object> data = userService.getUserInfo(token);
        if (data != null){
            User user = userService.getByUsername((String) data.get("name"));
            data.put("userId", user.getId());
            return Result.success(data);
        }
        return Result.fail(20003,"登录信息无效，请重新登录");
    }

    @PostMapping("/logout")
    public Result<?> logout(@RequestHeader("X-Token") String token){
        userService.logout(token);
        return Result.success("注销成功");
    }

//    @GetMapping("/list")
//    public Result<Map<String ,Object>> getUserList(@RequestParam(value = "username",required = false) String username,
//                                               @RequestParam(value = "phone",required = false) String phone,
//                                               @RequestParam("pageNo") Long pageNo,
//                                               @RequestParam("pageSize") Long pageSize){
//        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
//        wrapper.eq(StringUtils.hasLength(username),User::getUsername,username);
//        wrapper.eq(StringUtils.hasLength(phone),User::getPhone,phone);
//        // 排序
//        wrapper.orderByAsc(User::getId);
//
//        Page<User> page = new Page<>(pageNo,pageSize);
//        userService.page(page,wrapper);
//
//        // 封装数据
//        Map<String ,Object> data = new HashMap<>();
//        data.put("total",page.getTotal());
//        data.put("row",page.getRecords());
//
//        return Result.success(data);
//    }

    @Operation(summary = "用户列表")
    @GetMapping("/list")
    public Result<Map<String ,Object>> getUserList(
            @RequestParam(value = "username",required = false) String username,
            @RequestParam(value = "phone",required = false) String phone,
            @RequestParam(value = "email",required = false) String email,
            @RequestParam("pageNo") Long pageNo,
            @RequestParam("pageSize") Long pageSize){
        Map<String ,Object> data = userService.getUserList(username, phone, email ,pageNo, pageSize);
        return Result.success(data);
}


    @Operation(summary = "新增用户")
    @PostMapping
    public Result<?> addUser(@RequestBody User user){
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        userService.addUser(user);
        System.out.println(user);
        return Result.success("新增用户成功");
    }
    @PutMapping
    public Result<?> updateUser(@RequestBody User user){
        user.setPassword(null);
        userService.updateUser(user);
        return Result.success("修改用户成功");
    }
    @GetMapping("/{id}")
    public Result<User> getUserById(@PathVariable("id") Integer id){
        User user = userService.getUserById(id);
        return Result.success(user);
    }
    @DeleteMapping ("/{id}")
    public Result<User> deleteUserById(@PathVariable("id") Integer id){
        userService.deleteUserById(id);
        return Result.success("删除用户成功");
    }


}

