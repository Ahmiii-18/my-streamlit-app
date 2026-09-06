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

# 1. Global Page Configuration
st.set_page_config(
    page_title="GADM Spatial Analytics | SAP 70177829",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern Off-White CSS Theme Design System
st.markdown("""
<style>
    /* Main Canvas Background */
    .stApp {
        background-color: #f8f9fa;
        color: #1a1f2c;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Summary Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        color: #1a73e8;
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    
    /* Top Header Container */
    .hero-container {
        text-align: center;
        padding: 28px 20px;
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }
    
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1a73e8;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar Aesthetics */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Comparison & Information Cards */
    .info-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

# 3. Dashboard Title Banner
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🌐 Global Administrative Boundaries & Demographics</h1>
    <p style="color:#5f6368; font-size: 1.1rem; margin:0;">
        Exploratory Spatial Data Analysis Platform &nbsp;|&nbsp; <strong>Ahmad Sheraz</strong> &nbsp;|&nbsp; SAP ID: 70177829
    </p>
</div>
""", unsafe_allow_html=True)

# 4. Interactive Feature Breakdown & Explanation Guide
with st.expander("📖 What is happening here? (Dashboard Architecture & User Guide)", expanded=False):
    st.markdown("""
    ### Overview
    This interactive web application retrieves, processes, and visualizes spatial geometries and macroeconomic metrics across world countries in real time.

    #### System Architecture:
    1. **Data Pipeline**: The engine fetches vector boundary geometries (`countries.geojson`) alongside updated macroeconomic attributes (`population.csv` and `gdp.csv`) directly from open-data repositories.
    2. **Spatial Join Engine**: The tabular datasets are combined using standardized **ISO 3166-1 Alpha-3** boundary codes to pair geographic shapes with economic indices.
    3. **Interactive Control Panel**: The left sidebar provides real-time state management over the dataset (filtering by continent, population thresholds, or specific nations).

    #### How to Navigate & Interact:
    * **🎛️ Filter Controls**: Adjust continent toggles or the population range slider in the sidebar. All dynamic cards, choropleths, scatter plots, and ranking charts update instantly.
    * **🗺️ Choropleth Map Interaction**: Hover over any individual boundary to inspect full details. Use the map controls (top right of the chart) to zoom in, pan, or isolate specific geographic zones.
    * **⚔️ Side-by-Side Comparison**: Select two countries in the comparative inspection panel to measure relative population size, overall economy, and per-capita metrics.
    * **📋 Dataset Inspection & Export**: Scroll down to view the processed dataset table and hit **"Download Dataset as CSV"** to save your filtered subset locally.
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
    
    # Safe renaming of geometry attribute columns
    col_map = {"ISO3166-1-Alpha-3": "iso3"}
    if "name" in world.columns:
        col_map["name"] = "country_name"
    elif "ADMIN" in world.columns:
        col_map["ADMIN"] = "country_name"

    world.rename(columns=col_map, inplace=True)

    # Process and clean Population records
    pop_df = pd.read_csv(pop)
    pop_l = pop_df.sort_values("Year").groupby("Country Code").last().reset_index()[["Country Code", "Value"]].rename(columns={"Country Code": "iso3", "Value": "pop_est"})

    # Process and clean GDP records
    gdp_df = pd.read_csv(gdp)
    gdp_l = gdp_df.sort_values("Year").groupby("Country Code").last().reset_index()[["Country Code", "Value"]].rename(columns={"Country Code": "iso3", "Value": "gdp_usd"})

    # Merge Vector Shapes with Tabular Attribute Records
    world = world.merge(pop_l, on="iso3", how="left").merge(gdp_l, on="iso3", how="left")

    # Mapping Continent Classifications
    cmap = {
        "AFG":"Asia","ALB":"Europe","DZA":"Africa","AGO":"Africa","ARG":"South America","ARM":"Asia","AUS":"Oceania","AUT":"Europe","AZE":"Asia","BGD":"Asia","BLR":"Europe","BEL":"Europe","BEN":"Africa","BTN":"Asia","BOL":"South America","BIH":"Europe","BWA":"Africa","BRA":"South America","BRN":"Asia","BGR":"Europe","BFA":"Africa","BDI":"Africa","KHM":"Asia","CMR":"Africa","CAN":"North America","CAF":"Africa","TCD":"Africa","CHL":"South America","CHN":"Asia","COL":"South America","COD":"Africa","COG":"Africa","CRI":"North America","HRV":"Europe","CUB":"North America","CYP":"Europe","CZE":"Europe","DNK":"Europe","DJI":"Africa","DOM":"North America","ECU":"South America","EGY":"Africa","SLV":"North America","GNQ":"Africa","ERI":"Africa","EST":"Europe","ETH":"Africa","FJI":"Oceania","FIN":"Europe","FRA":"Europe","GAB":"Africa","GMB":"Africa","GEO":"Asia","DEU":"Europe","GHA":"Africa","GRC":"Europe","GTM":"North America","GIN":"Africa","GNB":"Africa","GUY":"South America","HTI":"North America","HND":"North America","HUN":"Europe","ISL":"Europe","IND":"Asia","IDN":"Asia","IRN":"Asia","IRQ":"Asia","IRL":"Europe","ISR":"Asia","ITA":"Europe","JAM":"North America","JPN":"Asia","JOR":"Asia","KAZ":"Asia","KEN":"Africa","PRK":"Asia","KOR":"Asia","KWT":"Asia","KGZ":"Asia","LAO":"Asia","LVA":"Europe","LBN":"Asia","LSO":"Africa","LBR":"Africa","LBY":"Africa","LTU":"Europe","LUX":"Europe","MKD":"Europe","MDG":"Africa","MWI":"Africa","MYS":"Asia","MDV":"Asia","MLI":"Africa","MLT":"Europe","MRT":"Africa","MUS":"Africa","MEX":"North America","MDA":"Europe","MNG":"Asia","MNE":"Europe","MAR":"Africa","MOZ":"Africa","MMR":"Asia","NAM":"Africa","NPL":"Asia","NLD":"Europe","NZL":"Oceania","NIC":"North America","NER":"Africa","NGA":"Africa","NOR":"Europe","OMN":"Asia","PAK":"Asia","PAN":"North America","PNG":"Oceania","PRY":"South America","PER":"South America","PHL":"Asia","POL":"Europe","PRT":"Europe","QAT":"Asia","ROU":"Europe","RUS":"Europe","RWA":"Africa","SAU":"Asia","SEN":"Africa","SRB":"Europe","SLE":"Africa","SGP":"Asia","SVK":"Europe","SVN":"Europe","SOM":"Africa","ZAF":"Africa","SSD":"Africa","ESP":"Europe","LKA":"Asia","SDN":"Africa","SUR":"South America","SWZ":"Africa","SWE":"Europe","CHE":"Europe","SYR":"Asia","TWN":"Asia","TJK":"Asia","TZA":"Africa","THA":"Asia","TLS":"Asia","TGO":"Africa","TTO":"North America","TUN":"Africa","TUR":"Asia","TKM":"Asia","UGA":"Africa","UKR":"Europe","ARE":"Asia","GBR":"Europe","USA":"North America","URY":"South America","UZB":"Asia","VEN":"South America","VNM":"Asia","YEM":"Asia","ZMB":"Africa","ZWE":"Africa"
    }
    world["continent"] = world["iso3"].map(cmap).fillna("Other")
    world["gdp_B"] = world["gdp_usd"] / 1e9
    world["pop_M"] = world["pop_est"] / 1e6
    world["gdp_per_capita"] = (world["gdp_usd"] / world["pop_est"]).round(2)
    return world

with st.spinner("Processing Geographic Vector Layers & Indicators..."):
    world = load_data()

# 6. Sidebar Dashboard Control Engine
st.sidebar.title("🎛️ Control Panel")

st.sidebar.markdown("---")
st.sidebar.subheader("1. Regional & Scale Filters")
all_cont = sorted([c for c in world["continent"].unique() if c != "Other"])
sel_cont = st.sidebar.multiselect("Active Continents", all_cont, default=all_cont)

pop_max = int(world["pop_M"].max() * 1.1)
pop_range = st.sidebar.slider("Population Scale (Millions)", 0, pop_max, (0, pop_max))

st.sidebar.markdown("---")
st.sidebar.subheader("2. Isolation & Search")
search_country = st.sidebar.selectbox(
    "Focus Single Country",
    options=["All Countries"] + sorted(world["country_name"].dropna().unique().tolist())
)

st.sidebar.markdown("---")
st.sidebar.subheader("3. Color Palette")
map_theme = st.sidebar.selectbox("Choropleth Color Scale", ["Blues", "Viridis", "Plasma", "Turbo", "Cividis"], index=0)

# Filter Data Logic
filtered = world[
    (world["continent"].isin(sel_cont) | (world["continent"] == "Other")) &
    (world["pop_M"].fillna(0) >= pop_range[0]) &
    (world["pop_M"].fillna(0) <= pop_range[1])
].copy()

if search_country != "All Countries":
    filtered = filtered[filtered["country_name"] == search_country]

plot_df = pd.DataFrame(filtered.drop(columns=["geometry"]))

st.sidebar.markdown("---")
st.sidebar.success(f"📊 **Matched Records**: **{len(plot_df)}** / **{len(world)}** total countries.")

# 7. Dynamic Summary Metric Cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌐 Evaluated Countries", f"{len(plot_df)}")
c2.metric("🌍 Continents Selected", f"{len(sel_cont)}")
c3.metric("👥 Combined Population", f"{plot_df['pop_M'].sum()/1000:.2f} B" if plot_df['pop_M'].sum()>=1000 else f"{plot_df['pop_M'].sum():.0f} M")
c4.metric("💰 Combined GDP", f"${plot_df['gdp_B'].sum()/1000:.2f} T" if plot_df['gdp_B'].sum()>=1000 else f"${plot_df['gdp_B'].sum():.1f} B")

st.markdown("---")

# 8. Interactive Choropleth Geospatial Map
st.subheader("🗺️ Dynamic Spatial Choropleth")

map_metric = st.radio(
    "Select Target Choropleth Metric:",
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

# 9. Macroeconomic Exploratory Charts
st.subheader("📈 Correlation & Variance Analysis")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Population vs GDP Logarithmic Scale Scatter**")
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
    st.markdown("**Economic Output Dispersion by Continent**")
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

# 10. Interactive Side-by-Side Country Comparison
st.subheader("⚔️ Comparative Country Inspector")
all_nations = sorted(world["country_name"].dropna().unique().tolist())
comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    c_one = st.selectbox("First Country", options=all_nations, index=all_nations.index("United States") if "United States" in all_nations else 0)
with comp_col2:
    c_two = st.selectbox("Second Country", options=all_nations, index=all_nations.index("China") if "China" in all_nations else 1)

if c_one and c_two:
    df_comp = world[world["country_name"].isin([c_one, c_two])].copy()
    
    r1_df = df_comp[df_comp["country_name"] == c_one]
    r2_df = df_comp[df_comp["country_name"] == c_two]
    
    if not r1_df.empty and not r2_df.empty:
        r1 = r1_df.iloc[0]
        r2 = r2_df.iloc[0]
        
        comp_card_a, comp_card_b = st.columns(2)
        
        with comp_card_a:
            st.markdown(f"""
            <div class="info-card">
                <h3 style="color:#1a73e8; margin-top:0;">{r1['country_name']}</h3>
                <p><b>Continent:</b> {r1['continent']}</p>
                <p><b>Population:</b> {r1['pop_M']:.2f} Million</p>
                <p><b>Total GDP:</b> ${r1['gdp_B']:.2f} Billion</p>
                <p><b>Per Capita Income:</b> ${r1['gdp_per_capita']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with comp_card_b:
            st.markdown(f"""
            <div class="info-card">
                <h3 style="color:#1a73e8; margin-top:0;">{r2['country_name']}</h3>
                <p><b>Continent:</b> {r2['continent']}</p>
                <p><b>Population:</b> {r2['pop_M']:.2f} Million</p>
                <p><b>Total GDP:</b> ${r2['gdp_B']:.2f} Billion</p>
                <p><b>Per Capita Income:</b> ${r2['gdp_per_capita']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# 11. Top Ranked Economies & Data Export Section
st.subheader("🏆 Top Ranked Economies & Raw Data Engine")
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

with st.expander("📋 View & Export Complete Dataset Table"):
    export_df = plot_df[["country_name", "iso3", "continent", "pop_M", "gdp_B", "gdp_per_capita"]].rename(
        columns={
            "country_name": "Country Name", 
            "iso3": "ISO Code", 
            "continent": "Continent", 
            "pop_M": "Population (M)", 
            "gdp_B": "GDP ($B)",
            "gdp_per_capita": "Per Capita GDP ($)"
        }
    ).sort_values("Population (M)", ascending=False)
    
    st.dataframe(export_df, use_container_width=True)
    
    csv_bytes = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Dataset as CSV",
        data=csv_bytes,
        file_name='gadm_world_demographics_export.csv',
        mime='text/csv'
    )