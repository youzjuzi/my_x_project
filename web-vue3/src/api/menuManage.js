import request from '@/utils/request'

export default {
  // 查询所有菜单（树形结构）
  getAllMenus() {
    return request({
      url: '/menu',
      method: 'get'
    })
  },
  // 根据ID查询单个菜单
  getMenuById(id) {
    return request({
      url: `/menu/${id}`,
      method: 'get'
    })
  },
  // 新增菜单
  addMenu(data) {
    return request({
      url: '/menu',
      method: 'post',
      data
    })
  },
  // 修改菜单
  updateMenu(data) {
    return request({
      url: '/menu',
      method: 'put',
      data
    })
  },
  // 删除菜单
  deleteMenu(id) {
    return request({
      url: `/menu/${id}`,
      method: 'delete'
    })
  }
}
