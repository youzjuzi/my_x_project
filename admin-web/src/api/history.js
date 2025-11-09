import request from '@/utils/request'

export function searchHistory(params) {
  return request({
    url: '/history/search',
    method: 'get',
    params: {

    }
  })
}

export default {
  getHistoryList(searchModel) {
    return request({
      url: '/history/list',
      method: 'get',
      params: {
        pageNo: searchModel.pageNo,
        pageSize: searchModel.pageSize,
        startTime: searchModel.startDate,
        endTime: searchModel.endDate,
        keyword: searchModel.keyword
      }
    })
  },
  deleteHistoryById(id) {
    return request({
      url: `/history/${id}`,
      method: 'delete'
    })
  },
  getAllHistoryList() {
    return request({
      url: '/history/all',
      method: 'get'
    })
  }
}
