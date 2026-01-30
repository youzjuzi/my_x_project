# 手语交流平台管理系统

> 一个基于 Vue 3 + Spring Boot 的手语学习与交流平台，支持题库管理、挑战模式、用户权限管理等功能。

## 📋 项目简介

本项目是一个完整的前后端分离管理系统，旨在为手语学习者提供交互式学习平台。系统包含题库管理、挑战闯关、用户管理、权限控制等核心功能模块。

### 核心功能

- 🎯 **题库管理**：支持单词、中文、数字等多种题型，自动生成拼音
- 📚 **题集管理**：将题目组织成主题题集，支持难度分级
- 🏆 **挑战模式**：用户可以参与闯关挑战，记录挑战历史
- 👥 **用户管理**：完整的用户注册、登录、权限控制
- 🔐 **角色权限**：基于 RBAC 的细粒度权限管理
- 📊 **数据统计**：用户学习进度追踪、挑战记录

---

## 🏗️ 项目结构

```
my_x_project/
├── web-vue3/              # 前端项目（Vue 3）
│   ├── src/
│   │   ├── api/           # API 接口定义
│   │   ├── components/    # 公共组件
│   │   ├── layout/        # 布局组件
│   │   ├── router/        # 路由配置
│   │   ├── store/         # Pinia 状态管理
│   │   ├── utils/         # 工具函数
│   │   └── views/         # 页面组件
│   │       └── sys/       # 系统管理模块
│   │           ├── user/          # 用户管理
│   │           ├── role/          # 角色管理
│   │           ├── menu/          # 菜单管理
│   │           ├── question_set/  # 题库管理
│   │           ├── question_bank/ # 题集管理
│   │           └── challenge/     # 挑战管理
│   ├── public/            # 静态资源
│   └── vite.config.ts     # Vite 配置
│
├── x-admin/               # 后端项目（Spring Boot）
│   ├── src/main/
│   │   ├── java/com/diy/
│   │   │   ├── controller/   # 控制器
│   │   │   ├── service/      # 业务逻辑层
│   │   │   ├── mapper/       # 数据访问层
│   │   │   ├── entity/       # 实体类
│   │   │   ├── config/       # 配置类
│   │   │   └── utils/        # 工具类
│   │   └── resources/
│   │       ├── application.yml  # 应用配置
│   │       └── mapper/          # MyBatis XML 映射
│   └── pom.xml            # Maven 依赖配置
│
└── README.md              # 本文档
```

---

## 💻 技术栈

### 前端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.x | 渐进式 JavaScript 框架 |
| Element Plus | 2.10.5 | Vue 3 组件库 |
| Vite | 最新 | 下一代前端构建工具 |
| Pinia | 2.3.1 | Vue 状态管理 |
| Axios | 1.11.0 | HTTP 客户端 |
| Vue Router | 最新 | 路由管理 |
| ECharts | 5.6.0 | 数据可视化 |
| Pinyin-Pro | 3.27.0 | 中文转拼音 |
| TypeScript | 最新 | 类型安全 |

### 后端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Spring Boot | 3.4.11 | 企业级应用框架 |
| JDK | 17 | Java 开发环境 |
| MyBatis Plus | 3.5.7 | 增强版 ORM 框架 |
| MySQL | 8.0+ | 关系型数据库 |
| Redis | 最新 | 缓存数据库 |
| Spring Security | 最新 | 安全框架 |
| JWT | 0.12.5 | 身份认证 |
| SpringDoc OpenAPI | 2.3.0 | API 文档 |
| Pinyin4j | 2.5.1 | 中文转拼音 |
| HikariCP | 默认 | 数据库连接池 |

---

## 🚀 快速开始

### 环境要求

- **Node.js**: 16.0 或更高版本
- **Java**: JDK 17
- **MySQL**: 8.0+
- **Redis**: 最新稳定版
- **Maven**: 3.6+

### 1. 数据库配置

#### 导入数据库

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入 SQL 文件
mysql -u root -p your_database_name < _localhost-2026_01_27_13_38_25-dump.sql
```

#### 修改后端配置

编辑 `x-admin/src/main/resources/application.yml`：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/your_database_name?useUnicode=true&characterEncoding=utf-8
    username: your_username
    password: your_password
```

### 2. 启动 Redis

```bash
# Windows
cd path\to\redis
redis-server.exe

# 或使用项目提供的脚本
redis.bat
```

### 3. 启动后端服务

```bash
cd x-admin

# 使用 Maven 启动
mvn spring-boot:run

# 或使用 IDE 直接运行 XAdminApplication 主类
```

后端服务启动后访问：`http://localhost:8080`

**API 文档：** `http://localhost:8080/swagger-ui/index.html`

### 4. 启动前端服务

```bash
cd web-vue3

# 安装依赖
npm install

# 启动开发服务器（连接生产环境后端）
npm run dev:prod

# 或连接测试环境
npm run dev:test
```

前端服务启动后访问：`http://localhost:8001`

---

## 📦 项目部署

### 前端打包

```bash
cd web-vue3

# 构建生产环境
npm run build:prod

# 构建测试环境
npm run build:test
```

打包后的文件在 `web-vue3/dist/` 目录。

### 后端打包

```bash
cd x-admin

# 使用 Maven 打包
mvn clean package

# 生成的 JAR 文件在 target/ 目录
java -jar target/x-admin-0.0.1-SNAPSHOT.jar
```

