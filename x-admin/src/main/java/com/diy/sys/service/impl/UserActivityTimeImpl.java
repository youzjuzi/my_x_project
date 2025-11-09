package com.diy.sys.service.impl;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.diy.sys.entity.UserActivityTime;
import com.diy.sys.mapper.UserActivityMapper;
import com.diy.sys.service.IUserActivityTimeService;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.Map;
import java.util.function.Function;

@Service
public class UserActivityTimeImpl extends ServiceImpl<UserActivityMapper, UserActivityTime> implements IUserActivityTimeService {

}
