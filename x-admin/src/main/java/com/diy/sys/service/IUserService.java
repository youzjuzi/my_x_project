package com.diy.sys.service;

import com.diy.sys.entity.User;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.Map;

/**
 * <p>
 *  服务类
 * </p>
 *
 * @author youzi
 * @since 2023-09-02
 */
public interface IUserService extends IService<User> {

    //注册接口
    Map<String, Object> register(User user);

    Map<String, Object> login(User user);

    Map<String, Object> getUserInfo(String token);

    void logout(String token);

    void addUser(User user);

    User getUserById(Integer id);

    void updateUser(User user);

    void deleteUserById(Integer id);

    User getByUsername(String username);

    Map<String, Object> getUserList(String username, String phone, String email, Long pageNo, Long pageSize);
}
