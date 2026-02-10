package com.diy;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@MapperScan("com.diy.*.mapper")
@EnableAsync
public class XAdminApplication {

    public static void main(String[] args) {
        SpringApplication.run(XAdminApplication.class, args);
    }

    // passwordEncoder Bean 已移至 SecurityConfig 中定义
    // 避免与 Spring Security 配置冲突
}
