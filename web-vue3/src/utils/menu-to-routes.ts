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

// 使用 import.meta.glob 自动发现所有组件
// 这是主要机制，无需手动添加新组件
const viewsModules = import.meta.glob('@/views/**/index.vue');

// 开发环境：输出所有扫描到的文件路径
if (import.meta.env.DEV) {
  const allPaths = Object.keys(viewsModules);
  console.log('[动态路由] import.meta.glob 扫描到的文件数量:', allPaths.length);
  console.log('[动态路由] import.meta.glob 扫描到的所有文件:', allPaths);
}

// 自动构建组件映射表
const componentMap: Record<string, () => Promise<RouteComponent>> = {
  // Layout 组件（特殊处理）
  Layout: Layout as () => Promise<RouteComponent>,
};

// 自动发现所有组件并添加到映射表
Object.keys(viewsModules).forEach((path) => {
  // import.meta.glob 返回的路径格式通常是 '@/views/xxx/yyy/index.vue'
  // 提取组件路径，例如: '@/views/sys/user/index.vue' -> 'sys/user'
  
  // 移除开头的 '@/views/' 和结尾的 '/index.vue'
  let componentPath = path;
  
  // 处理 '@/views/' 开头
  if (componentPath.startsWith('@/views/')) {
    componentPath = componentPath.substring(8); // 8 = '@/views/'.length
  } else if (componentPath.includes('/views/')) {
    // 处理包含 '/views/' 的路径
    const viewsIndex = componentPath.indexOf('/views/');
    componentPath = componentPath.substring(viewsIndex + 7); // 7 = '/views/'.length
  }
  
  // 移除结尾的 '/index.vue'
  if (componentPath.endsWith('/index.vue')) {
    componentPath = componentPath.substring(0, componentPath.length - 10); // 10 = '/index.vue'.length
  }
  
  // 如果成功提取到组件路径，添加到映射表
  if (componentPath && componentPath !== path) {
    componentMap[componentPath] = viewsModules[path] as () => Promise<RouteComponent>;
    
    // 开发环境输出调试信息
    if (import.meta.env.DEV) {
      console.log(`[动态路由] 自动发现组件: ${componentPath} <- ${path}`);
    }
  } else {
    // 如果无法匹配，输出警告
    if (import.meta.env.DEV) {
      console.warn(`[动态路由] 无法解析路径: ${path}`);
    }
  }
});

// 特殊映射：处理拼写错误或别名（可选，仅用于特殊情况）
const specialMappings: Record<string, string> = {
  // 支持拼写错误的 practive，映射到正确的 practice
  'learning/practice': 'learning/practive',
};

// 应用特殊映射
Object.keys(specialMappings).forEach((alias) => {
  const actualPath = specialMappings[alias];
  if (componentMap[actualPath]) {
    componentMap[alias] = componentMap[actualPath];
    if (import.meta.env.DEV) {
      console.log(`[动态路由] 特殊映射: ${alias} -> ${actualPath}`);
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
  let componentLoader = componentMap[componentPath];
  
  if (componentLoader) {
    return componentLoader;
  }

  // 如果映射表中没有，尝试动态导入（回退机制）
  // 这可以处理自动发现失败的情况
  try {
    const dynamicImport = () => import(`@/views/${componentPath}/index.vue`) as Promise<RouteComponent>;
    // 先尝试导入，如果成功则缓存
    componentMap[componentPath] = dynamicImport;
    if (import.meta.env.DEV) {
      console.log(`[动态路由] 使用动态导入回退机制: ${componentPath}`);
    }
    return dynamicImport;
  } catch (error) {
    // 如果动态导入也失败，输出错误信息
    console.error(`[动态路由] 组件路径 "${componentPath}" 未找到`);
    console.error(`[动态路由] 可用的组件路径:`, Object.keys(componentMap).sort());
    console.error(`[动态路由] 错误详情:`, error);
    
    return () => Promise.reject(
      new Error(`组件 "${componentPath}" 未找到。请确保该组件存在于 @/views/${componentPath}/index.vue`)
    ) as Promise<RouteComponent>;
  }
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

