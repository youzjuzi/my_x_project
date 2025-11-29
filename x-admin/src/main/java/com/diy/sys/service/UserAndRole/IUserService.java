package com.diy.sys.service.UserAndRole;

import com.diy.sys.entity.UserAndRole.User;
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

    String check(String username);

    /**
     * 修改密码
     * @param passwordMap 包含 token、oldPassword、newPassword 的 Map
     * @return 是否修改成功
     */
    Boolean changePassword(Map<String, String> passwordMap);

    /**
     * 更新手机号
     * @param phoneMap 包含 token、phone 的 Map
     * @return 是否更新成功
     */
    Boolean updatePhone(Map<String, String> phoneMap);

    /**
     * 更新邮箱
     * @param emailMap 包含 token、email 的 Map
     * @return 是否更新成功
     */
    Boolean updateEmail(Map<String, String> emailMap);

    /**
     * 更新头像
     * @param avatarMap 包含 token、avatar 的 Map
     * @return 是否更新成功
     */
    Boolean updateAvatar(Map<String, String> avatarMap);
}
