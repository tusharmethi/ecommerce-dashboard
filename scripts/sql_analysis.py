import pandas as pd
import sqlite3
import os

CLEAN_PATH = "data/orders_clean.csv"
DB_PATH    = "data/orders.db"

def load_to_sqlite():
    df = pd.read_csv(CLEAN_PATH)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("orders", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[DB] Loaded {len(df)} rows into SQLite → {DB_PATH}\n")

def run_query(conn, title, sql):
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    print()
    return df

def run_all_queries():
    conn = sqlite3.connect(DB_PATH)
    results = {}

    # ── KPI Summary ──────────────────────────────────────────────
    results["kpi"] = run_query(conn, "KPI SUMMARY", """
        SELECT
            COUNT(DISTINCT order_id)            AS total_orders,
            ROUND(SUM(revenue), 2)              AS total_revenue,
            ROUND(SUM(profit), 2)               AS total_profit,
            ROUND(AVG(revenue / quantity), 2)   AS avg_order_value,
            ROUND(SUM(profit) * 100.0
                  / SUM(revenue), 2)            AS profit_margin_pct
        FROM orders
    """)

    # ── Monthly Revenue Trend ─────────────────────────────────────
    results["monthly"] = run_query(conn, "MONTHLY REVENUE TREND", """
        SELECT
            year_month,
            COUNT(DISTINCT order_id)   AS orders,
            ROUND(SUM(revenue), 2)     AS revenue,
            ROUND(SUM(profit), 2)      AS profit
        FROM orders
        GROUP BY year_month
        ORDER BY year_month
    """)

    # ── Regional Performance ──────────────────────────────────────
    results["regional"] = run_query(conn, "REGIONAL PERFORMANCE", """
        SELECT
            region,
            COUNT(DISTINCT order_id)            AS total_orders,
            ROUND(SUM(revenue), 2)              AS total_revenue,
            ROUND(SUM(profit), 2)               AS total_profit,
            ROUND(SUM(profit)*100.0
                  / SUM(revenue), 2)            AS profit_margin_pct,
            ROUND(AVG(revenue / quantity), 2)   AS avg_order_value
        FROM orders
        GROUP BY region
        ORDER BY total_revenue DESC
    """)

    # ── Category Performance ──────────────────────────────────────
    results["category"] = run_query(conn, "CATEGORY PERFORMANCE", """
        SELECT
            category,
            sub_category,
            ROUND(SUM(revenue), 2)   AS revenue,
            ROUND(SUM(profit), 2)    AS profit,
            SUM(quantity)            AS units_sold,
            ROUND(SUM(profit)*100.0
                  / SUM(revenue), 2) AS margin_pct
        FROM orders
        GROUP BY category, sub_category
        ORDER BY revenue DESC
        LIMIT 15
    """)

    # ── Top 10 Products by Revenue ────────────────────────────────
    results["top_products"] = run_query(conn, "TOP 10 PRODUCTS BY REVENUE", """
        SELECT
            product_id,
            sub_category,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(SUM(profit), 2)  AS total_profit,
            SUM(quantity)          AS units_sold
        FROM orders
        GROUP BY product_id, sub_category
        ORDER BY total_revenue DESC
        LIMIT 10
    """)

    # ── Segment Analysis ──────────────────────────────────────────
    results["segment"] = run_query(conn, "CUSTOMER SEGMENT ANALYSIS", """
        SELECT
            segment,
            COUNT(DISTINCT order_id)            AS orders,
            ROUND(SUM(revenue), 2)              AS revenue,
            ROUND(SUM(profit), 2)               AS profit,
            ROUND(AVG(discount_percent), 2)     AS avg_discount_pct
        FROM orders
        GROUP BY segment
        ORDER BY revenue DESC
    """)

    # ── Year-over-Year Comparison ─────────────────────────────────
    results["yoy"] = run_query(conn, "YEAR-OVER-YEAR COMPARISON", """
        SELECT
            year,
            COUNT(DISTINCT order_id)  AS total_orders,
            ROUND(SUM(revenue), 2)    AS total_revenue,
            ROUND(SUM(profit), 2)     AS total_profit,
            ROUND(AVG(discount_percent), 2) AS avg_discount
        FROM orders
        GROUP BY year
        ORDER BY year
    """)

    conn.close()

    # ── Save all results to Excel ─────────────────────────────────
    out_path = "data/sql_results.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet, df in results.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
    print(f"[SAVED] All query results → {out_path}")

    return results

if __name__ == "__main__":
    print("=" * 60)
    print("  STEP 2: SQL AGGREGATIONS")
    print("=" * 60 + "\n")
    load_to_sqlite()
    run_all_queries()
