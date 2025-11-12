import request from '@/utils/request';


// 登录
export function login(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data
  });
}

//  注册
export function register(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data
  });
}


export function getInfo(token) {
  return request({
    url: '/user/info',
    method: 'get',
    params: { token }
  });
}

export function logout() {
  return request({
    url: '/user/logout',
    method: 'post',
  });
}
