import streamlit as st
import pandas as pd
import boto3
import io
from streamlit_echarts import st_echarts

# ✅ Streamlit Layout - Full Page
st.set_page_config(layout="wide")
st.title("📊 Procurement Dashboard - ECharts Version")

@st.cache_data
def load_data():
    # ✅ AWS S3 Configuration
    BUCKET_NAME = "proc.data"
    PROCESSED_FOLDER = "ProcessedData"

    # ✅ Initialize S3 client with credentials from Streamlit secrets
    s3 = boto3.client('s3',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
        aws_secret_access_key=st.secrets["AWS_SECRET_KEY"],
        region_name=st.secrets["AWS_REGION"]
    )

    # ✅ Fetch latest processed Excel file from S3
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"{PROCESSED_FOLDER}/")

    files = response.get('Contents', [])

    # Filter only Excel files
    excel_files = [f for f in files if f['Key'].endswith(('.xlsx', '.xls'))]

    if not excel_files:
        st.error("❌ No processed Excel data found in S3.")
        return None
        
    if st.button("🔄 Refresh Data"):
    st.experimental_rerun()
    
    # Get the latest Excel file based on LastModified timestamp
    latest_file = max(excel_files, key=lambda x: x['LastModified'])['Key']

    # ✅ Download file into memory
    file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=latest_file)
    df_dict = pd.read_excel(io.BytesIO(file_obj['Body'].read()), sheet_name=None)

    return df_dict  # ✅ Return the cleaned data dictionary

# Load the cleaned data
df_dict = load_data()
if df_dict is None:
    st.stop()

# ✅ Extract Data for Each Chart
df_daily_orders = df_dict['Daily Orders']
df_weekly_orders = df_dict['Weekly Orders']
df_monthly_orders = df_dict['Monthly Orders']
df_spending_distribution = df_dict['Spending Distribution']
df_buyer_analysis = df_dict['Buyer Analysis']
df_top_suppliers_spend = df_dict['Top 20 Suppliers (Spend)']
df_top_suppliers_pos = df_dict['Top 20 Suppliers (POs)']
df_time_trends = df_dict['Time Trends']

# ✅ Convert Month Numbers to Names
month_map = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
             7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

df_monthly_orders['MONTH'] = df_monthly_orders['MONTH'].map(month_map)
df_time_trends['MONTH'] = df_time_trends['MONTH'].map(month_map)

# ✅ Custom Colors & Styling (Dark Mode)
custom_colors = ["#5470c6", "#FF5400", "#6C757D", "#CAF0F8", "#03045E"]
background_color = "#222831"
axis_color = "#888"
text_color = "#fff"
grid_color = "#444"
tooltip_background = "#333"

# ✅ Layout: 2 Rows, 4 Charts per Row
col1, col2, col3, col4 = st.columns(4)

# 🛠️ Existing ECharts Visualizations (Unchanged)
# 🔹 ROW 1: Order Trends + Spending Breakdown
with col1:
    st.markdown("### Daily Orders")
    option_daily_orders = {
        "backgroundColor": background_color,
        "color": custom_colors,
        "tooltip": {"trigger": "axis", "backgroundColor": tooltip_background},
        "xAxis": {"type": "category", "data": df_daily_orders['DAY'].astype(str).tolist(), "axisLabel": {"color": text_color}},
        "yAxis": {"type": "value", "axisLabel": {"color": text_color}},
        "series": [{"name": "PO Count", "data": df_daily_orders['PO_Count'].tolist(), "type": "line", "smooth": True}]
    }
    st_echarts(option_daily_orders, height="400px")

with col2:
    st.markdown("### Weekly Orders")
    option_weekly_orders = {
        "backgroundColor": background_color,
        "color": custom_colors,
        "tooltip": {"trigger": "axis", "backgroundColor": tooltip_background},
        "xAxis": {"type": "category", "data": df_weekly_orders['WEEK'].astype(str).tolist(), "axisLabel": {"color": text_color}},
        "yAxis": {"type": "value", "axisLabel": {"color": text_color}},
        "series": [{"name": "PO Count", "data": df_weekly_orders['PO_Count'].tolist(), "type": "line", "smooth": True}]
    }
    st_echarts(option_weekly_orders, height="400px")

