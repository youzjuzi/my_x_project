package com.diy.sys.mapper.MenuAndRole;

import com.diy.sys.entity.MenuAndRole.RoleMenu;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import java.util.List;

/**
 * <p>
 *  Mapper 接口
 * </p>
 *
 * @author youzi
 * @since 2023-11-08
 */
public interface RoleMenuMapper extends BaseMapper<RoleMenu> {
    public List<Integer> getMenuIdsByRoleId(Integer roleId);
}
