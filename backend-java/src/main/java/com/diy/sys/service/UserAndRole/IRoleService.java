package com.diy.sys.service.UserAndRole;

import com.baomidou.mybatisplus.extension.service.IService;
import com.diy.sys.entity.UserAndRole.Role;

import java.util.Map;

public interface IRoleService extends IService<Role> {
    void addRole(Role role);

    Role getRoleById(Integer id);

    void updateRole(Role role);

    void deleteRoleById(Integer id);

    Map<String, Object> getRoleList(String roleName, Long pageNo, Long pageSize);
}
