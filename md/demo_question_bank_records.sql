-- Demo questions for the question list page.
-- Target table: x_question_bank
-- type: 1 = word, 2 = Chinese, 3 = number
-- difficulty: 1 = easy, 2 = medium, 3 = hard

CREATE TABLE IF NOT EXISTS x_question_bank_demo_backup_20260509 AS
SELECT *
FROM x_question_bank;

INSERT INTO x_question_bank (content, type, difficulty, pinyin, img_url, level_group, status)
SELECT v.content, v.type, v.difficulty, v.pinyin, v.img_url, v.level_group, v.status
FROM (
  SELECT '谢谢' AS content, 2 AS type, 1 AS difficulty, 'Xiexie' AS pinyin, NULL AS img_url, '1' AS level_group, 1 AS status
  UNION ALL SELECT '早上好', 2, 1, 'Zaoshanghao', NULL, '1', 1
  UNION ALL SELECT '晚上好', 2, 1, 'Wanshanghao', NULL, '1', 1
  UNION ALL SELECT '再见', 2, 1, 'Zaijian', NULL, '1', 1
  UNION ALL SELECT '朋友', 2, 1, 'Pengyou', NULL, '1', 1
  UNION ALL SELECT '家人', 2, 1, 'Jiaren', NULL, '1', 1
  UNION ALL SELECT '学校', 2, 1, 'Xuexiao', NULL, '1', 1
  UNION ALL SELECT '老师', 2, 1, 'Laoshi', NULL, '1', 1
  UNION ALL SELECT '学生', 2, 1, 'Xuesheng', NULL, '1', 1
  UNION ALL SELECT '开心', 2, 1, 'Kaixin', NULL, '1', 1

  UNION ALL SELECT '医院', 2, 2, 'Yiyuan', NULL, '2', 1
  UNION ALL SELECT '帮助', 2, 2, 'Bangzhu', NULL, '2', 1
  UNION ALL SELECT '学习', 2, 2, 'Xuexi', NULL, '2', 1
  UNION ALL SELECT '工作', 2, 2, 'Gongzuo', NULL, '2', 1
  UNION ALL SELECT '运动', 2, 2, 'Yundong', NULL, '2', 1
  UNION ALL SELECT '天气', 2, 2, 'Tianqi', NULL, '2', 1
  UNION ALL SELECT '手机', 2, 2, 'Shouji', NULL, '2', 1
  UNION ALL SELECT '电脑', 2, 2, 'Diannao', NULL, '2', 1
  UNION ALL SELECT '图书馆', 2, 2, 'Tushuguan', NULL, '2', 1
  UNION ALL SELECT '公共汽车', 2, 2, 'Gonggongqiche', NULL, '2', 1

  UNION ALL SELECT '自我介绍', 2, 3, 'Ziwojieshao', NULL, '3', 1
  UNION ALL SELECT '请再说一遍', 2, 3, 'Qingzaishuoyibian', NULL, '3', 1
  UNION ALL SELECT '我需要帮助', 2, 3, 'Woxuyaobangzhu', NULL, '3', 1
  UNION ALL SELECT '今天星期几', 2, 3, 'Jintianxingqiji', NULL, '3', 1
  UNION ALL SELECT '明天见', 2, 3, 'Mingtianjian', NULL, '3', 1
  UNION ALL SELECT '我喜欢学习手语', 2, 3, 'Woxihuanxuexishouyu', NULL, '3', 1
  UNION ALL SELECT '请问洗手间在哪里', 2, 3, 'Qingwenxishoujianzainali', NULL, '3', 1
  UNION ALL SELECT '我们一起努力', 2, 3, 'Womenyiqinuli', NULL, '3', 1

  UNION ALL SELECT 'HELLO', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'THANKS', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'GOOD', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'YES', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'NO', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'LOVE', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'HOME', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'BOOK', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'WATER', 1, 1, NULL, NULL, '1', 1
  UNION ALL SELECT 'FOOD', 1, 1, NULL, NULL, '1', 1

  UNION ALL SELECT 'FAMILY', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'SCHOOL', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'FRIEND', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'MORNING', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'EVENING', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'TEACHER', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'STUDENT', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'COMPUTER', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'HOSPITAL', 1, 2, NULL, NULL, '2', 1
  UNION ALL SELECT 'LIBRARY', 1, 2, NULL, NULL, '2', 1

  UNION ALL SELECT 'COMMUNICATION', 1, 3, NULL, NULL, '3', 1
  UNION ALL SELECT 'TRANSLATION', 1, 3, NULL, NULL, '3', 1
  UNION ALL SELECT 'RECOGNITION', 1, 3, NULL, NULL, '3', 1
  UNION ALL SELECT 'ACCESSIBILITY', 1, 3, NULL, NULL, '3', 1
  UNION ALL SELECT 'CONFIDENCE', 1, 3, NULL, NULL, '3', 1
  UNION ALL SELECT 'CHALLENGE', 1, 3, NULL, NULL, '3', 1
  UNION ALL SELECT 'PRACTICE', 1, 3, NULL, NULL, '3', 1
  UNION ALL SELECT 'PROGRESS', 1, 3, NULL, NULL, '3', 1

  UNION ALL SELECT '1024', 3, 1, NULL, NULL, '1', 1
  UNION ALL SELECT '2024', 3, 1, NULL, NULL, '1', 1
  UNION ALL SELECT '8888', 3, 1, NULL, NULL, '1', 1
  UNION ALL SELECT '9999', 3, 1, NULL, NULL, '1', 1
  UNION ALL SELECT '10086', 3, 1, NULL, NULL, '1', 1
  UNION ALL SELECT '123123', 3, 1, NULL, NULL, '1', 1
  UNION ALL SELECT '456789', 3, 1, NULL, NULL, '1', 1
  UNION ALL SELECT '987654', 3, 1, NULL, NULL, '1', 1

  UNION ALL SELECT '135790', 3, 2, NULL, NULL, '2', 1
  UNION ALL SELECT '246810', 3, 2, NULL, NULL, '2', 1
  UNION ALL SELECT '314159', 3, 2, NULL, NULL, '2', 1
  UNION ALL SELECT '271828', 3, 2, NULL, NULL, '2', 1
  UNION ALL SELECT '5201314', 3, 2, NULL, NULL, '2', 1
  UNION ALL SELECT '1314521', 3, 2, NULL, NULL, '2', 1
  UNION ALL SELECT '20260509', 3, 2, NULL, NULL, '2', 1
  UNION ALL SELECT '12345678', 3, 2, NULL, NULL, '2', 1

  UNION ALL SELECT '100200300', 3, 3, NULL, NULL, '3', 1
  UNION ALL SELECT '987654321', 3, 3, NULL, NULL, '3', 1
  UNION ALL SELECT '1123581321', 3, 3, NULL, NULL, '3', 1
  UNION ALL SELECT '3141592653', 3, 3, NULL, NULL, '3', 1
) v
WHERE NOT EXISTS (
  SELECT 1
  FROM x_question_bank q
  WHERE q.content = v.content
    AND q.type = v.type
    AND q.level_group = v.level_group
);

SELECT
  id,
  content,
  type,
  difficulty,
  pinyin,
  level_group,
  status
FROM x_question_bank
ORDER BY id DESC
LIMIT 20;

-- Optional rollback:
/*
DELETE q
FROM x_question_bank q
LEFT JOIN x_question_bank_demo_backup_20260509 b ON b.id = q.id
WHERE b.id IS NULL;
*/
