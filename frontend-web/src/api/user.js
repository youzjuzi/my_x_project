import request from '@/utils/request';


// 登录
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  });
}

//  注册
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  });
}


export function getInfo(token) {
  return request({
    url: '/auth/info',
    method: 'get',
    params: { token }
  });
}

export function logout(token) {
  return request({
    url: '/auth/logout',
    method: 'post',
    params: { token }
  });
}
