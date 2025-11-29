package com.diy.sys.service.challenge;

import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.entity.challenge.Challenge;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;
import java.util.Map;

/**
 * <p>
 * 挑战服务接口
 * </p>
 *
 * @author youzi
 * @since 2024
 */
public interface IChallengeService extends IService<Challenge> {

    /**
     * 根据条件查询题目
     * 
     * @param mode 挑战模式：random/questionSet
     * @param questionSetId 题库ID（questionSet模式必填）
     * @param types 题目类型列表（random模式必填）：1-单词，2-中文，3-数字
     * @param difficulties 难度列表（可选）：1-简单，2-中等，3-困难
     * @param count 题目数量（随机模式或题库随机模式）
     * @param random 是否随机（questionSet模式）
     * @return 题目列表
     */
    Map<String, Object> queryQuestions(String mode, Integer questionSetId, List<Integer> types, 
                                       List<Integer> difficulties, Integer count, Boolean random);

    /**
     * 开始挑战（创建挑战记录）
     * 
     * @param userId 用户ID
     * @param mode 挑战模式
     * @param questionSetId 题库ID（题库模式）
     * @param questionIds 题目ID列表
     * @param timeLimit 时间限制（秒）
     * @return 挑战记录和题目列表
     */
    Map<String, Object> startChallenge(Integer userId, String mode, Integer questionSetId, 
                                       List<Integer> questionIds, Integer timeLimit);

    /**
     * 提交挑战结果
     * 
     * @param userId 用户ID（用于验证挑战归属）
     * @param challengeId 挑战ID
     * @param score 得分
     * @param completedCount 完成题目数
     * @param timeUsed 使用时间（秒）
     * @return 挑战结果统计
     */
    Map<String, Object> submitChallenge(Integer userId, String challengeId, Integer score, 
                                         Integer completedCount, Integer timeUsed);

    /**
     * 获取挑战历史记录（分页）
     * 
     * @param userId 用户ID
     * @param pageNo 页码
     * @param pageSize 每页大小
     * @return 分页结果
     */
    Map<String, Object> getChallengeHistory(Integer userId, Long pageNo, Long pageSize);

    /**
     * 获取所有用户的挑战记录（管理员接口，分页）
     * 
     * @param userId 用户ID（可选，用于筛选特定用户）
     * @param mode 挑战模式（可选）：random/questionSet
     * @param status 状态（可选）：0-进行中，1-已完成，2-已放弃
     * @param pageNo 页码
     * @param pageSize 每页大小
     * @return 分页结果（包含用户信息）
     */
    Map<String, Object> getAllChallengeHistory(Integer userId, String mode, Integer status, Long pageNo, Long pageSize);
    
    /**
     * 获取所有有过挑战的用户列表
     * 
     * @return 用户列表
     */
    List<User> getUsersWithChallenges();
}

