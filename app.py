import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ----------------- Configuration & Styling -----------------
st.set_page_config(page_title="Move: Urban Mobility Analytics", layout="wide")

# Custom CSS for the requested design (light grey bg, charcoal text, muted blue, lavender accents)
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
        color: #36454F;
    }
    .sidebar .sidebar-content {
        background: #e6e9ef;
    }
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #36454F !important;
    }
    .stMetric-value {
        color: #4a708b !important; /* Muted blue */
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E6E6FA; /* Lavender */
        color: #36454F !important;
        border-bottom: 3px solid #4a708b !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Data Loading -----------------
@st.cache_data
def load_data():
    conn = sqlite3.connect('move.db')
    
    rides = pd.read_sql_query("SELECT * FROM rides", conn)
    drivers = pd.read_sql_query("SELECT * FROM drivers", conn)
    riders = pd.read_sql_query("SELECT * FROM riders", conn)
    conn.close()
    
    # Preprocessing
    rides['request_time'] = pd.to_datetime(rides['request_time'])
    rides['pickup_time'] = pd.to_datetime(rides['pickup_time'])
    rides['completion_time'] = pd.to_datetime(rides['completion_time'])
    
    rides['hour'] = rides['request_time'].dt.hour
    rides['day_of_week'] = rides['request_time'].dt.day_name()
    rides['is_weekend'] = rides['request_time'].dt.dayofweek >= 5
    rides['date'] = rides['request_time'].dt.date
    
    return rides, drivers, riders

try:
    rides, drivers, riders = load_data()
except Exception as e:
    st.error(f"Error loading data. Make sure to run generate_data.py first. Details: {e}")
    st.stop()

# ----------------- Dashboard Sidebar -----------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3204/3204369.png", width=100)
st.sidebar.title("MOVE Analytics")
page = st.sidebar.radio("Navigation", ["Executive Overview", "Demand & Supply", "Rider Experience", "Pricing", "Geographic Analysis", "Insights"])

# Filters
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")
city_filter = st.sidebar.multiselect("Select City", rides['city'].unique(), default=rides['city'].unique())
is_weekend_filter = st.sidebar.selectbox("Day Type", ["All", "Weekday", "Weekend"])

# Apply filters
filtered_rides = rides[rides['city'].isin(city_filter)]
if is_weekend_filter == "Weekday":
    filtered_rides = filtered_rides[~filtered_rides['is_weekend']]
elif is_weekend_filter == "Weekend":
    filtered_rides = filtered_rides[filtered_rides['is_weekend']]

# Colors for Plotly
COLOR_MUTED_BLUE = '#4a708b'
COLOR_LAVENDER = '#E6E6FA'
COLOR_CHARCOAL = '#36454F'
COLOR_PALETTE = ['#4a708b', '#7B90A5', '#A5B5C1', '#D4DBE2', '#E6E6FA', '#C8A2C8']

# ----------------- Helper Functions -----------------
def calc_demand_supply_ratio(df_rides, df_drivers, groupby_col):
    # Calculate rides requested per group
    demand = df_rides.groupby(groupby_col).size().reset_index(name='rides_requested')
    # Since driver supply in this dataset is static per city (join_date based), we estimate active drivers per hour
    # A simple proxy: total drivers available in city * some distribution, OR just use completed rides / driver 
    # For a realistic ratio: let's calculate active drivers per hour from unique driver_id in requests
    supply = df_rides.dropna(subset=['driver_id']).groupby(groupby_col)['driver_id'].nunique().reset_index(name='active_drivers')
    
    ratio = pd.merge(demand, supply, on=groupby_col, how='left')
    ratio['active_drivers'].fillna(1, inplace=True) # Avoid div by zero
    ratio['ds_ratio'] = ratio['rides_requested'] / ratio['active_drivers']
    return ratio

# ----------------- Pages -----------------

if page == "Executive Overview":
    st.title("Executive Overview")
    st.markdown("High-level performance metrics across the Move platform.")
    
    total_rides = len(filtered_rides)
    completion_rate = len(filtered_rides[filtered_rides['status'] == 'Completed']) / total_rides if total_rides else 0
    cancellation_rate = 1 - completion_rate
    avg_wait = filtered_rides['wait_time'].mean()
    avg_fare = filtered_rides['fare'].mean()
    avg_surge = filtered_rides['surge_multiplier'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rides Requested", f"{total_rides:,.0f}")
    col2.metric("Completion Rate", f"{completion_rate:.1%}")
    col3.metric("Cancellation Rate", f"{cancellation_rate:.1%}")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("Avg Wait Time (min)", f"{avg_wait:.1f}")
    col5.metric("Avg Fare ($)", f"{avg_fare:.2f}")
    col6.metric("Avg Surge Multiplier", f"{avg_surge:.2f}x")
    
    st.markdown("---")
    st.subheader("Daily Rides Trend")
    daily_rides = filtered_rides.groupby('date').size().reset_index(name='rides')
    fig = px.line(daily_rides, x='date', y='rides', color_discrete_sequence=[COLOR_MUTED_BLUE])
    fig.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
    st.plotly_chart(fig, use_container_width=True)

elif page == "Demand & Supply":
    st.title("Demand & Supply Analysis")
    
    st.subheader("Hourly Demand vs Supply")
    # Demand = total requests, Supply = unique active drivers
    hourly_ds = calc_demand_supply_ratio(filtered_rides, drivers, 'hour')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hourly_ds['hour'], y=hourly_ds['rides_requested'], name='Demand (Requests)', marker_color=COLOR_MUTED_BLUE))
    fig.add_trace(go.Scatter(x=hourly_ds['hour'], y=hourly_ds['active_drivers'], name='Supply (Active Drivers)', line=dict(color=COLOR_CHARCOAL, width=3)))
    fig.update_layout(barmode='group', plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Demand/Supply Ratio by Hour")
    fig2 = px.line(hourly_ds, x='hour', y='ds_ratio', markers=True, color_discrete_sequence=[COLOR_CHARCOAL])
    fig2.add_hline(y=1, line_dash="dash", annotation_text="Balance", annotation_position="bottom right")
    fig2.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Rider Experience":
    st.title("Rider Experience")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Wait Time Distribution")
        fig = px.histogram(filtered_rides.dropna(subset=['wait_time']), x='wait_time', nbins=30, color_discrete_sequence=[COLOR_MUTED_BLUE])
        fig.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Cancellations by Zone")
        cancel_df = filtered_rides[filtered_rides['status'] != 'Completed'].groupby('zone').size().reset_index(name='cancellations')
        cancel_df = cancel_df.sort_values('cancellations', ascending=False)
        fig2 = px.bar(cancel_df, x='zone', y='cancellations', color_discrete_sequence=[COLOR_LAVENDER])
        fig2.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
        st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("Completion vs Cancellation by Hour")
    status_hr = filtered_rides.groupby(['hour', 'status']).size().reset_index(name='count')
    fig3 = px.bar(status_hr, x='hour', y='count', color='status', color_discrete_map={'Completed': COLOR_MUTED_BLUE, 'Cancelled_Rider': COLOR_LAVENDER, 'Cancelled_Driver': COLOR_CHARCOAL})
    fig3.update_layout(barmode='stack', plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
    st.plotly_chart(fig3, use_container_width=True)

elif page == "Pricing":
    st.title("Pricing & Surge Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Average Surge by Hour")
        surge_hr = filtered_rides.groupby('hour')['surge_multiplier'].mean().reset_index()
        fig = px.line(surge_hr, x='hour', y='surge_multiplier', markers=True, color_discrete_sequence=[COLOR_CHARCOAL])
        fig.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Fare by City")
        fig2 = px.box(filtered_rides.dropna(subset=['fare']), x='city', y='fare', color='city', color_discrete_sequence=COLOR_PALETTE)
        fig2.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
        st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("Fare vs Distance")
    completed = filtered_rides[filtered_rides['status'] == 'Completed'].sample(min(2000, len(filtered_rides)))
    fig3 = px.scatter(completed, x='distance_km', y='fare', color='surge_multiplier', color_continuous_scale="Purples")
    fig3.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
    st.plotly_chart(fig3, use_container_width=True)

elif page == "Geographic Analysis":
    st.title("Geographic Analysis")
    
    st.subheader("Zone Performance Overview")
    zone_stats = filtered_rides.groupby(['city', 'zone']).agg(
        total_requests=('ride_id', 'count'),
        avg_wait=('wait_time', 'mean'),
        cancellations=('status', lambda x: (x != 'Completed').sum())
    ).reset_index()
    
    zone_stats['cancellation_rate'] = zone_stats['cancellations'] / zone_stats['total_requests']
    
    fig = px.scatter(zone_stats, x='total_requests', y='cancellation_rate', size='avg_wait', color='city', hover_name='zone', color_discrete_sequence=COLOR_PALETTE)
    fig.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(zone_stats.style.format({
        'cancellation_rate': '{:.1%}',
        'avg_wait': '{:.1f} min'
    }))

elif page == "Insights":
    st.title("Automated Insights & Statistical Analysis")
    
    st.markdown("This page presents data-driven insights derived directly from the underlying database.")
    
    # Calculate Insights dynamically
    ds_hr = calc_demand_supply_ratio(filtered_rides, drivers, 'hour')
    peak_hr = ds_hr.loc[ds_hr['rides_requested'].idxmax()]['hour']
    highest_ds = ds_hr.loc[ds_hr['ds_ratio'].idxmax()]
    
    zone_ds = calc_demand_supply_ratio(filtered_rides, drivers, 'zone')
    highest_zone_ds = zone_ds.loc[zone_ds['ds_ratio'].idxmax()]
    
    avg_surge = filtered_rides['surge_multiplier'].mean()
    high_surge_hr = filtered_rides.groupby('hour')['surge_multiplier'].mean().idxmax()
    
    st.subheader("Key Findings")
    st.info(f"**Peak Demand:** Peak demand occurs at {int(peak_hr)}:00 hours.")
    st.info(f"**Supply Imbalance:** At {int(highest_ds['hour'])}:00, the demand-supply ratio peaks at {highest_ds['ds_ratio']:.2f}, indicating significant driver shortages.")
    st.info(f"**Zone Hotspot:** Zone '{highest_zone_ds['zone']}' has the highest overall demand-supply ratio ({highest_zone_ds['ds_ratio']:.2f}).")
    st.info(f"**Surge Pricing:** The highest average surge multiplier occurs at {high_surge_hr}:00 hours.")
    
    st.subheader("Statistical Analysis (Wait Time ~ Demand-Supply Ratio)")
    
    # Regression
    # We need to map ds_ratio back to rides
    rides_with_ratio = pd.merge(filtered_rides, ds_hr[['hour', 'ds_ratio']], on='hour', how='left')
    reg_data = rides_with_ratio.dropna(subset=['wait_time', 'ds_ratio'])
    
    if len(reg_data) > 0:
        X = reg_data['ds_ratio']
        y = reg_data['wait_time']
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        
        r_squared = model.rsquared
        coef = model.params['ds_ratio']
        
        st.success(f"**Linear Regression Results:**")
        st.write(f"- **R²:** {r_squared:.4f}")
        st.write(f"- **Coefficient:** {coef:.2f}")
        st.markdown(f"**Interpretation:** The relationship between demand-supply ratio and wait time has an R² of {r_squared:.4f}. For every 1 unit increase in the demand-supply ratio, the average wait time increases by approximately {coef:.2f} minutes.")
        
        fig = px.scatter(x=reg_data['ds_ratio'].sample(min(1000, len(reg_data))), y=reg_data['wait_time'].sample(min(1000, len(reg_data))), labels={'x': 'DS Ratio', 'y': 'Wait Time'}, trendline="ols", color_discrete_sequence=[COLOR_MUTED_BLUE])
        fig.update_layout(plot_bgcolor='#f0f2f6', paper_bgcolor='#f0f2f6', font_color=COLOR_CHARCOAL)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough data to perform regression analysis.")
