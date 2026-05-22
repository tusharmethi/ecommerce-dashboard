# 🛒 E-Commerce Sales Analytics Dashboard

An interactive sales analytics dashboard built with **Python, Pandas, SQL, Streamlit, and Plotly** — analyzing 9,994 retail orders across 2022–2023.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.2-green?logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-5.22-blueviolet?logo=plotly)
![SQLite](https://img.shields.io/badge/SQL-SQLite-lightgrey?logo=sqlite)

---

## 📊 Features

- **KPI Cards** — Total Revenue, Profit, AOV, Margin, Orders
- **Monthly Revenue & Profit Trend** — Bar + line combo chart
- **Regional Performance** — Horizontal bar chart across 4 US regions
- **Category Breakdown** — Donut chart (Furniture, Office Supplies, Technology)
- **Top Sub-Categories** — Revenue vs Profit overlay chart
- **Customer Segment Analysis** — Consumer / Corporate / Home Office
- **Year-over-Year Comparison** — 2022 vs 2023
- **Raw Data Explorer** — Filterable table with 500-row preview
- **Sidebar Filters** — Year, Region, Category, Segment

---

## 🗂️ Project Structure

```
ecommerce-dashboard/
│
├── app.py                  # Main Streamlit dashboard
├── requirements.txt        # Python dependencies
├── .gitignore
├── README.md
│
├── data/
│   └── orders_raw.csv      # Raw Kaggle dataset
│
└── scripts/
    ├── clean_data.py       # Data cleaning with Pandas
    └── sql_analysis.py     # SQL aggregations via SQLite
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ecommerce-dashboard.git
cd ecommerce-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

The cleaning and SQL steps run **automatically** on first launch.

---

## 🧹 Data Cleaning (Pandas)

- Renamed columns to `snake_case`
- Filled 1 null in `ship_mode` with `"Unknown"`
- Parsed `order_date` as datetime
- Zero-padded `postal_code`
- Derived columns: `revenue`, `cost`, `profit`, `discount_amt`, `year`, `month`, `year_month`

---

## 🗄️ SQL Aggregations (SQLite)

| Query | Description |
|-------|-------------|
| KPI Summary | Total revenue, profit, AOV, margin |
| Monthly Trend | Revenue & profit grouped by month |
| Regional Performance | Revenue, profit, margin by region |
| Category Analysis | Revenue by category & sub-category |
| Top Products | Top 10 products by revenue |
| Segment Analysis | Consumer / Corporate / Home Office |
| Year-over-Year | 2022 vs 2023 comparison |

---

## 📦 Dataset

- **Source:** [Kaggle — Retail Orders](https://www.kaggle.com/datasets/ankitbansal06/retail-orders)
- **Rows:** 9,994
- **Period:** Jan 2022 – Dec 2023
- **Columns:** Order ID, Date, Region, Category, Sub-Category, Segment, Cost Price, List Price, Quantity, Discount %

---

## 👨‍💻 Author

**Tushar Methi** — B.Tech CSE, Poornima University (Batch 2027)  
[GitHub](https://github.com/YOUR_USERNAME) · [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)
