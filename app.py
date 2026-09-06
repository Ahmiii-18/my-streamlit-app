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

# 1. Page Config
st.set_page_config(
    page_title="Modern GADM Dashboard | SAP 70177829",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Off-White UI Styling
st.markdown("""
<style>
    /* Off-white background setup */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* Card containers */
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        color: #1a73e8;
    }
    
    /* Hero Header */
    .hero-container {
        text-align: center;
        padding: 20px 0;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1a73e8;
        margin-bottom: 5px;
    }
    
    /* Guide callout box */
    .guide-box {
        background-color: #ffffff;
        border-left: 4px solid #1a73e8;
        padding: 15px 20px;
        border-radius: 6px;
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🌐 GADM World Boundaries & Demographics</h1>
    <p style="color:#5f6368; font-size: 1.05rem; margin:0;">
        Interactive Analytics Dashboard &nbsp;|&nbsp; <strong>Ahmad Sheraz</strong> &nbsp;|&nbsp; SAP ID: 70177829
    </p>
</div>
""", unsafe_allow_html=True)

# 4. User Interaction & Feature Guide
with st.expander("📖 Interactive Dashboard Guide & Feature Breakdown", expanded=False):
    st.markdown("""
    Welcome to the **GADM World Administrative Boundaries Dashboard**. This platform allows you to perform real-time exploratory data analysis on spatial demography and macroeconomic metrics.

    #### How to Interact with the Dashboard:
    * **🎛️ Dynamic Sidebar Filtering**: Use the left sidebar to select specific continents or adjust the minimum population threshold slider. All metrics, maps, and statistical charts will update immediately.
    * **🗺️ Map Controls**: Hover over any country on the choropleth map to display detailed information (Country Name, ISO Code, Population, GDP). You can zoom in/out, pan across regions, or save map snapshots using the top-right toolbar on each chart.
    * **📊 Interactive Metric Switcher**: Toggle between **Population** and **GDP** views in the spatial section to re-index the map color gradient.
    * **📈 Chart Hover & Isolation**: Double-click on any continent name in chart legends to isolate that region, or single-click to turn visibility on/off.
    * **📋 Raw Data Inspection**: Scroll to the bottom and expand **"Explore Raw Data"** to filter, search, or sort the complete underlying dataset.
    """)

# 5. Data Engine
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
    return world

with st.spinner("Loading environment dataset..."):
    world = load_data()

# 6. Sidebar Controls
st.sidebar.title("🎛️ Dashboard Controls")
all_cont = sorted([c for c in world["continent"].unique() if c != "Other"])
sel_cont = st.sidebar.multiselect("Filter Continents", all_cont, default=all_cont)

pop_max = int(world["pop_M"].max() * 1.1)
pop_range = st.sidebar.slider("Population Threshold (Millions)", 0, pop_max, (0, pop_max))

filtered = world[
    (world["continent"].isin(sel_cont) | (world["continent"] == "Other")) &
    (world["pop_M"].fillna(0) >= pop_range[0]) &
    (world["pop_M"].fillna(0) <= pop_range[1])
].copy()

plot_df = pd.DataFrame(filtered.drop(columns=["geometry"]))

# 7. Summary Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌐 Total Countries", f"{len(plot_df)}")
c2.metric("🌍 Continents Selected", f"{len(sel_cont)}")
c3.metric("👥 Total Population", f"{plot_df['pop_M'].sum()/1000:.2f} B" if plot_df['pop_M'].sum()>=1000 else f"{plot_df['pop_M'].sum():.0f} M")
c4.metric("💰 Total GDP", f"${plot_df['gdp_B'].sum()/1000:.2f} T" if plot_df['gdp_B'].sum()>=1000 else f"${plot_df['gdp_B'].sum():.1f} B")

st.markdown("---")

# 8. Interactive Spatial Choropleth
st.subheader("🗺️ Dynamic World Spatial Analysis")

metric_choice = st.radio(
    "Select Map Variable:",
    options=["Population (Millions)", "GDP (Billion USD)"],
    horizontal=True
)

if metric_choice == "Population (Millions)":
    fig_map = px.choropleth(
        plot_df,
        locations="iso3",
        locationmode="ISO-3",
        color="pop_M",
        hover_name="country_name",
        hover_data={"pop_M": ":.2f", "gdp_B": ":.2f", "continent": True, "iso3": False},
        labels={"pop_M": "Population (M)", "gdp_B": "GDP ($B)"},
        color_continuous_scale="Blues",
        projection="natural earth",
        template="plotly_white"
    )
else:
    fig_map = px.choropleth(
        plot_df,
        locations="iso3",
        locationmode="ISO-3",
        color="gdp_B",
        hover_name="country_name",
        hover_data={"gdp_B": ":.2f", "pop_M": ":.2f", "continent": True, "iso3": False},
        labels={"gdp_B": "GDP ($B)", "pop_M": "Population (M)"},
        color_continuous_scale="Viridis",
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

# 9. Statistical Visualizations
st.subheader("📈 Macroeconomic Correlation & Variance")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Population vs GDP Relationship**")
    fig_scatter = px.scatter(
        plot_df.dropna(subset=["pop_M", "gdp_B"]),
        x="pop_M",
        y="gdp_B",
        color="continent",
        size="pop_M",
        hover_name="country_name",
        log_x=True,
        log_y=True,
        labels={"pop_M": "Population (Millions, Log Scale)", "gdp_B": "GDP (Billion USD, Log Scale)"},
        template="plotly_white"
    )
    fig_scatter.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff')
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_b:
    st.markdown("**Regional Economic Output Distribution**")
    fig_box = px.box(
        plot_df.dropna(subset=["gdp_B"]),
        x="continent",
        y="gdp_B",
        color="continent",
        points="all",
        hover_name="country_name",
        log_y=True,
        labels={"gdp_B": "GDP in Billions (Log Scale)", "continent": "Continent"},
        template="plotly_white"
    )
    fig_box.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# 10. Top Rankings & Data Table
st.subheader("🏆 Top Ranked Economies")
top10 = plot_df.nlargest(10, "pop_M")

fig_bar = px.bar(
    top10,
    x="pop_M",
    y="country_name",
    orientation="h",
    color="gdp_B",
    hover_data=["continent", "gdp_B"],
    labels={"pop_M": "Population (Millions)", "country_name": "Country Name", "gdp_B": "GDP ($B)"},
    color_continuous_scale="Blues",
    template="plotly_white"
)
fig_bar.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    paper_bgcolor='#ffffff',
    plot_bgcolor='#ffffff'
)
st.plotly_chart(fig_bar, use_container_width=True)

with st.expander("📋 View Complete Filtered Dataset"):
    st.dataframe(
        plot_df[["country_name", "iso3", "continent", "pop_M", "gdp_B"]].rename(
            columns={"country_name": "Country", "iso3": "ISO Code", "continent": "Continent", "pop_M": "Population (M)", "gdp_B": "GDP ($B)"}
        ).sort_values("Population (M)", ascending=False),
        use_container_width=True
    )