package com.diy.sys.service.dashboard;

import java.util.Map;

/**
 * <p>
 * 首页仪表盘统计服务接口
 * </p>
 *
 * @author youzi
 * @since 2024
 */
public interface IDashboardService {

    /**
     * 获取用户的仪表盘统计数据
     *
     * @param userId 用户ID
     * @return 统计数据 Map，包含：
     *         - streakDays: 连续学习天数
     *         - totalRecognitions: 总识别次数
     *         - challengeAccuracy: 挑战平均准确率 (%)
     *         - bestScore: 挑战最高分
     *         - recognitionTrend: 识别次数趋势 (%)
     *         - accuracyTrend: 准确率趋势 (%)
     */
    Map<String, Object> getStats(Integer userId);
}
