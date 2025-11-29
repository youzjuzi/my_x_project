package com.diy.sys.controller.MenuAndRole;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.diy.common.vo.Result;
import com.diy.sys.entity.MenuAndRole.Menu;
import com.diy.sys.service.MenuAndRole.IMenuService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * <p>
 *  菜单管理控制器
 * </p>
 *
 * @author youzi
 * @since 2023-11-08
 */
@Tag(name = "菜单管理接口")
@RestController
@RequestMapping("/menu")
public class MenuController {
    @Autowired
    private IMenuService menuService;

    /**
     * 查询所有菜单数据（树形结构）
     * 
     * @return 菜单列表
     */
    @Operation(summary = "查询所有菜单数据")
    @GetMapping
    public Result<List<Menu>> getAllMenu(){
        List<Menu> menuList = menuService.getAllMenu();
        return Result.success(menuList);
    }

    /**
     * 根据ID查询单个菜单
     * 
     * @param id 菜单ID
     * @return 菜单信息
     */
    @Operation(summary = "根据ID查询菜单")
    @GetMapping("/{id}")
    public Result<Menu> getMenuById(@PathVariable("id") Integer id) {
        try {
            Menu menu = menuService.getById(id);
            if (menu != null) {
                return Result.success(menu, "查询成功");
            } else {
                return Result.fail("菜单不存在");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 新增菜单
     * 
     * @param menu 菜单信息
     * @return 操作结果
     */
    @Operation(summary = "新增菜单")
    @PostMapping
    public Result<Menu> addMenu(@RequestBody Menu menu) {
        try {
            // 设置默认值
            if (menu.getIsLeaf() == null || menu.getIsLeaf().isEmpty()) {
                menu.setIsLeaf("Y"); // 默认为叶子节点
            }
            if (menu.getHidden() == null) {
                menu.setHidden(false); // 默认不隐藏
            }
            if (menu.getParentId() == null) {
                menu.setParentId(0); // 默认父级为0（根节点）
            }
            
            boolean success = menuService.save(menu);
            if (success) {
                return Result.success(menu, "新增菜单成功");
            } else {
                return Result.fail("新增菜单失败");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("新增菜单失败：" + e.getMessage());
        }
    }

    /**
     * 修改菜单
     * 
     * @param menu 菜单信息
     * @return 操作结果
     */
    @Operation(summary = "修改菜单")
    @PutMapping
    public Result<?> updateMenu(@RequestBody Menu menu) {
        try {
            if (menu.getMenuId() == null) {
                return Result.fail("菜单ID不能为空");
            }
            
            boolean success = menuService.updateById(menu);
            if (success) {
                return Result.success(menu, "修改菜单成功");
            } else {
                return Result.fail("修改菜单失败");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("修改菜单失败：" + e.getMessage());
        }
    }

    /**
     * 根据ID删除菜单
     * 
     * @param id 菜单ID
     * @return 操作结果
     */
    @Operation(summary = "删除菜单")
    @DeleteMapping("/{id}")
    public Result<?> deleteMenuById(@PathVariable("id") Integer id) {
        try {
            // 检查是否有子菜单
            LambdaQueryWrapper<Menu> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(Menu::getParentId, id);
            List<Menu> children = menuService.list(wrapper);
            if (children != null && !children.isEmpty()) {
                return Result.fail("删除失败：该菜单下存在子菜单，请先删除子菜单");
            }
            
            boolean success = menuService.removeById(id);
            if (success) {
                return Result.success("删除菜单成功");
            } else {
                return Result.fail("删除菜单失败，菜单可能不存在");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("删除菜单失败：" + e.getMessage());
        }
    }
}
