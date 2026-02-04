package com.diy.sys.controller.captcha;

import com.diy.common.vo.Result;
import com.diy.sys.service.captcha.ICaptchaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 验证码控制器
 * 
 * @author youzi
 * @since 2024
 */
@Tag(name = "验证码接口")
@RestController
@RequestMapping("/captcha")
public class CaptchaController {

    @Autowired
    private ICaptchaService captchaService;

    @Operation(summary = "生成验证码")
    @GetMapping("/generate")
    public Result<Map<String, Object>> generate() {
        System.out.println("CaptchaController: 接收到 generate 请求");
        try {
            Map<String, Object> data = captchaService.generate();
            return Result.success(data);
        } catch (Exception e) {
            e.printStackTrace();
            // 返回详细错误信息用于调试
            return Result.fail(500, "生成验证码失败: " + e.getMessage());
        }
    }

    @Operation(summary = "验证验证码")
    @PostMapping("/verify")
    public Result<Boolean> verify(@RequestParam String id, @RequestBody Map<String, Object> data) {
        boolean valid = captchaService.verify(id, data);
        if (valid) {
            return Result.success(true, "验证成功");
        } else {
            return Result.fail(20004, "验证失败");
        }
    }
}
