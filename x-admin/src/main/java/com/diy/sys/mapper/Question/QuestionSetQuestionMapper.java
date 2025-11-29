package com.diy.sys.mapper.Question;

import com.diy.sys.entity.Question.QuestionSetQuestion;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * <p>
 * 题库-题目关联 Mapper 接口
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Mapper
public interface QuestionSetQuestionMapper extends BaseMapper<QuestionSetQuestion> {
    
    /**
     * 根据题库ID查询题目ID列表
     * 
     * @param questionSetId 题库ID
     * @return 题目ID列表
     */
    List<Integer> getQuestionIdsByQuestionSetId(@Param("questionSetId") Integer questionSetId);
}

