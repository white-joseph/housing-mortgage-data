"""
Link HMDA and the FHFA UAD PUF at the census-tract x year level.

Input : data/clean/hmda/hmda_tract_year.dta
        data/clean/uad_clean.dta
Output: data/combined/hmda_uad_tract_year.dta  one row per tract x year

The merge is an outer join. link_status says where each row came from:
"both", "hmda_only" or "uad_only". UAD tract-years with fewer than 11
appraisals are suppressed in the public file, so many HMDA tracts have no match.
"""
from pyprojroot.here import here
import pandas as pd

YEARS = range(2018, 2023)    # years both datasets cover (UAD ends in 2022)

out_path = here("data/combined")
out_path.mkdir(parents=True, exist_ok=True)

# ---- HMDA: already one row per tract and year ---------------------------------
hmda = pd.read_stata(here("data/clean/hmda/hmda_tract_year.dta"))
hmda = hmda.rename(columns={"census_tract": "tract_fips", "activity_year": "year"})
hmda = hmda[hmda["year"].isin(YEARS)]
# prefix every column except the keys, so you can tell the source of each variable
hmda = hmda.rename(columns={c: f"hmda_{c}" for c in hmda.columns if c not in ["tract_fips", "year"]})

# ---- UAD: collapse appraisals to one row per tract and year -------------------
uad = pd.read_stata(here("data/clean/uad_clean.dta"), convert_categoricals=False)
uad = uad[uad["year"].isin(YEARS) & (uad["tract_fips"].str.len() == 11)]

# all appraisals in the tract-year
all_appraisals = uad.groupby(["tract_fips", "year"]).agg(
    uad_n_appraisals=("record_id", "size"),
    uad_appraised_value_mean=("appraised_value", "mean"),
)

# purchase appraisals only (the ones that have a contract price)
purchases = uad[uad["purchase"] == 1].groupby(["tract_fips", "year"]).agg(
    uad_n_purchase=("record_id", "size"),
    uad_contract_price_mean=("contract_price", "mean"),
    uad_purchase_value_mean=("appraised_value", "mean"),
    uad_appraisal_to_contract_mean=("appraisal_to_contract", "mean"),
)

uad = all_appraisals.join(purchases, how="left").reset_index()

# ---- merge ---------------------------------------------------------------------
combined = hmda.merge(uad, on=["tract_fips", "year"], how="outer", indicator="link_status")
combined["link_status"] = (combined["link_status"].astype(str)
                           .map({"both": "both", "left_only": "hmda_only", "right_only": "uad_only"}))

# ---- match rates, for the documentation ----------------------------------------
counts = combined.groupby(["year", "link_status"]).size().unstack(fill_value=0)
counts["share_hmda_tracts_matched"] = (counts["both"] / (counts["both"] + counts["hmda_only"])).round(3)
counts["share_uad_tracts_matched"] = (counts["both"] / (counts["both"] + counts["uad_only"])).round(3)
print(counts.to_string())

combined.to_stata(out_path / "hmda_uad_tract_year.dta", write_index=False, version=118)
print(f"Wrote {len(combined):,} rows")
