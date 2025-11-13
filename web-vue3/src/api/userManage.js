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
    },
    // 新增用户
    addUser(user) {
        return request({
            url: '/user',
            method: 'post',
            data: user
        })
    },
    // 检测账号是否已经存在
    checkUsername(username) {
        return request({
            url: '/user/checkUsername',
            method: 'get',
            params: { username }
        })
    }
}