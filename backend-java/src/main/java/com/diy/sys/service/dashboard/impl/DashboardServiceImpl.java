package com.diy.sys.service.dashboard.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.diy.sys.entity.challenge.Challenge;
import com.diy.sys.entity.sign.TranslationHistory;
import com.diy.sys.mapper.challenge.ChallengeMapper;
import com.diy.sys.mapper.sign.TranslationHistoryMapper;
import com.diy.sys.service.dashboard.IDashboardService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * <p>
 * 首页仪表盘统计服务实现类
 * 聚合 x_translation_history 和 x_challenge 两张表的数据
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Slf4j
@Service
public class DashboardServiceImpl implements IDashboardService {

    @Autowired
    private TranslationHistoryMapper translationHistoryMapper;

    @Autowired
    private ChallengeMapper challengeMapper;

    @Override
    public Map<String, Object> getStats(Integer userId) {
        Map<String, Object> stats = new HashMap<>();

        // ========== 1. 连续学习天数（Streak） ==========
        int streakDays = calculateStreakDays(userId);
        stats.put("streakDays", streakDays);

        // ========== 2. 总识别次数 ==========
        LambdaQueryWrapper<TranslationHistory> historyCountWrapper = new LambdaQueryWrapper<>();
        historyCountWrapper.eq(TranslationHistory::getUserId, userId);
        long totalRecognitions = translationHistoryMapper.selectCount(historyCountWrapper);
        stats.put("totalRecognitions", totalRecognitions);

        // ========== 3. 挑战平均准确率 ==========
        double challengeAccuracy = calculateChallengeAccuracy(userId);
        stats.put("challengeAccuracy", challengeAccuracy);

        // ========== 4. 挑战最高分 ==========
        int bestScore = calculateBestScore(userId);
        stats.put("bestScore", bestScore);

        // ========== 5. 识别次数趋势（近7天 vs 前7天） ==========
        double recognitionTrend = calculateRecognitionTrend(userId);
        stats.put("recognitionTrend", recognitionTrend);

        // ========== 6. 准确率趋势（最近5次 vs 之前5次） ==========
        double accuracyTrend = calculateAccuracyTrend(userId);
        stats.put("accuracyTrend", accuracyTrend);

        return stats;
    }

    /**
     * 计算连续学习天数
     * 从今天往前倒推，统计连续有活跃记录的天数（合并翻译历史和挑战记录）
     */
    private int calculateStreakDays(Integer userId) {
        // 从翻译历史表获取活跃日期
        QueryWrapper<TranslationHistory> historyWrapper = new QueryWrapper<>();
        historyWrapper.select("DISTINCT DATE(create_time) as date_str");
        historyWrapper.eq("user_id", userId);
        List<Object> historyDates = translationHistoryMapper.selectObjs(historyWrapper);

        // 从挑战表获取活跃日期
        QueryWrapper<Challenge> challengeWrapper = new QueryWrapper<>();
        challengeWrapper.select("DISTINCT DATE(create_time) as date_str");
        challengeWrapper.eq("user_id", userId);
        List<Object> challengeDates = challengeMapper.selectObjs(challengeWrapper);

        // 合并所有活跃日期到 Set
        Set<LocalDate> activeDates = new HashSet<>();
        for (Object obj : historyDates) {
            if (obj != null) {
                try {
                    activeDates.add(LocalDate.parse(obj.toString()));
                } catch (Exception e) {
                    log.warn("解析翻译历史日期失败: {}", obj);
                }
            }
        }
        for (Object obj : challengeDates) {
            if (obj != null) {
                try {
                    activeDates.add(LocalDate.parse(obj.toString()));
                } catch (Exception e) {
                    log.warn("解析挑战日期失败: {}", obj);
                }
            }
        }

        // 从今天往前倒推计算连续天数
        LocalDate today = LocalDate.now();
        int streak = 0;
        LocalDate checkDate = today;

        while (activeDates.contains(checkDate)) {
            streak++;
            checkDate = checkDate.minusDays(1);
        }

        return streak;
    }

    /**
     * 计算挑战平均准确率
     * 基于已完成的挑战记录（status=1），计算 completedCount/totalCount 的平均值
     */
    private double calculateChallengeAccuracy(Integer userId) {
        LambdaQueryWrapper<Challenge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Challenge::getUserId, userId);
        wrapper.eq(Challenge::getStatus, 1); // 只统计已完成的
        wrapper.gt(Challenge::getTotalCount, 0); // 总题数大于0

