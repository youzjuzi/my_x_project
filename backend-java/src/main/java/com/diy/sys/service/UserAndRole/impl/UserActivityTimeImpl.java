package com.diy.sys.service.UserAndRole.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.diy.sys.entity.UserAndRole.UserActivityTime;
import com.diy.sys.mapper.UserAndRole.UserActivityMapper;
import com.diy.sys.service.UserAndRole.IUserActivityTimeService;
import org.springframework.stereotype.Service;

@Service
public class UserActivityTimeImpl extends ServiceImpl<UserActivityMapper, UserActivityTime> implements IUserActivityTimeService {

}
