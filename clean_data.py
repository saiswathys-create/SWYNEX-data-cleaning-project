"""
clean_data.py
Cleans orders_raw.csv and writes orders_cleaned.csv plus a text summary
of every issue found and how it was fixed (cleaning_report.txt).
"""
import pandas as pd
import numpy as np

RAW_PATH = "/home/claude/project/orders_raw.csv"
CLEAN_PATH = "/home/claude/project/orders_cleaned.csv"
REPORT_PATH = "/home/claude/project/cleaning_report.txt"

report_lines = []
def log(line=""):
    print(line)
    report_lines.append(line)

df = pd.read_csv(RAW_PATH)
log(f"Loaded raw dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------------
# 1. DUPLICATE RECORDS
# ---------------------------------------------------------------
exact_dupes = df.duplicated().sum()
log(f"\n1) DUPLICATES\nExact duplicate rows found: {exact_dupes}")
df = df.drop_duplicates()

id_dupes = df.duplicated(subset="OrderID").sum()
log(f"Duplicate OrderIDs remaining (same ID, different data): {id_dupes}")
df = df.drop_duplicates(subset="OrderID", keep="first")
log(f"Rows after removing all duplicates: {len(df)}")

# ---------------------------------------------------------------
# 2. MISSING VALUES
# ---------------------------------------------------------------
log("\n2) MISSING VALUES (before fix)")
log(df.isna().sum().to_string())

# Email: unrecoverable identifier -> flag rather than invent
df["Email"] = df["Email"].fillna("unknown@unknown.com")

# Gender: fill with explicit 'Unknown' category (never invent demographic data)
df["Gender"] = df["Gender"].fillna("Unknown")

# Country: fill with 'Unknown'
df["Country"] = df["Country"].fillna("Unknown")

# SignupDate: leave as NaT after parsing (kept for transparency, not guessed)
# Price: impute with the median price of the same ProductCategory
df["Price"] = df["Price"].astype(str).str.replace("$", "", regex=False)
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
df["Price"] = df.groupby("ProductCategory")["Price"].transform(
    lambda s: s.fillna(s.median())
)

log("\nMISSING VALUES (after fix)")
log(df.isna().sum().to_string())

# ---------------------------------------------------------------
# 3. INCORRECT / INCONSISTENT DATA TYPES
# ---------------------------------------------------------------
log("\n3) DATA TYPE FIXES")

# Quantity: strip "units" text, cast to integer
before_types = df["Quantity"].apply(type).value_counts().to_string()
df["Quantity"] = (
    df["Quantity"].astype(str).str.extract(r"(\d+)").astype(float).astype("Int64")
)
log(f"Quantity: stripped text like 'units', cast to integer.\nBefore:\n{before_types}")

# Price already converted to float above
df["Price"] = df["Price"].round(2)
log("Price: stripped '$' symbols, converted to float, rounded to 2 decimals.")

# Dates: multiple string formats -> unified pandas datetime (YYYY-MM-DD)
df["SignupDate"] = pd.to_datetime(df["SignupDate"], errors="coerce", format="mixed")
df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce", format="mixed")
log("SignupDate / OrderDate: parsed mixed formats (YYYY-MM-DD, MM/DD/YYYY, "
    "DD-MM-YYYY, 'Month DD, YYYY') into a single standard datetime (YYYY-MM-DD).")

# ---------------------------------------------------------------
# 4. INCONSISTENT CATEGORICAL VALUES / TEXT
# ---------------------------------------------------------------
log("\n4) INCONSISTENT VALUES")

df["CustomerName"] = df["CustomerName"].str.strip()
log("CustomerName: trimmed leading/trailing whitespace.")

df["Email"] = df["Email"].str.strip().str.lower()
log("Email: trimmed whitespace, standardized to lowercase.")

gender_map = {
    "male": "Male", "m": "Male",
    "female": "Female", "f": "Female",
    "unknown": "Unknown"
}
before_vals = sorted(df["Gender"].dropna().unique().tolist())
df["Gender"] = df["Gender"].astype(str).str.strip().str.lower().map(gender_map).fillna("Unknown")
log(f"Gender: mapped variants {before_vals} -> {sorted(df['Gender'].unique().tolist())}")

country_map = {
    "usa": "United States", "u.s.a": "United States", "us": "United States",
    "united states": "United States",
    "uk": "United Kingdom", "u.k.": "United Kingdom", "united kingdom": "United Kingdom",
    "canada": "Canada", "australia": "Australia", "aus": "Australia",
    "germany": "Germany", "de": "Germany",
    "unknown": "Unknown"
}
before_vals = sorted(df["Country"].dropna().unique().tolist())
df["Country"] = df["Country"].astype(str).str.strip().str.lower().map(country_map).fillna("Unknown")
log(f"Country: mapped variants {before_vals} -> {sorted(df['Country'].unique().tolist())}")

status_map = {
    "delivered": "Delivered",
    "cancelled": "Cancelled", "canceled": "Cancelled",
    "pending": "Pending",
    "returned": "Returned"
}
before_vals = sorted(df["Status"].dropna().unique().tolist())
df["Status"] = df["Status"].astype(str).str.strip().str.lower().map(status_map)
log(f"Status: mapped variants {before_vals} -> {sorted(df['Status'].unique().tolist())}")

# ---------------------------------------------------------------
# Final checks & save
# ---------------------------------------------------------------
df = df.reset_index(drop=True)
log(f"\nFINAL cleaned dataset: {df.shape[0]} rows, {df.shape[1]} columns")
log("\nFinal dtypes:")
log(df.dtypes.to_string())

df.to_csv(CLEAN_PATH, index=False)
with open(REPORT_PATH, "w") as f:
    f.write("\n".join(report_lines))

print(f"\nSaved cleaned file to {CLEAN_PATH}")
print(f"Saved report to {REPORT_PATH}")
