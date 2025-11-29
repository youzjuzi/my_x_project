-- ----------------------------
-- 挑战功能数据库表
-- ----------------------------

use xdb;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for x_challenge
-- 挑战记录表
-- ----------------------------
DROP TABLE IF EXISTS `x_challenge`;
CREATE TABLE `x_challenge` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `challenge_id` varchar(64) NOT NULL COMMENT '挑战ID（唯一标识，UUID）',
  `user_id` int NOT NULL COMMENT '用户ID',
  `mode` varchar(20) NOT NULL COMMENT '挑战模式：random-随机挑战，questionSet-选择题库',
  `question_set_id` int DEFAULT NULL COMMENT '题库ID（题库模式时使用）',
  `time_limit` int NOT NULL COMMENT '时间限制（秒）',
  `time_used` int DEFAULT NULL COMMENT '实际使用时间（秒）',
  `score` int DEFAULT NULL COMMENT '得分',
  `completed_count` int DEFAULT NULL COMMENT '完成题目数',
  `total_count` int NOT NULL COMMENT '总题目数',
  `status` int DEFAULT 0 COMMENT '状态：0-进行中，1-已完成，2-已放弃',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `finish_time` datetime DEFAULT NULL COMMENT '完成时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_challenge_id` (`challenge_id`) USING BTREE,
  KEY `idx_user_id` (`user_id`) USING BTREE,
  KEY `idx_create_time` (`create_time`) USING BTREE,
  KEY `idx_status` (`status`) USING BTREE
) ENGINE = InnoDB 
  AUTO_INCREMENT = 1 
  CHARACTER SET = utf8mb4 
  COLLATE = utf8mb4_0900_ai_ci 
  COMMENT = '挑战记录表' 
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for x_challenge_question
-- 挑战题目关联表
-- ----------------------------
DROP TABLE IF EXISTS `x_challenge_question`;
CREATE TABLE `x_challenge_question` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `challenge_id` varchar(64) NOT NULL COMMENT '挑战ID',
  `question_id` int NOT NULL COMMENT '题目ID',
  `question_order` int NOT NULL COMMENT '题目顺序（从0开始）',
  `completed` tinyint DEFAULT 0 COMMENT '是否完成：0-未完成，1-已完成',
  `time_spent` int DEFAULT NULL COMMENT '花费时间（秒）',
  `score` int DEFAULT NULL COMMENT '该题得分',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_challenge_id` (`challenge_id`) USING BTREE,
  KEY `idx_question_id` (`question_id`) USING BTREE,
  KEY `idx_challenge_order` (`challenge_id`, `question_order`) USING BTREE
) ENGINE = InnoDB 
  AUTO_INCREMENT = 1 
  CHARACTER SET = utf8mb4 
  COLLATE = utf8mb4_0900_ai_ci 
  COMMENT = '挑战题目关联表' 
  ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;

