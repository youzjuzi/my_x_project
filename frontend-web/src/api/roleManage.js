import request from '@/utils/request'

export default {
  // 分页查询角色列表
  getRoleList(params) {
    return request({
      url: '/role/list',
      method: 'get',
      params
    })
  },
  getRoleById(id) {
    return request({
      url: `/role/${id}`,
      method: 'get'
    })
  },
  getAllRoleList() {
    return request({
      url: '/role/all',
      method: 'get'
    })
  },
  // 新增角色
  addRole(data) {
    return request({
      url: '/role',
      method: 'post',
      data
    })
  },
  // 修改角色
  updateRole(data) {
    return request({
      url: '/role',
      method: 'put',
      data
    })
  },
  // 删除角色
  deleteRole(id) {
    return request({
      url: `/role/${id}`,
      method: 'delete'
    })
  }
}
