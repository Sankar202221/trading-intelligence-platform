-- Trending Token Engine
-- Formula: 0.4 * Search Vol + 0.4 * Trade Vol + 0.2 * Watchlist Adds
-- Simplified version assuming linear scale for the raw counts.

WITH token_stats AS (
    SELECT 
        token,
        COUNT(CASE WHEN event_type = 'search' THEN 1 END) as search_vol,
        COUNT(CASE WHEN event_type = 'trade_executed' THEN 1 END) as trade_vol,
        COUNT(CASE WHEN event_type = 'add_to_watchlist' THEN 1 END) as watchlist_adds
    FROM events
    GROUP BY token
)
SELECT 
    token,
    search_vol,
    trade_vol,
    watchlist_adds,
    (0.4 * search_vol + 0.4 * trade_vol + 0.2 * watchlist_adds) as trend_score
FROM token_stats
ORDER BY trend_score DESC
LIMIT 10;
