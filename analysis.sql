-- ============================================
-- 豆瓣 Top250 数据分析
-- ============================================

-- 1. 总览
DELETE FROM movies WHERE title LIKE '测试%';
SELECT
    COUNT(*) AS 电影总数,
    ROUND(AVG(score)::numeric, 2) AS 平均分,
    MAX(score) AS 最高分,
    MIN(score) AS 最低分
FROM movies;

-- 2. Top 10 高分电影（评分相同按评价人数排序）
SELECT
    rank AS 排名,
    title AS 电影名,
    score AS 评分,
    votes AS 评价人数,
    quote AS 简介
FROM movies
ORDER BY score DESC, votes DESC
LIMIT 10;

-- 3. 评分分布 —— FLOOR(score) 分段
SELECT
    FLOOR(score) AS 分数段,
    COUNT(*) AS 电影数量
FROM movies
GROUP BY FLOOR(score)
ORDER BY 分数段 DESC;

-- 4. 窗口函数：评分排名 vs 人气排名，找"口碑好但小众"
WITH ranked_movies AS (
    SELECT
        title,
        score,
        votes,
        RANK() OVER (ORDER BY score DESC) AS 评分排名,
        RANK() OVER (ORDER BY votes DESC) AS 人气排名
    FROM movies
)
SELECT
    title AS 电影名,
    score AS 评分,
    votes AS 评价人数,
    评分排名,
    人气排名,
    (人气排名 - 评分排名) AS 排名差
FROM ranked_movies
WHERE 评分排名 <= 20
ORDER BY 评分排名;

-- 5. 评分 Top10 vs 人气 Top10 重合几部
WITH top_score AS (
    SELECT title FROM movies ORDER BY score DESC, votes DESC LIMIT 10
),
top_votes AS (
    SELECT title FROM movies ORDER BY votes DESC LIMIT 10
)
SELECT COUNT(*) AS 重合数量
FROM top_score
WHERE title IN (SELECT title FROM top_votes);
