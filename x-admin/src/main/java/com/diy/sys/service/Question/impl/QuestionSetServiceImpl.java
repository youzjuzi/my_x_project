package com.diy.sys.service.Question.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.diy.sys.entity.Question.QuestionSet;
import com.diy.sys.entity.Question.QuestionSetQuestion;
import com.diy.sys.mapper.Question.QuestionSetMapper;
import com.diy.sys.mapper.Question.QuestionSetQuestionMapper;
import com.diy.sys.service.Question.IQuestionSetService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.HashMap;
import java.util.List;
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
public class QuestionSetServiceImpl extends ServiceImpl<QuestionSetMapper, QuestionSet> implements IQuestionSetService {

    @Autowired
    private QuestionSetQuestionMapper questionSetQuestionMapper;

    /**
     * 分页查询题库列表
     * 
     * @param name 题库名称（模糊查询，可选）
     * @param status 状态（1-启用，0-禁用，可选）
     * @param pageNo 页码（从1开始）
     * @param pageSize 每页大小
     * @return 包含 total（总数）和 rows（数据列表）的 Map
     */
    @Override
    public Map<String, Object> getQuestionSetList(String name, Integer status, Long pageNo, Long pageSize) {
        // 构建查询条件
        LambdaQueryWrapper<QuestionSet> wrapper = new LambdaQueryWrapper<>();
        
        // 模糊查询题库名称（如果提供了名称）
        wrapper.like(StringUtils.hasLength(name), QuestionSet::getName, name);
        
        // 精确查询状态（如果提供了状态）
        wrapper.eq(status != null, QuestionSet::getStatus, status);
        
        // 按ID倒序排列（最新的在前）
        wrapper.orderByDesc(QuestionSet::getId);
        
        // 创建分页对象
        Page<QuestionSet> page = new Page<>(pageNo, pageSize);
        
        // 执行分页查询（MyBatis Plus 会自动处理分页逻辑）
        this.page(page, wrapper);
        
        // 构建返回结果
        Map<String, Object> data = new HashMap<>();
        data.put("total", page.getTotal());      // 总记录数
        data.put("rows", page.getRecords());     // 当前页数据列表
        
        return data;
    }

    @Override
    public List<Integer> getQuestionIdsByQuestionSetId(Integer questionSetId) {
        return questionSetQuestionMapper.getQuestionIdsByQuestionSetId(questionSetId);
    }

    @Override
    @Transactional
    public void updateQuestionSetQuestions(Integer questionSetId, List<Integer> questionIdList) {
        // 删除原有关联
        LambdaQueryWrapper<QuestionSetQuestion> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(QuestionSetQuestion::getQuestionSetId, questionSetId);
        questionSetQuestionMapper.delete(wrapper);
        
        // 新增关联
        if (questionIdList != null && !questionIdList.isEmpty()) {
            for (Integer questionId : questionIdList) {
                questionSetQuestionMapper.insert(new QuestionSetQuestion(null, questionSetId, questionId));
            }
        }
    }
}

