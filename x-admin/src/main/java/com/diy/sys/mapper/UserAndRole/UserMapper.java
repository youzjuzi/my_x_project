package com.diy.sys.mapper.UserAndRole;

import com.diy.sys.entity.UserAndRole.User;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import java.util.List;

/**
 * <p>
 *  Mapper 接口
 * </p>
 *
 * @author youzi
 * @since 2023-09-02
 */
public interface UserMapper extends BaseMapper<User> {


    public List<String> getRoleNameByUserId(Integer userId);

}
