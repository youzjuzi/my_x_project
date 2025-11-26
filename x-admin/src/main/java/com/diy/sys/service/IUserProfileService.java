package com.diy.sys.service;

import java.util.Map;

public interface IUserProfileService {


    Map<String, Object> getUserInfo(String token);
}
