package com.diy.sys.service.Question;

import com.diy.sys.entity.Question.QuestionSet;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;
import java.util.Map;

/**
 * <p>
 * 题库服务接口
 * </p>
 *
 * @author youzi
 * @since 2024
 */
public interface IQuestionSetService extends IService<QuestionSet> {

    /**
     * 分页查询题库列表
     * 
     * @param name 题库名称（模糊查询）
     * @param status 状态（可选）
     * @param pageNo 页码
     * @param pageSize 每页大小
     * @return 分页结果
     */
    Map<String, Object> getQuestionSetList(String name, Integer status, Long pageNo, Long pageSize);

    /**
     * 根据题库ID获取题目ID列表
     * 
     * @param questionSetId 题库ID
     * @return 题目ID列表
     */
    List<Integer> getQuestionIdsByQuestionSetId(Integer questionSetId);

    /**
     * 更新题库的题目关联
     * 
     * @param questionSetId 题库ID
     * @param questionIdList 题目ID列表
     */
    void updateQuestionSetQuestions(Integer questionSetId, List<Integer> questionIdList);
}

