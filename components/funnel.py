import streamlit as st
import plotly.graph_objects as go

def render(load_data):
    st.header("Search → Trade Funnel")
    st.write("Understand the drop-off at each stage of the trading funnel.")
    
    # Fetch unique values for filters
    filter_query = "SELECT DISTINCT country, device, segment FROM users"
    df_filters = load_data(filter_query)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        countries = df_filters['country'].dropna().unique().tolist()
        selected_country = st.selectbox("Country", ["All"] + countries)
        
    with col2:
        devices = df_filters['device'].dropna().unique().tolist()
        selected_device = st.selectbox("Device", ["All"] + devices)
        
    with col3:
        segments = df_filters['segment'].dropna().unique().tolist()
        selected_segment = st.selectbox("Segment", ["All"] + segments)
        
    # Build WHERE clause dynamically
    conditions = []
    if selected_country != "All":
        conditions.append(f"u.country = '{selected_country}'")
    if selected_device != "All":
        conditions.append(f"u.device = '{selected_device}'")
    if selected_segment != "All":
        conditions.append(f"u.segment = '{selected_segment}'")
        
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
        
    query = f"""
    WITH filtered_events AS (
        SELECT e.event_type 
        FROM events e
        JOIN users u ON e.user_id = u.user_id
        {where_clause}
    ),
    funnel_stages AS (
        SELECT
            COUNT(CASE WHEN event_type = 'search' THEN 1 END) as searches,
            COUNT(CASE WHEN event_type = 'view_token_page' THEN 1 END) as token_views,
            COUNT(CASE WHEN event_type = 'view_orderbook' THEN 1 END) as orderbooks,
            COUNT(CASE WHEN event_type = 'trade_executed' THEN 1 END) as trades
        FROM filtered_events
    )
    SELECT * FROM funnel_stages
    """
    
    df = load_data(query)
    
    if len(df) > 0 and df['searches'][0] > 0:
        counts = [int(df['searches'][0]), int(df['token_views'][0]), int(df['orderbooks'][0]), int(df['trades'][0])]
        stages = ["Searches", "Token Page Views", "Orderbook Views", "Trades Executed"]
        
        fig = go.Figure(go.Funnel(
            y = stages,
            x = counts,
            textinfo = "value+percent initial"
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Funnel Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Search to Token Page", f"{counts[1]/counts[0]*100:.1f}%")
        col2.metric("Token Page to Orderbook", f"{counts[2]/counts[1]*100:.1f}%" if counts[1] > 0 else "0.0%")
        col3.metric("Orderbook to Trade", f"{counts[3]/counts[2]*100:.1f}%" if counts[2] > 0 else "0.0%")
    else:
        st.warning("No data found for the selected filters.")
