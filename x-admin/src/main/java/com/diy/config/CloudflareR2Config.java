package com.diy.config;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Cloudflare R2 配置类
 * R2 兼容 S3 API，可以使用 AWS SDK
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "cloudflare.r2")
public class CloudflareR2Config {

    private String accessKey;
    private String secretKey;
    private String endpoint;
    private String bucketName;
    private String domain;

    @Bean
    public AmazonS3 amazonS3() {
        BasicAWSCredentials credentials = new BasicAWSCredentials(accessKey, secretKey);
        
        AwsClientBuilder.EndpointConfiguration endpointConfiguration = 
            new AwsClientBuilder.EndpointConfiguration(endpoint, "auto");
        
        return AmazonS3ClientBuilder.standard()
                .withCredentials(new AWSStaticCredentialsProvider(credentials))
                .withEndpointConfiguration(endpointConfiguration)
                .withPathStyleAccessEnabled(true)
                .build();
    }
}

