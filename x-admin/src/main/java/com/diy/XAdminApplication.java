package com.diy;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.data.redis.RedisAutoConfiguration;

@SpringBootApplication(exclude = {RedisAutoConfiguration.class})
@MapperScan("com.diy.*.mapper")

public class XAdminApplication {

    public static void main(String[] args) {
        SpringApplication.run(XAdminApplication.class, args);
    }

    // passwordEncoder Bean 已移至 SecurityConfig 中定义
    // 避免与 Spring Security 配置冲突
}
