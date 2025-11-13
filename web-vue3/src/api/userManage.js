import request from '@/utils/request'

export default {
    // 分页查询
    getUserList(searchModel) {
        return request({
            url: '/user/list',
            method: 'get',
            // 查询参数
            params: {
                pageNo: searchModel.pageNo,
                pageSize: searchModel.pageSize,
                username: searchModel.username,
                email: searchModel.email,
                phone: searchModel.phone,
            }
        })
    }
}