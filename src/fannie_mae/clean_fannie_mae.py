"""
Clean the Fannie Mae Single-Family Loan Performance data (primary dataset).

Input : data/raw/fannie-mae/{year}Q{quarter}.csv
Output: data/clean/fannie-mae/monthly/   loan-month panel (Parquet)
        data/clean/fannie-mae/loans/     one row per loan (Parquet and .dta)
        data/clean/fannie-mae/fannie_mae_msa_year.dta   MSA x year averages, for linking
        outputs/fannie_mae_cleaning_log.csv, outputs/fannie_mae_dlq_by_age.csv

Column names and types come from layout.py. Finished quarters are skipped on re-runs.
See docs/fannie_mae.md for the variable definitions.
"""
from pyprojroot.here import here
import sys
import time
import pandas as pd
import duckdb

sys.path.insert(0, str(here("src/fannie_mae")))    # this allows layout.py to be imported
from layout import (FIELDS, N_FIELDS, COLUMN_NAMES, NA_COLS, ORIG_COLS, MONTHLY_COLS, FIELD_INFO)

# ---- settings ----------------------------------------------------------------
QUARTERS = None        # None = every {year}Q{quarter}.csv in data/raw/fannie-mae. Or just use a list such as ["2023Q1"].
OVERWRITE = False      # False skips quarters whose outputs already exist
STRICT_LAYOUT = True   # True stops if a field the layout marks "NA" has values. False will just throw a warning.
MEMORY_LIMIT = "8GB"   # DuckDB memory cap.  Lower it if your computer runs out of memory.
THREADS = 4

raw_path = here("data/raw/fannie-mae")
out_path = here("data/clean/fannie-mae")
monthly_path = out_path / "monthly"
loans_path = out_path / "loans"
tmp_path = out_path / "tmp"
log_path = here("outputs/fannie_mae_cleaning_log.csv")
for p in (monthly_path, loans_path, tmp_path, log_path.parent):
    p.mkdir(parents=True, exist_ok=True)

# Zero balance codes that Fannie Mae counts as a credit event / default (see its statistical summary).
CREDIT_EVENT_CODES = ("02", "03", "09", "15")

con = duckdb.connect()
con.execute(f"SET memory_limit='{MEMORY_LIMIT}'")
con.execute(f"SET temp_directory='{tmp_path.as_posix()}'")   # where DuckDB spills to disk if it runs short of memory
if THREADS:
    con.execute(f"SET threads={int(THREADS)}")


# ---- SQL pieces --------------------------------------------------------------
def sql_path(p):
    """A path as DuckDB wants it: forward slashes, quotes escaped."""
    return p.as_posix().replace("'", "''")


def raw_source(csv_file):
    """DuckDB's reader for one raw file: pipe-delimited, no header, no quoting, all text."""
    cols = ", ".join(f"'{name}': 'VARCHAR'" for name in COLUMN_NAMES)
    return (f"read_csv('{sql_path(csv_file)}', delim='|', header=false, quote='', escape='', "
            f"encoding='latin-1', columns={{{cols}}})")


def typed(name):
    """SQL that turns one raw text field into its proper type. Blank becomes missing."""
    kind, _ = FIELD_INFO[name]
    text = f"NULLIF(TRIM({name}), '')"
    if kind == "str":
        return text
    if kind == "int":
        return f"TRY_CAST({text} AS INTEGER)"
    if kind == "num":
        return f"TRY_CAST({text} AS DOUBLE)"
    if kind == "date":    # MMYYYY -> first day of the month
        return f"CAST(TRY_STRPTIME({text}, '%m%Y') AS DATE)"
    raise ValueError(f"unknown type {kind} for {name}")


# dlq_status is text ("00", "01", ..., "99", "XX"); dlq_months is the number of months behind.
# "XX" (unknown) becomes missing and "99" (99 or more months) stays 99.
DLQ_MONTHS = "TRY_CAST(NULLIF(TRIM(dlq_status), '') AS SMALLINT)"


def select_list(columns):
    """SELECT list for the given fields, with dlq_months added right after dlq_status."""
    items = []
    for name in columns:
        items.append(f"{typed(name)} AS {name}")
        if name == "dlq_status":
            items.append(f"{DLQ_MONTHS} AS dlq_months")
    return ",\n    ".join(items)


