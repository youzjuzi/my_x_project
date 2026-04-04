package com.diy.sys.controller.dashboard;

import com.diy.common.utils.SecurityUtils;
import com.diy.common.vo.Result;
import com.diy.sys.service.dashboard.IDashboardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * <p>
 * 首页仪表盘统计控制器
 * 提供 Dashboard 页面所需的聚合统计数据
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Tag(name = "首页仪表盘接口")
@RestController
@RequestMapping("/dashboard")
public class DashboardController {

    @Autowired
    private IDashboardService dashboardService;

    /**
     * 获取当前用户的仪表盘统计数据
     *
     * @return 统计数据，包含：
     *         - streakDays: 连续学习天数
     *         - totalRecognitions: 总识别次数
     *         - challengeAccuracy: 挑战平均准确率 (%)
     *         - bestScore: 挑战最高分
     *         - recognitionTrend: 识别次数趋势 (%)
     *         - accuracyTrend: 准确率趋势 (%)
     */
    @Operation(summary = "获取仪表盘统计数据", description = "聚合翻译历史和挑战记录，返回首页四个卡片所需的统计指标")
    @GetMapping("/stats")
    public Result<Map<String, Object>> getStats() {
        Integer userId = SecurityUtils.getCurrentUserId();
        if (userId == null) {
            return Result.fail(20003, "无法获取用户信息，请重新登录");
        }

        Map<String, Object> data = dashboardService.getStats(userId);
        return Result.success(data, "查询成功");
    }
}
