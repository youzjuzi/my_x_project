package com.diy.sys.controller.sign;

import com.diy.common.vo.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;
import java.util.concurrent.TimeUnit;

import java.util.Map;

/**
 * 手语交互控制器
 * 处理 AI Server 推送的识别结果
 */
@Tag(name = "手语交互接口")
@RestController
@RequestMapping("/sign")
public class SignInteractionController {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private com.diy.sys.service.sign.ITranslationHistoryService translationHistoryService;

    @Operation(summary = "提交识别句子")
    @PostMapping("/submit")
    public Result<String> submitSentence(@RequestBody Map<String, String> payload) {
        String userId = payload.get("userId");
        String content = payload.get("content");

        System.out.println("SignInteractionController: 接收到 submit 请求 - User: " + userId + ", Content: " + content);

        if (userId == null || content == null) {
            return Result.fail("缺少 userId 或 content");
        }

        // 存入 Redis List: sign:buffer:{userId}
        // 使用 rightPush 将新句子追加到列表末尾
        String key = "sign:buffer:" + userId;
        redisTemplate.opsForList().rightPush(key, content);

        // 设置过期时间 30 分钟
        redisTemplate.expire(key, 30, TimeUnit.MINUTES);

        // 触发异步任务：模拟 AI 处理并存入数据库
        try {
            Integer uid = Integer.parseInt(userId);
            translationHistoryService.saveTranslationAsync(uid, content);
        } catch (NumberFormatException e) {
            System.out.println("Invalid userId: " + userId);
        }

        return Result.success("提交成功");
    }
}
