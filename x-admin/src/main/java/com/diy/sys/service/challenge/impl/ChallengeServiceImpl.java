package com.diy.sys.service.challenge.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.diy.sys.entity.Question.QuestionBank;
import com.diy.sys.entity.Question.QuestionSetQuestion;
import com.diy.sys.entity.challenge.Challenge;
import com.diy.sys.entity.challenge.ChallengeQuestion;
import com.diy.sys.mapper.Question.QuestionBankMapper;
import com.diy.sys.mapper.Question.QuestionSetQuestionMapper;
import com.diy.sys.mapper.challenge.ChallengeMapper;
import com.diy.sys.mapper.challenge.ChallengeQuestionMapper;
import com.diy.sys.service.challenge.IChallengeService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * <p>
 * 挑战服务实现类
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Service
public class ChallengeServiceImpl extends ServiceImpl<ChallengeMapper, Challenge> implements IChallengeService {

    @Autowired
    private QuestionBankMapper questionBankMapper;

    @Autowired
    private QuestionSetQuestionMapper questionSetQuestionMapper;

    @Autowired
    private ChallengeQuestionMapper challengeQuestionMapper;

    /**
     * 根据条件查询题目
     */
    @Override
    public Map<String, Object> queryQuestions(String mode, Integer questionSetId, List<Integer> types,
                                              List<Integer> difficulties, Integer count, Boolean random) {
        List<QuestionBank> allQuestions = new ArrayList<>();

        if ("random".equals(mode)) {
            // 随机挑战模式：根据类型和难度筛选
            LambdaQueryWrapper<QuestionBank> wrapper = new LambdaQueryWrapper<>();
            
            // 类型筛选
            if (types != null && !types.isEmpty()) {
                wrapper.in(QuestionBank::getType, types);
            }
            
            // 难度筛选
            if (difficulties != null && !difficulties.isEmpty()) {
                wrapper.in(QuestionBank::getDifficulty, difficulties);
            }
            
            // 只查询启用的题目
            wrapper.eq(QuestionBank::getStatus, 1);
            
            allQuestions = questionBankMapper.selectList(wrapper);
            
        } else if ("questionSet".equals(mode) && questionSetId != null) {
            // 题库模式：从题库中获取题目
            List<Integer> questionIds = questionSetQuestionMapper.getQuestionIdsByQuestionSetId(questionSetId);
            
            if (questionIds != null && !questionIds.isEmpty()) {
                LambdaQueryWrapper<QuestionBank> wrapper = new LambdaQueryWrapper<>();
                wrapper.in(QuestionBank::getId, questionIds);
                wrapper.eq(QuestionBank::getStatus, 1);
                allQuestions = questionBankMapper.selectList(wrapper);
            }
        }

        // 根据是否随机选择来决定题目顺序
        if ("questionSet".equals(mode) && Boolean.FALSE.equals(random)) {
            // 按顺序选择（不随机）：使用所有题目
            // 保持题目在题库中的顺序
            if (count != null && count > 0 && allQuestions.size() > count) {
                allQuestions = allQuestions.subList(0, count);
            }
        } else {
            // 随机打乱并选择指定数量的题目
            Collections.shuffle(allQuestions);
            if (count != null && count > 0 && allQuestions.size() > count) {
                allQuestions = allQuestions.subList(0, count);
            }
        }

        Map<String, Object> result = new HashMap<>();
        result.put("questions", allQuestions);
        result.put("total", allQuestions.size());

        return result;
    }

    /**
     * 开始挑战（创建挑战记录）
     */
    @Override
    @Transactional
    public Map<String, Object> startChallenge(Integer userId, String mode, Integer questionSetId,
                                               List<Integer> questionIds, Integer timeLimit) {
        // 生成挑战ID（UUID）
        String challengeId = UUID.randomUUID().toString().replace("-", "");

        // 创建挑战记录
        Challenge challenge = new Challenge();
        challenge.setChallengeId(challengeId);
        challenge.setUserId(userId);
        challenge.setMode(mode);
        challenge.setQuestionSetId(questionSetId);
        challenge.setTimeLimit(timeLimit);
        challenge.setTotalCount(questionIds != null ? questionIds.size() : 0);
        challenge.setStatus(0); // 进行中
        challenge.setCreateTime(LocalDateTime.now());

        this.save(challenge);

        // 保存挑战题目关联
        if (questionIds != null && !questionIds.isEmpty()) {
            for (int i = 0; i < questionIds.size(); i++) {
                ChallengeQuestion challengeQuestion = new ChallengeQuestion();
                challengeQuestion.setChallengeId(challengeId);
                challengeQuestion.setQuestionId(questionIds.get(i));
                challengeQuestion.setQuestionOrder(i);
                challengeQuestion.setCompleted(0);
                challengeQuestion.setCreateTime(LocalDateTime.now());
                challengeQuestionMapper.insert(challengeQuestion);
            }
        }

        // 获取题目详情
        List<QuestionBank> questions = new ArrayList<>();
        if (questionIds != null && !questionIds.isEmpty()) {
            LambdaQueryWrapper<QuestionBank> wrapper = new LambdaQueryWrapper<>();
            wrapper.in(QuestionBank::getId, questionIds);
            questions = questionBankMapper.selectList(wrapper);
            
            // 按照 questionIds 的顺序排序
            Map<Integer, QuestionBank> questionMap = questions.stream()
                    .collect(Collectors.toMap(QuestionBank::getId, q -> q));
            questions = questionIds.stream()
                    .map(questionMap::get)
                    .filter(Objects::nonNull)
                    .collect(Collectors.toList());
        }

        Map<String, Object> result = new HashMap<>();
        result.put("challengeId", challengeId);
        result.put("questions", questions);
        result.put("timeLimit", timeLimit);

        return result;
    }

