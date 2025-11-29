package com.diy.sys.service.UserAndRole.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.diy.sys.entity.UserAndRole.Role;
import com.diy.sys.entity.MenuAndRole.RoleMenu;
import com.diy.sys.mapper.UserAndRole.RoleMapper;
import com.diy.sys.mapper.MenuAndRole.RoleMenuMapper;
import com.diy.sys.service.UserAndRole.IRoleService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.HashMap;
import java.util.List;
import java.util.Map;


@Service
public class RoleServiceImpl extends ServiceImpl<RoleMapper, Role> implements IRoleService {

    @Autowired
    private RoleMenuMapper roleMenuMapper;
    @Override
    // 事务处理
    @Transactional
    public void addRole(Role role) {
        // 写入角色表
        this.baseMapper.insert(role);
        //写入角色权限表
        if(null != role.getMenuIdList()){
            for (Integer menuId : role.getMenuIdList()) {
                roleMenuMapper.insert(new RoleMenu(null,role.getRoleId(),menuId));
            }
        }

    }

    @Override
    public Role getRoleById(Integer id) {
        Role role = this.baseMapper.selectById(id);
        //查询角色权限
        List<Integer> menuIdsList = roleMenuMapper.getMenuIdsByRoleId(id);
        role.setMenuIdList(menuIdsList);
        return role;
    }

    // 更新角色
    @Override
    @Transactional
    public void updateRole(Role role) {
        // 修改角色表
        this.baseMapper.updateById(role);
        // 删除原有权限
        LambdaQueryWrapper<RoleMenu> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(RoleMenu::getRoleId,role.getRoleId());
        roleMenuMapper.delete(wrapper);
        // 新增权限
        if(null != role.getMenuIdList()){
            for (Integer menuId : role.getMenuIdList()) {
                roleMenuMapper.insert(new RoleMenu(null,role.getRoleId(),menuId));
            }
        }
    }

    @Override
    @Transactional
    public void deleteRoleById(Integer id) {
        this.baseMapper.deleteById(id);
        // 删除原有权限
        LambdaQueryWrapper<RoleMenu> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(RoleMenu::getRoleId,id);
        roleMenuMapper.delete(wrapper);
    }

    @Override
    public Map<String, Object> getRoleList(String roleName, Long pageNo, Long pageSize) {
         LambdaQueryWrapper<Role> wrapper = new LambdaQueryWrapper<>();
         wrapper.like(StringUtils.hasLength(roleName), Role::getRoleName, roleName);
         wrapper.orderByDesc(Role::getRoleId);

         Page<Role> page = new Page<>(pageNo, pageSize);
         this.page(page, wrapper);

         Map<String, Object> data = new HashMap<>();
         data.put("total", page.getTotal());
         data.put("rows", page.getRecords());

         return data;
    }
}
