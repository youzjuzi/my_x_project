import request from '@/utils/request'

/**
 * 根据条件查询题目
 */
export function queryQuestions(params) {
  return request({
    url: '/challenge/questions/query',
    method: 'post',
    params
  })
}

/**
 * 开始挑战
 */
export function startChallenge(data) {
  return request({
    url: '/challenge/start',
    method: 'post',
    data
  })
}

/**
 * 提交挑战结果
 */
export function submitChallenge(data) {
  return request({
    url: '/challenge/submit',
    method: 'post',
    data
  })
}

/**
 * 获取挑战历史记录
 */
export function getChallengeHistory(params) {
  return request({
    url: '/challenge/history',
    method: 'get',
    params
  })
}

/**
 * 获取所有用户的挑战记录（管理员接口）
 */
export function getAllChallengeHistory(params) {
  return request({
    url: '/challenge/admin/list',
    method: 'get',
    params
  })
}

/**
 * 获取所有有过挑战的用户列表
 */
export function getUsersWithChallenges() {
  return request({
    url: '/challenge/admin/users',
    method: 'get'
  })
}

