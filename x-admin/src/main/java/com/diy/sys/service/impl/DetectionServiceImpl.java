package com.diy.sys.service.impl;

import com.diy.sys.entity.Detection;
import com.diy.sys.repository.DetectionRepository;
import com.diy.sys.service.DetectionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
public class DetectionServiceImpl implements DetectionService {

    private final DetectionRepository detectionRepository;
    private final SimpMessagingTemplate messagingTemplate;

    @Autowired
    public DetectionServiceImpl(DetectionRepository detectionRepository, SimpMessagingTemplate messagingTemplate) {
        this.detectionRepository = detectionRepository;
        this.messagingTemplate = messagingTemplate;
    }

    @Override
    public void saveDetection(Detection detection) {
        if (detection.getTimestamp() == null) {
            detection.setTimestamp(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        }
        detectionRepository.saveDetection(detection);
    }

    @Override
    public List<Detection> getAllDetections() {
        return detectionRepository.getAllDetections();
    }

    @Override
    public List<Detection> getLatestDetections(int count) {
        return detectionRepository.getLatestDetections(count);
    }

    @Override
    @Scheduled(fixedRate = 1000)
    public void sendDetectionData() {
        List<Detection> detections = getAllDetections();
        messagingTemplate.convertAndSend("/topic/detections", detections);
    }
}
