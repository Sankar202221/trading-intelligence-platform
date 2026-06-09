import streamlit as st
import pandas as pd

def render(load_data):
    st.header("Search-to-Trade Opportunity Engine")
    st.write("Prioritize tokens by estimating the business impact of improving conversion rates.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        target_conversion = st.slider("Target Conversion Rate (%)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
    
    query = """
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
    
    df = load_data(query)
    
    if len(df) > 0:
        # Calculate impact
        df['target_conversion'] = target_conversion
        df['conversion_gap'] = df['target_conversion'] - df['actual_conversion']
        df['potential_trades'] = df.apply(lambda row: int(row['search_volume'] * (row['conversion_gap'] / 100)) if row['conversion_gap'] > 0 else 0, axis=1)
        
        # Sort by potential impact
        df = df.sort_values(by='potential_trades', ascending=False).reset_index(drop=True)
        
        # Assign Priority
        def get_priority(rank):
            if rank < 3: return 'P0'
            elif rank < 6: return 'P1'
            else: return 'P2'
        
        df['priority'] = [get_priority(i) for i in range(len(df))]
        
        st.subheader("Opportunity Ranking")
        
        display_df = df[['token', 'search_volume', 'actual_conversion', 'target_conversion', 'potential_trades', 'priority']].copy()
        display_df.columns = ['Token', 'Search Volume', 'Current Conv. (%)', 'Target Conv. (%)', 'Potential Extra Trades', 'Priority']
        display_df['Current Conv. (%)'] = display_df['Current Conv. (%)'].apply(lambda x: f"{x:.2f}%")
        display_df['Target Conv. (%)'] = display_df['Target Conv. (%)'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_df, use_container_width=True)
        
        if len(df) > 0:
            top_token = df.iloc[0]
            st.info(f"**Top Recommendation:** Focus on **{top_token['token']}**. It has a high search volume ({top_token['search_volume']:,}) but low conversion ({top_token['actual_conversion']:.1f}%). Reaching {target_conversion}% could yield **{top_token['potential_trades']:,}** additional trades.")
    else:
        st.warning("No data available.")
