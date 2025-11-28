import request from '@/utils/request'

export default {
  // 分页查询题目列表
  getQuestionList(params) {
    return request({
      url: '/challenge/question/list',
      method: 'get',
      params
    })
  },
  // 根据ID查询题目
  getQuestionById(id) {
    return request({
      url: `/challenge/question/${id}`,
      method: 'get'
    })
  },
  // 新增题目
  addQuestion(data) {
    return request({
      url: '/challenge/question',
      method: 'post',
      data
    })
  },
  // 修改题目
  updateQuestion(data) {
    return request({
      url: '/challenge/question',
      method: 'put',
      data
    })
  },
  // 删除题目
  deleteQuestion(id) {
    return request({
      url: `/challenge/question/${id}`,
      method: 'delete'
    })
  }
}

