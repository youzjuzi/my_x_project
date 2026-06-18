-- Demo data for the challenge history list.
-- Target table: x_challenge
-- Sort rule used by the page: create_time DESC

-- 1) Keep a one-time backup before changing demo data.
CREATE TABLE IF NOT EXISTS x_challenge_demo_backup_20260509 AS
SELECT *
FROM x_challenge;

CREATE TABLE IF NOT EXISTS x_user_demo_backup_20260509 AS
SELECT *
FROM x_user;

-- 2) Make several existing users look more natural for the demo.
-- Passwords are not changed.
UPDATE x_user
SET
  username = CASE id
    WHEN 2 THEN 'chenyu'
    WHEN 3 THEN 'linyue'
    WHEN 4 THEN 'wanghao'
    WHEN 5 THEN 'zhaomin'
    WHEN 10 THEN 'liuyang'
    WHEN 11 THEN 'qianrui'
    WHEN 20 THEN 'xujia'
    WHEN 21 THEN 'hanmei'
    WHEN 22 THEN 'zhouyi'
    ELSE username
  END,
  email = CASE id
    WHEN 2 THEN 'chenyu@example.com'
    WHEN 3 THEN 'linyue@example.com'
    WHEN 4 THEN 'wanghao@example.com'
    WHEN 5 THEN 'zhaomin@example.com'
    WHEN 10 THEN 'liuyang@example.com'
    WHEN 11 THEN 'qianrui@example.com'
    WHEN 20 THEN 'xujia@example.com'
    WHEN 21 THEN 'hanmei@example.com'
    WHEN 22 THEN 'zhouyi@example.com'
    ELSE email
  END,
  phone = CASE id
    WHEN 2 THEN '13810002002'
    WHEN 3 THEN '13810002003'
    WHEN 4 THEN '13810002004'
    WHEN 5 THEN '13810002005'
    WHEN 10 THEN '13810002010'
    WHEN 11 THEN '13810002011'
    WHEN 20 THEN '13810002020'
    WHEN 21 THEN '13810002021'
    WHEN 22 THEN '13810002022'
    ELSE phone
  END,
  status = 1,
  deleted = 0
WHERE id IN (2, 3, 4, 5, 10, 11, 20, 21, 22);

-- 3) Preview the current admin-heavy first page before changing it.
SELECT
  id,
  challenge_id,
  user_id,
  (SELECT username FROM x_user u WHERE u.id = x_challenge.user_id) AS username,
  mode,
  score,
  completed_count,
  total_count,
  time_used,
  time_limit,
  status,
  create_time,
  finish_time
FROM x_challenge
WHERE user_id = 1
ORDER BY create_time DESC, id DESC
LIMIT 10;

