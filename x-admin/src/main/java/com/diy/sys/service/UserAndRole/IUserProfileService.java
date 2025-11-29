package com.diy.sys.service.UserAndRole;

import java.util.Map;

public interface IUserProfileService {


    Map<String, Object> getUserInfo(String token);
}
