-- Trade conversion rate by token

WITH token_views AS (
    SELECT token, COUNT(*) as view_count
    FROM events
    WHERE event_type = 'view_token_page'
    GROUP BY token
),
token_trades AS (
    SELECT token, COUNT(*) as trade_count
    FROM events
    WHERE event_type = 'trade_executed'
    GROUP BY token
)
SELECT 
    v.token,
    v.view_count,
    COALESCE(t.trade_count, 0) as trade_count,
    ROUND(CAST(COALESCE(t.trade_count, 0) AS FLOAT) / v.view_count * 100, 2) as conversion_rate
FROM token_views v
LEFT JOIN token_trades t ON v.token = t.token
ORDER BY conversion_rate DESC;
