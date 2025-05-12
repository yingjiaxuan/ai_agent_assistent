-- 插入用户画像
INSERT INTO users (name, age, gender, education, occupation, city, interests, language, register_date, last_active)
VALUES
('张三', 24, '男', '本科', '留学生', '东京', '摄影,篮球,AI', '中文', '2024-06-01', '2024-06-10'),
('李四', 27, '女', '硕士', '工程师', '大阪', '旅行,美食,编程', '日语', '2024-05-15', '2024-06-09');

-- 插入对话历史
INSERT INTO conversations (user_id, role, content, timestamp, tags)
VALUES
(1, 'user', '我想找东京附近的樱花活动', '2024-06-01 10:00:00', '活动,樱花'),
(1, 'assistant', '推荐你去北大赏樱节，本周末开放。', '2024-06-01 10:00:05', '推荐,活动'),
(2, 'user', '大阪最近有什么美食节吗？', '2024-06-02 09:30:00', '美食,活动'),
(2, 'assistant', '大阪美食节将在6月10日举行，推荐参加。', '2024-06-02 09:30:10', '推荐,美食');

-- 插入记忆摘要
INSERT INTO memory_summaries (user_id, period, summary, created_at, revised_by_user, revised_content, revised_at)
VALUES
(1, '2024-05-25 ~ 2024-06-01', '本周主要关注实习申请，已完成Hitachi面试，计划周末赏樱。', '2024-06-01', 0, '', NULL),
(2, '2024-05-25 ~ 2024-06-01', '本周关注大阪美食节，准备与朋友一起参加。', '2024-06-01', 1, '准备和朋友一起参加美食节，期待新体验。', '2024-06-02');