import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy | Profitability Dashboard",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f0f1a; }
    .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid #2a2a4a;
    }
    section[data-testid="stSidebar"] * { color: #e0e0ff !important; }

    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        margin-bottom: 8px;
    }
    .kpi-value { font-size: 28px; font-weight: 800; margin: 4px 0; }
    .kpi-label { font-size: 12px; color: #8888aa; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-delta { font-size: 11px; margin-top: 4px; }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #7b5ea7 0%, transparent 100%);
        border-left: 4px solid #7b5ea7;
        padding: 8px 16px;
        border-radius: 4px;
        margin: 20px 0 12px 0;
        color: #e0e0ff !important;
        font-size: 16px;
        font-weight: 700;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #1a1a2e;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #8888aa;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #7b5ea7 !important;
        color: white !important;
    }

    /* Dataframe */
    .stDataFrame { background: #1a1a2e; border-radius: 8px; }

    /* Metric */
    [data-testid="stMetric"] {
        background: #1a1a2e;
        border: 1px solid #2a2a4a;
        border-radius: 10px;
        padding: 12px;
    }
    [data-testid="stMetricValue"] { color: #e0e0ff; }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    h1,h2,h3,h4 { color: #e0e0ff !important; }
    p, li { color: #aaaacc; }
</style>
""", unsafe_allow_html=True)

# ── Color Palettes ─────────────────────────────────────────────────────────────
DIV_COLOR    = {'Chocolate': '#7b5ea7', 'Sugar': '#f0a500', 'Other': '#4ecdc4'}
REGION_COLOR = {'Atlantic': '#e05c5c', 'Gulf': '#45b7d1', 'Interior': '#96ceb4', 'Pacific': '#ff6b9d'}
RISK_COLOR   = {'🔴 High Risk (<40%)': '#e05c5c', '🟡 Moderate (40-55%)': '#f0a500', '🟢 Healthy (>55%)': '#4ecdc4'}
PLOTLY_THEME = dict(paper_bgcolor='#0f0f1a', plot_bgcolor='#1a1a2e',
                    font_color='#e0e0ff', title_font_color='#f0a500',
                    legend=dict(bgcolor='#1a1a2e', bordercolor='#2a2a4a'))

# ── Data Loading & Processing ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Nassau_Candy_Distributor.csv")
    df.columns = [c.strip() for c in df.columns]
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date']  = pd.to_datetime(df['Ship Date'],  dayfirst=True)
    df['Month']      = df['Order Date'].dt.month
    df['Month Name'] = df['Order Date'].dt.strftime('%b')
    df['Quarter']    = df['Order Date'].dt.to_period('Q').astype(str)
    df['Year']       = df['Order Date'].dt.year
    df['Lead Time']  = (df['Ship Date'] - df['Order Date']).dt.days
    df['Product Name'] = df['Product Name'].str.strip()
    df['Division']     = df['Division'].str.strip()
    df = df[(df['Sales'] > 0) & (df['Units'] > 0) & (df['Cost'] > 0)]

    factory_map = {
        'Wonka Bar - Nutty Crunch Surprise':  "Lot's O' Nuts",
        'Wonka Bar - Fudge Mallows':          "Lot's O' Nuts",
        'Wonka Bar -Scrumdiddlyumptious':     "Lot's O' Nuts",
        'Wonka Bar - Milk Chocolate':         "Wicked Choccy's",
        'Wonka Bar - Triple Dazzle Caramel':  "Wicked Choccy's",
        'Laffy Taffy':                        'Sugar Shack',
        'SweeTARTS':                          'Sugar Shack',
        'Nerds':                              'Sugar Shack',
        'Fun Dip':                            'Sugar Shack',
        'Fizzy Lifting Drinks':               'Sugar Shack',
        'Everlasting Gobstopper':             'Secret Factory',
        'Hair Toffee':                        'The Other Factory',
        'Lickable Wallpaper':                 'Secret Factory',
        'Wonka Gum':                          'Secret Factory',
        'Kazookles':                          'The Other Factory',
    }
    df['Factory']        = df['Product Name'].map(factory_map)
    df['Gross Margin %'] = (df['Gross Profit'] / df['Sales']) * 100
    df['Profit per Unit']= df['Gross Profit'] / df['Units']
    df['Cost per Unit']  = df['Cost'] / df['Units']
    return df

df_raw = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍬 Nassau Candy")
    st.markdown("### Profitability Dashboard")
    st.markdown("---")

    st.markdown("#### 📅 Date Range")
    min_date = df_raw['Order Date'].min().date()
    max_date = df_raw['Order Date'].max().date()
    date_range = st.date_input("Select period", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

    st.markdown("#### 🏭 Division")
    divisions = st.multiselect("Select divisions",
                               options=df_raw['Division'].unique().tolist(),
                               default=df_raw['Division'].unique().tolist())

    st.markdown("#### 🌎 Region")
    regions = st.multiselect("Select regions",
                             options=df_raw['Region'].unique().tolist(),
                             default=df_raw['Region'].unique().tolist())

    st.markdown("#### 📊 Margin Threshold")
    margin_threshold = st.slider("Minimum Gross Margin %", 0, 100, 0, 5)

    st.markdown("#### 🔍 Product Search")
    product_search = st.text_input("Search product name", "")

    st.markdown("---")
    st.markdown("#### 🚚 Ship Mode")
    ship_modes = st.multiselect("Select ship modes",
                                options=df_raw['Ship Mode'].unique().tolist(),
                                default=df_raw['Ship Mode'].unique().tolist())

    st.markdown("---")
    st.caption("Nassau Candy Distributor | FY2024–2025")

# ── Filter Data ────────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = df_raw['Order Date'].min(), df_raw['Order Date'].max()

df = df_raw[
    (df_raw['Order Date'] >= start_date) &
    (df_raw['Order Date'] <= end_date) &
    (df_raw['Division'].isin(divisions)) &
    (df_raw['Region'].isin(regions)) &
    (df_raw['Gross Margin %'] >= margin_threshold) &
    (df_raw['Ship Mode'].isin(ship_modes))
]
if product_search:
    df = df[df['Product Name'].str.contains(product_search, case=False, na=False)]

# ── Aggregations ───────────────────────────────────────────────────────────────
total_sales  = df['Sales'].sum()
total_profit = df['Gross Profit'].sum()
total_cost   = df['Cost'].sum()
total_units  = df['Units'].sum()
overall_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

prod = df.groupby(['Product Name', 'Division', 'Factory']).agg(
    Total_Sales  =('Sales',         'sum'),
    Total_Profit =('Gross Profit',  'sum'),
    Total_Cost   =('Cost',          'sum'),
    Total_Units  =('Units',         'sum'),
    Order_Count  =('Row ID',        'count'),
).reset_index()
prod['Gross Margin %']       = (prod['Total_Profit'] / prod['Total_Sales']) * 100
prod['Profit per Unit']      = prod['Total_Profit'] / prod['Total_Units']
prod['Revenue Contribution'] = (prod['Total_Sales']  / total_sales)  * 100
prod['Profit Contribution']  = (prod['Total_Profit'] / total_profit) * 100
prod['Margin Risk'] = prod['Gross Margin %'].apply(
    lambda x: '🔴 High Risk (<40%)' if x < 40
    else ('🟡 Moderate (40-55%)' if x < 55 else '🟢 Healthy (>55%)')
)
median_sales  = prod['Total_Sales'].median()
median_margin = prod['Gross Margin %'].median()
def classify(row):
    hi_s = row['Total_Sales']    >= median_sales
    hi_m = row['Gross Margin %'] >= median_margin
    if hi_s and hi_m:       return '⭐ Star'
    if hi_s and not hi_m:   return '⚠️ Volume Trap'
    if not hi_s and hi_m:   return '💎 Hidden Gem'
    return '🔴 Laggard'
prod['Classification'] = prod.apply(classify, axis=1)
prod = prod.sort_values('Total_Profit', ascending=False).reset_index(drop=True)

div_agg = df.groupby('Division').agg(
    Total_Sales  =('Sales',        'sum'),
    Total_Profit =('Gross Profit', 'sum'),
    Total_Cost   =('Cost',         'sum'),
    Total_Units  =('Units',        'sum'),
).reset_index()
div_agg['Gross Margin %']       = div_agg['Total_Profit'] / div_agg['Total_Sales'] * 100
div_agg['Revenue Contribution'] = div_agg['Total_Sales']  / total_sales  * 100
div_agg['Profit Contribution']  = div_agg['Total_Profit'] / total_profit * 100

region_agg = df.groupby('Region').agg(
    Total_Sales  =('Sales',        'sum'),
    Total_Profit =('Gross Profit', 'sum'),
    Total_Units  =('Units',        'sum'),
).reset_index()
region_agg['Gross Margin %'] = region_agg['Total_Profit'] / region_agg['Total_Sales'] * 100

factory_agg = df.groupby('Factory').agg(
    Total_Sales  =('Sales',        'sum'),
    Total_Profit =('Gross Profit', 'sum'),
    Total_Units  =('Units',        'sum'),
).reset_index()
factory_agg['Gross Margin %'] = factory_agg['Total_Profit'] / factory_agg['Total_Sales'] * 100

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background: linear-gradient(90deg,#7b5ea7,#4ecdc4);
            padding:2px; border-radius:12px; margin-bottom:16px;'>
  <div style='background:#0f0f1a; border-radius:11px; padding:20px 24px;'>
    <h1 style='margin:0; font-size:28px; color:#f0a500;'>🍬 Nassau Candy Distributor</h1>
    <p style='margin:4px 0 0 0; color:#8888aa; font-size:14px;'>
      Product Line Profitability & Margin Performance Dashboard | FY2024–2025
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    (k1, "💰 Total Revenue",    f"${total_sales/1e6:.2f}M",       "#7b5ea7"),
    (k2, "📈 Gross Profit",     f"${total_profit/1e6:.2f}M",      "#4ecdc4"),
    (k3, "📊 Overall Margin",   f"{overall_margin:.1f}%",         "#f0a500"),
    (k4, "🏭 Total Cost",       f"${total_cost/1e6:.2f}M",        "#e05c5c"),
    (k5, "📦 Units Sold",       f"{total_units:,.0f}",            "#96ceb4"),
    (k6, "🧾 Total Orders",     f"{len(df):,}",                   "#ff6b9d"),
]
for col, label, value, color in kpis:
    col.markdown(f"""
    <div class='kpi-card' style='border-top: 3px solid {color};'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value' style='color:{color};'>{value}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── TABS ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏆 Product Profitability",
    "🏭 Division Performance",
    "📉 Pareto Analysis",
    "🔬 Cost Diagnostics",
    "📅 Time Series",
    "📋 Executive Summary",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PRODUCT PROFITABILITY
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>🏆 Product Profitability Leaderboard</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            prod.sort_values('Total_Profit'),
            x='Total_Profit', y='Product Name', orientation='h',
            color='Division', color_discrete_map=DIV_COLOR,
            title='Gross Profit by Product',
            labels={'Total_Profit': 'Total Gross Profit ($)', 'Product Name': ''},
            template='plotly_dark', text='Total_Profit',
        )
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont_size=9)
        fig.update_layout(**PLOTLY_THEME, height=480, showlegend=True,
                          title_font_size=14, margin=dict(l=10,r=80,t=40,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            prod.sort_values('Gross Margin %'),
            x='Gross Margin %', y='Product Name', orientation='h',
            color='Division', color_discrete_map=DIV_COLOR,
            title='Gross Margin % by Product',
            labels={'Gross Margin %': 'Gross Margin (%)', 'Product Name': ''},
            template='plotly_dark', text='Gross Margin %',
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside', textfont_size=9)
        avg_m = prod['Gross Margin %'].mean()
        fig.add_vline(x=avg_m, line_dash='dash', line_color='#f0a500',
                      annotation_text=f'Avg {avg_m:.1f}%', annotation_font_color='#f0a500')
        fig.update_layout(**PLOTLY_THEME, height=480, showlegend=True,
                          title_font_size=14, margin=dict(l=10,r=80,t=40,b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>🎯 Product Classification Matrix</div>", unsafe_allow_html=True)

    cls_color_map = {'⭐ Star':'#4ecdc4','⚠️ Volume Trap':'#f0a500',
                     '💎 Hidden Gem':'#7b5ea7','🔴 Laggard':'#e05c5c'}
    fig = px.scatter(
        prod, x='Total_Sales', y='Gross Margin %',
        size='Total_Profit', color='Classification',
        color_discrete_map=cls_color_map,
        hover_name='Product Name',
        hover_data={'Total_Profit': ':.2f', 'Division': True, 'Profit per Unit': ':.2f'},
        title='Sales vs Margin — Classification Matrix (Bubble = Total Profit)',
        labels={'Total_Sales':'Total Sales ($)','Gross Margin %':'Gross Margin (%)'},
        template='plotly_dark', size_max=55,
        text='Product Name',
    )
    fig.update_traces(textposition='top center', textfont_size=9)
    fig.add_vline(x=median_sales,  line_dash='dash', line_color='#444466')
    fig.add_hline(y=median_margin, line_dash='dash', line_color='#444466')
    fig.update_layout(**PLOTLY_THEME, height=520, title_font_size=14,
                      margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>📊 Profit per Unit Comparison</div>", unsafe_allow_html=True)
    fig = px.bar(
        prod.sort_values('Profit per Unit', ascending=False),
        x='Product Name', y='Profit per Unit',
        color='Division', color_discrete_map=DIV_COLOR,
        title='Profit per Unit by Product',
        template='plotly_dark', text='Profit per Unit',
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(**PLOTLY_THEME, height=380, xaxis_tickangle=-30,
                      title_font_size=14, margin=dict(l=10,r=10,t=50,b=80))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>📋 Full Product Metrics Table</div>", unsafe_allow_html=True)
    display_cols = ['Product Name','Division','Factory','Total_Sales','Total_Profit',
                    'Gross Margin %','Profit per Unit','Revenue Contribution',
                    'Profit Contribution','Classification','Margin Risk']
    st.dataframe(
        prod[display_cols].style
            .format({'Total_Sales':'${:,.0f}','Total_Profit':'${:,.0f}',
                     'Gross Margin %':'{:.1f}%','Profit per Unit':'${:.2f}',
                     'Revenue Contribution':'{:.1f}%','Profit Contribution':'{:.1f}%'}),
        use_container_width=True, height=420,
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DIVISION PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>🏭 Division Revenue vs Profit Overview</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, div_row in zip([c1, c2, c3], div_agg.itertuples()):
        color = DIV_COLOR.get(div_row.Division, '#7b5ea7')
        col.markdown(f"""
        <div class='kpi-card' style='border-top:3px solid {color};'>
            <div class='kpi-label' style='color:{color}; font-size:14px; font-weight:700;'>{div_row.Division}</div>
            <div style='margin:10px 0;'>
                <div class='kpi-label'>Revenue</div>
                <div class='kpi-value' style='color:{color}; font-size:20px;'>${div_row.Total_Sales:,.0f}</div>
            </div>
            <div style='margin:10px 0;'>
                <div class='kpi-label'>Gross Profit</div>
                <div class='kpi-value' style='color:#4ecdc4; font-size:20px;'>${div_row.Total_Profit:,.0f}</div>
            </div>
            <div>
                <div class='kpi-label'>Margin</div>
                <div class='kpi-value' style='color:#f0a500; font-size:22px;'>{div_row._8:.1f}%</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>📊 Division Detailed Comparison</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Revenue', x=div_agg['Division'],
                             y=div_agg['Total_Sales'], marker_color='#7b5ea7'))
        fig.add_trace(go.Bar(name='Gross Profit', x=div_agg['Division'],
                             y=div_agg['Total_Profit'], marker_color='#4ecdc4'))
        fig.update_layout(**PLOTLY_THEME, title='Revenue vs Profit by Division',
                          title_font_size=14, barmode='group', height=380)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.pie(div_agg, names='Division', values='Total_Profit',
                     color='Division', color_discrete_map=DIV_COLOR,
                     title='Profit Share by Division', hole=0.5,
                     template='plotly_dark')
        fig.update_layout(**PLOTLY_THEME, title_font_size=14, height=380)
        fig.update_traces(textinfo='label+percent', textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>🗺️ Revenue Treemap</div>", unsafe_allow_html=True)
    fig = px.treemap(
        prod, path=[px.Constant('Nassau Candy'), 'Division', 'Product Name'],
        values='Total_Sales', color='Gross Margin %',
        color_continuous_scale=['#e05c5c','#f0a500','#4ecdc4'],
        title='Revenue Treemap — Color = Gross Margin % (Red=Low → Teal=High)',
        template='plotly_dark',
        hover_data={'Total_Profit':':.2f','Gross Margin %':':.1f'},
    )
    fig.update_layout(**PLOTLY_THEME, title_font_size=14, height=480,
                      margin=dict(t=50,b=10,l=10,r=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>🌎 Regional Performance</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Revenue', x=region_agg['Region'],
                             y=region_agg['Total_Sales'],
                             marker_color=[REGION_COLOR[r] for r in region_agg['Region']]))
        fig.update_layout(**PLOTLY_THEME, title='Revenue by Region', height=360)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(region_agg.sort_values('Gross Margin %'),
                     x='Region', y='Gross Margin %',
                     color='Region', color_discrete_map=REGION_COLOR,
                     title='Gross Margin % by Region', template='plotly_dark',
                     text='Gross Margin %')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(**PLOTLY_THEME, title_font_size=14, height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>🏗️ Factory Performance</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Revenue', x=factory_agg['Factory'],
                             y=factory_agg['Total_Sales'], marker_color='#7b5ea7'))
        fig.add_trace(go.Bar(name='Profit',  x=factory_agg['Factory'],
                             y=factory_agg['Total_Profit'], marker_color='#4ecdc4'))
        fig.update_layout(**PLOTLY_THEME, title='Factory Revenue vs Profit',
                          barmode='group', height=380, xaxis_tickangle=-15)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(factory_agg.sort_values('Gross Margin %'),
                     x='Factory', y='Gross Margin %',
                     color='Gross Margin %', color_continuous_scale=['#e05c5c','#f0a500','#4ecdc4'],
                     title='Gross Margin % by Factory', template='plotly_dark', text='Gross Margin %')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(**PLOTLY_THEME, title_font_size=14, height=380, xaxis_tickangle=-15)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PARETO ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>📉 Pareto — Profit Concentration (80/20 Rule)</div>", unsafe_allow_html=True)

    prod_pareto = prod.sort_values('Total_Profit', ascending=False).copy()
    prod_pareto['Cum Profit %'] = prod_pareto['Total_Profit'].cumsum() / prod_pareto['Total_Profit'].sum() * 100
    prod_pareto['Cum Sales %']  = prod_pareto['Total_Sales'].cumsum()  / prod_pareto['Total_Sales'].sum()  * 100
    n80 = int((prod_pareto['Cum Profit %'] <= 80).sum())

    fig = make_subplots(specs=[[{'secondary_y': True}]])
    colors_bar = [DIV_COLOR.get(d,'#7b5ea7') for d in prod_pareto['Division']]
    fig.add_trace(go.Bar(x=prod_pareto['Product Name'], y=prod_pareto['Total_Profit'],
                         name='Gross Profit', marker_color=colors_bar), secondary_y=False)
    fig.add_trace(go.Scatter(x=prod_pareto['Product Name'], y=prod_pareto['Cum Profit %'],
                             name='Cumulative Profit %', mode='lines+markers',
                             line=dict(color='#f0a500', width=2.5),
                             marker=dict(size=6)), secondary_y=True)
    fig.add_hline(y=80, line_dash='dash', line_color='#e05c5c',
                  annotation_text='80% Threshold', secondary_y=True)
    fig.update_yaxes(title_text='Gross Profit ($)', secondary_y=False, color='#e0e0ff')
    fig.update_yaxes(title_text='Cumulative Profit %', secondary_y=True, color='#f0a500', range=[0,110])
    fig.update_layout(**PLOTLY_THEME, title='Pareto Analysis — Product Profit Concentration',
                      title_font_size=15, height=480, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""<div class='kpi-card' style='border-top:3px solid #4ecdc4;'>
        <div class='kpi-label'>Products driving 80% of profit</div>
        <div class='kpi-value' style='color:#4ecdc4;'>{n80} / {len(prod_pareto)}</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class='kpi-card' style='border-top:3px solid #f0a500;'>
        <div class='kpi-label'>Top product profit share</div>
        <div class='kpi-value' style='color:#f0a500;'>{prod_pareto['Profit Contribution'].iloc[0]:.1f}%</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class='kpi-card' style='border-top:3px solid #e05c5c;'>
        <div class='kpi-label'>Concentration risk</div>
        <div class='kpi-value' style='color:#e05c5c;'>{'HIGH' if n80 <= 5 else 'MODERATE'}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>🌎 Regional Profit Concentration</div>", unsafe_allow_html=True)
    fig = px.pie(region_agg, names='Region', values='Total_Profit',
                 color='Region', color_discrete_map=REGION_COLOR,
                 title='Profit Share by Region', hole=0.45, template='plotly_dark')
    fig.update_layout(**PLOTLY_THEME, height=380)
    fig.update_traces(textinfo='label+percent+value', textfont_size=11)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>📊 Revenue vs Profit Contribution Gap</div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Revenue Contribution %', x=prod['Product Name'],
                         y=prod['Revenue Contribution'], marker_color='#7b5ea7'))
    fig.add_trace(go.Bar(name='Profit Contribution %', x=prod['Product Name'],
                         y=prod['Profit Contribution'], marker_color='#4ecdc4'))
    fig.update_layout(**PLOTLY_THEME, title='Revenue vs Profit Contribution — Imbalance View',
                      barmode='group', height=400, xaxis_tickangle=-30, title_font_size=14)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — COST DIAGNOSTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>🔬 Cost vs Sales — Margin Risk Diagnostic</div>", unsafe_allow_html=True)

    fig = px.scatter(
        prod, x='Total_Cost', y='Total_Sales',
        color='Margin Risk', color_discrete_map=RISK_COLOR,
        size='Total_Units', hover_name='Product Name',
        hover_data={'Gross Margin %':':.1f','Total_Profit':':.2f','Division':True},
        title='Cost vs Sales — Margin Risk (Bubble = Units Sold)',
        labels={'Total_Cost':'Total Cost ($)','Total_Sales':'Total Sales ($)'},
        template='plotly_dark', size_max=50, text='Product Name',
    )
    max_val = max(prod['Total_Cost'].max(), prod['Total_Sales'].max()) * 1.05
    fig.add_trace(go.Scatter(x=[0,max_val], y=[0,max_val], mode='lines',
                             name='Break-Even Line',
                             line=dict(dash='dash', color='#555577', width=1.5)))
    fig.update_traces(textposition='top center', textfont_size=8,
                      selector=dict(mode='markers+text'))
    fig.update_layout(**PLOTLY_THEME, height=520, title_font_size=14)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>⚠️ Margin Risk Flag Summary</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        risk_summary = prod.groupby('Margin Risk').agg(
            Products=('Product Name','count'),
            Avg_Margin=('Gross Margin %','mean'),
            Total_Profit=('Total_Profit','sum'),
        ).reset_index()
        fig = px.bar(risk_summary, x='Margin Risk', y='Products',
                     color='Margin Risk', color_discrete_map=RISK_COLOR,
                     title='Products by Risk Category', template='plotly_dark', text='Products')
        fig.update_traces(textposition='outside')
        fig.update_layout(**PLOTLY_THEME, height=360, showlegend=False, title_font_size=13)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(prod.sort_values('Gross Margin %'),
                     x='Product Name', y='Gross Margin %',
                     color='Margin Risk', color_discrete_map=RISK_COLOR,
                     title='Margin % per Product — Risk View',
                     template='plotly_dark', text='Gross Margin %')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        avg_m = prod['Gross Margin %'].mean()
        fig.add_hline(y=avg_m, line_dash='dash', line_color='white',
                      annotation_text=f'Avg {avg_m:.1f}%')
        fig.update_layout(**PLOTLY_THEME, height=360, title_font_size=13,
                          xaxis_tickangle=-35, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>🔄 Cost vs Profit per Unit</div>", unsafe_allow_html=True)
    fig = px.scatter(
        prod, x='Total_Cost', y='Profit per Unit',
        color='Division', color_discrete_map=DIV_COLOR,
        size='Total_Units', hover_name='Product Name',
        title='Total Cost vs Profit per Unit — Efficiency View',
        template='plotly_dark', size_max=45, text='Product Name',
    )
    fig.update_traces(textposition='top center', textfont_size=8,
                      selector=dict(mode='markers+text'))
    fig.update_layout(**PLOTLY_THEME, height=440, title_font_size=14)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>📋 Full Risk Flags Table</div>", unsafe_allow_html=True)
    risk_table = prod[['Product Name','Division','Factory','Gross Margin %',
                        'Profit per Unit','Total_Cost','Total_Profit','Margin Risk','Classification']]
    st.dataframe(
        risk_table.sort_values('Gross Margin %').style
            .format({'Gross Margin %':'{:.1f}%','Profit per Unit':'${:.2f}',
                     'Total_Cost':'${:,.0f}','Total_Profit':'${:,.0f}'}),
        use_container_width=True, height=400,
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TIME SERIES
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("<div class='section-header'>📅 Monthly Profit Trend by Division</div>", unsafe_allow_html=True)

    monthly_div = df.groupby(['Year','Month','Month Name','Division'])['Gross Profit'].sum().reset_index()
    monthly_div['Period'] = monthly_div['Year'].astype(str) + '-' + monthly_div['Month'].astype(str).str.zfill(2)
    monthly_div = monthly_div.sort_values('Period')

    fig = px.line(monthly_div, x='Period', y='Gross Profit', color='Division',
                  color_discrete_map=DIV_COLOR, markers=True,
                  title='Monthly Gross Profit Trend by Division',
                  labels={'Gross Profit':'Gross Profit ($)','Period':'Month'},
                  template='plotly_dark')
    fig.update_layout(**PLOTLY_THEME, height=420, title_font_size=14,
                      xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>📊 Quarterly Performance</div>", unsafe_allow_html=True)
    qtr = df.groupby(['Quarter','Division']).agg(
        Total_Sales  =('Sales','sum'),
        Total_Profit =('Gross Profit','sum'),
    ).reset_index()
    qtr['Gross Margin %'] = qtr['Total_Profit'] / qtr['Total_Sales'] * 100

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(qtr, x='Quarter', y='Total_Profit', color='Division',
                     color_discrete_map=DIV_COLOR, barmode='group',
                     title='Quarterly Gross Profit by Division',
                     template='plotly_dark')
        fig.update_layout(**PLOTLY_THEME, height=380, title_font_size=13)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(qtr, x='Quarter', y='Gross Margin %', color='Division',
                      color_discrete_map=DIV_COLOR, markers=True,
                      title='Quarterly Margin % by Division',
                      template='plotly_dark')
        fig.update_layout(**PLOTLY_THEME, height=380, title_font_size=13)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>🌡️ Monthly Margin Heatmap by Product</div>", unsafe_allow_html=True)
    pivot = df.groupby(['Month Name','Product Name'])['Gross Margin %'].mean().unstack(fill_value=0)
    month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    pivot = pivot.reindex([m for m in month_order if m in pivot.index])

    fig = px.imshow(pivot, color_continuous_scale='RdYlGn', aspect='auto',
                    title='Monthly Gross Margin % Heatmap — All Products',
                    labels=dict(x='Product', y='Month', color='Gross Margin %'),
                    text_auto='.0f', template='plotly_dark')
    fig.update_layout(**PLOTLY_THEME, height=450, title_font_size=14,
                      xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>🚚 Ship Mode Analysis</div>", unsafe_allow_html=True)
    ship = df.groupby('Ship Mode').agg(
        Total_Sales  =('Sales','sum'),
        Total_Profit =('Gross Profit','sum'),
        Orders       =('Row ID','count'),
        Avg_Lead     =('Lead Time','mean'),
    ).reset_index()
    ship['Gross Margin %'] = ship['Total_Profit'] / ship['Total_Sales'] * 100

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(ship, x='Ship Mode', y='Orders', color='Gross Margin %',
                     color_continuous_scale='RdYlGn',
                     title='Orders & Margin by Ship Mode', template='plotly_dark', text='Orders')
        fig.update_traces(textposition='outside')
        fig.update_layout(**PLOTLY_THEME, height=360, title_font_size=13)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(ship, x='Ship Mode', y='Avg_Lead', color='Avg_Lead',
                     color_continuous_scale='RdYlGn_r',
                     title='Average Lead Time by Ship Mode (Days)',
                     template='plotly_dark', text='Avg_Lead')
        fig.update_traces(texttemplate='%{text:.1f}d', textposition='outside')
        fig.update_layout(**PLOTLY_THEME, height=360, title_font_size=13)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("<div class='section-header'>📋 Executive Summary</div>", unsafe_allow_html=True)

    top3_profit    = prod.nlargest(3,'Total_Profit')['Product Name'].tolist()
    top3_margin    = prod.nlargest(3,'Gross Margin %')['Product Name'].tolist()
    bottom3_margin = prod.nsmallest(3,'Gross Margin %')['Product Name'].tolist()
    stars  = prod[prod['Classification']=='⭐ Star']['Product Name'].tolist()
    traps  = prod[prod['Classification']=='⚠️ Volume Trap']['Product Name'].tolist()
    gems   = prod[prod['Classification']=='💎 Hidden Gem']['Product Name'].tolist()
    best_div    = div_agg.loc[div_agg['Gross Margin %'].idxmax(),'Division']
    worst_div   = div_agg.loc[div_agg['Gross Margin %'].idxmin(),'Division']
    best_region = region_agg.loc[region_agg['Gross Margin %'].idxmax(),'Region']
    n80 = int((prod_pareto['Cum Profit %'] <= 80).sum())

    st.markdown(f"""
    <div style='background:#1a1a2e; border:1px solid #2a2a4a; border-radius:12px; padding:28px; line-height:1.9;'>

    <h2 style='color:#f0a500; border-bottom:2px solid #7b5ea7; padding-bottom:10px;'>
    🍬 Nassau Candy Distributor — FY Executive Summary
    </h2>

    <h3 style='color:#4ecdc4;'>📊 Financial Performance</h3>
    <ul>
        <li>Total Revenue: <b style='color:#7b5ea7;'>${total_sales:,.2f}</b></li>
        <li>Total Gross Profit: <b style='color:#4ecdc4;'>${total_profit:,.2f}</b></li>
        <li>Total Cost: <b style='color:#e05c5c;'>${total_cost:,.2f}</b></li>
        <li>Overall Gross Margin: <b style='color:#f0a500;'>{overall_margin:.1f}%</b></li>
        <li>Total Orders Processed: <b style='color:#e0e0ff;'>{len(df):,}</b></li>
    </ul>

    <h3 style='color:#4ecdc4;'>🏆 Top Performers</h3>
    <ul>
        <li><b>Highest Profit Products:</b> {', '.join(top3_profit)}</li>
        <li><b>Highest Margin Products:</b> {', '.join(top3_margin)}</li>
        <li><b>Star Products (High Sales + High Margin):</b> {', '.join(stars) if stars else 'None under current filters'}</li>
        <li><b>Hidden Gems (Low Sales + High Margin):</b> {', '.join(gems) if gems else 'None'}</li>
        <li><b>Best Performing Division:</b> {best_div}</li>
        <li><b>Best Performing Region:</b> {best_region}</li>
    </ul>

    <h3 style='color:#e05c5c;'>⚠️ Risk Flags</h3>
    <ul>
        <li><b>Volume Traps (High Sales, Low Margin):</b> {', '.join(traps) if traps else 'None'}</li>
        <li><b>Lowest Margin Products:</b> {', '.join(bottom3_margin)}</li>
        <li><b>Weakest Division:</b> {worst_div}</li>
        <li><b>Pareto Risk:</b> Only <b style='color:#e05c5c;'>{n80} products</b> drive 80% of profit</li>
    </ul>

    <h3 style='color:#f0a500;'>🎯 Strategic Recommendations</h3>
    <ol>
        <li><b style='color:#4ecdc4;'>INVEST</b> — Prioritize shelf space, promotions, and supply chain for
            <b>{', '.join(top3_profit[:2])}</b> — your highest profit drivers.</li>
        <li><b style='color:#f0a500;'>REPRICE</b> — Volume Trap products dilute margins. Review pricing or
            renegotiate sourcing for <b>{', '.join(traps) if traps else 'flagged items'}</b>.</li>
        <li><b style='color:#e05c5c;'>REVIEW</b> — Bottom-margin products should be flagged for cost
            renegotiation or discontinuation: <b>{', '.join(bottom3_margin)}</b>.</li>
        <li><b style='color:#7b5ea7;'>DIVERSIFY</b> — Reduce concentration risk by scaling Hidden Gem
            products: <b>{', '.join(gems) if gems else 'see analysis'}</b>.</li>
        <li><b style='color:#96ceb4;'>REGIONAL</b> — Focus marketing investment in <b>{best_region}</b> region
            (highest margin) and investigate underperforming regions.</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>💾 Download Filtered Data</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        csv_prod = prod.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Product Analysis", csv_prod,
                           "nassau_product_analysis.csv", "text/csv", use_container_width=True)
    with c2:
        csv_div = div_agg.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Division Analysis", csv_div,
                           "nassau_division_analysis.csv", "text/csv", use_container_width=True)
    with c3:
        csv_raw = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Filtered Raw Data", csv_raw,
                           "nassau_filtered_data.csv", "text/csv", use_container_width=True)
