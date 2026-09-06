"""
Streamlit Modern Interactive Dashboard — GADM World Admin Boundaries EDA
SAP ID: 70177829
Run: streamlit run app.py
"""
import warnings
warnings.filterwarnings("ignore")

import os
import requests
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Modern GADM Dashboard | SAP 70177829",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Styling (Off-White Light Theme)
st.markdown("""
<style>
    /* Global off-white background */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* Styled metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        color: #1a73e8;
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    /* Main Hero Title */
    .hero-container {
        text-align: center;
        padding: 24px;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1a73e8;
        margin-bottom: 6px;
    }
    
    /* Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    /* Guide box */
    .guide-box {
        background-color: #ffffff;
        border-left: 4px solid #1a73e8;
        padding: 16px 20px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header Title
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🌐 GADM World Boundaries & Demographics</h1>
    <p style="color:#5f6368; font-size: 1.05rem; margin:0;">
        Interactive Analytics Dashboard &nbsp;|&nbsp; <strong>Ahmad Sheraz</strong> &nbsp;|&nbsp; SAP ID: 70177829
    </p>
</div>
""", unsafe_allow_html=True)

# 4. User Interaction & Feature Breakdown
with st.expander("📖 Interactive Guide & How to Use", expanded=False):
    st.markdown("""
    Welcome to the **GADM World Administrative Boundaries Dashboard**. This application enables spatial demographics analysis and macroeconomic comparison across global administrative boundaries.

    #### User Interaction Features:
    * **🎛️ Advanced Sidebar Controls**: Use the left sidebar to filter by region, filter by population scale, search specific countries, or switch colors/metrics.
    * **🔍 Specific Country Search**: Search and highlight individual countries dynamically across all visual analytics.
    * **🗺️ Interactive Spatial Map**: Hover over any country to inspect its name, total population, and GDP. Use the map toolbar to pan, zoom, or capture image exports.
    * **⚔️ Side-by-Side Country Comparison**: Compare two nations directly on macroeconomic indicators (GDP, Population, and GDP per Capita).
    * **📋 Complete Dataset Export**: Scroll to the data table at the bottom to explore or download the complete filtered dataset as a CSV file.
    """)

