"""
Streamlit Dashboard — GADM World Admin Boundaries EDA
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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="GADM EDA | SAP 70177829",
    page_icon="🌍",
    layout="wide"
)

# 2. Custom CSS & Header
st.markdown("""
<style>
.globe-svg { animation: spin 18s linear infinite; display:block; }
@keyframes spin { from { transform:rotate(0deg); } to { transform:rotate(360deg); } }
.hero-title {
  font-family: 'Segoe UI', sans-serif; font-size: 2.3rem; font-weight: 800;
  background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 50%, #00bcd4 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
}
</style>
<div style="display:flex;align-items:center;justify-content:center;gap:18px;margin-bottom:6px;">
  <svg class="globe-svg" width="62" height="62" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <radialGradient id="g1" cx="38%" cy="35%">
        <stop offset="0%" stop-color="#4fc3f7"/>
        <stop offset="60%" stop-color="#1565c0"/>
        <stop offset="100%" stop-color="#0d2b6e"/>
      </radialGradient>
    </defs>
    <circle cx="32" cy="32" r="30" fill="url(#g1)"/>
    <ellipse cx="32" cy="32" rx="13" ry="30" fill="none" stroke="#81d4fa" stroke-width="1.2" opacity="0.65"/>
    <ellipse cx="32" cy="32" rx="30" ry="12" fill="none" stroke="#81d4fa" stroke-width="1.2" opacity="0.65"/>
    <line x1="2" y1="32" x2="62" y2="32" stroke="#81d4fa" stroke-width="1" opacity="0.5"/>
    <line x1="32" y1="2" x2="32" y2="62" stroke="#81d4fa" stroke-width="1" opacity="0.5"/>
    <circle cx="22" cy="26" r="4.5" fill="#a5d6a7" opacity="0.85"/>
    <circle cx="38" cy="20" r="5.5" fill="#a5d6a7" opacity="0.85"/>
    <circle cx="44" cy="37" r="3.5" fill="#a5d6a7" opacity="0.8"/>
    <circle cx="20" cy="41" r="3" fill="#a5d6a7" opacity="0.75"/>
    <circle cx="32" cy="32" r="30" fill="none" stroke="#4fc3f7" stroke-width="2"/>
  </svg>
  <h1 class="hero-title">GADM World Admin Boundaries — EDA Dashboard</h1>
</div>
<p style="text-align:center;color:#546e7a;font-size:16px;margin-top:4px;">
  <strong style="color:#1a73e8;font-size:18px;">Ahmad Sheraz</strong>
  &nbsp;|&nbsp; Section B &nbsp;|&nbsp; GADM World Administrative Boundaries
</p>
<hr style="border:none;border-top:2px solid #e3f2fd;margin:16px 0;">
""", unsafe_allow_html=True)

# 3. Data Loading
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
    world.rename(columns={"ISO3166-1-Alpha-3": "iso3", "ISO3166-1-Alpha-2": "iso2"}, inplace=True)

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

try:
    with st.spinner("Loading GADM geographical data..."):
        world = load_data()
except Exception as e:
    st.error(f"Error loading geographical data: {e}")
    st.stop()

# 4. Sidebar Controls
st.sidebar.title("🔧 Filters & Controls")
all_cont = sorted([c for c in world["continent"].unique() if c != "Other"])
sel_cont = st.sidebar.multiselect("Select Continents", all_cont, default=all_cont)

pop_max = int(world["pop_M"].max() * 1.1)
pop_range = st.sidebar.slider("Population Range (Millions)", 0, pop_max, (0, pop_max))

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);padding:14px 16px;border-radius:10px;border-left:4px solid #1a73e8;">
  <p style="margin:0;font-size:15px;font-weight:700;color:#0d47a1;">👤 Ahmad Sheraz</p>
  <p style="margin:4px 0 0 0;font-size:13px;color:#546e7a;">SAP ID: 70177829 | Section B</p>
</div>
""", unsafe_allow_html=True)

# Filter Data
filtered = world[
    (world["continent"].isin(sel_cont) | (world["continent"] == "Other")) &
    (world["pop_M"].fillna(0) >= pop_range[0]) &
    (world["pop_M"].fillna(0) <= pop_range[1])
].copy()

# 5. Key Statistics Formatting
def fmt_pop(m):
    return f"{m/1000:.2f} Billion" if m >= 1000 else f"{m:.0f} Million"

def fmt_gdp(b):
    return f"${b/1000:.2f} Trillion" if b >= 1000 else f"${b:.1f} Billion"

st.subheader("📊 Key Statistics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌐 Total Countries", len(filtered))
c2.metric("🌍 Continents Selected", len(sel_cont))
c3.metric("👥 Total Population", fmt_pop(filtered["pop_M"].sum()))
c4.metric("💰 Total GDP", fmt_gdp(filtered["gdp_B"].sum()))

