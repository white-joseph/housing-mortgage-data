# Packages

from pyprojroot.here import here
import pandas as pd
import numpy as np

# Load data

enterprise_df = pd.read_csv(here("data/raw/uad/enterprise_uad.csv"))
fha_df = pd.read_csv(here("data/raw/uad/fha_uad.csv"))

# Relevant variables

keep_cols = ["record_id",
             "year",
             "state_fips_2010",
             "county_fips_2010",
             "tract_fips_2010",
             "state_fips_2020",
             "county_fips_2020",
             "tract_fips_2020",
             "purpose",
             "owner_occupied",
             "contract_price",
             "lot_size",
             "quality",
             "condition",
             "bathrooms",
             "bedrooms",
             "gross_living_area",
             "appraised_value",
             "appraisal_to_contract"
            ]

enterprise_clean = enterprise_df[keep_cols].copy()
fha_clean = fha_df[keep_cols].copy()

# Clean FIPS codes

## Convert enterprise to nullable integers
### 2010
enterprise_clean['state_fips_2010'] = enterprise_clean['state_fips_2010'].astype('Int64')
enterprise_clean['county_fips_2010'] = enterprise_clean['county_fips_2010'].astype('Int64')
enterprise_clean['tract_fips_2010'] = enterprise_clean['tract_fips_2010'].astype('Int64')
### 2020
enterprise_clean['state_fips_2020'] = enterprise_clean['state_fips_2020'].astype('Int64')
enterprise_clean['county_fips_2020'] = enterprise_clean['county_fips_2020'].astype('Int64')
enterprise_clean['tract_fips_2020'] = enterprise_clean['tract_fips_2020'].astype('Int64')

## Pad to correct digits, keep NaN as NaN
### 2010
enterprise_clean['state_fips_2010_clean'] = enterprise_clean['state_fips_2010'].astype(str).replace('<NA>', np.nan).str.zfill(2)
enterprise_clean['county_fips_2010_clean'] = enterprise_clean['county_fips_2010'].astype(str).replace('<NA>', np.nan).str.zfill(5)
enterprise_clean['tract_fips_2010_clean'] = enterprise_clean['tract_fips_2010'].astype(str).replace('<NA>', np.nan).str.zfill(11)
### 2020
enterprise_clean['state_fips_2020_clean'] = enterprise_clean['state_fips_2020'].astype(str).replace('<NA>', np.nan).str.zfill(2)
enterprise_clean['county_fips_2020_clean'] = enterprise_clean['county_fips_2020'].astype(str).replace('<NA>', np.nan).str.zfill(5)
enterprise_clean['tract_fips_2020_clean'] = enterprise_clean['tract_fips_2020'].astype(str).replace('<NA>', np.nan).str.zfill(11)

## Convert fha to nullable integers
### 2010
fha_clean['state_fips_2010'] = fha_clean['state_fips_2010'].astype('Int64')
fha_clean['county_fips_2010'] = fha_clean['county_fips_2010'].astype('Int64')
fha_clean['tract_fips_2010'] = fha_clean['tract_fips_2010'].astype('Int64')
### 2020
fha_clean['state_fips_2020'] = fha_clean['state_fips_2020'].astype('Int64')
fha_clean['county_fips_2020'] = fha_clean['county_fips_2020'].astype('Int64')
fha_clean['tract_fips_2020'] = fha_clean['tract_fips_2020'].astype('Int64')

## Pad to correct digits, keep NaN as NaN
### 2010
fha_clean['state_fips_2010_clean'] = fha_clean['state_fips_2010'].astype(str).replace('<NA>', np.nan).str.zfill(2)
fha_clean['county_fips_2010_clean'] = fha_clean['county_fips_2010'].astype(str).replace('<NA>', np.nan).str.zfill(5)
fha_clean['tract_fips_2010_clean'] = fha_clean['tract_fips_2010'].astype(str).replace('<NA>', np.nan).str.zfill(11)
### 2020
fha_clean['state_fips_2020_clean'] = fha_clean['state_fips_2020'].astype(str).replace('<NA>', np.nan).str.zfill(2)
fha_clean['county_fips_2020_clean'] = fha_clean['county_fips_2020'].astype(str).replace('<NA>', np.nan).str.zfill(5)
fha_clean['tract_fips_2020_clean'] = fha_clean['tract_fips_2020'].astype(str).replace('<NA>', np.nan).str.zfill(11)

# Create new cleaned fips columns

enterprise_clean["state_fips"] = np.where(enterprise_clean["year"] == 2022, enterprise_clean["state_fips_2020_clean"], enterprise_clean["state_fips_2010_clean"])
enterprise_clean["state_fips"] = enterprise_clean["state_fips"].astype("string")
enterprise_clean["county_fips"] = np.where(enterprise_clean["year"] == 2022, enterprise_clean["county_fips_2020_clean"], enterprise_clean["county_fips_2010_clean"])
enterprise_clean["county_fips"] = enterprise_clean["county_fips"].astype("string")
enterprise_clean["tract_fips"] = np.where(enterprise_clean["year"] == 2022, enterprise_clean["tract_fips_2020_clean"], enterprise_clean["tract_fips_2010_clean"])
enterprise_clean["tract_fips"] = enterprise_clean["tract_fips"].astype("string")

fha_clean["state_fips"] = np.where(fha_clean["year"] == 2022, fha_clean["state_fips_2020_clean"], fha_clean["state_fips_2010_clean"])
fha_clean["state_fips"] = fha_clean["state_fips"].astype("string")
fha_clean["county_fips"] = np.where(fha_clean["year"] == 2022, fha_clean["county_fips_2020_clean"], fha_clean["county_fips_2010_clean"])
fha_clean["county_fips"] = fha_clean["county_fips"].astype("string")
fha_clean["tract_fips"] = np.where(fha_clean["year"] == 2022, fha_clean["tract_fips_2020_clean"], fha_clean["tract_fips_2010_clean"])
fha_clean["tract_fips"] = fha_clean["tract_fips"].astype("string")