MONTHLY_SELECT = select_list(["loan_id", "act_period"] + MONTHLY_COLS)
# every field that is carried, for the loan-level query
CARRIED_SELECT = select_list([n for _, n, _, role in FIELDS if role in ("key", "orig", "monthly")])


def latest(name):
    """Latest non-missing value of a monthly field over the loan's history."""
    return f"arg_max({name}, act_period) FILTER (WHERE {name} IS NOT NULL) AS {name}"


ORIG_AGG = ",\n    ".join(
    f"arg_min({n}, act_period) FILTER (WHERE {n} IS NOT NULL) AS {n}" for n in ORIG_COLS)

# Foreclosure expenses and sale proceeds are reported after the disposition; use the latest report.
LOSS_FIELDS = ["foreclosure_costs", "pres_repair_costs", "asset_recovery_costs", "misc_holding_exp",
               "holding_taxes", "net_sales_proceeds", "credit_enh_proceeds", "repurch_whole_proceeds",
               "other_fc_proceeds", "fc_principal_writeoff", "principal_forgiveness", "non_int_bearing_upb"]
LOSS_AGG = ",\n    ".join(latest(n) for n in LOSS_FIELDS)


def loan_query(csv_file, quarter):
    """One row per loan: origination fields (first non-missing value) plus outcomes."""
    year, qtr = int(quarter[:4]), int(quarter[5])
    return f"""
    WITH t AS (
      SELECT
    {CARRIED_SELECT}
      FROM {raw_source(csv_file)}
    ),
    a AS (
      SELECT
        loan_id,
        {ORIG_AGG},
        count(*) AS n_months_obs,
        min(act_period) AS first_act_period,
        max(act_period) AS last_act_period,
        max(dlq_months) AS max_dlq_months,
        min(act_period) FILTER (WHERE dlq_months >= 3) AS first_dlq90_date,
        min(act_period) FILTER (WHERE dlq_months >= 6) AS first_dlq180_date,
        COALESCE(bool_or(mod_flag = 'Y'), false) AS ever_modified,
        min(act_period) FILTER (WHERE mod_flag = 'Y') AS first_mod_date,
        COALESCE(bool_or(borrower_assist_plan = 'F'), false) AS ever_forbearance,
        COALESCE(bool_or(borrower_assist_plan IN ('F', 'R', 'T', 'O')), false) AS ever_assist_plan,
        COALESCE(bool_or(adr_type IN ('P', 'C', 'D')), false) AS ever_payment_deferral,
        {latest("zero_bal_code")},
        {latest("zero_bal_date")},
        {latest("upb_at_removal")},
        arg_max(current_upb, act_period) FILTER (WHERE current_upb IS NOT NULL) AS last_current_upb,
        max(foreclosure_date) AS foreclosure_date,
        max(disposition_date) AS disposition_date,
        {LOSS_AGG},
        -- 0, 1, or 2 (= more than one) distinct values; min/max keeps memory low (COUNT DISTINCT does not)
        CASE WHEN min(zero_bal_code) <> max(zero_bal_code) THEN 2 WHEN min(zero_bal_code) IS NOT NULL THEN 1 ELSE 0 END
          AS qa_n_zb_codes,
        CASE WHEN min(msa) <> max(msa) THEN 2 WHEN min(msa) IS NOT NULL THEN 1 ELSE 0 END AS qa_n_msa
      FROM t
      GROUP BY loan_id
    )
    SELECT
      loan_id,
      '{quarter}' AS acq_quarter,
      {year} AS acq_year,
      {qtr} AS acq_qtr,
      * EXCLUDE (loan_id, ever_modified, ever_forbearance, ever_assist_plan, ever_payment_deferral),
      year(orig_date) AS orig_year,
      quarter(orig_date) AS orig_qtr,
      -- Classic FICO at origination: the new field (lowest score of all borrowers) when it is
      -- there, otherwise the lower of the old borrower / co-borrower scores
      COALESCE(orig_classic_fico, LEAST(cscore_b, cscore_c)) AS fico_orig,
      CAST(max_dlq_months >= 1 AS TINYINT) AS ever_dlq30,
      CAST(max_dlq_months >= 2 AS TINYINT) AS ever_dlq60,
      CAST(max_dlq_months >= 3 AS TINYINT) AS ever_dlq90,
      CAST(max_dlq_months >= 6 AS TINYINT) AS ever_dlq180,
      CAST(ever_modified AS TINYINT) AS ever_modified,
      CAST(ever_forbearance AS TINYINT) AS ever_forbearance,
      CAST(ever_assist_plan AS TINYINT) AS ever_assist_plan,
      CAST(ever_payment_deferral AS TINYINT) AS ever_payment_deferral,
      CAST(zero_bal_code IS NOT NULL AS TINYINT) AS terminated,
      CAST(COALESCE(zero_bal_code = '01', false) AS TINYINT) AS prepaid,
      CAST(COALESCE(zero_bal_code = '06', false) AS TINYINT) AS repurchased,
      CAST(COALESCE(zero_bal_code IN {CREDIT_EVENT_CODES}, false) AS TINYINT) AS credit_event,
      CAST(COALESCE(zero_bal_code IN {CREDIT_EVENT_CODES} AND disposition_date IS NOT NULL, false) AS TINYINT)
        AS default_completed,
      -- Fannie Mae FAQ 53: repurchased = code 06, or code 02/03/09 with repurchase make whole proceeds
      CAST(COALESCE(zero_bal_code = '06'
                    OR (zero_bal_code IN ('02', '03', '09') AND repurch_whole_proceeds > 0), false) AS TINYINT)
        AS repurch_or_made_whole,
      -- Fannie Mae FAQ 51: the liquidation date is the disposition date for codes 02/03/09/15 and
      -- the zero balance date for the others (01, 06, 16, 96)
      CASE WHEN zero_bal_code IN {CREDIT_EVENT_CODES} THEN disposition_date ELSE zero_bal_date END
        AS liquidation_date,
      -- the UPB when the loan left the data if it did, otherwise the latest reported balance
      CASE WHEN zero_bal_code IS NOT NULL THEN upb_at_removal ELSE last_current_upb END AS final_upb
    FROM a
    """


