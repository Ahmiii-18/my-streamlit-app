# GADM World Admin Boundaries — EDA Project
**SAP ID:** 70177829  
**Dataset:** GADM World Administrative Boundaries (Level 0–3)  
**Course:** EDA 350 / Data Analysis

---

## 📁 Project Structure
```
gadm_eda_project/
├── app.py              ← Streamlit web app (for deployment)
├── eda_gadm.py         ← Standalone EDA script (generates all graphs)
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
└── screenshots/        ← All graph screenshots (auto-generated)
```

---

## 🔧 How to Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run EDA script (generates all screenshots)
```bash
python eda_gadm.py
```

### 3. Run Streamlit app
```bash
streamlit run app.py
```
Open browser at `http://localhost:8501`

---

## 📊 Visualizations Included

| # | Graph | Type |
|---|-------|------|
| 1 | World Population Choropleth | Geographic Map |
| 2 | World GDP Choropleth | Geographic Map |
| 3 | Countries per Continent | Horizontal Bar |
| 4 | Population Distribution | Histogram |
| 5 | Top 10 Most Populated Countries | Bar Chart |
| 6 | GDP vs Population Scatter | Scatter Plot |
| 7 | GDP Boxplot per Continent | Box Plot |

---

## 🚀 Deployment (Render — +5 Bonus Marks)

1. Push this folder to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Click **Deploy** → Get your public URL!

---

## 📌 Dataset Info
- **Source:** GADM (Database of Global Administrative Areas)
- **SAP ID:** 70177829
- **Direct Download:** `gadm_410-levels.zip`
- **Description:** Administrative boundaries for every country down to level 3 as Shapefile/GeoPackage