# 5. Cached Data Engine
@st.cache_data
def load_data():
    os.makedirs("data", exist_ok=True)
    def dl(url, path):
        if not os.path.exists(path):
            r = requests.get(url, verify=False, timeout=15)
            with open(path, "wb") as f:
                f.write(r.content)
        return path

    geo = dl("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson", "data/countries.geojson")
    pop = dl("https://raw.githubusercontent.com/datasets/population/master/data/population.csv", "data/pop.csv")
    gdp = dl("https://raw.githubusercontent.com/datasets/gdp/master/data/gdp.csv", "data/gdp.csv")

    world = gpd.read_file(geo)
    col_map = {"ISO3166-1-Alpha-3": "iso3"}
    if "name" in world.columns:
        col_map["name"] = "country_name"
    elif "ADMIN" in world.columns:
        col_map["ADMIN"] = "country_name"

    world.rename(columns=col_map, inplace=True)

    pop_df = pd.read_csv(pop)
    pop_l = pop_df.sort_values("Year").groupby("Country Code").last().reset_index()[["Country Code", "Value"]].rename(columns={"Country Code": "iso3", "Value": "pop_est"})

    gdp_df = pd.read_csv(gdp)
    gdp_l = gdp_df.sort_values("Year").groupby("Country Code").last().reset_index()[["Country Code", "Value"]].rename(columns={"Country Code": "iso3", "Value": "gdp_usd"})

    world = world.merge(pop_l, on="iso3", how="left").merge(gdp_l, on="iso3", how="left")

    cmap = {
        "AFG":"Asia","ALB":"Europe","DZA":"Africa","AGO":"Africa","ARG":"South America","ARM":"Asia","AUS":"Oceania","AUT":"Europe","AZE":"Asia","BGD":"Asia","BLR":"Europe","BEL":"Europe","BEN":"Africa","BTN":"Asia","BOL":"South America","BIH":"Europe","BWA":"Africa","BRA":"South America","BRN":"Asia","BGR":"Europe","BFA":"Africa","BDI":"Africa","KHM":"Asia","CMR":"Africa","CAN":"North America","CAF":"Africa","TCD":"Africa","CHL":"South America","CHN":"Asia","COL":"South America","COD":"Africa","COG":"Africa","CRI":"North America","HRV":"Europe","CUB":"North America","CYP":"Europe","CZE":"Europe","DNK":"Europe","DJI":"Africa","DOM":"North America","ECU":"South America","EGY":"Africa","SLV":"North America","GNQ":"Africa","ERI":"Africa","EST":"Europe","ETH":"Africa","FJI":"Oceania","FIN":"Europe","FRA":"Europe","GAB":"Africa","GMB":"Africa","GEO":"Asia","DEU":"Europe","GHA":"Africa","GRC":"Europe","GTM":"North America","GIN":"Africa","GNB":"Africa","GUY":"South America","HTI":"North America","HND":"North America","HUN":"Europe","ISL":"Europe","IND":"Asia","IDN":"Asia","IRN":"Asia","IRQ":"Asia","IRL":"Europe","ISR":"Asia","ITA":"Europe","JAM":"North America","JPN":"Asia","JOR":"Asia","KAZ":"Asia","KEN":"Africa","PRK":"Asia","KOR":"Asia","KWT":"Asia","KGZ":"Asia","LAO":"Asia","LVA":"Europe","LBN":"Asia","LSO":"Africa","LBR":"Africa","LBY":"Africa","LTU":"Europe","LUX":"Europe","MKD":"Europe","MDG":"Africa","MWI":"Africa","MYS":"Asia","MDV":"Asia","MLI":"Africa","MLT":"Europe","MRT":"Africa","MUS":"Africa","MEX":"North America","MDA":"Europe","MNG":"Asia","MNE":"Europe","MAR":"Africa","MOZ":"Africa","MMR":"Asia","NAM":"Africa","NPL":"Asia","NLD":"Europe","NZL":"Oceania","NIC":"North America","NER":"Africa","NGA":"Africa","NOR":"Europe","OMN":"Asia","PAK":"Asia","PAN":"North America","PNG":"Oceania","PRY":"South America","PER":"South America","PHL":"Asia","POL":"Europe","PRT":"Europe","QAT":"Asia","ROU":"Europe","RUS":"Europe","RWA":"Africa","SAU":"Asia","SEN":"Africa","SRB":"Europe","SLE":"Africa","SGP":"Asia","SVK":"Europe","SVN":"Europe","SOM":"Africa","ZAF":"Africa","SSD":"Africa","ESP":"Europe","LKA":"Asia","SDN":"Africa","SUR":"South America","SWZ":"Africa","SWE":"Europe","CHE":"Europe","SYR":"Asia","TWN":"Asia","TJK":"Asia","TZA":"Africa","THA":"Asia","TLS":"Asia","TGO":"Africa","TTO":"North America","TUN":"Africa","TUR":"Asia","TKM":"Asia","UGA":"Africa","UKR":"Europe","ARE":"Asia","GBR":"Europe","USA":"North America","URY":"South America","UZB":"Asia","VEN":"South America","VNM":"Asia","YEM":"Asia","ZMB":"Africa","ZWE":"Africa"
    }
    world["continent"] = world["iso3"].map(cmap).fillna("Other")
    world["gdp_B"] = world["gdp_usd"] / 1e9
    world["pop_M"] = world["pop_est"] / 1e6
    world["gdp_per_capita"] = (world["gdp_usd"] / world["pop_est"]).round(2)
    return world

with st.spinner("Initializing GADM Dataset Engine..."):
    world = load_data()

