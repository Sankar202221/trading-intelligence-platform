-- Search to Trade Funnel

WITH funnel_stages AS (
    SELECT
        COUNT(CASE WHEN event_type = 'search' THEN 1 END) as searches,
        COUNT(CASE WHEN event_type = 'view_token_page' THEN 1 END) as token_views,
        COUNT(CASE WHEN event_type = 'view_orderbook' THEN 1 END) as orderbooks,
        COUNT(CASE WHEN event_type = 'trade_executed' THEN 1 END) as trades
    FROM events
)
SELECT 
    searches,
    token_views,
    orderbooks,
    trades,
    ROUND(CAST(token_views AS FLOAT) / NULLIF(searches, 0) * 100, 2) as pct_to_page,
    ROUND(CAST(orderbooks AS FLOAT) / NULLIF(token_views, 0) * 100, 2) as pct_to_orderbook,
    ROUND(CAST(trades AS FLOAT) / NULLIF(orderbooks, 0) * 100, 2) as pct_to_trade,
    ROUND(CAST(trades AS FLOAT) / NULLIF(searches, 0) * 100, 2) as overall_conversion
FROM funnel_stages;
