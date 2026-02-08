package com.diy.sys.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.diy.sys.entity.Detection;

public interface IHistoryService extends IService<Detection> {
    void deleteDetectionById(String session_id);

}
