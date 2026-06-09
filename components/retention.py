import streamlit as st
import pandas as pd
import plotly.express as px

def render(load_data):
    st.header("Cohort Retention Matrix")
    st.write("Track how often users return to the platform after their first visit.")
    
    # Calculate retention
    query = """
    WITH user_first_event AS (
        SELECT user_id, MIN(DATE(timestamp)) as first_date
        FROM events
        GROUP BY user_id
    ),
    user_activity AS (
        SELECT DISTINCT e.user_id, DATE(e.timestamp) as activity_date
        FROM events e
    ),
    cohort_activity AS (
        SELECT 
            f.user_id,
            f.first_date,
            a.activity_date,
            CAST(julianday(a.activity_date) - julianday(f.first_date) AS INTEGER) as days_since_first
        FROM user_first_event f
        JOIN user_activity a ON f.user_id = a.user_id
    ),
    cohort_sizes AS (
        SELECT first_date, COUNT(DISTINCT user_id) as cohort_size
        FROM user_first_event
        GROUP BY first_date
    ),
    retention_counts AS (
        SELECT 
            first_date,
            days_since_first,
            COUNT(DISTINCT user_id) as retained_users
        FROM cohort_activity
        GROUP BY first_date, days_since_first
    )
    SELECT 
        r.first_date as "Cohort",
        s.cohort_size as "Cohort Size",
        r.days_since_first as "Day",
        r.retained_users
    FROM retention_counts r
    JOIN cohort_sizes s ON r.first_date = s.first_date
    WHERE r.days_since_first IN (0, 1, 7, 30)
    ORDER BY r.first_date, r.days_since_first
    """
    
    df = load_data(query)
    
    if len(df) > 0:
        # Pivot the data
        pivot_df = df.pivot(index=["Cohort", "Cohort Size"], columns="Day", values="retained_users").reset_index()
        
        # Calculate percentages
        for day in [0, 1, 7, 30]:
            if day in pivot_df.columns:
                pivot_df[f"Day {day}"] = (pivot_df[day] / pivot_df["Cohort Size"] * 100).round(1)
            else:
                pivot_df[f"Day {day}"] = 0.0
                
        # Drop the raw counts
        columns_to_keep = ["Cohort", "Cohort Size", "Day 1", "Day 7", "Day 30"]
        
        # Only keep columns that actually exist in pivot_df (in case dataset spans <30 days)
        valid_cols = [c for c in columns_to_keep if c in pivot_df.columns]
        display_df = pivot_df[valid_cols].copy()
        
        # Format as percentages
        for col in ["Day 1", "Day 7", "Day 30"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%")
            
        st.dataframe(display_df.sort_values("Cohort", ascending=False), use_container_width=True)
        
        # Plot overall retention curve
        overall_query = """
        WITH user_first_event AS (
            SELECT user_id, MIN(DATE(timestamp)) as first_date
            FROM events
            GROUP BY user_id
        ),
        user_activity AS (
            SELECT DISTINCT e.user_id, DATE(e.timestamp) as activity_date
            FROM events e
        ),
        cohort_activity AS (
            SELECT 
                f.user_id,
                CAST(julianday(a.activity_date) - julianday(f.first_date) AS INTEGER) as days_since_first
            FROM user_first_event f
            JOIN user_activity a ON f.user_id = a.user_id
        )
        SELECT 
            days_since_first as "Day",
            COUNT(DISTINCT user_id) as retained_users
        FROM cohort_activity
        WHERE days_since_first <= 30
        GROUP BY days_since_first
        ORDER BY days_since_first
        """
        overall_df = load_data(overall_query)
        if len(overall_df) > 0:
            total_users = overall_df['retained_users'].iloc[0]
            overall_df['Retention Rate (%)'] = (overall_df['retained_users'] / total_users) * 100
            
            fig = px.line(overall_df, x='Day', y='Retention Rate (%)', title="Overall Retention Curve (Days 0-30)", markers=True)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough data to calculate retention.")