# 6. Sidebar Implementation & Custom Controls
st.sidebar.title("🎛️ Dashboard Controls")

st.sidebar.markdown("---")
st.sidebar.subheader("1. Regional Filters")
all_cont = sorted([c for c in world["continent"].unique() if c != "Other"])
sel_cont = st.sidebar.multiselect("Select Continents", all_cont, default=all_cont)

pop_max = int(world["pop_M"].max() * 1.1)
pop_range = st.sidebar.slider("Population Range (Millions)", 0, pop_max, (0, pop_max))

st.sidebar.markdown("---")
st.sidebar.subheader("2. Search & Focus")
search_country = st.sidebar.selectbox(
    "Focus Country",
    options=["All Countries"] + sorted(world["country_name"].dropna().unique().tolist())
)

st.sidebar.markdown("---")
st.sidebar.subheader("3. Visualization Settings")
map_theme = st.sidebar.selectbox("Map Color Palette", ["Blues", "Viridis", "Cividis", "Plasma", "Turbo"], index=0)

# Filter Dataset
filtered = world[
    (world["continent"].isin(sel_cont) | (world["continent"] == "Other")) &
    (world["pop_M"].fillna(0) >= pop_range[0]) &
    (world["pop_M"].fillna(0) <= pop_range[1])
].copy()

if search_country != "All Countries":
    filtered = filtered[filtered["country_name"] == search_country]

plot_df = pd.DataFrame(filtered.drop(columns=["geometry"]))

# Sidebar Status Callout
st.sidebar.markdown("---")
st.sidebar.info(f"📊 **Active Selection**: Showing **{len(plot_df)}** out of **{len(world)}** total administrative boundaries.")

# 7. Summary KPI Cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌐 Total Countries", f"{len(plot_df)}")
c2.metric("🌍 Continents Selected", f"{len(sel_cont)}")
c3.metric("👥 Population", f"{plot_df['pop_M'].sum()/1000:.2f} B" if plot_df['pop_M'].sum()>=1000 else f"{plot_df['pop_M'].sum():.0f} M")
c4.metric("💰 Total GDP", f"${plot_df['gdp_B'].sum()/1000:.2f} T" if plot_df['gdp_B'].sum()>=1000 else f"${plot_df['gdp_B'].sum():.1f} B")

st.markdown("---")

# 8. Interactive Spatial Visualizations
st.subheader("🗺️ Dynamic Spatial Analytics")

map_metric = st.radio(
    "Choose Map Metric Variable:",
    options=["Population (Millions)", "GDP (Billion USD)"],
    horizontal=True
)

color_col = "pop_M" if map_metric == "Population (Millions)" else "gdp_B"
label_name = "Population (M)" if map_metric == "Population (Millions)" else "GDP ($B)"

fig_map = px.choropleth(
    plot_df,
    locations="iso3",
    locationmode="ISO-3",
    color=color_col,
    hover_name="country_name",
    hover_data={"pop_M": ":.2f", "gdp_B": ":.2f", "gdp_per_capita": ":.0f", "continent": True, "iso3": False},
    labels={color_col: label_name, "pop_M": "Population (M)", "gdp_B": "GDP ($B)", "gdp_per_capita": "GDP Per Capita ($)"},
    color_continuous_scale=map_theme,
    projection="natural earth",
    template="plotly_white"
)

