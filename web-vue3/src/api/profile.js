import request from '@/utils/request';



// 获取用户信息
export function getProfileInfo() {
  return request({
    url: '/profile/getInfo',
    method: 'get'
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
export function changePassword(oldPassword, newPassword) {
  return request({
      url: '/profile/changePassword',
      method: 'post',
      data: {
        oldPassword,
        newPassword
      }
  })
}
// 手机号码更改/绑定
export function updatePhone(phone) {
  return request({
    url: '/profile/updatePhone',
    method: 'post',
    data: { phone }
  })
}

// 邮箱更改/绑定
export function updateEmail(email) {
  return request({
    url: '/profile/updateEmail',
    method: 'post',
    data: { email }
  })
}
