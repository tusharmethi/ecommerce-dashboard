import pandas as pd
import os

RAW_PATH = "data/orders_raw.csv"
CLEAN_PATH = "data/orders_clean.csv"

def clean_data():
    print("=" * 50)
    print("STEP 1: DATA CLEANING")
    print("=" * 50)

    # --- Load ---
    df = pd.read_csv(RAW_PATH)
    print(f"\n[1] Loaded raw data: {df.shape[0]} rows, {df.shape[1]} columns")

    # --- Rename columns (snake_case) ---
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    print(f"[2] Renamed columns: {list(df.columns)}")

    # --- Handle nulls ---
    null_counts = df.isnull().sum()
    print(f"\n[3] Null values before cleaning:\n{null_counts[null_counts > 0]}")
    df["ship_mode"] = df["ship_mode"].fillna("Unknown")
    print("    → Filled null ship_mode with 'Unknown'")

    # --- Remove duplicates ---
    before = len(df)
    df.drop_duplicates(inplace=True)
    print(f"\n[4] Duplicates removed: {before - len(df)}")

    # --- Fix data types ---
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["postal_code"] = df["postal_code"].astype(str).str.zfill(5)
    print("\n[5] Fixed dtypes: order_date → datetime, postal_code → zero-padded string")

    # --- Derived columns ---
    df["revenue"]       = df["list_price"] * df["quantity"]
    df["cost"]          = df["cost_price"] * df["quantity"]
    df["profit"]        = df["revenue"] - df["cost"]
    df["discount_amt"]  = (df["discount_percent"] / 100) * df["revenue"]
    df["year"]          = df["order_date"].dt.year
    df["month"]         = df["order_date"].dt.month
    df["month_name"]    = df["order_date"].dt.strftime("%b")
    df["year_month"]    = df["order_date"].dt.to_period("M").astype(str)
    print("\n[6] Derived columns added: revenue, cost, profit, discount_amt, year, month, year_month")

    # --- Save ---
    os.makedirs("data", exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"\n[7] Clean data saved → {CLEAN_PATH}")

    # --- Summary ---
    print("\n" + "=" * 50)
    print("CLEANING SUMMARY")
    print("=" * 50)
    print(f"  Rows         : {len(df)}")
    print(f"  Columns      : {len(df.columns)}")
    print(f"  Date Range   : {df['order_date'].min().date()} to {df['order_date'].max().date()}")
    print(f"  Total Revenue: ${df['revenue'].sum():,.2f}")
    print(f"  Total Profit : ${df['profit'].sum():,.2f}")
    print(f"  Regions      : {sorted(df['region'].unique())}")
    print(f"  Categories   : {sorted(df['category'].unique())}")
    print("=" * 50)

    return df

if __name__ == "__main__":
    clean_data()
