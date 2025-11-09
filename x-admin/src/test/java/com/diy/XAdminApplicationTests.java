package com.diy;

import com.diy.sys.entity.User;
import com.diy.sys.mapper.UserMapper;
import com.diy.sys.service.IUserService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@SpringBootTest
class XAdminApplicationTests {

    @Resource
    private UserMapper userMapper;
    //  导入用户服务
    @Autowired
    private IUserService userService;

    //测试注册
    @Test
    void testRegister() {

        User newUser = new User();
        newUser.setUsername("testUse");
        newUser.setPassword("testPassword");
        newUser.setPhone("123456789");

        Map<String, Object> result = userService.register(newUser);

        // 检查是否插入成功
        System.out.printf("result: %s\n", result);

    }
    //测试登录
    @Test
    void testLogin() {
        User user = new User();
        user.setUsername("testUser3123");
        user.setPassword("testPassword");

        Map<String, Object> result = userService.login(user);

        // 检查是否登录成功
        System.out.printf("result: %s\n", result);
    }



    @Test
    void testMapper() {
        List<User> users = userMapper.selectList(null);
        users.forEach(System.out::println);
    }
    // 测试注册



}
