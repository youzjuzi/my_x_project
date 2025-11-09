import router from './router'
import store from './store'
import { Message } from 'element-ui'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style
import { getToken } from '@/utils/auth' // get token from cookie
import getPageTitle from '@/utils/get-page-title'
import Layout from '@/layout'

NProgress.configure({ showSpinner: false }) // NProgress Configuration

const whiteList = ['/login'] // no redirect whitelist

router.beforeEach(async(to, from, next) => {
  // start progress bar
  NProgress.start()

  // set page title
  document.title = getPageTitle(to.meta.title)

  // determine whether the user has logged in
  const hasToken = getToken()

  if (hasToken) {
    if (to.path === '/login') {
      // if is logged in, redirect to the home page
      next({ path: '/' })
      NProgress.done()
    } else {
      const hasGetUserInfo = store.getters.name
      if (hasGetUserInfo) {
        next()
      } else {
        try {
          // get user info
          await store.dispatch('user/getInfo')

          // 路由转换
          const rawRoutes = store.getters.menuList
          const uniqueRoutes = removeDuplicateRoutes(rawRoutes) // 去除重复路由
          const myRoutes = myFilterAsyncRouters(uniqueRoutes)
          // 404
          myRoutes.push({ path: '*', redirect: '/404', hidden: true })
          // 动态添加路由
          router.addRoutes(myRoutes)
          // 保存到全局变量
          global.myRoutes = myRoutes
          console.log('myRoutes', global.myRoutes)

          next({ ...to, replace: true }) // hack方法 确保addRoutes已完成
          // next()
        } catch (error) {
          // remove token and go to login page to re-login
          await store.dispatch('user/resetToken')
          Message.error({
            message: error || 'Has Error'
          })
          next(`/login?redirect=${to.path}`)
          NProgress.done()
        }
      }
    }
  } else {
    /* has no token*/

    if (whiteList.indexOf(to.path) !== -1) {
      // in the free login whitelist, go directly
      next()
    } else {
      // other pages that do not have permission to access are redirected to the login page.
      next(`/login?redirect=${to.path}`)
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  // finish progress bar
  NProgress.done()
})

function removeDuplicateRoutes(routes) {
  const pathSet = new Set()
  const uniqueRoutes = []

  routes.forEach(route => {
    if (!pathSet.has(route.path)) {
      // 如果路径是唯一的，添加到Set中并推入uniqueRoutes数组
      pathSet.add(route.path)
      uniqueRoutes.push(route)

      // 如果存在子路由，递归地对它们进行去重处理
      if (route.children && route.children.length) {
        route.children = removeDuplicateRoutes(route.children)
      }
    }
  })
  return uniqueRoutes
}

function myFilterAsyncRouters(menuList) {
  menuList.filter(menu => {
    if (menu.component === 'Layout') {
      menu.component = Layout
    } else {
      menu.component = require(`@/views/${menu.component}.vue`).default
    }
    if (menu.children && menu.children.length) {
      console.log('menu.children', menu.children)
      menu.children = myFilterAsyncRouters(menu.children)
    }
    return true
  })
  return menuList
}