-- 4) Make the latest 10 admin rows look realistic for a demo.
-- The rows are reassigned to existing enabled users so the list no longer looks like one account generated everything.
-- Score follows the current game rule roughly: 10 points per completed item.
UPDATE x_challenge c
JOIN (
  SELECT
    id,
    ROW_NUMBER() OVER (ORDER BY create_time DESC, id DESC) AS rn
  FROM (
    SELECT id, create_time
    FROM x_challenge
    WHERE user_id = 1
    ORDER BY create_time DESC, id DESC
    LIMIT 10
  ) latest_rows
) d ON d.id = c.id
SET
  c.user_id = CASE d.rn
    WHEN 1 THEN 1
    WHEN 2 THEN IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 2 AND u.deleted = 0), 2, 1)
    WHEN 3 THEN IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 3 AND u.deleted = 0), 3, 1)
    WHEN 4 THEN IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 4 AND u.deleted = 0), 4, 1)
    WHEN 5 THEN IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 5 AND u.deleted = 0), 5, 1)
    WHEN 6 THEN IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 10 AND u.deleted = 0), 10, 1)
    WHEN 7 THEN IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 11 AND u.deleted = 0), 11, 1)
    WHEN 8 THEN IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 20 AND u.deleted = 0), 20, 1)
    WHEN 9 THEN IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 21 AND u.deleted = 0), 21, 1)
    ELSE IF(EXISTS(SELECT 1 FROM x_user u WHERE u.id = 22 AND u.deleted = 0), 22, 1)
  END,
  c.mode = CASE d.rn
    WHEN 3 THEN 'questionSet'
    WHEN 7 THEN 'questionSet'
    ELSE 'random'
  END,
  c.question_set_id = CASE
    WHEN d.rn IN (3, 7) THEN COALESCE(
      c.question_set_id,
      (SELECT MIN(qs.id) FROM x_question_set qs WHERE qs.status = 1),
      (SELECT MIN(qs2.id) FROM x_question_set qs2)
    )
    ELSE NULL
  END,
  c.total_count = CASE d.rn
    WHEN 1 THEN 10
    WHEN 2 THEN 12
    WHEN 3 THEN 8
    WHEN 4 THEN 15
    WHEN 5 THEN 10
    WHEN 6 THEN 6
    WHEN 7 THEN 12
    WHEN 8 THEN 10
    WHEN 9 THEN 8
    ELSE 14
  END,
  c.completed_count = CASE d.rn
    WHEN 1 THEN 9
    WHEN 2 THEN 10
    WHEN 3 THEN 8
    WHEN 4 THEN 11
    WHEN 5 THEN 7
    WHEN 6 THEN 6
    WHEN 7 THEN 9
    WHEN 8 THEN 5
    WHEN 9 THEN 3
    ELSE 0
  END,
  c.score = CASE d.rn
    WHEN 1 THEN 90
    WHEN 2 THEN 100
    WHEN 3 THEN 80
    WHEN 4 THEN 110
    WHEN 5 THEN 70
    WHEN 6 THEN 60
    WHEN 7 THEN 90
    WHEN 8 THEN 50
    WHEN 9 THEN 30
    ELSE 0
  END,
  c.time_limit = CASE d.rn
    WHEN 1 THEN 120
    WHEN 2 THEN 180
    WHEN 3 THEN 120
    WHEN 4 THEN 240
    WHEN 5 THEN 180
    WHEN 6 THEN 90
    WHEN 7 THEN 180
    WHEN 8 THEN 150
    WHEN 9 THEN 120
    ELSE 180
  END,
  c.time_used = CASE d.rn
    WHEN 1 THEN 96
    WHEN 2 THEN 142
    WHEN 3 THEN 88
    WHEN 4 THEN 211
    WHEN 5 THEN 136
    WHEN 6 THEN 74
    WHEN 7 THEN 163
    WHEN 8 THEN 129
    WHEN 9 THEN 67
    ELSE 0
  END,
  c.status = CASE d.rn
    WHEN 9 THEN 2
    WHEN 10 THEN 0
    ELSE 1
  END,
  c.create_time = CASE d.rn
    WHEN 1 THEN NOW() - INTERVAL 18 MINUTE
    WHEN 2 THEN NOW() - INTERVAL 2 HOUR
    WHEN 3 THEN NOW() - INTERVAL 5 HOUR
    WHEN 4 THEN NOW() - INTERVAL 1 DAY
    WHEN 5 THEN NOW() - INTERVAL 2 DAY
    WHEN 6 THEN NOW() - INTERVAL 3 DAY
    WHEN 7 THEN NOW() - INTERVAL 5 DAY
    WHEN 8 THEN NOW() - INTERVAL 7 DAY
    WHEN 9 THEN NOW() - INTERVAL 9 DAY
    ELSE NOW() - INTERVAL 12 DAY
  END,
  c.finish_time = CASE d.rn
    WHEN 10 THEN NULL
    ELSE DATE_ADD(
      CASE d.rn
        WHEN 1 THEN NOW() - INTERVAL 18 MINUTE
        WHEN 2 THEN NOW() - INTERVAL 2 HOUR
        WHEN 3 THEN NOW() - INTERVAL 5 HOUR
        WHEN 4 THEN NOW() - INTERVAL 1 DAY
        WHEN 5 THEN NOW() - INTERVAL 2 DAY
        WHEN 6 THEN NOW() - INTERVAL 3 DAY
        WHEN 7 THEN NOW() - INTERVAL 5 DAY
        WHEN 8 THEN NOW() - INTERVAL 7 DAY
        WHEN 9 THEN NOW() - INTERVAL 9 DAY
        ELSE NOW() - INTERVAL 12 DAY
      END,
      INTERVAL CASE d.rn
        WHEN 1 THEN 96
        WHEN 2 THEN 142
        WHEN 3 THEN 88
        WHEN 4 THEN 211
        WHEN 5 THEN 136
        WHEN 6 THEN 74
        WHEN 7 THEN 163
        WHEN 8 THEN 129
        WHEN 9 THEN 67
        ELSE 0
      END SECOND
    )
  END;

-- 5) Check the updated first page.
SELECT
  c.id,
  c.challenge_id,
  c.user_id,
  u.username,
  c.mode,
  c.question_set_id,
  c.score,
  c.completed_count,
  c.total_count,
  ROUND(c.completed_count / NULLIF(c.total_count, 0) * 100) AS accuracy_percent,
  c.time_used,
  c.time_limit,
  c.status,
  c.create_time,
  c.finish_time
FROM x_challenge c
LEFT JOIN x_user u ON u.id = c.user_id
ORDER BY c.create_time DESC, c.id DESC
LIMIT 10;

-- 6) Optional rollback for the changed rows.
-- Run this only if you want to restore the rows from the backup table.
/*
UPDATE x_user u
JOIN x_user_demo_backup_20260509 b ON b.id = u.id
SET
  u.username = b.username,
  u.password = b.password,
  u.email = b.email,
  u.phone = b.phone,
  u.status = b.status,
  u.avatar = b.avatar,
  u.deleted = b.deleted;

UPDATE x_challenge c
JOIN x_challenge_demo_backup_20260509 b ON b.id = c.id
SET
  c.challenge_id = b.challenge_id,
  c.user_id = b.user_id,
  c.mode = b.mode,
  c.question_set_id = b.question_set_id,
  c.time_limit = b.time_limit,
  c.time_used = b.time_used,
  c.score = b.score,
  c.completed_count = b.completed_count,
  c.total_count = b.total_count,
  c.status = b.status,
  c.create_time = b.create_time,
  c.finish_time = b.finish_time;
*/