# Convert 9's to NaN

enterprise_clean.loc[enterprise_clean["purpose"] == 9, "purpose"] = np.nan
enterprise_clean.loc[enterprise_clean["owner_occupied"] == 9, "owner_occupied"] = np.nan
enterprise_clean.loc[enterprise_clean["lot_size"] == 9, "lot_size"] = np.nan
enterprise_clean.loc[enterprise_clean["quality"] == 9, "quality"] = np.nan
enterprise_clean.loc[enterprise_clean["condition"] == 9, "condition"] = np.nan
enterprise_clean.loc[enterprise_clean["bathrooms"] == 9, "bathrooms"] = np.nan
enterprise_clean.loc[enterprise_clean["bedrooms"] == 9, "bedrooms"] = np.nan
enterprise_clean.loc[enterprise_clean["gross_living_area"] == 9, "gross_living_area"] = np.nan

fha_clean.loc[fha_clean["purpose"] == 9, "purpose"] = np.nan
fha_clean.loc[fha_clean["owner_occupied"] == 9, "owner_occupied"] = np.nan
fha_clean.loc[fha_clean["lot_size"] == 9, "lot_size"] = np.nan
fha_clean.loc[fha_clean["quality"] == 9, "quality"] = np.nan
fha_clean.loc[fha_clean["condition"] == 9, "condition"] = np.nan
fha_clean.loc[fha_clean["bathrooms"] == 9, "bathrooms"] = np.nan
fha_clean.loc[fha_clean["bedrooms"] == 9, "bedrooms"] = np.nan
fha_clean.loc[fha_clean["gross_living_area"] == 9, "gross_living_area"] = np.nan

# Convert to ordered categorical

enterprise_clean["lot_size"] = pd.Categorical(
    enterprise_clean["lot_size"], categories=[1, 2, 3, 4, 5], ordered=True
)

enterprise_clean["quality"] = pd.Categorical(
    enterprise_clean["quality"], categories=[1, 2, 3, 4, 5], ordered=True
)

enterprise_clean["condition"] = pd.Categorical(
    enterprise_clean["condition"], categories=[1, 2, 3, 4, 5], ordered=True
)

enterprise_clean["bathrooms"] = pd.Categorical(
    enterprise_clean["bathrooms"], categories=[1, 2, 3, 4], ordered=True
)

enterprise_clean["bedrooms"] = pd.Categorical(
    enterprise_clean["bedrooms"], categories=[1, 2, 3], ordered=True
)

enterprise_clean["gross_living_area"] = pd.Categorical(
    enterprise_clean["gross_living_area"], categories=[1, 2, 3, 4, 5, 6, 7, 8], ordered=True
)

fha_clean["lot_size"] = pd.Categorical(
    fha_clean["lot_size"], categories=[1, 2, 3, 4, 5], ordered=True
)

fha_clean["quality"] = pd.Categorical(
    fha_clean["quality"], categories=[1, 2, 3, 4, 5], ordered=True
)

fha_clean["condition"] = pd.Categorical(
    fha_clean["condition"], categories=[1, 2, 3, 4, 5], ordered=True
)

fha_clean["bathrooms"] = pd.Categorical(
    fha_clean["bathrooms"], categories=[1, 2, 3, 4], ordered=True
)

fha_clean["bedrooms"] = pd.Categorical(
    fha_clean["bedrooms"], categories=[1, 2, 3], ordered=True
)

fha_clean["gross_living_area"] = pd.Categorical(
    fha_clean["gross_living_area"], categories=[1, 2, 3, 4, 5, 6, 7, 8], ordered=True
)

# Convert to categorical

enterprise_clean["purpose"] = enterprise_clean["purpose"].astype("category")
enterprise_clean["owner_occupied"] = enterprise_clean["owner_occupied"].astype("category")

fha_clean["purpose"] = fha_clean["purpose"].astype("category")
fha_clean["owner_occupied"] = fha_clean["owner_occupied"].astype("category")

# Create purchase and conver to boolean

enterprise_clean["purchase"] = np.select(
    [enterprise_clean["purpose"].isna(), enterprise_clean["purpose"] == 1],
    [np.nan, True],
    default=False,
)
fha_clean["purchase"] = np.select(
    [fha_clean["purpose"].isna(), fha_clean["purpose"] == 1],
    [np.nan, True],
    default=False,
)

# Define which dataset the observation comes from

enterprise_clean["program"] = "enterprise"
fha_clean["program"] = "fha"

# Drop columns

drop_cols = [
    "state_fips_2010", "county_fips_2010", "tract_fips_2010",
    "state_fips_2020", "county_fips_2020", "tract_fips_2020",
    "state_fips_2010_clean", "county_fips_2010_clean", "tract_fips_2010_clean",
    "state_fips_2020_clean", "county_fips_2020_clean", "tract_fips_2020_clean",
]
enterprise_clean = enterprise_clean.drop(columns=drop_cols, errors="ignore")
fha_clean = fha_clean.drop(columns=drop_cols, errors="ignore")

# Stack datasets

df_clean = pd.concat([enterprise_clean, fha_clean], ignore_index=True)

# Save cleaned data as .parquet and .dta

df_clean.to_parquet(here("data/clean/uad_clean.parquet"), index=False)
df_clean.to_stata(here("data/clean/uad_clean.dta"), write_index=False)