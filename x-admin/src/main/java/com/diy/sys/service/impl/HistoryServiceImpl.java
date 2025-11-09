package com.diy.sys.service.impl;

import com.baomidou.mybatisplus.core.conditions.Wrapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.diy.sys.entity.Detection;
import com.diy.sys.mapper.HistoryMapper;
import com.diy.sys.service.IHistoryService;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.Map;
import java.util.function.Function;

@Service
public class HistoryServiceImpl extends ServiceImpl<HistoryMapper,Detection> implements IHistoryService {
    @Override
    public boolean saveBatch(Collection<Detection> entityList, int batchSize) {
        return false;
    }

    @Override
    public boolean saveOrUpdateBatch(Collection<Detection> entityList, int batchSize) {
        return false;
    }

    @Override
    public boolean updateBatchById(Collection<Detection> entityList, int batchSize) {
        return false;
    }

    @Override
    public boolean saveOrUpdate(Detection entity) {
        return false;
    }

    @Override
    public Detection getOne(Wrapper<Detection> queryWrapper, boolean throwEx) {
        return null;
    }

    @Override
    public Map<String, Object> getMap(Wrapper<Detection> queryWrapper) {
        return null;
    }

    @Override
    public <V> V getObj(Wrapper<Detection> queryWrapper, Function<? super Object, V> mapper) {
        return null;
    }


    @Override
    public Class<Detection> getEntityClass() {
        return null;
    }

    @Override
    public void deleteDetectionById(String session_id) {
        this.baseMapper.deleteById(session_id);
    }
}
