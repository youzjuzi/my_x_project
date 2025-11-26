package com.diy.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import lombok.extern.slf4j.Slf4j;

/**
 * Web MVC 配置类
 * 已移除本地文件存储配置，现在使用 Cloudflare R2 图床
 */
@Slf4j
@Configuration
public class MyWebMvcConfiguration implements WebMvcConfigurer {
    // 如果需要添加其他 Web MVC 配置，可以在这里添加
}