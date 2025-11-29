import request from '@/utils/request'

export default {
  // 分页查询题库列表
  getQuestionSetList(params) {
    return request({
      url: '/questionSet/list',
      method: 'get',
      params
    })
  },
  // 根据ID查询单个题库
  getQuestionSetById(id) {
    return request({
      url: `/questionSet/${id}`,
      method: 'get'
    })
  },
  // 查询所有题库（不分页）
  getAllQuestionSets() {
    return request({
      url: '/questionSet/all',
      method: 'get'
    })
  },
  // 新增题库
  addQuestionSet(data) {
    return request({
      url: '/questionSet',
      method: 'post',
      data
    })
  },
  // 修改题库
  updateQuestionSet(data) {
    return request({
      url: '/questionSet',
      method: 'put',
      data
    })
  },
  // 删除题库
  deleteQuestionSet(id) {
    return request({
      url: `/questionSet/${id}`,
      method: 'delete'
    })
  },
  // 获取题库下的题目ID列表
  getQuestionIdsByQuestionSetId(id) {
    return request({
      url: `/questionSet/${id}/questions`,
      method: 'get'
    })
  },
  // 更新题库的题目关联
  updateQuestionSetQuestions(id, questionIdList) {
    return request({
      url: `/questionSet/${id}/questions`,
      method: 'put',
      data: questionIdList
    })
  }
}

