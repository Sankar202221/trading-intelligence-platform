import streamlit as st

def render(load_data):
    st.header("Search Ranking Engine")
    st.write("Improves discovery of high-quality tokens instead of merely popular tokens by using normalized metrics.")
    st.latex(r"Score = 0.35 \times Search_{norm} + 0.30 \times Trade_{norm} + 0.20 \times Watchlist_{norm} + 0.15 \times Conversion_{norm}")
    
    query = """
    WITH token_stats AS (
        SELECT 
            token,
            COUNT(CASE WHEN event_type = 'search' THEN 1 END) as search_vol,
            COUNT(CASE WHEN event_type = 'trade_executed' THEN 1 END) as trade_vol,
            COUNT(CASE WHEN event_type = 'add_to_watchlist' THEN 1 END) as watchlist_adds
        FROM events
        GROUP BY token
    ),
    calc_stats AS (
        SELECT 
            token,
            CAST(search_vol AS FLOAT) as search_vol,
            CAST(trade_vol AS FLOAT) as trade_vol,
            CAST(watchlist_adds AS FLOAT) as watchlist_adds,
            CASE WHEN search_vol > 0 THEN (CAST(trade_vol AS FLOAT) / search_vol) * 100 ELSE 0 END as conversion_rate
        FROM token_stats
    ),
    min_max_stats AS (
        SELECT
            MIN(search_vol) as min_search, MAX(search_vol) as max_search,
            MIN(trade_vol) as min_trade, MAX(trade_vol) as max_trade,
            MIN(watchlist_adds) as min_watchlist, MAX(watchlist_adds) as max_watchlist,
            MIN(conversion_rate) as min_conv, MAX(conversion_rate) as max_conv
        FROM calc_stats
    ),
    normalized_stats AS (
        SELECT
            c.token,
            c.search_vol,
            c.trade_vol,
            c.watchlist_adds,
            c.conversion_rate,
            CASE WHEN m.max_search > m.min_search THEN (c.search_vol - m.min_search) / (m.max_search - m.min_search) ELSE 0 END as search_norm,
            CASE WHEN m.max_trade > m.min_trade THEN (c.trade_vol - m.min_trade) / (m.max_trade - m.min_trade) ELSE 0 END as trade_norm,
            CASE WHEN m.max_watchlist > m.min_watchlist THEN (c.watchlist_adds - m.min_watchlist) / (m.max_watchlist - m.min_watchlist) ELSE 0 END as watchlist_norm,
            CASE WHEN m.max_conv > m.min_conv THEN (c.conversion_rate - m.min_conv) / (m.max_conv - m.min_conv) ELSE 0 END as conversion_norm
        FROM calc_stats c
        CROSS JOIN min_max_stats m
    )
    SELECT 
        token,
        CAST(search_vol AS INTEGER) as search_vol,
        CAST(trade_vol AS INTEGER) as trade_vol,
        CAST(watchlist_adds AS INTEGER) as watchlist_adds,
        ROUND(conversion_rate, 2) as conversion_rate,
        ROUND((0.35 * search_norm + 0.30 * trade_norm + 0.20 * watchlist_norm + 0.15 * conversion_norm) * 100, 2) as trend_score
    FROM normalized_stats
    ORDER BY trend_score DESC
    LIMIT 10
    """
    df = load_data(query)
    
    st.dataframe(df.style.highlight_max(subset=['trend_score'], color='lightgreen'), use_container_width=True)
    
    st.subheader("Top Trending Tokens")
    for i, row in df.iterrows():
        st.markdown(f"**{i+1}. {row['token']}** (Score: {row['trend_score']})")

