package com.diy.sys.service;

import com.diy.sys.entity.Detection;

import java.util.List;

public interface DetectionService {
    void saveDetection(Detection detection);
    List<Detection> getAllDetections();
    List<Detection> getLatestDetections(int count);
    void sendDetectionData();
}
