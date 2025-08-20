"""
Vehicle Registration Dashboard - Main Streamlit Application
Interactive dashboard for analyzing vehicle registration data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Initialize app data if needed (for cloud deployment)
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from init_app import initialize_app
    initialize_app()
except Exception as e:
    st.warning(f"Initialization warning: {e}")

from data_processor import VehicleDataProcessor
from database import DatabaseManager

# Page configuration
st.set_page_config(
    page_title="Vehicle Registration Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stSelectbox label {
        font-weight: 600;
        color: #2C3E50;
    }
</style>
""", unsafe_allow_html=True)

class VehicleDashboard:
    """
    Main dashboard class
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        self.processor = VehicleDataProcessor()
        
    def run(self):
        """
        Main dashboard function
        """
        # Header
        st.markdown('<h1 class="main-header">🚗 Vehicle Registration Analytics Dashboard</h1>', 
                   unsafe_allow_html=True)
        st.markdown("---")
        
        # Sidebar
        self.create_sidebar()
        
        # Check if data exists
        if not self.check_data_availability():
            return
        
        # Main content
        self.create_main_content()
    
    def check_data_availability(self):
        """
        Check if data is available in the database
        """
        stats = self.db.get_summary_stats()
        
        if stats.get('total_records', 0) == 0:
            st.error("No data found in the database!")
            st.info("Please run the data collector first: `python src/data_collector.py`")
            
            with st.expander("How to generate sample data"):
                st.code("""
# Navigate to project directory
cd vehicle-dashboard

# Install dependencies
pip install -r requirements.txt

# Generate sample data
python src/data_collector.py

