package com.diy.sys.service.sign.impl;

import com.diy.sys.entity.sign.TranslationHistory;
import com.diy.sys.mapper.sign.TranslationHistoryMapper;
import com.diy.sys.service.sign.ITranslationHistoryService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

/**
 * <p>
 * 手语翻译历史记录表 服务实现类
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Service
public class TranslationHistoryServiceImpl extends ServiceImpl<TranslationHistoryMapper, TranslationHistory>
        implements ITranslationHistoryService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @org.springframework.beans.factory.annotation.Value("${ai.deepseek.api-key}")
    private String apiKey;

    @org.springframework.beans.factory.annotation.Value("${ai.deepseek.url}")
    private String apiUrl;

    @org.springframework.beans.factory.annotation.Value("${ai.deepseek.model}")
    private String model;

    // ==================== Private Methods for AI Chat History ====================

    private static final String CHAT_HISTORY_PREFIX = "ai:chat:history:";
    private static final long CHAT_HISTORY_TTL = 30; // 30 minutes

    private java.util.List<com.alibaba.fastjson2.JSONObject> getChatHistory(Integer userId) {
        String key = CHAT_HISTORY_PREFIX + userId;
        java.util.List<Object> historyList = redisTemplate.opsForList().range(key, 0, -1);
        java.util.List<com.alibaba.fastjson2.JSONObject> messages = new java.util.ArrayList<>();

        if (historyList != null) {
            for (Object obj : historyList) {
                try {
                    String jsonStr = obj.toString();
                    messages.add(com.alibaba.fastjson2.JSONObject.parseObject(jsonStr));
                } catch (Exception e) {
                    System.err.println("Error parsing chat history: " + e.getMessage());
                }
            }
        }
        return messages;
    }

    private void saveChatHistory(Integer userId, String role, String content) {
        String key = CHAT_HISTORY_PREFIX + userId;
        com.alibaba.fastjson2.JSONObject message = new com.alibaba.fastjson2.JSONObject();
        message.put("role", role);
        message.put("content", content);

        redisTemplate.opsForList().rightPush(key, message.toString());
        redisTemplate.expire(key, CHAT_HISTORY_TTL, java.util.concurrent.TimeUnit.MINUTES);
    }

    @Override
    @Async
    public void saveTranslationAsync(Integer userId, String content) {
        long startTime = System.currentTimeMillis();
        String resultSentence = content;
        int isAiPolished = 0;

        // 1. 调用 DeepSeek API 进行翻译
        try {
            if (apiKey != null && !apiKey.isEmpty()) {
                // 构建系统提示词
                String systemPrompt = "你是一个智能手语翻译助手。请将以下【手语词汇流】翻译成【自然中文口语】。\n\n参考示例：\n输入：[你, 吃, 饭] -> 输出：你吃饭了吗？\n输入：[书, 我, 给, 他] -> 输出：我把书给了他。\n输入：[昨天, 球, 打, 我, 去] -> 输出：我昨天去打球了。\n输入：[不, 喜欢, 苹果, 我] -> 输出：我不喜欢苹果。\n";

                // 获取历史记录
                java.util.List<com.alibaba.fastjson2.JSONObject> messages = new java.util.ArrayList<>();

                // 添加 System Prompt
                com.alibaba.fastjson2.JSONObject systemMsg = new com.alibaba.fastjson2.JSONObject();
                systemMsg.put("role", "system");
                systemMsg.put("content", systemPrompt);
                messages.add(systemMsg);

                // 添加 History
                messages.addAll(getChatHistory(userId));

                // 添加 Current User Input
                String userContent = String.format("输入：[%s] -> 输出：", content);
                com.alibaba.fastjson2.JSONObject userMsg = new com.alibaba.fastjson2.JSONObject();
                userMsg.put("role", "user");
                userMsg.put("content", userContent);
                messages.add(userMsg);

                String aiResult = callDeepSeekApi(messages);
                if (aiResult != null && !aiResult.trim().isEmpty()) {
                    resultSentence = aiResult.trim();
                    isAiPolished = 1;

                    // 保存到历史记录
                    saveChatHistory(userId, "user", userContent);
                    saveChatHistory(userId, "assistant", resultSentence);
                }
            }
        } catch (Exception e) {
            System.err.println("DeepSeek API call failed: " + e.getMessage());
            e.printStackTrace();
        }

        // 2. 确保至少 5 秒耗时
        long elapsed = System.currentTimeMillis() - startTime;
        if (elapsed < 5000) {
            try {
                Thread.sleep(5000 - elapsed);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        // 3. 存入数据库
        TranslationHistory history = new TranslationHistory();
        history.setUserId(userId.longValue());
        history.setOriginalWords(content);
        history.setResultSentence(resultSentence);
        history.setIsAiPolished(isAiPolished);
        history.setCreateTime(LocalDateTime.now());
        history.setIsDeleted(0);

        this.save(history);

        // 4. 从 Redis 删除缓存
        String key = "sign:buffer:" + userId;
        redisTemplate.opsForList().remove(key, 1, content);

        System.out.println(
                "Async save translation completed for user: " + userId + ", AI polished: " + (isAiPolished == 1));

        // 5. 通知前端
        if (isAiPolished == 1) {
            notifyFrontend(userId, resultSentence);
        }
    }

    private void notifyFrontend(Integer userId, String result) {
        System.out.println("Preparing to notify frontend for user: " + userId);
        try {
            com.alibaba.fastjson2.JSONObject payload = new com.alibaba.fastjson2.JSONObject();
            payload.put("userId", userId);
            payload.put("result", result);
            String jsonBody = payload.toString();
            System.out.println("Sending notification payload: " + jsonBody);

            java.net.http.HttpClient client = java.net.http.HttpClient.newHttpClient();
            java.net.http.HttpRequest request = java.net.http.HttpRequest.newBuilder()
                    .uri(java.net.URI.create("http://localhost:8000/notify/ai_result"))
                    .header("Content-Type", "application/json")
                    .POST(java.net.http.HttpRequest.BodyPublishers.ofString(jsonBody))
                    .build();

            // 使用同步发送以便于调试
            java.net.http.HttpResponse<String> response = client.send(request,
                    java.net.http.HttpResponse.BodyHandlers.ofString());

            System.out.println("Notification response: " + response.statusCode() + " " + response.body());

            if (response.statusCode() != 200) {
                System.err.println("Failed to notify frontend: " + response.statusCode());
            }
        } catch (Exception e) {
            System.err.println("Error notifying frontend: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private String callDeepSeekApi(java.util.List<com.alibaba.fastjson2.JSONObject> messages) throws Exception {
        com.alibaba.fastjson2.JSONObject requestBody = new com.alibaba.fastjson2.JSONObject();
        requestBody.put("model", model);
        requestBody.put("stream", false);
        requestBody.put("messages", messages);

        java.net.http.HttpClient client = java.net.http.HttpClient.newHttpClient();
        java.net.http.HttpRequest request = java.net.http.HttpRequest.newBuilder()
                .uri(java.net.URI.create(apiUrl))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + apiKey)
                .POST(java.net.http.HttpRequest.BodyPublishers.ofString(requestBody.toString()))
                .build();

        java.net.http.HttpResponse<String> response = client.send(request,
                java.net.http.HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() == 200) {
            com.alibaba.fastjson2.JSONObject responseJson = com.alibaba.fastjson2.JSONObject
                    .parseObject(response.body());
            com.alibaba.fastjson2.JSONArray choices = responseJson.getJSONArray("choices");
            if (choices != null && !choices.isEmpty()) {
                com.alibaba.fastjson2.JSONObject choice = choices.getJSONObject(0);
                com.alibaba.fastjson2.JSONObject msg = choice.getJSONObject("message");
                return msg.getString("content");
            }
        } else {
            System.err.println("DeepSeek API error: " + response.statusCode() + " " + response.body());
        }
        return null;
    }
}
