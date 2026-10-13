"""
Clean the HMDA Snapshot National Loan-Level Dataset (2018-2025).

Run from anywhere inside the repo:  python src/hmda/clean_hmda.py

Input : data/raw/hmda/hmda_{year}.csv           (made by download_hmda.py)
Output: data/clean/hmda/hmda_clean_{year}.dta   loan-level, one file per year
        data/clean/hmda/hmda_tract_year.dta     tract x year averages (used for linking)

Sample: originated, first-lien, home-purchase, owner-occupied, site-built,
1-4 unit, closed-end, non-reverse, non-business loans. To change it (for
example to add refinances), edit keep_rows() below.

Everything is read as text and converted afterwards, because the raw files
mix numbers with strings like "Exempt" and "NA".
"""
from pyprojroot.here import here
import pandas as pd

# ---- settings ----------------------------------------------------------------
YEARS = range(2018, 2026)     # 2018 to 2025 (the end is exclusive)
CHUNKSIZE = 1_000_000         # rows read at a time; lower it if you run out of memory

raw_path = here("data/raw/hmda")
out_path = here("data/clean/hmda")
out_path.mkdir(parents=True, exist_ok=True)

# ---- columns -----------------------------------------------------------------
# The raw files have 99 columns. We keep these.
KEEP = [
    "activity_year", "lei", "derived_msa_md", "state_code", "county_code", "census_tract",
    "conforming_loan_limit", "derived_loan_product_type", "derived_dwelling_category",
    "action_taken", "purchaser_type", "preapproval", "loan_type", "loan_purpose",
    "lien_status", "reverse_mortgage", "open_end_line_of_credit",
    "business_or_commercial_purpose", "hoepa_status",
    "loan_amount", "combined_loan_to_value_ratio",
    "loan_to_value_ratio",            # the 2018 name for combined_loan_to_value_ratio
    "interest_rate", "rate_spread", "total_loan_costs", "discount_points", "loan_term",
    "property_value", "construction_method", "occupancy_type", "total_units",
    "derived_ethnicity", "derived_race", "derived_sex",
    "income", "debt_to_income_ratio", "applicant_credit_score_type", "applicant_age",
    "tract_population", "tract_minority_population_percent",
    "ffiec_msa_md_median_family_income", "tract_to_msa_income_percentage",
    "tract_owner_occupied_units", "tract_one_to_four_family_homes",
    "tract_median_age_of_housing_units",
]

# Continuous variables -> numbers. Text such as "Exempt" becomes missing.
NUMERIC = [
    "loan_amount", "combined_loan_to_value_ratio", "interest_rate", "rate_spread",
    "total_loan_costs", "discount_points", "loan_term", "property_value", "income",
    "tract_population", "tract_minority_population_percent",
    "ffiec_msa_md_median_family_income", "tract_to_msa_income_percentage",
    "tract_owner_occupied_units", "tract_one_to_four_family_homes",
    "tract_median_age_of_housing_units",
]

# Code-only variables -> small integers (the code 1111 means "exempt" and stays a code).
CODE_COLS = [
    "purchaser_type", "preapproval", "loan_type", "hoepa_status",
    "applicant_credit_score_type", "total_units",
]

# Text with a few distinct values -> labelled integers in Stata.
# lei is left out on purpose: too many lenders for Stata's value-label limit.
CATEGORICAL = ["derived_loan_product_type", "derived_ethnicity", "derived_race", "derived_sex"]

# Constant after the sample filter, so no information. Dropped.
DROP_AFTER_FILTER = [
    "action_taken", "lien_status", "loan_purpose", "occupancy_type",
    "construction_method", "derived_dwelling_category", "open_end_line_of_credit",
    "reverse_mortgage", "business_or_commercial_purpose",
]

# Stata names can be at most 32 characters, so shorten the three long ones.
STATA_NAMES = {
    "tract_minority_population_percent": "tract_minority_pct",
    "ffiec_msa_md_median_family_income": "msa_md_median_fam_income",
    "tract_median_age_of_housing_units": "tract_median_housing_age",
}