# ---- steps -------------------------------------------------------------------
def check_layout(csv_file):
    """Count the rows, and the values found in fields the layout says are not used."""
    with open(csv_file, "r", encoding="latin-1", newline="") as f:
        n_fields = len(f.readline().rstrip("\r\n").split("|"))
    if n_fields != N_FIELDS:
        raise RuntimeError(f"{csv_file.name} has {n_fields} fields on its first line, expected {N_FIELDS}. "
                           "A file with 113 fields is from an older release: download it again. "
                           "Run check_fannie_mae.py to see every file.")
    counts = ", ".join(f"count(NULLIF(TRIM({n}), '')) AS {n}" for n in NA_COLS)
    try:
        row = con.execute(f"SELECT count(*) AS n_rows, {counts} FROM {raw_source(csv_file)}").df().iloc[0]
    except duckdb.Error as e:
        raise RuntimeError(f"DuckDB could not read {csv_file.name} as {N_FIELDS} pipe-delimited fields. "
                           "A truncated or damaged download is the usual cause: download it again. "
                           f"DuckDB said: {str(e)[:500]}") from e
    populated = {n: int(row[n]) for n in NA_COLS if row[n] > 0}
    return int(row["n_rows"]), populated


def write_parquet(query, out_file, row_group_size=500_000):
    """Run a query into a Parquet file. A ".part" file is renamed only when finished."""
    tmp = out_file.with_name(out_file.name + ".part")
    tmp.unlink(missing_ok=True)
    con.execute(f"COPY ({query}) TO '{sql_path(tmp)}' "
                f"(FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE {row_group_size})")
    tmp.replace(out_file)


