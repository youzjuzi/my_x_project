import request from '@/utils/request';

/**
 * 生成验证码
 * 返回数据包含：
 * - id: 验证码ID
 * - backgroundImage: 背景图片 (base64)
 * - templateImage: 滑块图片 (base64)
 * - backgroundImageWidth/Height: 背景图尺寸
 * - templateImageWidth/Height: 滑块尺寸
 */
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

/**
 * 验证验证码
 * @param {string} id 验证码ID
 * @param {object} data 验证数据，包含：
 *   - x: 滑动终点X坐标
 *   - y: 滑动终点Y坐标 (可选)
 *   - bgImageWidth: 背景图宽度
 *   - bgImageHeight: 背景图高度
 *   - templateImageWidth: 滑块宽度 (可选)
 *   - templateImageHeight: 滑块高度 (可选)
 *   - startTime: 开始滑动时间戳
 *   - endTime: 结束滑动时间戳
 *   - trackList: 滑动轨迹数组 [{x, y, t}] (可选，用于行为分析)
 */
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
