import type { RouteRecordRaw, RouteComponent } from 'vue-router';

// Layout 组件 - 使用动态导入
// @ts-ignore
const Layout = (): RouteComponent => import('@/layout/index.vue');

// 菜单项接口定义
export interface MenuItem {
  menuId: number;
  component: string;
  path: string;
  redirect?: string | null;
  name: string;
  title: string;
  icon?: string;
  parentId: number;
  isLeaf: string; // 'Y' | 'N'
  hidden?: boolean;
  children?: MenuItem[];
  meta?: {
    icon?: string;
    title?: string;
    [key: string]: any;
  };
}

// 组件映射表 - 将后端返回的 component 路径映射到实际的组件导入函数
// 手动列出所有组件，确保 Vite 可以正确静态分析
const componentMap: Record<string, () => Promise<RouteComponent>> = {
  // Layout 组件
  Layout: Layout as () => Promise<RouteComponent>,
  
  // sys 模块
  // @ts-ignore
  'sys/user': () => import('@/views/sys/user/index.vue'),
  // @ts-ignore
  'sys/role': () => import('@/views/sys/role/index.vue'),
  
  // translation 模块
  // @ts-ignore
  'translation/translation': () => import('@/views/translation/translation/index.vue'),
  // @ts-ignore
  'translation/reverse_translation': () => import('@/views/translation/reverse_translation/index.vue'),
  
  // logging 模块
  // @ts-ignore
  'logging/translation_history': () => import('@/views/logging/translation_history/index.vue'),
  // @ts-ignore
  'logging/system_logs': () => import('@/views/logging/system_logs/index.vue'),
};

// 使用 import.meta.glob 作为补充，自动发现其他组件
// 这样可以支持未来新增的组件
const viewsModules = import.meta.glob('@/views/**/index.vue');

// 自动构建组件映射表（补充）
Object.keys(viewsModules).forEach((path) => {
  // import.meta.glob 返回的路径格式可能是 '@/views/...'
  // 提取组件路径，例如: '@/views/sys/user/index.vue' -> 'sys/user'
  const match = path.match(/@\/views\/(.+)\/index\.vue$/);
  if (match) {
    const componentPath = match[1];
    // 如果组件映射表中还没有，则添加
    if (!componentMap[componentPath]) {
      componentMap[componentPath] = viewsModules[path] as () => Promise<RouteComponent>;
      // 调试信息（开发环境）
      if (import.meta.env.DEV) {
        console.log(`[动态路由] 自动注册组件: ${componentPath}`);
      }
    }
  }
});

// 输出所有已注册的组件（开发环境）
if (import.meta.env.DEV) {
  console.log('[动态路由] 已注册的组件:', Object.keys(componentMap));
}

/**
 * 动态加载组件
 * @param componentPath 组件路径，如 'sys/user' 或 'translation/translation'
 */
function loadComponent(componentPath: string): () => Promise<RouteComponent> {
  // 如果组件路径是 'Layout'，返回 Layout 组件
  if (componentPath === 'Layout') {
    return Layout as () => Promise<RouteComponent>;
  }

  // 从映射表中获取组件
  const componentLoader = componentMap[componentPath];
  
  if (componentLoader) {
    return componentLoader;
  }

  // 如果映射表中没有，输出错误信息
  console.error(`[动态路由] 组件路径 "${componentPath}" 未在 componentMap 中定义`);
  console.error(`[动态路由] 可用的组件路径:`, Object.keys(componentMap));
  
  // 返回一个错误组件，而不是尝试动态导入（因为 Vite 不支持）
  return () => Promise.reject(
    new Error(`组件 "${componentPath}" 未找到。请确保该组件存在于 @/views/${componentPath}/index.vue`)
  ) as Promise<RouteComponent>;
}

/**
 * 将菜单项转换为路由配置
 * @param menu 菜单项
 */
function menuToRoute(menu: MenuItem): RouteRecordRaw {
  // @ts-ignore - 使用 any 类型以支持动态路由配置
  const route: any = {
    path: menu.path, // 路径
    name: menu.name, // 名称
    component: loadComponent(menu.component), // 组件
    meta: {
      title: menu.meta?.title || menu.title, // 标题
      icon: menu.meta?.icon || menu.icon || '', // 图标
      hidden: menu.hidden || false,
      ...menu.meta // 元数据
    }
  };
  // 如果有 redirect 且不为空字符串，添加 redirect 属性
  if (menu.redirect && menu.redirect.trim() !== '') {
    route.redirect = menu.redirect;
  }

  // 如果有子菜单，递归处理
  if (menu.children && menu.children.length > 0) {
    const children = menu.children
      .filter(child => !child.hidden) // 过滤掉隐藏的子菜单
      .map(child => menuToRoute(child));
    if (children.length > 0) {
      route.children = children;
    }
  }

  return route as RouteRecordRaw;
}

/**
 * 将菜单列表转换为路由列表
 * @param menuList 菜单列表
 */
export function menuListToRoutes(menuList: MenuItem[]): RouteRecordRaw[] {
  if (!menuList || menuList.length === 0) {
    return [];
  }

  return menuList
    .filter(menu => !menu.hidden) // 过滤掉隐藏的菜单
    .map(menu => menuToRoute(menu));
}

