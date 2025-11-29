package com.diy.sys.service.Question.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.diy.sys.entity.Question.QuestionBank;
import com.diy.sys.mapper.Question.QuestionBankMapper;
import com.diy.sys.service.Question.IQuestionBankService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.HashMap;
import java.util.Map;

/**
 * <p>
 * 题库服务实现类
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Service
public class QuestionBankServiceImpl extends ServiceImpl<QuestionBankMapper, QuestionBank> implements IQuestionBankService {

    @Override
    public Map<String, Object> getQuestionList(String content, Integer type, Integer difficulty, String levelGroup, Long pageNo, Long pageSize) {
        LambdaQueryWrapper<QuestionBank> wrapper = new LambdaQueryWrapper<>();
        
        // 模糊查询题目内容
        wrapper.like(StringUtils.hasLength(content), QuestionBank::getContent, content);
        
        // 精确查询类型
        wrapper.eq(type != null, QuestionBank::getType, type);
        
        // 精确查询难度
        wrapper.eq(difficulty != null, QuestionBank::getDifficulty, difficulty);
        
        // 精确查询级别组
        wrapper.eq(StringUtils.hasLength(levelGroup), QuestionBank::getLevelGroup, levelGroup);
        
        // 按ID倒序排列（最新的在前）
        wrapper.orderByDesc(QuestionBank::getId);
        
        // 分页查询
        Page<QuestionBank> page = new Page<>(pageNo, pageSize);
        this.page(page, wrapper);
        
        // 构建返回结果
        Map<String, Object> data = new HashMap<>();
        data.put("total", page.getTotal());
        data.put("rows", page.getRecords());
        
        return data;
    }
}

