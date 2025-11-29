package com.diy.sys.controller.challenge;

import com.diy.common.utils.SecurityUtils;
import com.diy.common.vo.Result;
import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.service.challenge.IChallengeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * <p>
 * 挑战控制器
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Tag(name = "挑战接口")
@RestController
@RequestMapping("/challenge")
@PreAuthorize("hasPermission('/learning/challenge', 'MENU')")
public class ChallengeController {
    
    @Autowired
    private IChallengeService challengeService;

    /**
     * 根据条件查询题目
     * 
     * @param mode 挑战模式：random/questionSet
     * @param questionSetId 题库ID（questionSet模式必填）
     * @param types 题目类型列表（random模式必填，多个用逗号分隔）：1-单词，2-中文，3-数字
     * @param difficulties 难度列表（可选，多个用逗号分隔）：1-简单，2-中等，3-困难
     * @param count 题目数量（随机模式或题库随机模式）
     * @param random 是否随机（questionSet模式，默认true）
     * @return 题目列表
     */
    @Operation(summary = "根据条件查询题目", description = "支持随机挑战和题库模式，可筛选类型和难度")
    @PostMapping("/questions/query")
    public Result<Map<String, Object>> queryQuestions(
            @RequestParam("mode") String mode,
            @RequestParam(value = "questionSetId", required = false) Integer questionSetId,
            @RequestParam(value = "types", required = false) String types,
            @RequestParam(value = "difficulties", required = false) String difficulties,
            @RequestParam(value = "count", required = false) Integer count,
            @RequestParam(value = "random", defaultValue = "true") Boolean random) {
        try {
            // 参数验证
            if (!"random".equals(mode) && !"questionSet".equals(mode)) {
                return Result.fail("挑战模式必须是 random 或 questionSet");
            }
            
            if ("questionSet".equals(mode) && questionSetId == null) {
                return Result.fail("题库模式必须提供 questionSetId");
            }
            
            if ("random".equals(mode) && (types == null || types.trim().isEmpty())) {
                return Result.fail("随机模式必须提供 types");
            }

            // 解析类型列表
            List<Integer> typeList = null;
            if (types != null && !types.trim().isEmpty()) {
                String[] typeArray = types.split(",");
                typeList = new java.util.ArrayList<>();
                for (String type : typeArray) {
                    typeList.add(Integer.parseInt(type.trim()));
                }
            }

            // 解析难度列表
            List<Integer> difficultyList = null;
            if (difficulties != null && !difficulties.trim().isEmpty()) {
                String[] difficultyArray = difficulties.split(",");
                difficultyList = new java.util.ArrayList<>();
                for (String difficulty : difficultyArray) {
                    difficultyList.add(Integer.parseInt(difficulty.trim()));
                }
            }

            Map<String, Object> data = challengeService.queryQuestions(
                    mode, questionSetId, typeList, difficultyList, count, random);
            
            return Result.success(data, "查询成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 开始挑战（创建挑战记录）
     * 
     * @param requestBody 请求体，包含：
     *                    - mode: 挑战模式
     *                    - questionSetId: 题库ID（题库模式）
     *                    - questionIds: 题目ID列表
     *                    - timeLimit: 时间限制（秒）
     * @return 挑战记录和题目列表
     */
    @Operation(summary = "开始挑战", description = "创建挑战记录并返回题目列表")
    @PostMapping("/start")
    public Result<Map<String, Object>> startChallenge(
            @RequestBody Map<String, Object> requestBody) {
        try {
            // 从SecurityContext获取当前用户ID
            Integer userId = SecurityUtils.getCurrentUserId();
            if (userId == null) {
                return Result.fail(20003, "无法获取用户信息，请重新登录");
            }
            String mode = (String) requestBody.get("mode");
            Integer questionSetId = (Integer) requestBody.get("questionSetId");
            @SuppressWarnings("unchecked")
            List<Integer> questionIds = (List<Integer>) requestBody.get("questionIds");
            Integer timeLimit = (Integer) requestBody.get("timeLimit");

            // 参数验证
            if (mode == null || (!"random".equals(mode) && !"questionSet".equals(mode))) {
                return Result.fail("挑战模式必须是 random 或 questionSet");
            }
            if (questionIds == null || questionIds.isEmpty()) {
                return Result.fail("题目ID列表不能为空");
            }
            if (timeLimit == null || timeLimit <= 0) {
                return Result.fail("时间限制必须大于0");
            }

            Map<String, Object> data = challengeService.startChallenge(
                    userId, mode, questionSetId, questionIds, timeLimit);
            
            return Result.success(data, "挑战开始成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("开始挑战失败：" + e.getMessage());
        }
    }

    /**
     * 提交挑战结果
     * 
     * @param requestBody 请求体，包含：
     *                    - challengeId: 挑战ID
     *                    - score: 得分
     *                    - completedCount: 完成题目数
     *                    - timeUsed: 使用时间（秒）
     * @return 挑战结果统计
     */
    @Operation(summary = "提交挑战结果", description = "保存挑战结果并返回统计信息，包含用户验证、重复提交检查、分数验证等")
    @PostMapping("/submit")
    public Result<Map<String, Object>> submitChallenge(
            @RequestBody Map<String, Object> requestBody) {
        try {
            // 从SecurityContext获取当前用户ID
            Integer userId = SecurityUtils.getCurrentUserId();
            if (userId == null) {
                return Result.fail(20003, "无法获取用户信息，请重新登录");
            }
            String challengeId = (String) requestBody.get("challengeId");
            Integer score = (Integer) requestBody.get("score");
            Integer completedCount = (Integer) requestBody.get("completedCount");
            Integer timeUsed = (Integer) requestBody.get("timeUsed");

            // 参数验证
            if (challengeId == null || challengeId.trim().isEmpty()) {
                return Result.fail("挑战ID不能为空");
            }
            if (score == null) {
                return Result.fail("得分不能为空");
            }
            if (completedCount == null) {
                return Result.fail("完成题目数不能为空");
            }
            if (timeUsed == null) {
                return Result.fail("使用时间不能为空");
            }

            Map<String, Object> data = challengeService.submitChallenge(
                    userId, challengeId, score, completedCount, timeUsed);
            
            return Result.success(data, "提交成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("提交失败：" + e.getMessage());
        }
    }

    /**
     * 获取挑战历史记录（分页）
     * 
     * @param pageNo 页码
     * @param pageSize 每页大小
     * @return 分页结果
     */
    @Operation(summary = "获取挑战历史记录", description = "分页查询用户的挑战历史记录")
    @GetMapping("/history")
    public Result<Map<String, Object>> getChallengeHistory(
            @RequestParam("pageNo") Long pageNo,
            @RequestParam("pageSize") Long pageSize) {
        try {
            // 从SecurityContext获取当前用户ID
            Integer userId = SecurityUtils.getCurrentUserId();
            if (userId == null) {
                return Result.fail(20003, "无法获取用户信息，请重新登录");
            }

            // 参数验证
            if (pageNo == null || pageNo < 1) {
                return Result.fail("页码必须大于0");
            }
            if (pageSize == null || pageSize < 1) {
                return Result.fail("每页大小必须大于0");
            }

            Map<String, Object> data = challengeService.getChallengeHistory(userId, pageNo, pageSize);
            
            return Result.success(data, "查询成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 获取所有用户的挑战记录（管理员接口，分页）
     * 
     * @param userId 用户ID（可选，用于筛选特定用户）
     * @param mode 挑战模式（可选）：random/questionSet
     * @param status 状态（可选）：0-进行中，1-已完成，2-已放弃
     * @param pageNo 页码
     * @param pageSize 每页大小
     * @return 分页结果
     */
    @Operation(summary = "获取所有用户的挑战记录", description = "管理员接口，支持按用户、模式、状态筛选")
    @PreAuthorize("hasPermission('/sys/challenge', 'MENU')")
    @GetMapping("/admin/list")
    public Result<Map<String, Object>> getAllChallengeHistory(
            @RequestParam(value = "userId", required = false) Integer userId,
            @RequestParam(value = "mode", required = false) String mode,
            @RequestParam(value = "status", required = false) Integer status,
            @RequestParam("pageNo") Long pageNo,
            @RequestParam("pageSize") Long pageSize) {
        try {
            // 参数验证
            if (pageNo == null || pageNo < 1) {
                return Result.fail("页码必须大于0");
            }
            if (pageSize == null || pageSize < 1) {
                return Result.fail("每页大小必须大于0");
            }

            Map<String, Object> data = challengeService.getAllChallengeHistory(userId, mode, status, pageNo, pageSize);
            return Result.success(data, "查询成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 获取所有有过挑战的用户列表
     * 
     * @return 用户列表
     */
    @Operation(summary = "获取所有有过挑战的用户列表", description = "用于下拉框选择")
    @PreAuthorize("hasPermission('/sys/challenge', 'MENU')")
    @GetMapping("/admin/users")
    public Result<List<User>> getUsersWithChallenges() {
        try {
            List<User> users = challengeService.getUsersWithChallenges();
            return Result.success(users, "查询成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }
}
