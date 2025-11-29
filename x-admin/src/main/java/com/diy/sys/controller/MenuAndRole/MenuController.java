package com.diy.sys.controller.MenuAndRole;

import com.diy.common.vo.Result;
import com.diy.sys.entity.MenuAndRole.Menu;
import com.diy.sys.service.MenuAndRole.IMenuService;
import io.swagger.v3.oas.annotations.Operation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * <p>
 *  前端控制器
 * </p>
 *
 * @author youzi
 * @since 2023-11-08
 */
@RestController
@RequestMapping("/menu")
public class MenuController {
    @Autowired
    private IMenuService menuService;
    @Operation(summary = "查询所有菜单数据")
    @GetMapping
    public Result<List<Menu>> getAllMenu(){
        List<Menu> menuList = menuService.getAllMenu();
        return Result.success(menuList);
    }
}
