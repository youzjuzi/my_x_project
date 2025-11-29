# Spring Security 安全策略文档

## 概述

本项目已集成 Spring Security，实现了基于 JWT 的无状态认证和基于角色的访问控制（RBAC）。

## 安全架构

### 1. 认证机制
- **JWT Token 认证**：使用自定义的 `JwtAuthenticationFilter` 从请求头 `X-Token` 中提取 Token
- **无状态会话**：使用 `SessionCreationPolicy.STATELESS`，不创建服务器端会话

### 2. 授权机制
- **角色授权**：基于用户角色（ROLE_ADMIN, ROLE_USER 等）
- **菜单权限授权**：基于用户可访问的菜单路径（MENU_/path 格式）

### 3. 权限加载流程
1. 用户登录后，前端获取 JWT Token
2. 每次请求携带 Token 在 `X-Token` 请求头中
3. `JwtAuthenticationFilter` 提取并验证 Token
4. `CustomUserDetailsService` 加载用户角色和菜单权限
5. Spring Security 根据权限决定是否允许访问

## 配置说明

### 公开访问的接口
以下接口不需要认证即可访问：
- `/user/login` - 用户登录
- `/user/register` - 用户注册
- `/captcha` - 验证码
- `/error` - 错误页面
- `/swagger-ui/**` - Swagger UI
- `/v3/**` - OpenAPI 文档

### 需要认证的接口
所有其他接口都需要携带有效的 JWT Token。

## 使用方法

### 1. 在 Controller 中使用方法级安全

#### 基于角色的控制
```java
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/admin/users")
public Result<?> getUsers() {
    // 只有 ADMIN 角色可以访问
}

@PreAuthorize("hasAnyRole('ADMIN', 'USER')")
@GetMapping("/common/data")
public Result<?> getData() {
    // ADMIN 或 USER 都可以访问
}
```

#### 基于菜单权限的控制
```java
@PreAuthorize("hasPermission('/sys/user', 'MENU')")
@GetMapping("/user/list")
public Result<?> getUserList() {
    // 只有拥有 /sys/user 菜单权限的用户可以访问
}

@PreAuthorize("hasPermission('/challenge/admin/list', 'MENU')")
@GetMapping("/challenge/admin/list")
public Result<?> getChallengeList() {
    // 只有拥有该菜单权限的用户可以访问
}
```

### 2. 获取当前认证用户

```java
@Autowired
private Authentication authentication;

@GetMapping("/current")
public Result<?> getCurrentUser() {
    // 方式1：从 SecurityContext 获取
    Authentication auth = SecurityContextHolder.getContext().getAuthentication();
    String username = auth.getName();
    
    // 方式2：从方法参数注入
    @AuthenticationPrincipal UserDetails userDetails
    // 或
    Authentication authentication
    
    return Result.success(userDetails);
}
```

## 权限格式

### 角色权限
- 格式：`ROLE_角色名称`
- 示例：`ROLE_ADMIN`, `ROLE_USER`
- 来源：数据库 `x_role` 表的 `role_name` 字段

### 菜单权限
- 格式：`MENU_菜单路径`
- 示例：`MENU_/sys/user`, `MENU_/challenge/admin/list`
- 来源：数据库 `x_menu` 表的 `path` 字段，通过 `x_role_menu` 关联

## 安全建议

1. **逐步启用**：建议先在测试环境验证，确认无误后再启用
2. **路径匹配**：确保菜单路径与 API 路径一致
3. **角色管理**：合理分配角色和菜单权限
4. **Token 安全**：确保 JWT 密钥安全，定期更换
5. **日志记录**：已记录认证和授权失败日志，便于排查

## 迁移步骤

1. ✅ 添加 Spring Security 依赖
2. ✅ 创建安全配置类
3. ✅ 创建 JWT 认证过滤器
4. ✅ 创建用户详情服务
5. ✅ 创建权限评估器
6. ⏳ 逐步在 Controller 中添加方法级安全注解
7. ⏳ 测试验证
8. ⏳ 启用拦截器（可选，Spring Security 已提供认证）

## 注意事项

1. **与现有拦截器的关系**：
   - 当前 `JwtValidateInterceptor` 被注释掉了
   - Spring Security 的 `JwtAuthenticationFilter` 已提供认证功能
   - 建议保留拦截器配置，但可以禁用拦截器

2. **CORS 配置**：
   - Spring Security 的 CORS 配置会覆盖 `MyCorsConfig`
   - 已在 `SecurityConfig` 中配置 CORS

3. **密码编码**：
   - 使用 BCrypt 密码编码器
   - 确保用户密码使用 BCrypt 加密存储

4. **异常处理**：
   - 未认证：返回 401，消息 "登录信息无效或已过期，请重新登录"
   - 权限不足：返回 403，消息 "权限不足，无法访问该资源"

