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

# 2. Custom Modern UI Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        color: #00d2ff;
    }
    .hero-container {
        text-align: center;
        padding: 10px 0 25px 0;
        background: linear-gradient(135deg, rgba(26,115,232,0.15) 0%, rgba(0,188,212,0.15) 100%);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 25px;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🌐 GADM World Boundaries & Demographics</h1>
    <p style="color:#a0aec0; font-size: 1.1rem; margin:0;">
        Interactive Analytics Dashboard &nbsp;|&nbsp; <strong>Ahmad Sheraz</strong> &nbsp;|&nbsp; SAP ID: 70177829
    </p>
</div>
""", unsafe_allow_html=True)

# 4. Data Engine
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
    # Rename 'name' or 'ADMIN' to 'country_name' safely
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

with st.spinner("Initializing Interactive Engine..."):
    world = load_data()

# 5. Sidebar Controls
st.sidebar.title("🎛️ Interactive Controls")
all_cont = sorted([c for c in world["continent"].unique() if c != "Other"])
sel_cont = st.sidebar.multiselect("Filter Continents", all_cont, default=all_cont)

pop_max = int(world["pop_M"].max() * 1.1)
pop_range = st.sidebar.slider("Population Threshold (Millions)", 0, pop_max, (0, pop_max))

filtered = world[
    (world["continent"].isin(sel_cont) | (world["continent"] == "Other")) &
    (world["pop_M"].fillna(0) >= pop_range[0]) &
    (world["pop_M"].fillna(0) <= pop_range[1])
].copy()

# Convert GeoDataFrame to DataFrame
plot_df = pd.DataFrame(filtered.drop(columns=["geometry"]))

# 6. Key Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌐 Total Countries", f"{len(plot_df)}")
c2.metric("🌍 Continents Selected", f"{len(sel_cont)}")
c3.metric("👥 Total Population", f"{plot_df['pop_M'].sum()/1000:.2f} B" if plot_df['pop_M'].sum()>=1000 else f"{plot_df['pop_M'].sum():.0f} M")
c4.metric("💰 Total GDP", f"${plot_df['gdp_B'].sum()/1000:.2f} T" if plot_df['gdp_B'].sum()>=1000 else f"${plot_df['gdp_B'].sum():.1f} B")

st.markdown("---")

# 7. Interactive Geospatial Visualizations
st.subheader("🗺️ Dynamic World Choropleths")
map_tab1, map_tab2 = st.tabs(["Interactive Population Map", "Interactive GDP Map"])

with map_tab1:
    fig_pop = px.choropleth(
        plot_df,
        locations="iso3",
        locationmode="ISO-3",
        color="pop_M",
        hover_name="country_name",
        hover_data={"pop_M": ":.2f", "gdp_B": ":.2f", "continent": True, "iso3": False},
        labels={"pop_M": "Population (M)", "gdp_B": "GDP ($B)"},
        color_continuous_scale="Viridis",
        projection="natural earth"
    )
    fig_pop.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    st.plotly_chart(fig_pop, use_container_width=True)

with map_tab2:
    fig_gdp = px.choropleth(
        plot_df,
        locations="iso3",
        locationmode="ISO-3",
        color="gdp_B",
        hover_name="country_name",
        hover_data={"gdp_B": ":.2f", "pop_M": ":.2f", "continent": True, "iso3": False},
        labels={"gdp_B": "GDP ($B)", "pop_M": "Population (M)"},
        color_continuous_scale="Cividis",
        projection="natural earth"
    )
    fig_gdp.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    st.plotly_chart(fig_gdp, use_container_width=True)

st.markdown("---")

# 8. Interactive Analytical Charts
st.subheader("📈 Statistical Explorer")
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
        template="plotly_dark"
    )
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_b:
    st.markdown("**GDP Distribution by Continent**")
    fig_box = px.box(
        plot_df.dropna(subset=["gdp_B"]),
        x="continent",
        y="gdp_B",
        color="continent",
        points="all",
        hover_name="country_name",
        log_y=True,
        labels={"gdp_B": "GDP in Billions (Log Scale)"},
        template="plotly_dark"
    )
    fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# 9. Top 10 Dynamic Ranking
st.subheader("🏆 Top 10 Ranked Nations")
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
    template="plotly_dark"
)
fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_bar, use_container_width=True)

# 10. Data View
with st.expander("📋 Explore Raw Data"):
    st.dataframe(
        plot_df[["country_name", "iso3", "continent", "pop_M", "gdp_B"]].rename(
            columns={"country_name": "Country", "iso3": "ISO Code", "continent": "Continent", "pop_M": "Population (M)", "gdp_B": "GDP ($B)"}
        ).sort_values("Population (M)", ascending=False),
        use_container_width=True
    )