st.markdown("---")

# 6. Map Visualizations
st.subheader("🗺️ Spatial Distribution Maps")
t1, t2 = st.tabs(["Population Choropleth", "GDP Choropleth"])

with t1:
    fig, ax = plt.subplots(figsize=(16, 7))
    filtered.plot(
        column="pop_est", ax=ax, legend=True, cmap="YlOrRd",
        legend_kwds={"label": "Population", "orientation": "horizontal", "shrink": 0.5},
        missing_kwds={"color": "#eee"}, edgecolor="white", linewidth=0.3
    )
    ax.set_title("GADM World Administrative Boundaries — Population Density", fontsize=12, fontweight="bold")
    ax.set_axis_off()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with t2:
    fig, ax = plt.subplots(figsize=(16, 7))
    filtered.plot(
        column="gdp_usd", ax=ax, legend=True, cmap="Blues",
        legend_kwds={"label": "GDP (USD)", "orientation": "horizontal", "shrink": 0.5},
        missing_kwds={"color": "#eee"}, edgecolor="white", linewidth=0.3
    )
    ax.set_title("GADM World Administrative Boundaries — Gross Domestic Product (GDP)", fontsize=12, fontweight="bold")
    ax.set_axis_off()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# 7. Distribution Analysis
st.subheader("📈 Statistical Distributions")
ca, cb = st.columns(2)

with ca:
    st.markdown("**Countries per Continent**")
    cc = filtered[filtered["continent"] != "Other"].groupby("continent")["name"].count().sort_values()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh(cc.index, cc.values, color=plt.cm.Set2(np.linspace(0, 1, len(cc))), edgecolor="white")
    for i, (idx, val) in enumerate(cc.items()):
        ax.text(val + 0.2, i, str(val), va="center", fontweight="bold")
    ax.set_xlabel("Number of Countries")
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with cb:
    st.markdown("**Population Spread (Log Scale)**")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(np.log10(filtered["pop_est"].dropna() + 1), bins=20, color="#1a73e8", edgecolor="white", alpha=0.85)
    ax.set_xlabel("log₁₀(Population)")
    ax.set_ylabel("Country Count")
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# 8. Relationship Analysis
st.subheader("🔍 Macroeconomic Relationships")
cc2, cd2 = st.columns(2)

with cc2:
    st.markdown("**GDP vs Population**")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    conts = [c for c in filtered["continent"].unique() if c != "Other"]
    cmap2 = matplotlib.colormaps["tab10"].resampled(max(1, len(conts)))
    for i, cont in enumerate(conts):
        sub = filtered[(filtered["continent"] == cont)].dropna(subset=["pop_M", "gdp_B"])
        ax.scatter(sub["pop_M"], sub["gdp_B"], label=cont, color=cmap2(i), alpha=0.75, s=45, edgecolors="white")
    ax.set_xlabel("Population (Millions)")
    ax.set_ylabel("GDP (Billion USD)")
    ax.legend(title="Continent", fontsize=8)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with cd2:
    st.markdown("**GDP Variance across Continents**")
    wc = filtered[(filtered["continent"] != "Other")].dropna(subset=["gdp_usd"])
    fig, ax = plt.subplots(figsize=(7, 4.5))
    if len(wc) > 0:
        co = wc.groupby("continent")["gdp_usd"].median().sort_values(ascending=False).index
        sns.boxplot(data=wc, x="continent", y="gdp_usd", order=co, palette="Set2", ax=ax)
        ax.set_yscale("log")
        ax.set_xlabel("Continent")
        ax.set_ylabel("GDP USD (Log Scale)")
        plt.xticks(rotation=25, ha="right")
        sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# 9. Top 10 Summary Table
st.subheader("🏆 Top 10 Countries by Population")
top10 = filtered.nlargest(10, "pop_est")[["name", "continent", "pop_M", "gdp_B"]].rename(
    columns={"name": "Country", "continent": "Continent", "pop_M": "Population (M)", "gdp_B": "GDP (B USD)"}
).reset_index(drop=True)

col_t, col_b = st.columns([1, 1])
with col_t:
    st.dataframe(top10.round(1), use_container_width=True)

with col_b:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh(top10["Country"], top10["Population (M)"], color=plt.cm.tab10(np.linspace(0, 1, len(top10))), edgecolor="white")
    ax.set_xlabel("Population (Millions)")
    ax.invert_yaxis()
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with st.expander("📋 View Complete Dataset"):
    st.dataframe(filtered.drop(columns="geometry").round(2).reset_index(drop=True), use_container_width=True)

st.markdown("<p style='text-align:center;color:#bdc3c7;font-size:12px;margin-top:20px;'>GADM EDA Dashboard | Developed by Ahmad Sheraz (SAP ID: 70177829)</p>", unsafe_allow_html=True)