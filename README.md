# 🌍 GADM World Administrative Boundaries — EDA Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://my-streamlt-app.streamlit.app/)

**Author:** Ahmad Sheraz  
**SAP ID:** 70177829  
**Section:** B  
**Live Application:** [GADM EDA Dashboard](https://my-streamlt-app.streamlit.app/)

---

## 📌 Project Overview

This interactive Exploratory Data Analysis (EDA) dashboard analyzes global administrative boundaries, spatial demography, and macroeconomic indicators using **GADM** and **World Bank** datasets. Built with Python and Streamlit, the application provides interactive geographic choropleths, macroeconomic scatter plots, and dynamic filtering across continents and population thresholds.

---

## 🛠️ Key Features

* **Interactive Filters:** Filter data dynamically by continent selections and population ranges in real time.
* **Geospatial Choropleths:** Spatial visualizations mapping population distribution and total GDP across global administrative boundaries.
* **Statistical Distribution Analysis:** Analyzes country counts per continent and population variance on logarithmic scales.
* **Macroeconomic Correlations:** Explores relationships between population size and economic output (GDP).
* **Summary & Data Export:** Features dynamic metric cards, top 10 rankings, and an expandable raw tabular dataset view.

---

## 📁 Project Structure

```text
GADM/
├── app.py              # Main Streamlit web application
├── eda_gadm.py         # Standalone EDA script for static figure generation
├── requirements.txt    # Required Python dependencies
├── runtime.txt         # Environment Python runtime configuration
└── README.md           # Project documentation