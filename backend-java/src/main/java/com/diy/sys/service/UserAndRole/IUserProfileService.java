package com.diy.sys.service.UserAndRole;

import java.util.Map;

public interface IUserProfileService {

    Map<String, Object> getUserInfo(String token);

    /**
     * 根据用户ID获取用户完整信息
     * @param userId 用户ID
     * @return 用户信息Map
     */
    Map<String, Object> getUserInfoByUserId(Integer userId);
}
