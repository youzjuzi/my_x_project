package com.diy.sys.repository;


import com.diy.sys.entity.Detection;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class DetectionRepository {
    private final RedisTemplate<String, Detection> redisTemplate;

    @Autowired
    public DetectionRepository(RedisTemplate<String, Detection> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public List<Detection> getAllDetections() {
        return redisTemplate.opsForList().range("detections", 0, -1);
    }

    public void saveDetection(Detection detection) {
        redisTemplate.opsForList().rightPush("detections", detection);
    }

    public List<Detection> getLatestDetections(int count) {
        long size = redisTemplate.opsForList().size("detections");
        return redisTemplate.opsForList().range("detections", Math.max(0, size - count), -1);
    }
}
