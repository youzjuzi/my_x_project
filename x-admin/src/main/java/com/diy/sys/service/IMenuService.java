package com.diy.sys.service;

import com.diy.sys.entity.Menu;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

/**
 * <p>
 *  服务类
 * </p>
 *
 * @author youzi
 * @since 2023-11-08
 */
public interface IMenuService extends IService<Menu> {
    List<Menu> getAllMenu();
    List<Menu> getMenuListByUserId(Integer userId);
}
