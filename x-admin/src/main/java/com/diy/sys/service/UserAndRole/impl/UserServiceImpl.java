package com.diy.sys.service.UserAndRole.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.diy.common.utils.JwtUtil;
import com.diy.sys.entity.MenuAndRole.Menu;
import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.entity.UserAndRole.UserActivityTime;
import com.diy.sys.entity.UserAndRole.UserRole;
import com.diy.sys.mapper.UserAndRole.UserActivityMapper;
import com.diy.sys.mapper.UserAndRole.UserMapper;
import com.diy.sys.mapper.UserAndRole.UserRoleMapper;
import com.diy.sys.service.MenuAndRole.IMenuService;
import com.diy.sys.service.UserAndRole.IUserService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * <p>
 *  服务实现类
 * </p>
 *
 * @author youzi
 * @since 2023-09-02
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements IUserService {

    private static final Integer DEFAULT_ROLE_ID = 3;

    @Autowired
    private JwtUtil jwtUtil;
    @Autowired
    private PasswordEncoder passwordEncoder;
    @Autowired
    private UserRoleMapper userRoleMapper;
    @Autowired
    private IMenuService menuService;
    @Autowired
    private UserActivityMapper userActivityMapper;


    //注册
    @Override
    public Map<String, Object> register(User user) {
        // 检测用户名是否已经存在
        LambdaQueryWrapper<User> Wrapper = new LambdaQueryWrapper();
        Wrapper.eq(User::getUsername,user.getUsername());
        User existUser = this.baseMapper.selectOne(Wrapper);
        if (existUser != null){
            return null;
        }
        //密码加密
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        this.baseMapper.insert(user);
        // 默认分配普通用户角色
        userRoleMapper.insert(new UserRole(null, user.getId(), DEFAULT_ROLE_ID));
        Map<String,Object> data = new HashMap<>();
        data.put("name", user.getUsername());
        return data;
    }

    //登录
    @Override
    public Map<String, Object> login(User user) {
        //根据用户名查询
        LambdaQueryWrapper<User> Wrapper = new LambdaQueryWrapper();
        Wrapper.eq(User::getUsername,user.getUsername());
        User loginUser = this.baseMapper.selectOne(Wrapper);
        //结果不为空并且密码和传入密码匹配，则需要生成token
        if (loginUser != null && passwordEncoder.matches(user.getPassword(),loginUser.getPassword())){
            loginUser.setPassword(null);
            //创建jwt
            String token = jwtUtil.createToken(loginUser);
            // 记录登录时间
            UserActivityTime userActivityTime = new UserActivityTime();
            userActivityTime.setUserId(loginUser.getId());
            userActivityTime.setActivityTime(LocalDateTime.now());
            userActivityMapper.insert(userActivityTime);

            System.out.println(userActivityTime);
            // 返回数据
            Map<String, Object> data = new HashMap<>();
            data.put("token",token);

            return data;
        }
        return null;
    }

    //根据token获取用户信息
    @Override
    public Map<String, Object> getUserInfo(String token) {
        User loginUser = null;
        try {
            loginUser = jwtUtil.parseToken(token, User.class);

        } catch (Exception e) {
            e.printStackTrace();
        }

        if (loginUser != null){
            Map<String, Object> data = new HashMap<>();
            data.put("name",loginUser.getUsername());
            data.put("avatar",loginUser.getAvatar());

            //角色
            List<String> roleList = this.baseMapper.getRoleNameByUserId(loginUser.getId());
            data.put("roles",roleList);

            // 权限列表
            List<Menu> menuList = menuService.getMenuListByUserId(loginUser.getId());
            data.put("menuList",menuList);


            return data;

        }
        return null;
    }

    @Override
    public void logout(String token) {
        // JWT token 无需在服务端删除，客户端删除即可
    }

    @Override
    @Transactional
    public void addUser(User user) {
        // 写入用户表
        this.baseMapper.insert(user);
        // 写入用户角色表
        List<Integer> roleIdList = user.getRoleIdList();
        if (roleIdList == null || roleIdList.isEmpty()) {
            roleIdList = new ArrayList<>();
            roleIdList.add(DEFAULT_ROLE_ID);
        }
        for (Integer roleId : roleIdList) {
            userRoleMapper.insert(new UserRole(null, user.getId(), roleId));
        }
    }

    @Override
    public User getUserById(Integer id) {
        User user = this.baseMapper.selectById(id);

        LambdaQueryWrapper<UserRole> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserRole::getUserId,id);
        List<UserRole> userRoleList = userRoleMapper.selectList(wrapper);

        List<Integer> roleIdList = userRoleList.stream().map(UserRole::getRoleId).collect(Collectors.toList());

        user.setRoleIdList(roleIdList);
        return user;
    }

    // 修改用户
    @Override
    @Transactional
    public void updateUser(User user) {
        if(user.getPassword() == null) {
            // 使用update(wrapper)方法排除密码字段
            UpdateWrapper<User> updateWrapper = new UpdateWrapper<>();
            updateWrapper.eq("id", user.getId());
            updateWrapper.set("username", user.getUsername());
            updateWrapper.set("email", user.getEmail());
            updateWrapper.set("phone", user.getPhone());
            updateWrapper.set("status", user.getStatus());
            updateWrapper.set("avatar", user.getAvatar());
            // 不设置password字段
            this.update(updateWrapper);
        } else {
            user.setPassword(passwordEncoder.encode(user.getPassword()));
            // 更新用户表
            this.baseMapper.updateById(user);
        }
        // 删除原有角色
        LambdaQueryWrapper<UserRole> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserRole::getUserId,user.getId());

        userRoleMapper.delete(wrapper);
        // 设置新的角色
        List<Integer> roleIdList = user.getRoleIdList();
        if (roleIdList == null || roleIdList.isEmpty()) {
            roleIdList = new ArrayList<>();
            roleIdList.add(DEFAULT_ROLE_ID);
        }
        for (Integer roleId : roleIdList) {
            userRoleMapper.insert(new UserRole(null,user.getId(),roleId));
        }
    }

    @Override
    public void deleteUserById(Integer id) {
        this.baseMapper.deleteById(id);
        // 删除原有角色
        LambdaQueryWrapper<UserRole> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserRole::getUserId,id);
        userRoleMapper.delete(wrapper);
    }

    @Override
    public User getByUsername(String username) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username);
        return this.getOne(wrapper);
    }


    // 获取用户列表，包括角色和权限
    @Override
    public Map<String, Object> getUserList(String username, String phone, String email, Long pageNo, Long pageSize) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.hasLength(username), User::getUsername, username);
        wrapper.like(StringUtils.hasLength(phone), User::getPhone, phone);
        wrapper.like(StringUtils.hasLength(email), User::getEmail, email);
        wrapper.orderByAsc(User::getId);
        Page<User> page = new Page<>(pageNo, pageSize);
        this.page(page, wrapper);

        List<User> records = page.getRecords();
        if (records != null && !records.isEmpty()) {
            List<Integer> userIds = records.stream()
                    .map(User::getId)
                    .collect(Collectors.toList());

            LambdaQueryWrapper<UserRole> roleWrapper = new LambdaQueryWrapper<>();
            roleWrapper.in(UserRole::getUserId, userIds);
            List<UserRole> userRoles = userRoleMapper.selectList(roleWrapper);

            Map<Integer, List<Integer>> userRoleMap = userRoles.stream()
                    .collect(Collectors.groupingBy(UserRole::getUserId,
                            Collectors.mapping(UserRole::getRoleId, Collectors.toList())));

            records.forEach(user -> {
                List<Integer> roleIdList = userRoleMap.get(user.getId());
                user.setRoleIdList(roleIdList);
            });
        }
        Map<String, Object> data = new HashMap<>();
        data.put("total", page.getTotal());
        data.put("row", records);
        return data;
    }

    // 检测用户名
    @Override
    public String check(String username) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username);
        return this.count(wrapper) > 0 ? "0" : "1";
    }

    /**
     * 修改密码
     * @param passwordMap 包含 token、oldPassword、newPassword 的 Map
     * @return 是否修改成功
     */
    @Override
    @Transactional
    public Boolean changePassword(Map<String, String> passwordMap) {
        String token = passwordMap.get("token");
        String oldPassword = passwordMap.get("oldPassword");
        String newPassword = passwordMap.get("newPassword");

        if (token == null || oldPassword == null || newPassword == null) {
            throw new RuntimeException("参数不完整");
        }

        // 1. 根据 token 解析用户信息
        User loginUser = null;
        try {
            loginUser = jwtUtil.parseToken(token, User.class);
        } catch (Exception e) {
            throw new RuntimeException("Token 无效，请重新登录");
        }

        if (loginUser == null || loginUser.getId() == null) {
            throw new RuntimeException("用户信息无效");
        }

        // 2. 从数据库获取用户信息
        User dbUser = this.getById(loginUser.getId());
        if (dbUser == null) {
            throw new RuntimeException("用户不存在");
        }

        // 3. 验证旧密码是否正确
        if (!passwordEncoder.matches(oldPassword, dbUser.getPassword())) {
            throw new RuntimeException("旧密码错误");
        }

        // 4. 验证新密码不能与旧密码相同
        if (passwordEncoder.matches(newPassword, dbUser.getPassword())) {
            throw new RuntimeException("新密码不能与旧密码相同");
        }

        // 5. 加密新密码并更新
        String encodedNewPassword = passwordEncoder.encode(newPassword);
        UpdateWrapper<User> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("id", dbUser.getId());
        updateWrapper.set("password", encodedNewPassword);
        boolean success = this.update(updateWrapper);

        return success;
    }

    /**
     * 更新手机号
     * @param phoneMap 包含 token、phone 的 Map
     * @return 是否更新成功
     */
    @Override
    @Transactional
    public Boolean updatePhone(Map<String, String> phoneMap) {
        String token = phoneMap.get("token");
        String phone = phoneMap.get("phone");

        if (token == null || phone == null || phone.trim().isEmpty()) {
            throw new RuntimeException("参数不完整");
        }

        // 1. 根据 token 解析用户信息
        User loginUser = null;
        try {
            loginUser = jwtUtil.parseToken(token, User.class);
        } catch (Exception e) {
            throw new RuntimeException("Token 无效，请重新登录");
        }

        if (loginUser == null || loginUser.getId() == null) {
            throw new RuntimeException("用户信息无效");
        }

        // 2. 验证手机号格式（简单验证：11位数字）
        if (!phone.matches("^1[3-9]\\d{9}$")) {
            throw new RuntimeException("手机号格式不正确");
        }

        // 3. 更新手机号
        UpdateWrapper<User> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("id", loginUser.getId());
        updateWrapper.set("phone", phone);
        return this.update(updateWrapper);
    }

    /**
     * 更新邮箱
     * @param emailMap 包含 token、email 的 Map
     * @return 是否更新成功
     */
    @Override
    @Transactional
    public Boolean updateEmail(Map<String, String> emailMap) {
        String token = emailMap.get("token");
        String email = emailMap.get("email");

        if (token == null || email == null || email.trim().isEmpty()) {
            throw new RuntimeException("参数不完整");
        }

        // 1. 根据 token 解析用户信息
        User loginUser = null;
        try {
            loginUser = jwtUtil.parseToken(token, User.class);
        } catch (Exception e) {
            throw new RuntimeException("Token 无效，请重新登录");
        }

        if (loginUser == null || loginUser.getId() == null) {
            throw new RuntimeException("用户信息无效");
        }

        // 2. 验证邮箱格式
        if (!email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")) {
            throw new RuntimeException("邮箱格式不正确");
        }

        // 3. 更新邮箱
        UpdateWrapper<User> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("id", loginUser.getId());
        updateWrapper.set("email", email);
        return this.update(updateWrapper);
    }

    /**
     * 更新头像
     * @param avatarMap 包含 token、avatar 的 Map
     * @return 是否更新成功
     */
    @Override
    @Transactional
    public Boolean updateAvatar(Map<String, String> avatarMap) {
        String token = avatarMap.get("token");
        String avatar = avatarMap.get("avatar");

        if (token == null || avatar == null || avatar.trim().isEmpty()) {
            throw new RuntimeException("参数不完整");
        }

        // 1. 根据 token 解析用户信息
        User loginUser = null;
        try {
            loginUser = jwtUtil.parseToken(token, User.class);
        } catch (Exception e) {
            throw new RuntimeException("Token 无效，请重新登录");
        }

        if (loginUser == null || loginUser.getId() == null) {
            throw new RuntimeException("用户信息无效");
        }

        // 2. 更新头像
        UpdateWrapper<User> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("id", loginUser.getId());
        updateWrapper.set("avatar", avatar);
        return this.update(updateWrapper);
    }
}