with col3:
    st.markdown("### Monthly Orders")
    option_monthly_orders = {
        "backgroundColor": background_color,
        "color": custom_colors,
        "tooltip": {"trigger": "axis", "backgroundColor": tooltip_background},
        "xAxis": {"type": "category", "data": df_monthly_orders['MONTH'].astype(str).tolist(), "axisLabel": {"color": text_color}},
        "yAxis": {"type": "value", "axisLabel": {"color": text_color}},
        "series": [{"name": "PO Count", "data": df_monthly_orders['PO_Count'].tolist(), "type": "bar"}]
    }
    st_echarts(option_monthly_orders, height="400px")

with col4:
    st.markdown("### Spending Distribution")
    option_spending = {
        "backgroundColor": background_color,
        "color": custom_colors,
        "tooltip": {"trigger": "item", "formatter": "{b}: {d}%", "backgroundColor": tooltip_background},
        "series": [{"type": "pie", "radius": ["40%", "70%"], "label": {"show": False},
                    "data": [{"value": v, "name": n} for v, n in zip(df_spending_distribution['PO_AMOUNT'], df_spending_distribution['TYPE'])]}]
    }
    st_echarts(option_spending, height="400px")

# 🔹 ROW 2: Buyer Analysis + Supplier Breakdown
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown("### Buyer Analysis")
    option_buyer = {
        "backgroundColor": background_color,
        "color": custom_colors,
        "tooltip": {"trigger": "item", "formatter": "{b}: {d}%", "backgroundColor": tooltip_background},
        "series": [{"type": "pie", "radius": ["40%", "70%"], "label": {"show": False},
                    "data": [{"value": v, "name": n} for v, n in zip(df_buyer_analysis['Total_Spending_EUR'], df_buyer_analysis['BUYER'])]}]
    }
    st_echarts(option_buyer, height="400px")

with col6:
    st.markdown("### Top 20 by PO Value")
    option_top_suppliers = {
        "backgroundColor": background_color,
        "color": custom_colors,
        "tooltip": {
    "trigger": "axis",
    "position": """function (point, params, dom, rect, size) {
        return [point[0], '10%'];
    }""",
    "backgroundColor": tooltip_background
},
        "xAxis": {"type": "category", "data": df_top_suppliers_spend['SUPPLIER'].tolist(), "axisLabel": {"color": text_color}},
        "yAxis": {"type": "value", "axisLabel": {"color": text_color}},
        "series": [{"name": "Total Spend", "data": df_top_suppliers_spend['Total_Spend_EUR'].tolist(), "type": "bar"}]
    }
    st_echarts(option_top_suppliers, height="400px")

with col7:
    st.markdown("### Top 20 by PO Count")
    option_top_pos = {
        "backgroundColor": background_color,
        "color": custom_colors,
        "tooltip": {"trigger": "axis", "backgroundColor": tooltip_background},
        "xAxis": {"type": "category", "data": df_top_suppliers_pos['SUPPLIER'].tolist(), "axisLabel": {"color": text_color}},
        "yAxis": {"type": "value", "axisLabel": {"color": text_color}},
        "series": [{"name": "PO Count", "data": df_top_suppliers_pos['Number_of_POs'].tolist(), "type": "bar"}]
    }
    st_echarts(option_top_pos, height="400px")

with col8:
    st.markdown("### Total Spend Trends")
    option_time_trends = {
        "backgroundColor": background_color,
        "color": custom_colors,
        "tooltip": {"trigger": "axis", "backgroundColor": tooltip_background},
        "xAxis": {"type": "category", "data": df_time_trends['MONTH'].astype(str).tolist(), "axisLabel": {"color": text_color}},
        "yAxis": {"type": "value", "axisLabel": {"color": text_color}},
        "series": [{"name": "Total Spend", "data": df_time_trends['Total_Spend_EUR'].tolist(), "type": "line"}]
    }
    st_echarts(option_time_trends, height="400px")
