package com.diy.sys.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.diy.sys.entity.Role;
import com.diy.sys.entity.RoleMenu;
import com.diy.sys.mapper.RoleMapper;
import com.diy.sys.mapper.RoleMenuMapper;
import com.diy.sys.service.IRoleService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;


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
}
