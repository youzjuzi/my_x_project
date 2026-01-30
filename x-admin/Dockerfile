# 1.构建阶段（Maven编译）
FROM maven:3.9-eclipse-temurin-17 AS build-stage
WORKDIR /app

# 配置阿里云 Maven 镜像 (解决国内网络问题)
RUN mkdir -p /root/.m2 && \
    echo '<?xml version="1.0" encoding="UTF-8"?>\n\
    <settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"\n\
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n\
    xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">\n\
    <mirrors>\n\
    <mirror>\n\
    <id>aliyunmaven</id>\n\
    <mirrorOf>*</mirrorOf>\n\
    <name>阿里云公共仓库</name>\n\
    <url>https://maven.aliyun.com/repository/public</url>\n\
    </mirror>\n\
    </mirrors>\n\
    </settings>' > /root/.m2/settings.xml

# 复制pom文件和源码
COPY pom.xml .
COPY src ./src
# 编译打包 (依赖会在此步骤自动下载)
RUN mvn clean package -DskipTests -B

# 2.运行阶段（使用精简的JRE镜像）
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
# 从构建阶段复制生成的 jar 包
COPY --from=build-stage /app/target/*.jar app.jar
# 自定义9999端口
EXPOSE 9999
ENTRYPOINT ["java", "-jar", "app.jar"]

