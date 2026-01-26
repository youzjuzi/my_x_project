import request from '@/utils/request';

// 生成验证码
export function generateCaptcha() {
  console.log('调用 generateCaptcha，URL: /captcha/generate');
  return request({
    url: '/captcha/generate',
    method: 'get'
  }).catch(error => {
    console.error('generateCaptcha 请求失败:', error);
    throw error;
  });
}

// 验证验证码
export function verifyCaptcha(id, data) {
  console.log('调用 verifyCaptcha，ID:', id, 'Data:', data);
  return request({
    url: '/captcha/verify',
    method: 'post',
    params: { id },
    data
  }).catch(error => {
    console.error('verifyCaptcha 请求失败:', error);
    throw error;
  });
}

