import request from '@/utils/request'

export default {
  getDetectionList() {
    return request({
      url: '/detections',
      method: 'get'
    })
  }
}
