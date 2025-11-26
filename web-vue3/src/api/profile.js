import request from '@/utils/request';



// 获取用户信息
export function getProfileInfo(token) {
  return request({
    url: '/profile/getInfo',
    method: 'get',
    params: { token }
  });
}



// 检测账号是否存在
export function checkUsername(username) {
  return request({
      url: '/profile/checkUsername',
      method: 'get',
      params: { username }
  })
}

//更改密码
export function changePassword(password) {
  return request({
      url: '/profile/changePassword',
      method: 'post',
      data: { password }
  })
}


