package com.diy.sys.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.diy.common.vo.Result;
import com.diy.sys.entity.Role;
import com.diy.sys.service.IRoleService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;


//@RestController
//@RequestMapping("/role")
//public class RoleController {
//    @Autowired
//    private IRoleService roleService;
//    @GetMapping("/list")
//    public Result<Map<String ,Object>> getRoleList(@RequestParam(value = "roleName",required = false) String roleName,
//                                                   @RequestParam("pageNo") Long pageNo,
//                                                   @RequestParam("pageSize") Long pageSize){
//        LambdaQueryWrapper<Role> wrapper = new LambdaQueryWrapper<>();
//        wrapper.eq(StringUtils.hasLength(roleName),Role::getRoleName,roleName);
//        wrapper.orderByAsc(Role::getRoleId);
//
//        Page<Role> page = new Page<>(pageNo,pageSize);
//        roleService.page(page,wrapper);
//
//        Map<String ,Object> data = new HashMap<>();
//        data.put("total",page.getTotal());
//        data.put("row",page.getRecords());
//
//        return Result.success(data);
//    }
//
//    @PutMapping
//    public Result<?> addRole(@RequestBody Role role){
//        roleService.save(role);
//        return Result.success("新增角色成功");
//    }
//    @PostMapping
//    public Result<?> updateRole(@RequestBody Role role){
//        roleService.updateById(role);
//        return Result.success("修改角色成功");
//    }
//    @GetMapping("/{id}")
//    public Result<Role> getRoleById(@PathVariable("id") Integer id){
//        Role role = roleService.getById(id);
//        return Result.success(role);
//    }
//    @DeleteMapping("/{id}")
//    public Result<Role> deleteRoleById(@PathVariable("id") Integer id){
//        roleService.removeById(id);
//        return Result.success("删除角色成功");
//    }
//
//
//}
@RestController
@RequestMapping("/role")
public class RoleController {

    @Autowired
    private IRoleService roleService;

    @GetMapping("/list")
    public Result<Map<String,Object>> getUserList(@RequestParam(value = "roleName",required = false) String roleName,
                                                  @RequestParam(value = "pageNo") Long pageNo,
                                                  @RequestParam(value = "pageSize") Long pageSize){
        Map<String,Object> data = roleService.getRoleList(roleName, pageNo, pageSize);
        return Result.success(data);

    }

    @PostMapping
    public Result<?> addRole(@RequestBody Role role){
        roleService.addRole(role);
        return Result.success("新增角色成功");
    }

    @PutMapping
    public Result<?> updateRole(@RequestBody Role role){
        roleService.updateRole(role);
        return Result.success("修改角色成功");
    }

    @GetMapping("/{id}")
    public Result<Role> getRoleById(@PathVariable("id") Integer id){
        Role role = roleService.getRoleById(id);
        return Result.success(role);
    }

    @DeleteMapping("/{id}")
    public Result<Role> deleteRoleById(@PathVariable("id") Integer id){
        roleService.deleteRoleById(id);
        return Result.success("删除角色成功");
    }

    @GetMapping("/all")
    public Result<List<Role>> getAllRole(){
        List<Role> roleList = roleService.list();
        return Result.success(roleList);
    }
}