        List<Challenge> completedChallenges = challengeMapper.selectList(wrapper);

        if (completedChallenges.isEmpty()) {
            return 0.0;
        }

        double totalAccuracy = 0.0;
        for (Challenge c : completedChallenges) {
            totalAccuracy += (double) c.getCompletedCount() / c.getTotalCount();
        }

        double avgAccuracy = (totalAccuracy / completedChallenges.size()) * 100;
        // 保留一位小数
        return BigDecimal.valueOf(avgAccuracy).setScale(1, RoundingMode.HALF_UP).doubleValue();
    }

    /**
     * 计算最高分
     */
    private int calculateBestScore(Integer userId) {
        LambdaQueryWrapper<Challenge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Challenge::getUserId, userId);
        wrapper.eq(Challenge::getStatus, 1); // 只统计已完成的
        wrapper.orderByDesc(Challenge::getScore);
        wrapper.last("LIMIT 1");

        Challenge best = challengeMapper.selectOne(wrapper);
        return best != null && best.getScore() != null ? best.getScore() : 0;
    }

    /**
     * 计算识别次数趋势
     * 近7天新增次数 vs 前7天新增次数的百分比变化
     */
    private double calculateRecognitionTrend(Integer userId) {
        LocalDate today = LocalDate.now();
        // 近7天的起始时间
        LocalDateTime recent7Start = today.minusDays(6).atStartOfDay();
        // 前7天的时间范围
        LocalDateTime prev7Start = today.minusDays(13).atStartOfDay();
        LocalDateTime prev7End = today.minusDays(7).atTime(LocalTime.MAX);

        // 近7天识别次数
        LambdaQueryWrapper<TranslationHistory> recentWrapper = new LambdaQueryWrapper<>();
        recentWrapper.eq(TranslationHistory::getUserId, userId);
        recentWrapper.ge(TranslationHistory::getCreateTime, recent7Start);
        long recentCount = translationHistoryMapper.selectCount(recentWrapper);

        // 前7天识别次数
        LambdaQueryWrapper<TranslationHistory> prevWrapper = new LambdaQueryWrapper<>();
        prevWrapper.eq(TranslationHistory::getUserId, userId);
        prevWrapper.ge(TranslationHistory::getCreateTime, prev7Start);
        prevWrapper.le(TranslationHistory::getCreateTime, prev7End);
        long prevCount = translationHistoryMapper.selectCount(prevWrapper);

        if (prevCount == 0) {
            return recentCount > 0 ? 100.0 : 0.0;
        }

        double trend = ((double) (recentCount - prevCount) / prevCount) * 100;
        return BigDecimal.valueOf(trend).setScale(1, RoundingMode.HALF_UP).doubleValue();
    }

    /**
     * 计算准确率趋势
     * 最近5次挑战的平均准确率 vs 之前5次的平均准确率
     */
    private double calculateAccuracyTrend(Integer userId) {
        LambdaQueryWrapper<Challenge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Challenge::getUserId, userId);
        wrapper.eq(Challenge::getStatus, 1);
        wrapper.gt(Challenge::getTotalCount, 0);
        wrapper.orderByDesc(Challenge::getCreateTime);
        wrapper.last("LIMIT 10");

        List<Challenge> recentChallenges = challengeMapper.selectList(wrapper);

        if (recentChallenges.size() < 2) {
            return 0.0; // 数据不足，不计算趋势
        }

        // 分成两组：最近一半 vs 之前一半
        int mid = recentChallenges.size() / 2;
        List<Challenge> recent = recentChallenges.subList(0, mid);
        List<Challenge> prev = recentChallenges.subList(mid, recentChallenges.size());

        double recentAvg = recent.stream()
                .mapToDouble(c -> (double) c.getCompletedCount() / c.getTotalCount())
                .average().orElse(0.0);

        double prevAvg = prev.stream()
                .mapToDouble(c -> (double) c.getCompletedCount() / c.getTotalCount())
                .average().orElse(0.0);

        // 差值百分比
        double trend = (recentAvg - prevAvg) * 100;
        return BigDecimal.valueOf(trend).setScale(1, RoundingMode.HALF_UP).doubleValue();
    }
}
