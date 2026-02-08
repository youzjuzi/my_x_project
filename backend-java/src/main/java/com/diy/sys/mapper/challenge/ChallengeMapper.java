package com.diy.sys.mapper.challenge;

import com.diy.sys.entity.UserAndRole.User;
import com.diy.sys.entity.challenge.Challenge;
import com.diy.sys.entity.challenge.ChallengeWithUser;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * <p>
 * 挑战记录 Mapper 接口
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Mapper
public interface ChallengeMapper extends BaseMapper<Challenge> {
    
    /**
     * 查询挑战记录（包含用户信息）
     */
    List<ChallengeWithUser> getChallengeListWithUser(
            @Param("userId") Integer userId,
            @Param("mode") String mode,
            @Param("status") Integer status
    );
    
    /**
     * 获取所有有过挑战的用户列表
     */
    List<User> getUsersWithChallenges();
}

