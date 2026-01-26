package com.diy.config;

/**
 * Tianai-Captcha 配置类
 * 注意：如果需要使用完整的 Tianai-Captcha 功能，请取消下面的注释并配置相关属性
 * 
 * @author youzi
 * @since 2024
 */
// @Configuration
public class CaptchaConfig {
    
    // 如果需要使用完整的 Tianai-Captcha，请取消以下注释
    /*
    @Bean
    @ConfigurationProperties(prefix = "tianai.captcha")
    public CaptchaProperties captchaProperties() {
        return new CaptchaProperties();
    }
    
    @Bean
    public ImageCaptchaApplication imageCaptchaApplication(CaptchaProperties captchaProperties) {
        return new ImageCaptchaApplication(captchaProperties);
    }
    
    @Bean
    public SecondaryVerificationApplication secondaryVerificationApplication(ImageCaptchaApplication imageCaptchaApplication) {
        return new SecondaryVerificationApplication(imageCaptchaApplication);
    }
    */
}
