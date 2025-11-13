import request from '@/utils/request'

export default {
    getAllRoleList() {
    return request({
      url: '/role/all',
      method: 'get'
    })
  }
}