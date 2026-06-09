-- User Segmentation Metrics
-- Calculates the number of users, total trades, and average trades per user in each segment

SELECT 
    u.segment,
    COUNT(DISTINCT u.user_id) as total_users,
    COUNT(CASE WHEN e.event_type = 'trade_executed' THEN 1 END) as total_trades,
    ROUND(CAST(COUNT(CASE WHEN e.event_type = 'trade_executed' THEN 1 END) AS FLOAT) / COUNT(DISTINCT u.user_id), 2) as avg_trades_per_user
FROM users u
LEFT JOIN events e ON u.user_id = e.user_id
GROUP BY u.segment
ORDER BY avg_trades_per_user DESC;