---

### Docker 部署

本项目的 Docker 环境已预置以下优化：
- **后端镜像**：配置阿里云 Maven 镜像加速依赖下载，解决国内网络构建超时问题。
- **前端镜像**：配置 npm 淘宝镜像加速构建。

#### 常用命令

```bash
# 一键构建并启动服务（推荐）
docker compose up -d --build

# 查看实时日志
docker compose logs -f

# 停止并移除容器
docker compose down
```

#### 常见问题

**端口冲突 (9999)**
启动时若出现 `bind: address already in use` 错误，通常是因为本地 IDE 或终端已运行了后端服务。
解决方案：
1. 停止本地运行的 Java 进程（检查占用端口：`lsof -i :9999`）。
2. 或修改 `docker-compose.yml` 中的映射端口（例如修改为 `9998:9999`）。

---

## 🎯 功能模块详解

### 1. 用户管理

- 用户注册、登录、登出
- 用户信息管理（头像、邮箱、电话等）
- 用户状态控制（启用/禁用）
- 密码加密存储

### 2. 角色权限管理

- 角色创建与编辑
- 菜单权限分配
- 基于 RBAC 的权限控制
- 动态路由生成

### 3. 菜单管理

- 菜单树形结构管理
- 支持多级菜单嵌套
- 菜单图标配置（支持本地 SVG 和外部图标）
- 菜单状态控制（显示/隐藏）

### 4. 题库管理

- 题目类型：单词、中文、数字
- 难度分级：简单、中等、困难
- 自动生成中文拼音
- 关卡体系（1-100 关）
- 图片支持

### 5. 题集管理

- 将题目组织成主题题集
- 题集封面设置
- 题集状态控制
- 题目关联管理

### 6. 挑战系统

- 用户闯关挑战
- 挑战历史记录
- 挑战模式选择
- 挑战状态追踪

---

## 🔐 权限说明

系统采用 **基于角色的访问控制（RBAC）** 模型：

```
用户 (User) → 角色 (Role) → 菜单权限 (Menu)
```

- **超级管理员**：拥有所有权限
- **普通管理员**：可管理题库、题集、用户
- **普通用户**：仅可参与挑战、查看个人信息

---

## 🛠️ 开发指南

### 前端开发

#### 添加新页面

1. 在 `src/views/` 下创建页面组件
2. 在数据库 `menu` 表中添加菜单记录
3. 组件必须使用 `defineOptions` 定义 `name`（与路由 name 一致）

```vue
<script setup lang="ts">
defineOptions({
  name: 'yourRouteName' // ⚠️ 必须与路由 name 完全一致
})
</script>
```

#### keep-alive 缓存机制

系统使用 `keep-alive` 缓存页面组件，避免重复请求：

- 组件 `name` 必须与路由 `name` 匹配
- 缓存列表由 `store/tagsView.ts` 管理
- 详见：[walkthrough.md](file:///C:/Users/zyc/.gemini/antigravity/brain/f60e2ad5-9c37-4c62-b4c9-6591582e4430/walkthrough.md)

### 后端开发

#### 添加新接口

1. 在 `controller/` 下创建控制器
2. 在 `service/` 实现业务逻辑
3. 在 `mapper/` 定义数据访问接口
4. 在 `resources/mapper/` 编写 MyBatis XML 映射

#### 数据库连接池配置

HikariCP 配置位于 `application.yml`：

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 5      # 最大连接数
      minimum-idle: 2           # 最小空闲连接数
      connection-timeout: 20000  # 连接超时（毫秒）
```

---

## 🎨 自定义配置

### 修改网站标题

编辑 `web-vue3/src/settings.ts`：

```typescript
const settings = {
  title: '手语交流平台',  // 修改网站标题
  // ...
};
```

### 修改网站图标

替换 `web-vue3/public/favicon.ico` 文件。

详见：[browser-title-icon-config.md](file:///C:/Users/zyc/.gemini/antigravity/brain/f60e2ad5-9c37-4c62-b4c9-6591582e4430/browser-title-icon-config.md)

---

## 🐛 常见问题

### 1. 前端无法访问后端接口

**原因：** CORS 跨域问题

**解决：** 检查后端 `application.yml` 中的 CORS 配置

### 2. keep-alive 缓存不生效

**原因：** 组件 `name` 与路由 `name` 不匹配

**解决：** 确保 `defineOptions({ name: 'xxx' })` 中的 name 与数据库菜单表中的 `name` 字段一致

### 3. 数据库连接失败

**原因：** 数据源配置错误或数据库未启动

**解决：** 检查 `application.yml` 中的数据库配置

### 4. Redis 连接失败

**原因：** Redis 服务未启动

**解决：** 启动 Redis 服务

```bash
# Windows
redis-server.exe

# Linux/Mac
redis-server
```

---

## 📝 开发规范

### 代码风格

- 前端：遵循 ESLint 规范
- 后端：遵循阿里巴巴 Java 开发规范

### Git 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具链相关
```

---

## 📄 许可证

本项目仅用于学习交流，请勿用于商业用途。

---

## 🙏 致谢

- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [Spring Boot](https://spring.io/projects/spring-boot)
- [MyBatis Plus](https://baomidou.com/)

---

## 📞 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

**最后更新：** 2026-01-27
