# syntax=docker/dockerfile:1
ARG BACKEND_BUILD_IMAGE=maven:3.9-eclipse-temurin-17
ARG BACKEND_RUNTIME_IMAGE=maven:3.9-eclipse-temurin-17

# 1.构建阶段（Maven编译）
FROM ${BACKEND_BUILD_IMAGE} AS build-stage
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

# 先只复制 pom.xml；pom 不变时依赖层可复用
COPY pom.xml .
# --mount=type=cache 将宿主机的 Maven 本地仓库挂载进来，跨构建复用已下载的 jar，避免重复下载
RUN --mount=type=cache,target=/root/.m2/repository \
    mvn dependency:go-offline -B

# 再复制源码并编译打包（同样复用缓存中的依赖）
COPY src ./src
RUN --mount=type=cache,target=/root/.m2/repository \
    mvn clean package -DskipTests -B

# 2.运行阶段
# 默认复用 Maven + Temurin 17 镜像，避免部分镜像站缺少 eclipse-temurin:17-jre-alpine。
# 如服务器能正常拉取轻量 JRE 镜像，可设置：
# BACKEND_RUNTIME_IMAGE=eclipse-temurin:17-jre-alpine
FROM ${BACKEND_RUNTIME_IMAGE}
WORKDIR /app
# 从构建阶段复制生成的 jar 包
COPY --from=build-stage /app/target/*.jar app.jar
# 自定义9999端口
EXPOSE 9999
ENTRYPOINT ["java", "-jar", "app.jar"]