# ---- functions ---------------------------------------------------------------
def keep_rows(df):
    """Apply the sample restriction. Values are still text, hence the quotes."""
    return df[
        (df["action_taken"] == "1")                     # originated
        & (df["lien_status"] == "1")                    # first lien
        & (df["loan_purpose"] == "1")                   # home purchase
        & (df["occupancy_type"] == "1")                 # principal residence
        & (df["construction_method"] == "1")            # site-built
        & df["total_units"].isin(["1", "2", "3", "4"])  # 1-4 units
        # "!= 1" instead of "== 2" so loans with an exempt/blank flag are kept
        & (df["open_end_line_of_credit"] != "1")        # closed-end
        & (df["reverse_mortgage"] != "1")
        & (df["business_or_commercial_purpose"] != "1")
    ]


def clean_chunk(chunk):
    """Filter one chunk of raw rows and convert the column types."""
    chunk = chunk.rename(columns={"loan_to_value_ratio": "combined_loan_to_value_ratio"})
    chunk = keep_rows(chunk).drop(columns=DROP_AFTER_FILTER)
    for c in NUMERIC:
        chunk[c] = pd.to_numeric(chunk[c], errors="coerce")
    for c in CODE_COLS:
        s = pd.to_numeric(chunk[c], errors="coerce")
        # integers if nothing is missing, otherwise floats (they can hold missing)
        chunk[c] = s.astype("int16") if s.notna().all() else s.astype("float32")
    return chunk


def clean_year(year):
    """Read one year in chunks and return (clean data, number of raw rows)."""
    pieces, n_read = [], 0
    chunks = pd.read_csv(raw_path / f"hmda_{year}.csv", dtype=str,
                         usecols=lambda c: c in KEEP, chunksize=CHUNKSIZE)
    for chunk in chunks:
        n_read += len(chunk)
        pieces.append(clean_chunk(chunk))
    df = pd.concat(pieces, ignore_index=True)

    # A valid tract has 11 digits (state 2 + county 3 + tract 6); a county has 5.
    df.loc[~df["census_tract"].str.fullmatch(r"\d{11}", na=False), "census_tract"] = pd.NA
    df.loc[~df["county_code"].str.fullmatch(r"\d{5}", na=False), "county_code"] = pd.NA

    df["activity_year"] = df["activity_year"].astype(int)
    for c in CATEGORICAL:
        df[c] = df[c].astype("category")
    return df.rename(columns=STATA_NAMES), n_read


def tract_year_table(df):
    """One row per census tract and year (loans with no valid tract are dropped).

    n_loans counts loans in our sample, not every HMDA loan in the tract.
    Income is in $ thousands.
    """
    g = df.dropna(subset=["census_tract"]).groupby(["census_tract", "activity_year"])
    return g.agg(
        n_loans=("loan_amount", "size"),
        loan_amount_mean=("loan_amount", "mean"),
        loan_amount_median=("loan_amount", "median"),
        property_value_mean=("property_value", "mean"),
        income_mean=("income", "mean"),
        cltv_mean=("combined_loan_to_value_ratio", "mean"),
        interest_rate_mean=("interest_rate", "mean"),
    ).reset_index()


def save_stata(df, path):
    """Write a .dta file. Stata has no missing text, so missing text becomes ""."""
    df = df.copy()
    for c in df.select_dtypes(include=["object", "string"]).columns:
        df[c] = df[c].astype(object).where(df[c].notna(), "")
    df.to_stata(path, write_index=False, version=118)


# ---- run ---------------------------------------------------------------------
tract_tables = []   # one small table per year, stacked at the end

for year in YEARS:
    df, n_read = clean_year(year)
    missing_tract = df["census_tract"].isna().mean()
    print(f"{year}: {n_read:,} rows read, {len(df):,} kept ({missing_tract:.1%} missing tract)")

    save_stata(df, out_path / f"hmda_clean_{year}.dta")
    tract_tables.append(tract_year_table(df))
    del df   # free memory before the next year

tract_year = pd.concat(tract_tables, ignore_index=True)
save_stata(tract_year, out_path / "hmda_tract_year.dta")
print(f"Tract-year rows: {len(tract_year):,}")
