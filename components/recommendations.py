import streamlit as st

def render(load_data):
    st.header("Feature 6: Automated Product Recommendations")
    st.write("Generates insights based on analytics data.")
    
    # Mocking an insight engine based on real SQL queries
    
    query_conversion = """
    WITH token_views AS (
        SELECT token, COUNT(*) as view_count FROM events WHERE event_type = 'view_token_page' GROUP BY token
    ),
    token_trades AS (
        SELECT token, COUNT(*) as trade_count FROM events WHERE event_type = 'trade_executed' GROUP BY token
    )
    SELECT v.token, v.view_count, COALESCE(t.trade_count, 0) as trade_count,
           ROUND(CAST(COALESCE(t.trade_count, 0) AS FLOAT) / v.view_count * 100, 2) as conversion_rate
    FROM token_views v LEFT JOIN token_trades t ON v.token = t.token
    ORDER BY conversion_rate ASC LIMIT 3
    """
    df_low_conv = load_data(query_conversion)
    
    query_high_search = """
    SELECT token, COUNT(*) as search_volume
    FROM events WHERE event_type = 'search' GROUP BY token ORDER BY search_volume DESC LIMIT 3
    """
    df_high_search = load_data(query_high_search)
    
    st.subheader("Insight Engine Output")
    
    for i, row in df_low_conv.iterrows():
        token = row['token']
        conv = row['conversion_rate']
        views = row['view_count']
        
        # See if this token is highly searched
        is_high_search = token in df_high_search['token'].values
        
        st.info(f"**Insight:** `{token}` has a very low Trade Conversion Rate of {conv}% (from {views} views).")
        
        if is_high_search:
            st.error(f"**Alert:** `{token}` is one of the most searched tokens, meaning we are losing significant potential volume.")
            
        st.success(f"**Recommendation:** Improve the `{token}` token information page. Consider adding localized news, clear project fundamentals, or a simpler buy widget.")
        st.markdown("---")