# Run the dashboard
streamlit run src/dashboard.py
                """)
            return False
        
        return True
    
    def create_sidebar(self):
        """
        Create sidebar with filters
        """
        st.sidebar.header("📊 Dashboard Filters")
        
        # Date range
        date_range = self.db.get_date_range()
        
        if date_range['min_date'] and date_range['max_date']:
            min_date = pd.to_datetime(date_range['min_date']).date()
            max_date = pd.to_datetime(date_range['max_date']).date()
            
            st.sidebar.subheader("📅 Date Range")
            start_date = st.sidebar.date_input(
                "Start Date", 
                min_date,
                min_value=min_date,
                max_value=max_date
            )
            end_date = st.sidebar.date_input(
                "End Date", 
                max_date,
                min_value=min_date,
                max_value=max_date
            )
            
            # Store in session state
            st.session_state.start_date = start_date.strftime('%Y-%m-%d')
            st.session_state.end_date = end_date.strftime('%Y-%m-%d')
        
        # Vehicle categories
        st.sidebar.subheader("🚗 Vehicle Categories")
        categories = self.db.get_unique_values('vehicle_category')
        selected_categories = st.sidebar.multiselect(
            "Select Categories",
            categories,
            default=categories
        )
        st.session_state.selected_categories = selected_categories
        
        # Manufacturers
        st.sidebar.subheader("🏭 Manufacturers")
        manufacturers = self.db.get_unique_values('manufacturer')
        selected_manufacturers = st.sidebar.multiselect(
            "Select Manufacturers",
            manufacturers,
            default=manufacturers[:10]  # Default to first 10
        )
        st.session_state.selected_manufacturers = selected_manufacturers
        
        # States
        st.sidebar.subheader("🗺️ States")
        states = self.db.get_unique_values('state_name')
        selected_states = st.sidebar.multiselect(
            "Select States",
            states,
            default=states[:5]  # Default to first 5
        )
        st.session_state.selected_states = selected_states
    
    def create_main_content(self):
        """
        Create main dashboard content
        """
        # Load filtered data
        data = self.get_filtered_data()
        
        if data.empty:
            st.warning("No data available for the selected filters.")
            return
        
        # Key Metrics
        self.display_key_metrics(data)
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Growth Analysis", "🏆 Market Share", "📋 Detailed Data"])
        
        with tab1:
            self.create_trends_tab(data)
        
        with tab2:
            self.create_growth_tab(data)
        
        with tab3:
            self.create_market_share_tab(data)
        
        with tab4:
            self.create_data_tab(data)
    
    def get_filtered_data(self):
        """
        Get filtered data based on sidebar selections
        """
        start_date = st.session_state.get('start_date')
        end_date = st.session_state.get('end_date')
        categories = st.session_state.get('selected_categories', [])
        manufacturers = st.session_state.get('selected_manufacturers', [])
        states = st.session_state.get('selected_states', [])
        
        # Convert state names to codes for database query
        if states:
            state_codes = []
            all_states = self.db.execute_query("SELECT DISTINCT state_code, state_name FROM vehicle_registrations")
            state_map = dict(zip(all_states['state_name'], all_states['state_code']))
            state_codes = [state_map.get(state) for state in states if state_map.get(state)]
        else:
            state_codes = None
        
        return self.db.get_filtered_data(
            start_date=start_date,
            end_date=end_date,
            vehicle_categories=categories if categories else None,
            manufacturers=manufacturers if manufacturers else None,
            states=state_codes
        )
    
    def display_key_metrics(self, data):
        """
        Display key performance metrics
        """
        st.subheader("📊 Key Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_registrations = data['registrations'].sum()
            st.metric("Total Registrations", f"{total_registrations:,}")
        
        with col2:
            unique_manufacturers = data['manufacturer'].nunique()
            st.metric("Active Manufacturers", unique_manufacturers)
        
        with col3:
            avg_monthly = data.groupby(['year', 'month'])['registrations'].sum().mean()
            st.metric("Avg Monthly Registrations", f"{avg_monthly:,.0f}")
        
        with col4:
            latest_month = data.groupby(['year', 'month'])['registrations'].sum().tail(1).values[0]
            st.metric("Latest Month Registrations", f"{latest_month:,}")
    
    def create_trends_tab(self, data):
        """
        Create trends analysis tab
        """
        st.subheader("📈 Registration Trends")
        
        # Monthly trends by category
        monthly_data = data.groupby(['year', 'month', 'vehicle_category'])['registrations'].sum().reset_index()
        monthly_data['date'] = pd.to_datetime(monthly_data[['year', 'month']].assign(day=1))
        
        fig = px.line(
            monthly_data, 
            x='date', 
            y='registrations', 
            color='vehicle_category',
            title='Monthly Registration Trends by Vehicle Category',
            labels={'registrations': 'Registrations', 'date': 'Date'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top manufacturers trend
        st.subheader("🏭 Top Manufacturers Trend")
        
        # Get top 5 manufacturers by total registrations
        top_manufacturers = data.groupby('manufacturer')['registrations'].sum().nlargest(5).index
        
        mfr_monthly = data[data['manufacturer'].isin(top_manufacturers)].groupby(['year', 'month', 'manufacturer'])['registrations'].sum().reset_index()
        mfr_monthly['date'] = pd.to_datetime(mfr_monthly[['year', 'month']].assign(day=1))
        
        fig2 = px.line(
            mfr_monthly,
            x='date',
            y='registrations',
            color='manufacturer',
            title='Monthly Trends - Top 5 Manufacturers',
            labels={'registrations': 'Registrations', 'date': 'Date'}
        )
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, use_container_width=True)
    
    def create_growth_tab(self, data):
        """
        Create growth analysis tab
        """
        st.subheader("📊 Growth Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Year-over-Year Growth")
            yoy_data = self.processor.calculate_yoy_growth(data)
            
            if not yoy_data.empty:
                # Latest YoY growth by category
                latest_yoy = yoy_data.groupby('vehicle_category')['yoy_growth'].last().reset_index()
                latest_yoy = latest_yoy.dropna()
                
                if not latest_yoy.empty:
                    fig_yoy = px.bar(
                        latest_yoy,
                        x='vehicle_category',
                        y='yoy_growth',
                        title='Latest YoY Growth Rate by Category',
                        labels={'yoy_growth': 'YoY Growth (%)', 'vehicle_category': 'Category'}
                    )
                    fig_yoy.update_layout(height=400)
                    st.plotly_chart(fig_yoy, use_container_width=True)
                else:
                    st.info("Insufficient data for YoY calculation")
            else:
                st.info("No YoY data available")
        
        with col2:
            st.subheader("Quarter-over-Quarter Growth")
            qoq_data = self.processor.calculate_qoq_growth(data)
            
            if not qoq_data.empty:
                # Latest QoQ growth by category
                latest_qoq = qoq_data.groupby('vehicle_category')['qoq_growth'].last().reset_index()
                latest_qoq = latest_qoq.dropna()
                
                if not latest_qoq.empty:
                    fig_qoq = px.bar(
                        latest_qoq,
                        x='vehicle_category',
                        y='qoq_growth',
                        title='Latest QoQ Growth Rate by Category',
                        labels={'qoq_growth': 'QoQ Growth (%)', 'vehicle_category': 'Category'}
                    )
                    fig_qoq.update_layout(height=400)
                    st.plotly_chart(fig_qoq, use_container_width=True)
                else:
                    st.info("Insufficient data for QoQ calculation")
            else:
                st.info("No QoQ data available")
        
        # Growth trends over time
        st.subheader("Growth Trends Over Time")
        
        if not yoy_data.empty:
            yoy_trend = yoy_data.groupby(['year_month', 'vehicle_category'])['yoy_growth'].mean().reset_index()
            yoy_trend['date'] = yoy_trend['year_month'].astype(str)
            
            fig_trend = px.line(
                yoy_trend,
                x='date',
                y='yoy_growth',
                color='vehicle_category',
                title='YoY Growth Trend by Category',
                labels={'yoy_growth': 'YoY Growth (%)', 'date': 'Period'}
            )
            fig_trend.update_layout(height=500)
            st.plotly_chart(fig_trend, use_container_width=True)
    
    def create_market_share_tab(self, data):
        """
        Create market share analysis tab
        """
        st.subheader("🏆 Market Share Analysis")
        
        # Market share calculation
        market_share = self.processor.calculate_market_share(data)
        
        if not market_share.empty:
            # Latest market share by category
            latest_period = market_share['year_month'].max()
            latest_share = market_share[market_share['year_month'] == latest_period]
            
            for category in latest_share['vehicle_category'].unique():
                st.subheader(f"{category} Category - Market Share")
                
                cat_data = latest_share[latest_share['vehicle_category'] == category]
                cat_data = cat_data.nlargest(10, 'market_share')  # Top 10
                
                fig = px.pie(
                    cat_data,
                    values='market_share',
                    names='manufacturer',
                    title=f'{category} Market Share Distribution'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Market share trends
        st.subheader("Market Share Trends")
        
        if not market_share.empty:
            # Top 3 manufacturers in each category
            top_manufacturers = (market_share.groupby(['vehicle_category', 'manufacturer'])['market_share']
                               .mean().reset_index()
                               .sort_values(['vehicle_category', 'market_share'], ascending=[True, False])
                               .groupby('vehicle_category').head(3))
            
            for category in top_manufacturers['vehicle_category'].unique():
                cat_top = top_manufacturers[top_manufacturers['vehicle_category'] == category]
                trend_data = market_share[
                    (market_share['vehicle_category'] == category) & 
                    (market_share['manufacturer'].isin(cat_top['manufacturer']))
                ]
                
                if not trend_data.empty:
                    trend_data['date'] = trend_data['year_month'].astype(str)
                    
                    fig = px.line(
                        trend_data,
                        x='date',
                        y='market_share',
                        color='manufacturer',
                        title=f'{category} - Market Share Trends (Top 3 Manufacturers)',
                        labels={'market_share': 'Market Share (%)', 'date': 'Period'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
    
    def create_data_tab(self, data):
        """
        Create detailed data tab
        """
        st.subheader("📋 Detailed Registration Data")
        
        # Summary statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Summary by Category")
            category_summary = data.groupby('vehicle_category').agg({
                'registrations': ['sum', 'mean', 'count']
            }).round(2)
            category_summary.columns = ['Total', 'Average', 'Records']
            st.dataframe(category_summary)
        
        with col2:
            st.subheader("Summary by State")
            state_summary = data.groupby('state_name').agg({
                'registrations': 'sum'
            }).sort_values('registrations', ascending=False).head(10)
            state_summary.columns = ['Total Registrations']
            st.dataframe(state_summary)
        
        # Raw data with pagination
        st.subheader("Raw Data")
        
        # Add search functionality
        search_term = st.text_input("Search in data (manufacturer, state, etc.)")
        
        display_data = data.copy()
        if search_term:
            mask = (
                display_data['manufacturer'].str.contains(search_term, case=False, na=False) |
                display_data['state_name'].str.contains(search_term, case=False, na=False) |
                display_data['vehicle_category'].str.contains(search_term, case=False, na=False)
            )
            display_data = display_data[mask]
        
        # Display data
        st.dataframe(
            display_data.sort_values(['date', 'state_name', 'vehicle_category', 'manufacturer']),
            use_container_width=True
        )
        
        # Download button
        csv = display_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"vehicle_registrations_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def main():
    """
    Main function to run the dashboard
    """
    dashboard = VehicleDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
