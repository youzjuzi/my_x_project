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

