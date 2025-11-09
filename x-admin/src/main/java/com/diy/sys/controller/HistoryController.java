package com.diy.sys.controller;


import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.diy.common.vo.Result;
import com.diy.sys.entity.Detection;
import com.diy.sys.entity.FormattedDetectionDTO;
import com.diy.sys.entity.Role;
import com.diy.sys.service.IHistoryService;
import com.diy.sys.service.impl.HistoryServiceImpl;
import io.swagger.annotations.Api;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Api(tags = {"翻译历史接口"})
@RestController
@RequestMapping("/history")
public class HistoryController {
    @Autowired
    private IHistoryService historyService;
    @GetMapping("/list")
    public Result<Map<String,Object>> getHistoryList(
                                                     @RequestParam(value = "keyword",required = false) String className,
                                                     @RequestParam(value = "pageNo") Long pageNo,
                                                     @RequestParam(value = "pageSize") Long pageSize,
                                                     @RequestParam(value = "startTime",required = false) String startTime,
                                                     @RequestParam(value = "endTime",required = false) String endTime){
        LambdaQueryWrapper<Detection> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StringUtils.hasLength(className),Detection::getClassName,className);
        DateTimeFormatter dbFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        if (StringUtils.hasLength(startTime) && StringUtils.hasLength(endTime)) {
            LocalDateTime start = LocalDateTime.parse(startTime, DateTimeFormatter.ISO_DATE_TIME);
            LocalDateTime end = LocalDateTime.parse(endTime, DateTimeFormatter.ISO_DATE_TIME);

            wrapper.ge(Detection::getTimestamp, start.format(dbFormatter));
            wrapper.le(Detection::getTimestamp, end.format(dbFormatter));
        }

        wrapper.orderByDesc(Detection::getSessionId);

        Page<Detection> page = new Page<>(pageNo,pageSize);
        historyService.page(page, wrapper);

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

        List<FormattedDetectionDTO> formattedRecords = page.getRecords().stream()
                .map(detection -> {
                    FormattedDetectionDTO dto = new FormattedDetectionDTO();
                    LocalDateTime dateTime = LocalDateTime.parse(detection.getTimestamp());
                    dto.setTimestamp(dateTime.format(formatter));
                    dto.setSource(detection.getSource());
                    dto.setConfidence(Math.round(detection.getConfidence() * 100.0) / 100.0);
                    dto.setSessionId(detection.getSessionId());
                    dto.setClassName(detection.getClassName());
                    dto.setUserId(detection.getUserId());
                    return dto;
                })
                .collect(Collectors.toList());

        Map<String,Object> data = new HashMap<>();
        data.put("total",page.getTotal());
        data.put("rows",formattedRecords);

        return Result.success(data);

    }


    
    @GetMapping("/all")
    public Result<List<Detection>> getAllHistory() {
        List<Detection> list = historyService.list();
        return Result.success(list, "查询成功");
    }
    @DeleteMapping("/{session_id}")
    public Result<Detection> deleteDetectionById(@PathVariable("session_id") String session_id) {
        historyService.deleteDetectionById(session_id);
        return Result.success("删除成功");
    }
}
