-- Top searched tokens by total volume
SELECT 
    token,
    COUNT(*) as search_volume
FROM events
WHERE event_type = 'search'
GROUP BY token
ORDER BY search_volume DESC
LIMIT 10;

-- Searches by device
SELECT 
    u.device,
    COUNT(e.timestamp) as search_count
FROM events e
JOIN users u ON e.user_id = u.user_id
WHERE e.event_type = 'search'
GROUP BY u.device
ORDER BY search_count DESC;

-- Searches by country (Top 10)
SELECT 
    u.country,
    COUNT(e.timestamp) as search_count
FROM events e
JOIN users u ON e.user_id = u.user_id
WHERE e.event_type = 'search'
GROUP BY u.country
ORDER BY search_count DESC
LIMIT 10;
