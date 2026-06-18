-- Demo question sets for the question set list page.
-- Run md/demo_question_bank_records.sql first so these sets can pick up the new questions.

CREATE TABLE IF NOT EXISTS x_question_set_demo_backup_20260509 AS
SELECT *
FROM x_question_set;

CREATE TABLE IF NOT EXISTS x_set_question_demo_backup_20260509 AS
SELECT *
FROM x_set_question;

-- Add a few clean demo question sets. Keep the count small for presentation.
INSERT INTO x_question_set (name, cover, description, status)
SELECT v.name, NULL, v.description, 1
FROM (
  SELECT '中文基础入门' AS name, '适合初学者练习日常中文手语词汇' AS description
  UNION ALL SELECT '常用单词练习', '覆盖问候、生活、学习等常用英文单词'
  UNION ALL SELECT '数字专项训练', '从短数字到长数字串的识别训练'
  UNION ALL SELECT '综合进阶挑战', '混合中文、单词和数字，适合演示挑战模式'
) v
WHERE NOT EXISTS (
  SELECT 1
  FROM x_question_set s
  WHERE s.name = v.name
);

-- 中文基础入门
INSERT INTO x_set_question (question_id, set_id)
SELECT q.id, s.id
FROM x_question_bank q
JOIN x_question_set s ON s.name = '中文基础入门'
WHERE q.content IN ('谢谢', '早上好', '晚上好', '再见', '朋友', '家人', '学校', '老师', '学生', '开心')
  AND NOT EXISTS (
    SELECT 1
    FROM x_set_question sq
    WHERE sq.question_id = q.id
      AND sq.set_id = s.id
  );

-- 常用单词练习
INSERT INTO x_set_question (question_id, set_id)
SELECT q.id, s.id
FROM x_question_bank q
JOIN x_question_set s ON s.name = '常用单词练习'
WHERE q.content IN ('HELLO', 'THANKS', 'GOOD', 'YES', 'NO', 'LOVE', 'HOME', 'BOOK', 'WATER', 'FOOD', 'FAMILY', 'SCHOOL')
  AND NOT EXISTS (
    SELECT 1
    FROM x_set_question sq
    WHERE sq.question_id = q.id
      AND sq.set_id = s.id
  );

-- 数字专项训练
INSERT INTO x_set_question (question_id, set_id)
SELECT q.id, s.id
FROM x_question_bank q
JOIN x_question_set s ON s.name = '数字专项训练'
WHERE q.content IN ('1024', '2024', '8888', '9999', '10086', '123123', '456789', '987654', '135790', '246810')
  AND NOT EXISTS (
    SELECT 1
    FROM x_set_question sq
    WHERE sq.question_id = q.id
      AND sq.set_id = s.id
  );

-- 综合进阶挑战
INSERT INTO x_set_question (question_id, set_id)
SELECT q.id, s.id
FROM x_question_bank q
JOIN x_question_set s ON s.name = '综合进阶挑战'
WHERE q.content IN (
  '医院', '帮助', '图书馆', '公共汽车',
  'COMMUNICATION', 'TRANSLATION', 'RECOGNITION', 'CHALLENGE',
  '5201314', '20260509', '987654321', '3141592653'
)
  AND NOT EXISTS (
    SELECT 1
    FROM x_set_question sq
    WHERE sq.question_id = q.id
      AND sq.set_id = s.id
  );

SELECT
  s.id,
  s.name,
  s.description,
  s.status,
  COUNT(sq.id) AS question_count
FROM x_question_set s
LEFT JOIN x_set_question sq ON sq.set_id = s.id
WHERE s.name IN ('中文基础入门', '常用单词练习', '数字专项训练', '综合进阶挑战')
GROUP BY s.id, s.name, s.description, s.status
ORDER BY s.id DESC;

-- Optional rollback:
/*
DELETE sq
FROM x_set_question sq
LEFT JOIN x_set_question_demo_backup_20260509 b ON b.id = sq.id
WHERE b.id IS NULL;

DELETE s
FROM x_question_set s
LEFT JOIN x_question_set_demo_backup_20260509 b ON b.id = s.id
WHERE b.id IS NULL;
*/
