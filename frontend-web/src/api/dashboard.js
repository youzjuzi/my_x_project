import request from '@/utils/request'

/**
 * 获取仪表盘统计数据
 * 返回：streakDays, totalRecognitions, challengeAccuracy, bestScore, recognitionTrend, accuracyTrend
 */
export function getDashboardStats() {
  return request({
    url: '/dashboard/stats',
    method: 'get'
  })
}
