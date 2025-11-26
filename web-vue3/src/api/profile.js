import request from '@/utils/request';


// 获取用户信息
export function getProfileInfo(token) {
  return request({
    url: '/profile/getInfo',
    method: 'get',
    params: { token }
  });
}