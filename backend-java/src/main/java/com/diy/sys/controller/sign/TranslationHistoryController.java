package com.diy.sys.controller.sign;

import com.diy.common.vo.Result;
import com.diy.sys.service.sign.ITranslationHistoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * <p>
 * 手语翻译历史记录控制器
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Tag(name = "手语翻译历史接口")
@RestController
@RequestMapping("/sign/history")
public class TranslationHistoryController {

    @Autowired
    private ITranslationHistoryService translationHistoryService;

    /**
     * 分页查询翻译历史
     *
     * @param userId   用户ID
     * @param pageNo   页码
     * @param pageSize 每页大小
     * @return 分页结果
     */
    @Operation(summary = "分页查询翻译历史")
    @GetMapping("/list")
    public Result<Map<String, Object>> getHistoryList(
            @RequestParam("userId") Integer userId,
            @RequestParam(value = "pageNo", defaultValue = "1") Long pageNo,
            @RequestParam(value = "pageSize", defaultValue = "10") Long pageSize,
            @RequestParam(value = "startDate", required = false) String startDate,
            @RequestParam(value = "endDate", required = false) String endDate,
            @RequestParam(value = "keyword", required = false) String keyword) {
        Map<String, Object> data = translationHistoryService.getHistoryList(userId, pageNo, pageSize, startDate,
                endDate, keyword);
        return Result.success(data, "查询成功");
    }

    /**
     * 获取指定月份的有记录的日期列表
     *
     * @param userId 用户ID
     * @param year   年份
     * @param month  月份
     * @return 日期列表 (yyyy-MM-dd)
     */
    @Operation(summary = "获取活动日期列表")
    @GetMapping("/dates")
    public Result<List<String>> getActivityDates(
            @RequestParam("userId") Integer userId,
            @RequestParam("year") Integer year,
            @RequestParam("month") Integer month) {
        List<String> dates = translationHistoryService.getActivityDates(userId, year, month);
        return Result.success(dates, "查询成功");
    }
}
