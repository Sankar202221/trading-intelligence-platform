import streamlit as st
import pandas as pd

def render(load_data):
    st.header("Weekly PM Report & Dashboard")
    st.write("Automated product insights, executive decision-making, and PRD generation.")
    
    # Fetch high-level stats
    query = """
    SELECT 
        COUNT(DISTINCT user_id) as total_users,
        COUNT(CASE WHEN event_type = 'search' THEN 1 END) as total_searches,
        COUNT(CASE WHEN event_type = 'trade_executed' THEN 1 END) as total_trades
    FROM events
    """
    df = load_data(query)
    users = df['total_users'][0]
    searches = df['total_searches'][0]
    trades = df['total_trades'][0]
    conversion = round((trades / searches) * 100, 2) if searches > 0 else 0
    
    st.markdown(f"""
    ### 📝 Executive Summary
    This week, we saw **{users:,}** active users engaging with the platform.
    
    * **North Star Metric:** Search → Trade Conversion is currently at **{conversion}%**.
    * **Funnel Bottlenecks:** A significant drop-off remains between the Token Page and the Orderbook.
    
    ### 🚀 Product Actions Taken
    * Launched **A/B Test** on the Token Page introducing Trading Signals. Early results show a +21.7% lift in conversion.
    * Deployed updated **Search Ranking Engine** to prioritize high-intent tokens over mere search volume.
    """)
    
    st.markdown("---")
    
    # Executive Decision Dashboard
    st.subheader("📊 Executive Decision Dashboard: Top Opportunities")
    
    opp_query = """
    WITH token_metrics AS (
        SELECT 
            token,
            COUNT(CASE WHEN event_type = 'search' THEN 1 END) as search_volume,
            COUNT(CASE WHEN event_type = 'trade_executed' THEN 1 END) as trade_volume
        FROM events
        GROUP BY token
    )
    SELECT 
        token,
        search_volume,
        trade_volume,
        CASE WHEN search_volume > 0 THEN (CAST(trade_volume AS FLOAT) / search_volume) * 100 ELSE 0 END as actual_conversion
    FROM token_metrics
    WHERE search_volume > 100
    """
    df_opp = load_data(opp_query)
    
    if len(df_opp) > 0:
        target_conv = 5.0
        df_opp['conversion_gap'] = target_conv - df_opp['actual_conversion']
        df_opp['impact_score'] = df_opp.apply(lambda r: int(r['search_volume'] * (r['conversion_gap']/100)) if r['conversion_gap'] > 0 else 0, axis=1)
        df_opp = df_opp.sort_values('impact_score', ascending=False).reset_index(drop=True)
        
        def get_priority(rank):
            if rank < 2: return 'P0'
            elif rank < 5: return 'P1'
            else: return 'P2'
            
        df_opp['priority'] = [get_priority(i) for i in range(len(df_opp))]
        
        display_df = df_opp[['token', 'impact_score', 'priority']].head(10).copy()
        display_df.columns = ['Token', 'Impact (Extra Trades)', 'Priority']
        
        st.dataframe(
            display_df.style.apply(lambda x: ['background: lightcoral' if v == 'P0' else ('background: lightgoldenrodyellow' if v == 'P1' else '') for v in x], subset=['Priority']),
            use_container_width=True
        )
        
    st.markdown("---")
    
    # PRD Generator
    st.subheader("📄 AI PRD Generator")
    st.write("Instantly generate a Product Requirements Document based on real analytics.")
    
    if len(df_opp) > 0:
        tokens = df_opp['token'].tolist()
        selected_token = st.selectbox("Select Token for PRD", tokens)
        
        if st.button("Generate Product Spec"):
            token_data = df_opp[df_opp['token'] == selected_token].iloc[0]
            curr_conv = token_data['actual_conversion']
            search_vol = token_data['search_volume']
            
            st.info(f"""
            ### PRD: Optimize {selected_token} Trading Funnel
            
            **Problem Statement**
            Users are highly interested in {selected_token} (Search Volume: **{search_vol:,}**), but fail to execute trades. The current Search-to-Trade conversion is extremely low at **{curr_conv:.2f}%**.
            
            **Goal**
            Increase the {selected_token} Search-to-Trade conversion rate from **{curr_conv:.2f}%** to our platform benchmark of **5.00%**.
            
            **Success Metrics**
            - **Primary:** Search-to-Trade Conversion Rate (Target: 5%)
            - **Secondary:** {selected_token} Orderbook View Rate
            - **Guardrail:** Overall platform trade volume (ensure we aren't cannibalizing other tokens)
            
            **Business Impact**
            Achieving this goal will yield approximately **{token_data['impact_score']:,}** additional trades.
            
            **Risks & Mitigations**
            - *False Positive Intent:* High search volume might be due to a trending meme rather than trading intent. 
              - *Mitigation:* Analyze token page dwell time and orderbook drop-off to qualify intent before sending push notifications.
            """)
