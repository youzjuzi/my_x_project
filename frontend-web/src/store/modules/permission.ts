import { defineStore } from 'pinia';
import { asyncRoutes, constantRoutes } from '@/router';
import type { RouteRecordRaw } from 'vue-router';
import { menuListToRoutes, type MenuItem } from '@/utils/menu-to-routes';

interface IPermissionState {
  routes: Array<RouteRecordRaw>;
  addRoutes: Array<RouteRecordRaw>;
}

/**
 * Use meta.role to determine if the current user has permission
 * @param roles
 * @param route
 */
function hasPermission(roles:string[], route:RouteRecordRaw):boolean {
  if (route.meta && route.meta.roles) {
    const rolesArr = route.meta.roles as string[];
    return roles.some(role => rolesArr.includes(role));
  } else {
    return true;
  }
}

/**
 * Filter asynchronous routing tables by recursion
 * @param routes asyncRoutes
 * @param roles
 */
export function filterAsyncRoutes(routes:RouteRecordRaw[], roles: string[]): Array<RouteRecordRaw> {
  const res:Array<RouteRecordRaw> = [];

  routes.forEach(route => {
    const tmp = { ...route };
    if (hasPermission(roles, tmp)) {
      if (tmp.children) {
        tmp.children = filterAsyncRoutes(tmp.children, roles);
      }
      res.push(tmp);
    }
  });

  return res;
}

export default defineStore({
  id: 'permission',
  state: ():IPermissionState => ({
    routes: [],
    addRoutes: []
  }),
  getters: {},
  actions: {
    setRoutes(routes: RouteRecordRaw[]) {
      this.addRoutes = routes.slice();
      this.routes = constantRoutes.concat(routes);
    },
    clearRoutes() {
      this.addRoutes = [];
      this.routes = constantRoutes.slice();
    },
    /**
     * 根据菜单列表生成路由
     * @param menuList 菜单列表
     */
    generateRoutesFromMenu(menuList: MenuItem[]): RouteRecordRaw[] {
      const routes = menuListToRoutes(menuList);
      this.setRoutes(routes);
      return routes;
    },
    /**
     * 根据角色生成路由（保留原有功能，用于兼容）
     * @param roles 角色列表
     */
    generateRoutes(roles: string[]) {
      let accessedRoutes;
      if (roles.includes('admin')) {
        accessedRoutes = asyncRoutes || [];
      } else {
        accessedRoutes = filterAsyncRoutes(asyncRoutes, roles);
      }
      this.setRoutes(accessedRoutes);
      return accessedRoutes;
    }
  }
});
