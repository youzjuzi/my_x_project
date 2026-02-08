package com.diy.sys.service.MenuAndRole.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.diy.sys.entity.MenuAndRole.Menu;
import com.diy.sys.mapper.MenuAndRole.MenuMapper;
import com.diy.sys.service.MenuAndRole.IMenuCacheService;
import com.diy.sys.service.MenuAndRole.IMenuService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * <p>
 * 服务实现类
 * </p>
 *
 * @author youzi
 * @since 2023-11-08
 */
@Service
public class MenuServiceImpl extends ServiceImpl<MenuMapper, Menu> implements IMenuService {

    @Autowired
    private IMenuCacheService menuCacheService;

    @Override
    public List<Menu> getAllMenu() {
        // 查询一级菜单
        LambdaQueryWrapper<Menu> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Menu::getParentId, 0);
        List<Menu> list = this.list(wrapper);
        // 填充二级菜单
        setMenuChildren(list);

        return list;
    }

    @Override
    public List<Menu> getMenuListByUserId(Integer userId) {
        // 优先从 Redis 缓存获取
        List<Menu> cachedMenuList = menuCacheService.getMenuTree(userId);
        if (cachedMenuList != null) {
            System.out.println("从 Redis 缓存获取菜单树 - userId: " + userId);
            return cachedMenuList;
        }

        System.out.println("从数据库查询菜单树 - userId: " + userId);
        // 一级菜单
        List<Menu> menuList = this.baseMapper.getMenuListByUserId(userId, 0);
        // 子菜单
        setMenuChildrenByUserId(userId, menuList);

        // 存入 Redis 缓存
        menuCacheService.saveMenuTree(userId, menuList);

        return menuList;
    }

    private void setMenuChildrenByUserId(Integer userId, List<Menu> menuList) {
        if (menuList != null) {
            for (Menu menu : menuList) {
                List<Menu> subMenuList = this.baseMapper.getMenuListByUserId(userId, menu.getMenuId());
                menu.setChildren(subMenuList);
                setMenuChildrenByUserId(userId, subMenuList);
            }
        }
    }

    private void setMenuChildren(List<Menu> list) {
        if (list != null) {
            for (Menu menu : list) {
                LambdaQueryWrapper<Menu> subWrapper = new LambdaQueryWrapper<>();
                subWrapper.eq(Menu::getParentId, menu.getMenuId());
                List<Menu> subList = this.list(subWrapper);
                menu.setChildren(subList);
                // 递归
                setMenuChildren(subList);
            }
        }
    }
}
