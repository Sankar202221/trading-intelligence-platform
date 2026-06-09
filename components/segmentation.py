import streamlit as st
import plotly.express as px

def render(load_data):
    st.header("Feature 3: User Segmentation")
    st.write("Analyze different user cohorts based on their trading behavior.")
    
    query = """
    SELECT 
        u.segment,
        COUNT(DISTINCT u.user_id) as total_users,
        COUNT(CASE WHEN e.event_type = 'trade_executed' THEN 1 END) as total_trades,
        ROUND(CAST(COUNT(CASE WHEN e.event_type = 'trade_executed' THEN 1 END) AS FLOAT) / COUNT(DISTINCT u.user_id), 2) as avg_trades_per_user
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.segment
    ORDER BY total_trades DESC
    """
    df = load_data(query)
    
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df, values='total_users', names='segment', title="User Base by Segment")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(df, x='segment', y='avg_trades_per_user', title="Average Trades per User", color='avg_trades_per_user', color_continuous_scale='Viridis')
        st.plotly_chart(fig2, use_container_width=True)
