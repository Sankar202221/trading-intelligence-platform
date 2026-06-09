-- Day 1 Retention Example (Simplified for SQLite)
-- Assuming join_date in users table and timestamp in events

WITH first_activity AS (
    SELECT user_id, MIN(DATE(timestamp)) as first_date
    FROM events
    GROUP BY user_id
),
activity_after_d1 AS (
    SELECT DISTINCT e.user_id
    FROM events e
    JOIN first_activity fa ON e.user_id = fa.user_id
    WHERE DATE(e.timestamp) = DATE(fa.first_date, '+1 day')
)
SELECT 
    COUNT(fa.user_id) as total_users,
    COUNT(a.user_id) as retained_users,
    ROUND(CAST(COUNT(a.user_id) AS FLOAT) / COUNT(fa.user_id) * 100, 2) as d1_retention_rate
FROM first_activity fa
LEFT JOIN activity_after_d1 a ON fa.user_id = a.user_id;