    /**
     * 提交挑战结果
     * 包含安全验证：
     * 1. 验证用户身份（必须是挑战的创建者）
     * 2. 验证挑战是否已提交（防止重复提交）
     * 3. 验证完成题目数不超过总题目数
     * 4. 验证使用时间不超过时间限制
     * 
     * 计分规则：每个字母或数字识别成功加10分，不设置最高分数限制
     */
    @Override
    @Transactional
    public Map<String, Object> submitChallenge(Integer userId, String challengeId, Integer score, 
                                                Integer completedCount, Integer timeUsed) {
        // 查询挑战记录
        LambdaQueryWrapper<Challenge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Challenge::getChallengeId, challengeId);
        Challenge challenge = this.getOne(wrapper);

        // 验证1：挑战记录是否存在
        if (challenge == null) {
            throw new RuntimeException("挑战记录不存在");
        }

        // 验证2：用户身份验证（必须是挑战的创建者）
        if (!challenge.getUserId().equals(userId)) {
            throw new RuntimeException("无权提交此挑战结果");
        }

        // 验证3：挑战是否已经提交过（防止重复提交）
        if (challenge.getStatus() != null && challenge.getStatus() == 1) {
            throw new RuntimeException("该挑战已经提交过，不能重复提交");
        }

        // 验证4：分数不能为负数
        if (score < 0) {
            throw new RuntimeException("分数不能为负数");
        }

        // 验证5：完成题目数不能超过总题目数
        if (completedCount < 0 || completedCount > challenge.getTotalCount()) {
            throw new RuntimeException("完成题目数异常，不能超过总题目数 " + challenge.getTotalCount());
        }

        // 验证6：使用时间不能超过时间限制
        if (timeUsed < 0 || timeUsed > challenge.getTimeLimit()) {
            throw new RuntimeException("使用时间异常，不能超过时间限制 " + challenge.getTimeLimit() + " 秒");
        }

        // 更新挑战记录
        challenge.setScore(score);
        challenge.setCompletedCount(completedCount);
        challenge.setTimeUsed(timeUsed);
        challenge.setStatus(1); // 已完成
        challenge.setFinishTime(LocalDateTime.now());
        this.updateById(challenge);

        // 计算准确率
        double accuracy = challenge.getTotalCount() > 0 
                ? (double) completedCount / challenge.getTotalCount() 
                : 0.0;

        // 评级
        String rank = "一般";
        if (accuracy >= 0.9) {
            rank = "优秀";
        } else if (accuracy >= 0.7) {
            rank = "良好";
        } else if (accuracy >= 0.5) {
            rank = "及格";
        }

        Map<String, Object> result = new HashMap<>();
        result.put("challengeId", challengeId);
        
        Map<String, Object> resultData = new HashMap<>();
        resultData.put("score", score);
        resultData.put("completedCount", completedCount);
        resultData.put("totalCount", challenge.getTotalCount());
        resultData.put("timeUsed", timeUsed);
        resultData.put("accuracy", accuracy);
        resultData.put("rank", rank);
        
        result.put("result", resultData);

        return result;
    }

    /**
     * 获取挑战历史记录（分页）
     */
    @Override
    public Map<String, Object> getChallengeHistory(Integer userId, Long pageNo, Long pageSize) {
        LambdaQueryWrapper<Challenge> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Challenge::getUserId, userId);
        wrapper.orderByDesc(Challenge::getCreateTime);

        Page<Challenge> page = new Page<>(pageNo, pageSize);
        this.page(page, wrapper);

        Map<String, Object> result = new HashMap<>();
        result.put("total", page.getTotal());
        result.put("rows", page.getRecords());

        return result;
    }
}

