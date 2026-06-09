import streamlit as st
import pandas as pd
import sqlite3
import config
from components import search_analytics, funnel, segmentation, trending, kpis, recommendations, ab_testing, pm_report, opportunity, retention

st.set_page_config(page_title="Binance Trading Intelligence Platform", layout="wide", page_icon="📈")

st.title("Binance Trading Intelligence Platform")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Feature", 
    [
        "KPI Dashboard for Execution", 
        "Search Analytics", 
        "Search → Trade Funnel", 
        "User Segmentation", 
        "Search Ranking Engine", 
        "Product Recommendations", 
        "A/B Testing Module", 
        "Search-to-Trade Opportunity Engine",
        "Cohort Retention",
        "Weekly PM Report"
    ]
)

@st.cache_data
def load_data(query):
    conn = sqlite3.connect(config.DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

if page == "KPI Dashboard for Execution":
    kpis.render(load_data)
elif page == "Search Analytics":
    search_analytics.render(load_data)
elif page == "Search → Trade Funnel":
    funnel.render(load_data)
elif page == "User Segmentation":
    segmentation.render(load_data)
elif page == "Search Ranking Engine":
    trending.render(load_data)
elif page == "Product Recommendations":
    recommendations.render(load_data)
elif page == "A/B Testing Module":
    ab_testing.render(load_data)
elif page == "Search-to-Trade Opportunity Engine":
    opportunity.render(load_data)
elif page == "Cohort Retention":
    retention.render(load_data)
elif page == "Weekly PM Report":
    pm_report.render(load_data)

st.sidebar.markdown("---")
st.sidebar.info("Data is generated synthetically to simulate a Binance-like environment.")
