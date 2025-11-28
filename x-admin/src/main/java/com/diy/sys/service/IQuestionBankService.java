package com.diy.sys.service;

import com.diy.sys.entity.QuestionBank;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.Map;

/**
 * <p>
 * 题库服务接口
 * </p>
 *
 * @author youzi
 * @since 2024
 */
public interface IQuestionBankService extends IService<QuestionBank> {

    /**
     * 分页查询题目列表
     * 
     * @param content 题目内容（模糊查询）
     * @param type 题目类型（1:单词 2:中文 3:数字）
     * @param difficulty 难度（1:简单 2:中等 3:困难）
     * @param levelGroup 级别组
     * @param pageNo 页码
     * @param pageSize 每页大小
     * @return 分页结果
     */
    Map<String, Object> getQuestionList(String content, Integer type, Integer difficulty, String levelGroup, Long pageNo, Long pageSize);
}

