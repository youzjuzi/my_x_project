package com.diy.sys.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.diy.sys.entity.Role;
import com.diy.sys.entity.User;

public interface IRoleService extends IService<Role> {
    void addRole(Role role);

    Role getRoleById(Integer id);

    void updateRole(Role role);

    void deleteRoleById(Integer id);
}