def save_stata(df, path):
    """Write a .dta file. Stata has no missing text, so missing text becomes ""; dates become
    Stata monthly dates (%tm); whole-number columns are shrunk to save space."""
    df = df.copy()
    dates = {}
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_datetime64_any_dtype(s):
            dates[c] = "tm"
        elif pd.api.types.is_numeric_dtype(s) or pd.api.types.is_bool_dtype(s):
            if str(s.dtype)[:1] in ("I", "U", "F", "b"):        # pandas nullable Int*/Float*/boolean
                s = s.astype("float64")
            if pd.api.types.is_bool_dtype(s):
                s = s.astype("int8")
            if pd.api.types.is_float_dtype(s):
                nn = s.dropna()
                if len(nn) and (nn % 1 == 0).all() and nn.abs().max() < 1e7:
                    s = s.astype("float32")                     # exact for whole numbers below 16 million
            elif pd.api.types.is_integer_dtype(s):
                s = pd.to_numeric(s, downcast="integer")
                if s.dtype.itemsize > 2:                        # int32/int64: some pandas versions cannot write them
                    s = s.astype("float64")                     # exact for any count here
            df[c] = s
        else:
            df[c] = s.astype(object).where(s.notna(), "")
    df.to_stata(path, write_index=False, version=118, convert_dates=dates)


def quarter_log(quarter, csv_file, n_rows_read, loans_file, monthly_file):
    """Row counts and data checks for the log, read back from the loan-level file."""
    both = "orig_classic_fico IS NOT NULL AND LEAST(cscore_b, cscore_c) IS NOT NULL"
    r = con.execute(f"""
        SELECT
          count(*) AS n_loans,
          sum(n_months_obs) AS n_rows_loans,
          min(first_act_period) AS first_act_period,
          max(last_act_period) AS last_act_period,
          sum(terminated) AS n_terminated,
          sum(credit_event) AS n_credit_event,
          sum(default_completed) AS n_default_completed,
          avg(CAST(fico_orig IS NULL AS INTEGER)) AS share_missing_fico,
          (SELECT count(DISTINCT loan_id) FROM (
             SELECT loan_id FROM read_parquet('{sql_path(monthly_file)}')
             GROUP BY loan_id, act_period HAVING count(*) > 1)) AS n_loans_dup_months,
          sum(CAST(qa_n_zb_codes > 1 AS INTEGER)) AS n_loans_multi_zb,
          sum(CAST(qa_n_msa > 1 AS INTEGER)) AS n_loans_multi_msa,
          count(*) FILTER (WHERE {both}) AS fico_both_n,
          avg(CAST(orig_classic_fico = LEAST(cscore_b, cscore_c) AS INTEGER)) FILTER (WHERE {both}) AS fico_equal_share
        FROM read_parquet('{sql_path(loans_file)}')
    """).df().iloc[0].to_dict()
    if int(r["n_rows_loans"]) != n_rows_read:
        raise RuntimeError(f"{quarter}: {n_rows_read:,} rows read but the loans account for "
                           f"{int(r['n_rows_loans']):,}")
    out = {"quarter": quarter, "file_gb": round(csv_file.stat().st_size / 1e9, 2),
           "rows_read": n_rows_read}
    for k, v in r.items():
        if k == "n_rows_loans":
            continue
        if k in ("first_act_period", "last_act_period"):
            out[k] = pd.Timestamp(v).strftime("%Y-%m")
        elif k in ("share_missing_fico", "fico_equal_share"):
            out[k] = None if pd.isna(v) else round(float(v), 4)
        else:
            out[k] = int(v)
    return out


def write_msa_year():
    """MSA x origination year averages over every loan-level file that exists, for linking.
    n_loans only counts loans in the quarters downloaded, not all Fannie Mae loans."""
    files = sorted(loans_path.glob("fannie_mae_loans_*.parquet"))
    if not files:
        return
    df = con.execute(f"""
        SELECT
          msa,
          orig_year,
          count(*) AS n_loans,
          avg(orig_upb) AS orig_upb_mean,
          median(orig_upb) AS orig_upb_median,
          avg(oltv) AS oltv_mean,
          avg(fico_orig) AS fico_mean,
          avg(orig_rate) AS orig_rate_mean,
          avg(dti) AS dti_mean,
          avg(CAST(purpose = 'P' AS INTEGER)) AS share_purchase
        FROM read_parquet('{sql_path(loans_path)}/fannie_mae_loans_*.parquet')
        WHERE msa IS NOT NULL AND orig_year IS NOT NULL
        GROUP BY msa, orig_year
        ORDER BY msa, orig_year
    """).df()
    save_stata(df, out_path / "fannie_mae_msa_year.dta")
    print(f"MSA x year rows: {len(df):,} (from {len(files)} quarter files)")


