package com.diy.security.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.diy.sys.entity.MenuAndRole.Menu;
import com.diy.sys.entity.UserAndRole.Role;
import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.entity.UserAndRole.UserRole;
import com.diy.sys.mapper.MenuAndRole.RoleMenuMapper;
import com.diy.sys.mapper.UserAndRole.RoleMapper;
import com.diy.sys.mapper.UserAndRole.UserRoleMapper;
import com.diy.sys.service.MenuAndRole.IMenuService;
import com.diy.sys.service.UserAndRole.IUserService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 自定义用户详情服务
 * 
 * 功能：
 * 1. 根据用户ID加载用户信息
 * 2. 加载用户的角色
 * 3. 加载用户可访问的菜单路径（作为权限）
 * 4. 构建 Spring Security UserDetails 对象
 * 
 * @author youzi
 * @since 2024
 */
@Slf4j
@Service
public class CustomUserDetailsService implements UserDetailsService {

    @Autowired
    private IUserService userService;

    @Autowired
    private UserRoleMapper userRoleMapper;

    @Autowired
    private RoleMenuMapper roleMenuMapper;

    @Autowired
    private RoleMapper roleMapper;

    @Autowired
    private IMenuService menuService;

    /**
     * 根据用户名加载用户（Spring Security 标准方法）
     * 本项目使用用户ID，所以这个方法可以委托给 loadUserByUserId
     */
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userService.getByUsername(username);
        if (user == null) {
            throw new UsernameNotFoundException("用户不存在: " + username);
        }
        return loadUserByUserId(user.getId());
    }

    /**
     * 根据用户ID加载用户详情（自定义方法）
     * 
     * @param userId 用户ID
     * @return UserDetails
     */
    public UserDetails loadUserByUserId(Integer userId) {
        // 1. 加载用户基本信息
        User user = userService.getUserById(userId);
        if (user == null) {
            throw new UsernameNotFoundException("用户不存在: " + userId);
        }

        // 2. 检查用户状态
        if (user.getDeleted() != null && user.getDeleted() == 1) {
            throw new UsernameNotFoundException("用户已被删除: " + userId);
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            throw new UsernameNotFoundException("用户已被禁用: " + userId);
        }

        // 3. 加载用户角色
        List<GrantedAuthority> authorities = loadUserAuthorities(userId);

        // 4. 构建 UserDetails 对象
        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getUsername())
                .password(user.getPassword() != null ? user.getPassword() : "") // 密码用于认证，JWT 模式下可能不需要
                .authorities(authorities)
                .accountExpired(false)
                .accountLocked(false)
                .credentialsExpired(false)
                .disabled(user.getStatus() != null && user.getStatus() == 0)
                .build();
    }

    /**
     * 加载用户权限（角色 + 菜单路径）
     * 
     * 权限格式：
     * - 角色权限：ROLE_ADMIN, ROLE_USER 等
     * - 菜单权限：MENU_/sys/user, MENU_/challenge/admin/list 等
     */
    private List<GrantedAuthority> loadUserAuthorities(Integer userId) {
        List<GrantedAuthority> authorities = new ArrayList<>();

        // 1. 获取用户的角色列表
        LambdaQueryWrapper<UserRole> userRoleWrapper = new LambdaQueryWrapper<>();
        userRoleWrapper.eq(UserRole::getUserId, userId);
        List<UserRole> userRoles = userRoleMapper.selectList(userRoleWrapper);

        if (userRoles.isEmpty()) {
            log.warn("用户 {} 没有分配角色", userId);
            return authorities;
        }

        // 2. 获取所有角色ID
        List<Integer> roleIds = userRoles.stream()
                .map(UserRole::getRoleId)
                .collect(Collectors.toList());

        // 3. 为每个角色添加角色权限（ROLE_XXX）
        for (Integer roleId : roleIds) {
            // 从数据库查询角色信息
            Role role = roleMapper.selectById(roleId);
            if (role != null && role.getRoleName() != null) {
                // 将角色名称转换为 Spring Security 角色格式（ROLE_XXX）
                String roleName = role.getRoleName().toUpperCase();
                if (!roleName.startsWith("ROLE_")) {
                    roleName = "ROLE_" + roleName;
                }
                authorities.add(new SimpleGrantedAuthority(roleName));
            } else {
                // 如果角色不存在，使用默认角色
                if (roleId == 1) {
                    authorities.add(new SimpleGrantedAuthority("ROLE_ADMIN"));
                } else {
                    authorities.add(new SimpleGrantedAuthority("ROLE_USER"));
                }
            }
        }

        // 4. 获取用户可访问的菜单路径（作为权限）
        // 先查询所有菜单，建立菜单ID到菜单对象的映射，方便查找父菜单
        List<Menu> allMenus = menuService.list();
        java.util.Map<Integer, Menu> menuMap = allMenus.stream()
                .collect(Collectors.toMap(Menu::getMenuId, menu -> menu));
        
        Set<String> menuPaths = new HashSet<>();
        for (Integer roleId : roleIds) {
            List<Integer> menuIds = roleMenuMapper.getMenuIdsByRoleId(roleId);
            
            for (Integer menuId : menuIds) {
                Menu menu = menuService.getById(menuId);
                if (menu != null && menu.getPath() != null && !menu.getPath().isEmpty()) {
                    String fullPath = buildFullMenuPath(menu, menuMap);
                    if (fullPath != null && !fullPath.isEmpty()) {
                        if (!fullPath.startsWith("/")) {
                            fullPath = "/" + fullPath;
                        }
                        menuPaths.add("MENU_" + fullPath);
                    }
                    loadChildrenMenuPaths(menu, menuMap, menuPaths);
                }
            }
        }

        for (String menuPath : menuPaths) {
            authorities.add(new SimpleGrantedAuthority(menuPath));
        }
        return authorities;
    }

    /**
     * 构建完整的菜单路径（处理父子关系）
     * 
     * 如果菜单是子菜单（有父菜单），需要组合父菜单和子菜单的路径
     * 例如：父菜单 path="/sys"，子菜单 path="user" -> 完整路径="/sys/user"
     * 
     * @param menu 当前菜单
     * @param menuMap 所有菜单的映射（menuId -> Menu）
     * @return 完整的菜单路径
     */
    private String buildFullMenuPath(Menu menu, java.util.Map<Integer, Menu> menuMap) {
        if (menu == null || menu.getPath() == null || menu.getPath().isEmpty()) {
            return null;
        }

        String menuPath = menu.getPath();
        
        // 如果菜单路径已经是绝对路径（以/开头），且没有父菜单，直接返回
        // 如果菜单路径已经是绝对路径（如 /sys/challenge），直接返回，不需要组合父菜单
        if (menuPath.startsWith("/")) {
            // 如果菜单有父菜单，但路径已经是绝对路径，可能需要检查是否需要组合
            // 但通常绝对路径已经是完整路径，直接返回
            if (menu.getParentId() == null || menu.getParentId() == 0) {
                return menuPath;
            }
            // 如果路径是绝对路径，但又有父菜单，可能是特殊情况，需要检查
            // 例如：父菜单是 /sys，子菜单是 /sys/challenge（绝对路径）
            // 这种情况下，如果子菜单路径已经包含父菜单路径，直接返回子菜单路径
            Menu parentMenu = menuMap.get(menu.getParentId());
            if (parentMenu != null && parentMenu.getPath() != null) {
                String parentPath = parentMenu.getPath();
                if (menuPath.startsWith(parentPath + "/") || menuPath.equals(parentPath)) {
                    // 子菜单路径已经包含父菜单路径，直接返回
                    return menuPath;
                }
            }
            // 如果子菜单是绝对路径但不包含父菜单路径，直接返回子菜单路径
            return menuPath;
        }
        
        // 如果菜单有父菜单，需要组合路径
        if (menu.getParentId() != null && menu.getParentId() > 0) {
            Menu parentMenu = menuMap.get(menu.getParentId());
            if (parentMenu != null && parentMenu.getPath() != null && !parentMenu.getPath().isEmpty()) {
                String parentPath = parentMenu.getPath();
                // 如果父菜单路径是绝对路径（以/开头），直接组合
                if (parentPath.startsWith("/")) {
                    // 组合父菜单和子菜单路径
                    return parentPath + "/" + menuPath;
                } else {
                    // 如果父菜单路径也是相对路径，递归构建
                    String fullParentPath = buildFullMenuPath(parentMenu, menuMap);
                    if (fullParentPath != null) {
                        return fullParentPath + "/" + menuPath;
                    }
                }
            }
        }
        
        // 如果没有父菜单，直接返回当前菜单路径
        return menuPath;
    }

    /**
     * 递归加载所有子菜单的权限
     * 
     * @param parentMenu 父菜单
     * @param menuMap 所有菜单的映射（menuId -> Menu）
     * @param menuPaths 权限路径集合
     */
    private void loadChildrenMenuPaths(Menu parentMenu, java.util.Map<Integer, Menu> menuMap, Set<String> menuPaths) {
        if (parentMenu == null || parentMenu.getMenuId() == null) {
            return;
        }
        
        // 查找所有子菜单
        for (Menu menu : menuMap.values()) {
            if (menu.getParentId() != null && menu.getParentId().equals(parentMenu.getMenuId())) {
                // 构建子菜单的完整路径
                String fullPath = buildFullMenuPath(menu, menuMap);
                if (fullPath != null && !fullPath.isEmpty()) {
                    // 确保路径以 / 开头
                    if (!fullPath.startsWith("/")) {
                        fullPath = "/" + fullPath;
                    }
                    // 添加子菜单权限：MENU_/path
                    menuPaths.add("MENU_" + fullPath);
                }
                
                // 递归加载子菜单的子菜单
                loadChildrenMenuPaths(menu, menuMap, menuPaths);
            }
        }
    }
}