fig_map.update_layout(
    margin={"r":0,"t":10,"l":0,"b":0},
    paper_bgcolor='#ffffff',
    plot_bgcolor='#ffffff'
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# 9. Statistical Analysis Charts
st.subheader("📈 Correlation & Distribution")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Population vs GDP Correlation**")
    fig_scatter = px.scatter(
        plot_df.dropna(subset=["pop_M", "gdp_B"]),
        x="pop_M",
        y="gdp_B",
        color="continent",
        size="pop_M",
        hover_name="country_name",
        log_x=True,
        log_y=True,
        labels={"pop_M": "Population (Millions, Log)", "gdp_B": "GDP (Billion USD, Log)"},
        template="plotly_white"
    )
    fig_scatter.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff')
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_b:
    st.markdown("**Regional Economic Output Variance**")
    fig_box = px.box(
        plot_df.dropna(subset=["gdp_B"]),
        x="continent",
        y="gdp_B",
        color="continent",
        points="all",
        hover_name="country_name",
        log_y=True,
        labels={"gdp_B": "GDP ($ Billions, Log Scale)", "continent": "Continent"},
        template="plotly_white"
    )
    fig_box.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# 10. Country Comparison Interactive Tool
st.subheader("⚔️ Direct Country Comparison Tool")
all_nations = sorted(world["country_name"].dropna().unique().tolist())
comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    c_one = st.selectbox("Select Country A", options=all_nations, index=all_nations.index("United States") if "United States" in all_nations else 0)
with comp_col2:
    c_two = st.selectbox("Select Country B", options=all_nations, index=all_nations.index("China") if "China" in all_nations else 1)

if c_one and c_two:
    df_comp = world[world["country_name"].isin([c_one, c_two])].copy()
    
    comp_metrics_col1, comp_metrics_col2 = st.columns(2)
    
    row1 = df_comp[df_comp["country_name"] == c_one].iloc[0] if len(df_comp[df_comp["country_name"] == c_one]) > 0 else None
    row2 = df_comp[df_comp["country_name"] == c_two].iloc[0] if len(df_comp[df_comp["country_name"] == c_two]) > 0 else None
    
    if row1 is not None and row2 is not None:
        with comp_metrics_col1:
            st.markdown(f"### {row1['country_name']}")
            st.write(f"**Continent:** {row1['continent']}")
            st.write(f"**Population:** {row1['pop_M']:.2f} Million")
            st.write(f"**GDP:** ${row1['gdp_B']:.2f} Billion")
            st.write(f"**GDP Per Capita:** ${row1['gdp_per_capita']:,.2f}")
            
        with comp_metrics_col2:
            st.markdown(f"### {row2['country_name']}")
            st.write(f"**Continent:** {row2['continent']}")
            st.write(f"**Population:** {row2['pop_M']:.2f} Million")
            st.write(f"**GDP:** ${row2['gdp_B']:.2f} Billion")
            st.write(f"**GDP Per Capita:** ${row2['gdp_per_capita']:,.2f}")

st.markdown("---")

# 11. Top 10 Dynamic Ranking & Export Table
st.subheader("🏆 Top Ranked Economies & Data Export")
top10 = plot_df.nlargest(10, "pop_M")

fig_bar = px.bar(
    top10,
    x="pop_M",
    y="country_name",
    orientation="h",
    color="gdp_B",
    hover_data=["continent", "gdp_B"],
    labels={"pop_M": "Population (Millions)", "country_name": "Country", "gdp_B": "GDP ($B)"},
    color_continuous_scale="Blues",
    template="plotly_white"
)
fig_bar.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    paper_bgcolor='#ffffff',
    plot_bgcolor='#ffffff'
)
st.plotly_chart(fig_bar, use_container_width=True)

with st.expander("📋 View & Export Full Filtered Dataset"):
    export_df = plot_df[["country_name", "iso3", "continent", "pop_M", "gdp_B", "gdp_per_capita"]].rename(
        columns={
            "country_name": "Country", 
            "iso3": "ISO Code", 
            "continent": "Continent", 
            "pop_M": "Population (M)", 
            "gdp_B": "GDP ($B)",
            "gdp_per_capita": "GDP Per Capita ($)"
        }
    ).sort_values("Population (M)", ascending=False)
    
    st.dataframe(export_df, use_container_width=True)
    
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Dataset as CSV",
        data=csv,
        file_name='gadm_world_demographics.csv',
        mime='text/csv'
    )