def write_dlq_by_age():
    """Share of loans behind on payments, by acquisition quarter and loan age (months), from the
    monthly panels. Small, so it is saved as a CSV for the R report. Each loan is counted at
    every age it is still reporting, so later ages are loans that have not yet left the data."""
    files = sorted(monthly_path.glob("fannie_mae_monthly_*.parquet"))
    if not files:
        return
    df = con.execute(f"""
        SELECT
          regexp_extract(filename, '(\\d{{4}}Q\\d)\\.parquet$', 1) AS acq_quarter,
          loan_age,
          count(*) AS n_loan_months,
          count(dlq_months) AS n_known,
          avg(CAST(dlq_months >= 1 AS INTEGER)) AS share_dlq30,
          avg(CAST(dlq_months >= 3 AS INTEGER)) AS share_dlq90
        FROM read_parquet('{sql_path(monthly_path)}/fannie_mae_monthly_*.parquet', filename=true)
        WHERE loan_age BETWEEN 0 AND 180
        GROUP BY 1, 2
        ORDER BY 1, 2
    """).df()
    df.round({"share_dlq30": 5, "share_dlq90": 5}).to_csv(log_path.parent / "fannie_mae_dlq_by_age.csv",
                                                           index=False)
    print(f"Delinquency by loan age: {len(df):,} rows")


# ---- run ---------------------------------------------------------------------
found = sorted(p.stem for p in raw_path.glob("*.csv") if len(p.stem) == 6 and p.stem[4] == "Q")
quarters = found if QUARTERS is None else list(QUARTERS)
missing = [q for q in quarters if q not in found]
if missing:
    sys.exit(f"Not in {raw_path}: {missing}")
if not quarters:
    sys.exit(f"No quarterly CSV files in {raw_path}")

# the existing log is kept so quarters skipped this time keep their row
log = {}
if log_path.exists():
    log = {r["quarter"]: r for r in pd.read_csv(log_path, dtype={"quarter": str}).to_dict("records")}

for quarter in quarters:
    csv_file = raw_path / f"{quarter}.csv"
    monthly_file = monthly_path / f"fannie_mae_monthly_{quarter}.parquet"
    loans_file = loans_path / f"fannie_mae_loans_{quarter}.parquet"
    stata_file = loans_path / f"fannie_mae_loans_{quarter}.dta"

    if not OVERWRITE and monthly_file.exists() and loans_file.exists() and stata_file.exists():
        print(f"{quarter}: already cleaned, skipping")
        continue

    t0 = time.time()
    n_rows, populated = check_layout(csv_file)
    if populated:
        msg = (f"{quarter}: fields the layout marks NA have values: {populated}. "
               "The layout may have changed; compare with the current Glossary and File Layout.")
        if STRICT_LAYOUT:
            raise RuntimeError(msg)
        print("WARNING: " + msg)
    print(f"{quarter}: {n_rows:,} monthly rows, layout check passed ({time.time() - t0:.0f}s)")

    write_parquet(f"SELECT {MONTHLY_SELECT} FROM {raw_source(csv_file)}", monthly_file)
    print(f"{quarter}: monthly panel written ({time.time() - t0:.0f}s)")

    con.execute("SET preserve_insertion_order=false")      # row order does not matter for a GROUP BY; saves memory
    write_parquet(loan_query(csv_file, quarter), loans_file, row_group_size=100_000)
    con.execute("SET preserve_insertion_order=true")
    row = quarter_log(quarter, csv_file, n_rows, loans_file, monthly_file)
    print(f"{quarter}: {row['n_loans']:,} loans, {row['n_default_completed']:,} completed defaults "
          f"({time.time() - t0:.0f}s)")

    loans = con.execute(f"SELECT * EXCLUDE (qa_n_zb_codes, qa_n_msa) "
                        f"FROM read_parquet('{sql_path(loans_file)}')").df()
    save_stata(loans, stata_file)
    del loans
    print(f"{quarter}: done in {time.time() - t0:.0f}s")

    log[quarter] = row
    pd.DataFrame([log[q] for q in sorted(log)]).to_csv(log_path, index=False)   # saved after every quarter

write_msa_year()
write_dlq_by_age()
try:
    tmp_path.rmdir()      # only works if DuckDB left nothing behind
except OSError:
    pass
print("Done.")
