import request from '@/utils/request'

export default {
  getAllMenus() {
    return request({
      url: '/menu',
      method: 'get'
    })
  }
}
