import streamlit as st
import pandas as pd
import plotly.express as px

def render(load_data):
    st.header("KPI Dashboard for Execution")
    st.write("Track top level metrics over time.")
    
    # Simple overall KPIs
    query_totals = """
    SELECT 
        COUNT(DISTINCT user_id) as total_users,
        COUNT(*) as total_events,
        COUNT(CASE WHEN event_type = 'trade_executed' THEN 1 END) as total_trades
    FROM events
    """
    df_totals = load_data(query_totals)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Active Users", f"{df_totals['total_users'][0]:,}")
    col2.metric("Total Events", f"{df_totals['total_events'][0]:,}")
    col3.metric("Total Trades Executed", f"{df_totals['total_trades'][0]:,}")
    
    st.subheader("Daily Search & Trade Volume")
    query_daily = """
    SELECT 
        DATE(timestamp) as date,
        COUNT(CASE WHEN event_type = 'search' THEN 1 END) as searches,
        COUNT(CASE WHEN event_type = 'trade_executed' THEN 1 END) as trades
    FROM events
    GROUP BY DATE(timestamp)
    ORDER BY date
    """
    df_daily = load_data(query_daily)
    
    if len(df_daily) > 0:
        fig = px.line(df_daily, x='date', y=['searches', 'trades'], title="Searches vs Trades over time")
        st.plotly_chart(fig, use_container_width=True)
        
    st.subheader("Day 1 Retention")
    query_retention = """
    WITH first_activity AS (
        SELECT user_id, MIN(DATE(timestamp)) as first_date
        FROM events
        GROUP BY user_id
    ),
    activity_after_d1 AS (
        SELECT DISTINCT e.user_id
        FROM events e
        JOIN first_activity fa ON e.user_id = fa.user_id
        WHERE DATE(e.timestamp) = DATE(fa.first_date, '+1 day')
    )
    SELECT 
        COUNT(fa.user_id) as total_users,
        COUNT(a.user_id) as retained_users,
        ROUND(CAST(COUNT(a.user_id) AS FLOAT) / COUNT(fa.user_id) * 100, 2) as d1_retention_rate
    FROM first_activity fa
    LEFT JOIN activity_after_d1 a ON fa.user_id = a.user_id
    """
    df_retention = load_data(query_retention)
    if len(df_retention) > 0:
        rate = df_retention['d1_retention_rate'][0]
        st.metric("Day 1 Retention Rate", f"{rate}%")
