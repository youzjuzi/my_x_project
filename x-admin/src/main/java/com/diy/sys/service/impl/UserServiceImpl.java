package com.diy.sys.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.diy.common.utils.JwtUtil;
import com.diy.common.vo.Result;
import com.diy.sys.entity.Menu;
import com.diy.sys.entity.User;
import com.diy.sys.entity.UserActivityTime;
import com.diy.sys.entity.UserRole;
import com.diy.sys.mapper.UserActivityMapper;
import com.diy.sys.mapper.UserMapper;
import com.diy.sys.mapper.UserRoleMapper;
import com.diy.sys.service.IMenuService;
import com.diy.sys.service.IUserService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
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

    @Autowired
    private JwtUtil jwtUtil;
    @Autowired
    private RedisTemplate redisTemplate;
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
        //结果不为空并且密码和传入密码匹配，则需要生成token，并且用户信息存入redis
        if (loginUser != null && passwordEncoder.matches(user.getPassword(),loginUser.getPassword())){
            // 暂时用UUID, 终极方案是jwt
            //String key = "user:" + UUID.randomUUID();
            // 存入redis
            loginUser.setPassword(null);
            //redisTemplate.opsForValue().set(key,loginUser,30, TimeUnit.MINUTES);
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

//    @Override
//    public Map<String, Object> login(User user) {
//        //根据用户名与密码取查询
//        LambdaQueryWrapper<User> Wrapper = new LambdaQueryWrapper();
//        Wrapper.eq(User::getUsername,user.getUsername());
//        Wrapper.eq(User::getPassword,user.getPassword());
//        User loginUser = this.baseMapper.selectOne(Wrapper);
//        //结果不为空，则需要生成token，并且用户信息存入redis
//        if (loginUser != null){
//            // 暂时用UUID, 终极方案是jwt
//            String key = "user:" + UUID.randomUUID();
//
//            // 存入redis
//            loginUser.setPassword(null);
//            redisTemplate.opsForValue().set(key,loginUser,30, TimeUnit.MINUTES);
//
//            // 返回数据
//            Map<String, Object> data = new HashMap<>();
//            data.put("token",key);
//            return data;
//        }
//        return null;
//    }

    //根据token获取用户信息
    @Override
    public Map<String, Object> getUserInfo(String token) {
        //根据token获取用户信息，redis
        //Object obj = redisTemplate.opsForValue().get(token);
        User loginUser = null;
        try {
            loginUser = jwtUtil.parseToken(token, User.class);

        } catch (Exception e) {
            e.printStackTrace();
        }

        if (loginUser != null){
            //User loginUser = JSON.parseObject(JSON.toJSONString(obj),User.class);
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
        //redisTemplate.delete(token);
    }

    @Override
    @Transactional
    public void addUser(User user) {
        // 写入用户表
        this.baseMapper.insert(user);
        // 写入用户角色表
        List<Integer> roleIdList = user.getRoleIdList();
        if (roleIdList != null){
            for (Integer roleId : roleIdList) {
                userRoleMapper.insert(new UserRole(null,user.getId(),roleId));
            }
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

    @Override
    @Transactional
    public void updateUser(User user) {
        // 更新用户表
        this.baseMapper.updateById(user);
        // 删除原有角色
        LambdaQueryWrapper<UserRole> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserRole::getUserId,user.getId());
        userRoleMapper.delete(wrapper);
        // 设置新的角色
        List<Integer> roleIdList = user.getRoleIdList();
        if (roleIdList != null){
            for (Integer roleId : roleIdList) {
                userRoleMapper.insert(new UserRole(null,user.getId(),roleId));
            }
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

    @Override
    public Map<String, Object> getUserList(String username, String phone, Long pageNo, Long pageSize) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StringUtils.hasLength(username), User::getUsername, username);
        wrapper.eq(StringUtils.hasLength(phone), User::getPhone, phone);
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
}
