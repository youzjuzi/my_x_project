# Spring Security 迁移指南

## 当前状态

✅ **已完成的基础配置**：
1. Spring Security 依赖已添加
2. 安全配置类已创建
3. JWT 认证过滤器已实现
4. 用户详情服务已实现（加载角色和菜单权限）
5. 权限评估器已创建（支持菜单权限检查）
6. 异常处理器已配置

## 迁移步骤（逐步进行）

### 第一步：测试基础认证（当前阶段）

1. **启动应用**，验证以下功能：
   - ✅ 公开接口（/user/login, /user/register）可以正常访问
   - ✅ 需要认证的接口会要求 Token
   - ✅ Token 无效时返回 401
   - ✅ 权限不足时返回 403

2. **测试 JWT 认证**：
   ```bash
   # 1. 登录获取 Token
   POST /user/login
   {
     "username": "admin",
     "password": "123456"
   }
   
   # 2. 使用 Token 访问需要认证的接口
   GET /challenge/history?pageNo=1&pageSize=10
   Headers: X-Token: <your-token>
   ```

### 第二步：在 Controller 中添加方法级安全注解

#### 示例1：管理员接口（基于角色）

```java
@RestController
@RequestMapping("/challenge/admin")
public class ChallengeAdminController {
    
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/list")
    public Result<?> getAllChallengeHistory() {
        // 只有 ADMIN 角色可以访问
    }
}
```

#### 示例2：基于菜单权限

```java
@RestController
@RequestMapping("/user")
public class UserController {
    
    @PreAuthorize("hasPermission('/sys/user', 'MENU')")
    @GetMapping("/list")
    public Result<?> getUserList() {
        // 只有拥有 /sys/user 菜单权限的用户可以访问
    }
}
```

#### 示例3：组合条件

```java
@PreAuthorize("hasRole('ADMIN') and hasPermission('/sys/role', 'MENU')")
@PutMapping("/role")
public Result<?> updateRole() {
    // 需要 ADMIN 角色且拥有菜单权限
}
```

### 第三步：逐步迁移各个 Controller

建议按以下顺序迁移：

1. **挑战管理接口** (`ChallengeController`)
   - `/challenge/admin/**` - 添加 `@PreAuthorize("hasRole('ADMIN')")`
   
2. **用户管理接口** (`UserController`)
   - `/user/**` - 添加 `@PreAuthorize("hasPermission('/sys/user', 'MENU')")`
   
3. **角色管理接口** (`RoleController`)
   - `/role/**` - 添加 `@PreAuthorize("hasPermission('/sys/role', 'MENU')")`
   
4. **菜单管理接口** (`MenuController`)
   - `/menu/**` - 添加 `@PreAuthorize("hasPermission('/sys/menu', 'MENU')")`
   
5. **题库管理接口** (`QuestionSetController`)
   - `/questionSet/**` - 添加 `@PreAuthorize("hasPermission('/sys/question_set', 'MENU')")`
   
6. **题目管理接口** (`ChallengeController` 中的题目相关接口)
   - `/challenge/question/**` - 添加 `@PreAuthorize("hasPermission('/sys/question_bank', 'MENU')")`

### 第四步：调整路径匹配规则

在 `SecurityConfig.java` 中，可以根据实际需求调整路径匹配：

```java
.authorizeHttpRequests(auth -> auth
    // 公开接口
    .requestMatchers("/user/login", "/user/register", "/captcha").permitAll()
    
    // 需要认证的接口（具体权限由方法级注解控制）
    .anyRequest().authenticated()
)
```

### 第五步：禁用旧的拦截器（可选）

当 Spring Security 完全启用后，可以禁用旧的拦截器：

```java
// MyInterceptorConfig.java
@Override
public void addInterceptors(InterceptorRegistry registry) {
    // 暂时保留，但拦截器内部已经返回 true，不进行拦截
    // 等 Spring Security 稳定后，可以完全移除
}
```

## 菜单路径与 API 路径的映射

确保数据库中的菜单路径与 API 路径一致：

| 菜单路径 | API 路径 | 权限标识 |
|---------|---------|---------|
| `/sys/user` | `/user/**` | `MENU_/sys/user` |
| `/sys/role` | `/role/**` | `MENU_/sys/role` |
| `/sys/menu` | `/menu/**` | `MENU_/sys/menu` |
| `/sys/question_bank` | `/challenge/question/**` | `MENU_/sys/question_bank` |
| `/sys/question_set` | `/questionSet/**` | `MENU_/sys/question_set` |
| `/sys/challange` | `/challenge/admin/**` | `MENU_/sys/challange` |

## 常见问题

### Q1: 如何获取当前登录用户？
```java
// 方式1：从 SecurityContext
Authentication auth = SecurityContextHolder.getContext().getAuthentication();
String username = auth.getName();

// 方式2：从方法参数
@GetMapping("/info")
public Result<?> getInfo(@AuthenticationPrincipal UserDetails userDetails) {
    // 使用 userDetails
}
```

### Q2: 如何检查用户是否有某个权限？
```java
Authentication auth = SecurityContextHolder.getContext().getAuthentication();
boolean hasPermission = auth.getAuthorities().stream()
    .anyMatch(a -> a.getAuthority().equals("MENU_/sys/user"));
```

### Q3: 如何动态检查权限？
使用 `@PreAuthorize` 注解：
```java
@PreAuthorize("hasPermission(#menuPath, 'MENU')")
public Result<?> checkMenu(String menuPath) {
    // ...
}
```

## 测试清单

- [ ] 公开接口可以正常访问（不需要 Token）
- [ ] 需要认证的接口在无 Token 时返回 401
- [ ] 有效 Token 可以正常访问接口
- [ ] 无效 Token 返回 401
- [ ] 权限不足时返回 403
- [ ] 角色权限控制正常工作
- [ ] 菜单权限控制正常工作
- [ ] 现有功能不受影响

## 注意事项

1. **逐步迁移**：不要一次性在所有接口上添加安全注解，先测试几个接口
2. **路径一致性**：确保菜单路径与 API 路径匹配
3. **角色名称**：确保数据库中的角色名称正确（会转换为 ROLE_XXX 格式）
4. **日志监控**：关注认证和授权失败的日志
5. **回滚方案**：如果出现问题，可以暂时禁用 Spring Security（注释掉 @EnableWebSecurity）

