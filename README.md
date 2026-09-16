# E-Commerce Orders — Data Cleaning Project

## Dataset
`orders_raw.csv` — 530 rows / 11 columns of e-commerce order records
(customer info, product category, quantity, price, order/signup dates,
status). The data mirrors the structure of common public e-commerce order
datasets (e.g. Kaggle-style order exports) and contains the typical data
quality problems found in raw exports.

## Issues identified in the raw data

| Issue | Details |
|---|---|
| **Duplicate records** | 30 exact duplicate rows (same values in every column). |
| **Missing values** | `Email` (33), `Gender` (18), `Country` (25), `SignupDate` (20), `Price` (17) had blank/NaN entries. |
| **Incorrect data types** | `Quantity` stored as text (e.g. `"8 units"`) instead of an integer; `Price` stored as text with a `$` prefix instead of a float; `SignupDate`/`OrderDate` stored as strings in four different formats (`YYYY-MM-DD`, `MM/DD/YYYY`, `DD-MM-YYYY`, `Month DD, YYYY`). |
| **Inconsistent values** | `Gender` had 11 variants of Male/Female (`M`, `male`, `MALE`, `" Female "`, etc.); `Country` had 19 variants (`USA`, `U.S.A`, `usa`, `US`, etc.); `Status` had 11 variants (`delivered`, `DELIVERED`, `Canceled`/`Cancelled`, etc.); `CustomerName` had stray leading/trailing whitespace. |

## Cleaning steps (`clean_data.py`, Python/pandas)

1. **Duplicates** — removed 30 exact duplicate rows with `drop_duplicates()`,
   then checked for duplicate `OrderID`s (none remained after the first pass).
2. **Missing values**
   - `Email`, `Gender`, `Country` → filled with an explicit `"Unknown"` /
     placeholder value rather than guessing personal data.
   - `Price` → imputed using the **median price within the same product
     category** (more accurate than a global median).
   - `SignupDate` → left as a null date where unrecoverable, so no dates
     were fabricated.
3. **Data types**
   - `Quantity`: stripped non-numeric text (`"units"`) and cast to `Int64`.
   - `Price`: stripped `$` symbols and cast to `float64`, rounded to 2 dp.
   - `SignupDate` / `OrderDate`: parsed all four date formats into a single
     standard `datetime64` column (`YYYY-MM-DD`).
4. **Inconsistent values**
   - `CustomerName`, `Email`: trimmed whitespace; emails lowercased.
   - `Gender`: mapped 11 variants → `Male` / `Female` / `Unknown`.
   - `Country`: mapped 19 variants → 5 standardized country names + `Unknown`.
   - `Status`: mapped 11 variants → `Delivered` / `Cancelled` / `Pending` / `Returned`.

## Result

| | Raw | Cleaned |
|---|---|---|
| Rows | 530 | 500 |
| Duplicate rows | 30 | 0 |
| Missing values | 113 cells | 20 (only unrecoverable `SignupDate`s, kept as null rather than invented) |
| Category variants (Gender/Country/Status) | 41 combined | 13 combined |

Full step-by-step console output is saved in `cleaning_report.txt`.

## Files in this repo

- `orders_raw.csv` — original messy dataset
- `clean_data.py` — cleaning script (Python + pandas)
- `orders_cleaned.csv` — final cleaned dataset
- `cleaning_report.txt` — log of every issue found and how it was fixed
- `README.md` — this file

## How to reproduce

```bash
pip install pandas numpy
python clean_data.py
```
