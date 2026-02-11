import request from '@/utils/request';

/**
 * 分页查询翻译历史
 * @param {Object} params - 查询参数 { userId, pageNo, pageSize }
 */
export function getHistoryList(params) {
    return request({
        url: '/sign/history/list',
        method: 'get',
        params
    });
}
/**
 * 获取活动日期列表
 * @param {Object} params - { userId, year, month }
 */
export function getActivityDates(params) {
    return request({
        url: '/sign/history/dates',
        method: 'get',
        params
    });
}
