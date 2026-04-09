import streamlit as st
import pandas as pd
import plotly.express as px
from database import engine
import json

st.set_page_config(page_title="Counter-Manipulator AI", layout="wide", page_icon="🛡️")

# Custom CSS for dark mode cyber-aesthetics
st.markdown("""
<style>
    .benign-badge { background-color: #1b5e20; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem;}
    .suspicious-badge { background-color: #f57f17; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem;}
    .critical-badge { background-color: #b71c1c; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem;}
    .reason-chip { background-color: #37474f; color: #eceff1; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-right: 4px; border: 1px solid #546e7a;}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SEnTRY: Counter-Manipulator AI")
st.markdown("Behavior-Based Manipulation Scoring & Operations Telemetry Dashboard")

def load_data():
    scores = pd.read_sql("SELECT * FROM source_risk_scores ORDER BY as_of_time DESC", engine)
    features = pd.read_sql("SELECT * FROM source_feature_snapshots ORDER BY as_of_time DESC", engine)
    events = pd.read_sql("SELECT * FROM interaction_events ORDER BY event_time DESC", engine)
    alerts = pd.read_sql("SELECT * FROM alerts ORDER BY created_at DESC", engine)
    sources = pd.read_sql("SELECT * FROM sources", engine)
    return scores, features, events, alerts, sources

try:
    scores_df, features_df, events_df, alerts_df, sources_df = load_data()
except Exception as e:
    st.error(f"Database connection error or uninitialized tables: {e}")
    st.stop()

if scores_df.empty or sources_df.empty:
    st.info("No tracking data available yet. Please run the event seeder and scoring pipeline.")
    st.stop()

# Build the main view: Latest Score per Source
latest_scores = scores_df.loc[scores_df.groupby('source_id')['as_of_time'].idxmax()]
# Join with sources
latest_scores = latest_scores.merge(sources_df, left_on='source_id', right_on='id', suffixes=('_score', '_source'))

# Layout
tab1, tab2, tab3 = st.tabs(["🚦 External Agents Overview", "📊 Feature Telemetry", "🚨 Operations Alerts"])

with tab1:
    st.subheader("Monitored Counterparties / Sources")
    
    # Sort by risk score descending
    latest_scores = latest_scores.sort_values(by='risk_score', ascending=False)
    
    for idx, row in latest_scores.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 3, 1])
            col1.markdown(f"**Key:** `{row['source_key']}`<br/>**Type:** {row['source_type']}", unsafe_allow_html=True)
            
            # Risk Score with color
            c = "#ff5252" if row['risk_score'] >= 70 else "#ffa400" if row['risk_score'] >= 35 else "#69f0ae"
            col2.markdown(f"<div style='font-size:1.8rem; color:{c};'>{row['risk_score']:.1f}</div>", unsafe_allow_html=True)
            
            # Label Badge
            if row['risk_label'] == 'benign':
                col3.markdown("<br/><span class='benign-badge'>BENIGN</span>", unsafe_allow_html=True)
            elif row['risk_label'] == 'suspicious':
                col3.markdown("<br/><span class='suspicious-badge'>SUSPICIOUS</span>", unsafe_allow_html=True)
            else:
                col3.markdown("<br/><span class='critical-badge'>MANUAL REVIEW</span>", unsafe_allow_html=True)
                
            # Reason Chips
            reasons = []
            if isinstance(row['reason_codes_json'], str):
                try:
                    reasons = json.loads(row['reason_codes_json'])
                except:
                    pass
            chips_html = "".join([f"<span class='reason-chip'>{r}</span>" for r in reasons])
            col4.markdown(f"<br/>{chips_html if chips_html else '-'}", unsafe_allow_html=True)
            
            # Detail Drawer Trigger (Expander)
            with st.expander("🔍 View Complete History & Events"):
                st.caption(f"Last Evaluation: {row['as_of_time']}")
                
                c_history, c_events = st.columns(2)
                
                # Historic scores trend
                source_scores = scores_df[scores_df['source_id'] == row['source_id']].sort_values(by='as_of_time')
                if len(source_scores) > 1:
                    fig = px.line(source_scores, x='as_of_time', y='risk_score', 
                                  title="Risk Score Trajectory", markers=True, height=250)
                    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                    c_history.plotly_chart(fig, use_container_width=True)
                else:
                    c_history.info("Not enough history for trend chart.")
                    
                # Recent raw events
                source_events = events_df[events_df['source_id'] == row['source_id']].head(10)
                if not source_events.empty:
                    c_events.write("**Latest Raw Interaction Events**")
                    c_events.dataframe(source_events[['event_time', 'event_type', 'proposal_size', 'success_flag', 'destination_address']], height=250)
                else:
                    c_events.write("No raw events found.")
            
        st.markdown("---")

with tab2:
    st.subheader("Feature Snapshot Forensics")
    selected_source = st.selectbox("Inspect Source Key", options=sources_df['source_key'].tolist())
    s_id = sources_df[sources_df['source_key'] == selected_source].iloc[0]['id']
    
    s_features = features_df[features_df['source_id'] == s_id].sort_values(by="as_of_time", ascending=False)
    if not s_features.empty:
        st.dataframe(s_features.head(50), use_container_width=True)
        
        c1, c2 = st.columns(2)
        fig_vol = px.bar(s_features, x='as_of_time', y='interaction_count', color='window_name', title="Interaction Volume by Window")
        c1.plotly_chart(fig_vol, use_container_width=True)
        
        fig_success = px.line(s_features, x='as_of_time', y='success_rate', color='window_name', markers=True, title="Success Rate Degradation")
        c2.plotly_chart(fig_success, use_container_width=True)
    else:
        st.info("No rolling window features calculated yet.")

with tab3:
    st.subheader("Active Operations Alerts")
    if not alerts_df.empty:
        active_alerts = alerts_df[alerts_df['status'] == 'open'].merge(sources_df, left_on='source_id', right_on='id', suffixes=('', '_source'))
        if active_alerts.empty:
            st.success("All clear. No active alerts.")
        else:
            for _, alert in active_alerts.sort_values(by='created_at', ascending=False).iterrows():
                if alert['severity'] == 'critical':
                    st.error(f"### 🚨 {alert['title']}\n**Time:** {alert['created_at']}\n\n**Details:** {alert['message']}\n\n**Agent:** `{alert['source_key']}`")
                else:
                    st.warning(f"### ⚠️ {alert['title']}\n**Time:** {alert['created_at']}\n\n**Details:** {alert['message']}\n\n**Agent:** `{alert['source_key']}`")
    else:
        st.success("No alerts generated yet in system history.")
