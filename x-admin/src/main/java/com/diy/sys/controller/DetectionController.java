package com.diy.sys.controller;


import com.diy.common.vo.Result;
import com.diy.sys.entity.Detection;
import com.diy.sys.entity.Role;
import com.diy.sys.service.DetectionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/detections")
public class DetectionController {
    private final DetectionService detectionService;

    @Autowired
    public DetectionController(DetectionService detectionService) {
        this.detectionService = detectionService;
    }

    @GetMapping
    public Result<List<Detection>> getAllDetections() {
        List<Detection> detectionList = detectionService.getAllDetections();
        return Result.success(detectionList);
    }

    @PostMapping
    public void addDetection(@RequestBody Detection detection) {
        detectionService.saveDetection(detection);
    }

    @GetMapping("/latest")
    public List<Detection> getLatestDetections(@RequestParam(defaultValue = "10") int count) {
        return detectionService.getLatestDetections(count);
    }

    @MessageMapping("/detection")
    @SendTo("/topic/detections")
    public List<Detection> handleDetection(Detection detection) {
        detectionService.saveDetection(detection);
        return detectionService.getAllDetections();
    }
}
