package com.diy.config;


import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {
    @Bean
    public OpenAPI api() {
        return new OpenAPI()
                .info(apiInfo())
                .addSecurityItem(new SecurityRequirement().addList("X-Token"))
                .components(new Components()
                        .addSecuritySchemes("X-Token",
                                new SecurityScheme()
                                        .type(SecurityScheme.Type.APIKEY)
                                        .in(SecurityScheme.In.HEADER)
                                        .name("X-Token")));
    }

    private Info apiInfo() {
        return new Info()
                .title("系统接口文档")
                .description("SpringBoot+Vue")
                .version("1.0")
                .contact(new Contact()
                        .name("zyc")
                        .url("http://www.qqcn.cn")
                        .email("qqcn@aliyun.com"));
    }
}
