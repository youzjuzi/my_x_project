import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

export function register(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

export default {
  getAllUsers() {
    return request({
      url: '/user/all',
      method: 'get'
    })
  },
  getAllTime() {
    return request({
      url: '/user/time',
      method: 'get'
    })
  },
  getUserList(searchModel) {
    return request({
      url: '/user/list',
      method: 'get',
      params: {
        pageNo: searchModel.pageNo,
        pageSize: searchModel.pageSize,
        username: searchModel.username,
        phone: searchModel.phone
      }
    })
  },
  addUser(user) {
    return request({
      url: '/user',
      method: 'post',
      data: user
    })
  },
  getUserById(id) {
    return request({
      // url: '/user/' + id,
      url: `/user/${id}`,
      method: 'get'
    })
  },
  saveUser(user) {
    if (user.id == null && user.id === undefined) {
      return this.addUser(user)
    }
    return this.updateUser(user)
  },
  updateUser(user) {
    return request({
      url: '/user',
      method: 'put',
      data: user
    })
  },
  deletUserById(id) {
    return request({
      url: `/user/${id}`,
      method: 'delete'
    })
  }
}
