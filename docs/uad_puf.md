# Documentation for the Uniform Appraisal Dataset (UAD) Appraisal-Level Public Use File (PUF)

Official documentation can be found [here](https://www.fhfa.gov/document/d/uad-al/uad-puf-2.1-data-documentation.pdf) and the data dictionary [here](https://www.fhfa.gov/document/d/uad-al/uad-puf-2.1-data-dictionary.pdf). This data was created by the Federal Housing Finance Agency (FHFA) and can be split into two separate datasets:

- (1) The Enterprise UAD Appraisal-Level PUF
- (2) The FHA UAD Appraisal-Level PUF

The former is a based on a 5% representative sample of nationally representative random sample of appraisals for single-family mortgages acquired by the Enterprises. The current release (Version 2.1) covers appraisals from 2013-2022. The latter is based on a five percent nationally representative random sample of appraisals for single-family mortgages insured by the Federal Housing Administration (FHA). The current release (Version 1.0) covers appraisals from 2017-2022.

Each observation in this dataset represents a single property appraisal record. The dataset is appraisal-level, so a property that was appraised twice, i.e., at purchase and refinancing, would be two separate observations. There are several geographic identifiers, including the state and county fips code for the 2010 and 2020 census, respectively. They also include the tract fips code for the 2010 census for appraisals that were conducted from 2013 - 2021, and then the tract fips codes for the 2020 census for properties appraised in 2022. The dataset includes properties in the 50 U.S. states, the District of Columbia, and Puerto Rico. 

## Access & Redistribution

The UAD Appraisal-Level PUF is fully public, with no registration, licensing, or data-use agreement required. Raw files, cleaned files, and derived outputs can be shared freely.

## Cleaned Dataset

The cleaning script (`src/uad/clean_uad.py`) subsets both raw files to the 19 columns above, applies the transformations below, and stacks Enterprise and FHA datasets into a single file, `uad_clean` (1,748,342 rows, one row per appraisal, unique on `record_id`).

**What changed from the raw files:**
- FIPS codes are zero-padded (state: 2 digits, county: 5, tract: 11) and coalesced into single `state_fips`/`county_fips`/`tract_fips` columns, using the 2010 fips for 2013-2021 and 2020 fips for 2022.
- The `'9' = Missing` is true `NaN` in `purpose`, `owner_occupied`, `lot_size`, `quality`, `condition`, `bathrooms`, `bedrooms`, and `gross_living_area`.
- Those same eight fields are converted to categorical datatypes, with the six ordinal/binned fields (`lot_size`, `quality`, `condition`, `bathrooms`, `bedrooms`, `gross_living_area`) changed to ordered categories. Category codes are unchanged from the raw numeric coding

**New columns:**
- `purchase`: A boolean, `True` when `purpose == 1` (Home Purchase), `False` for refinance/other, missing when `purpose` itself is missing.
- `program` — `'enterprise'` or `'fha'`, identifying which source file the row came from, since the two are now stacked into one table.

**Output files:**  `data/clean/uad_clean.dta`

| Column Name | Data Type | Description | Count of NaN | % Null |
| :--- | :--- | :--- | ---: | ---: |
| `record_id` | int64 | Unique appraisal ID (unchanged from raw). | 0 | 0.00 |
| `year` | int64 | Appraisal year. | 0 | 0.00 |
| `purpose` | category | Loan purpose; codes unchanged (1/2/3), '9' recoded to NaN. | 341 | 0.02 |
| `owner_occupied` | category | Occupancy status; codes unchanged (1/2), '9' recoded to NaN. | 335 | 0.02 |
| `contract_price` | float64 | Contract price (purchase transactions only; unchanged). | 792456 | 45.33 |
| `lot_size` | category (ordered) | Binned lot size, codes 1-5. | 9717 | 0.56 |
| `quality` | category (ordered) | Construction quality, codes 1-5. | 32 | 0.00 |
| `condition` | category (ordered) | Condition rating, codes 1-5. | 24 | 0.00 |
| `bathrooms` | category (ordered) | Bathroom count, codes 1-4. | 7757 | 0.44 |
| `bedrooms` | category (ordered) | Bedroom count, codes 1-3. | 1101 | 0.06 |
| `gross_living_area` | category (ordered) | Binned square footage, codes 1-8. | 333 | 0.02 |
| `appraised_value` | float64 | Final appraised value (unchanged). | 7209 | 0.41 |
| `appraisal_to_contract` | float64 | Appraised value as % of contract price (unchanged). | 797975 | 45.64 |
| `state_fips` | string | 2-digit state FIPS, coalesced across vintages. | 0 | 0.00 |
| `county_fips` | string | 5-digit county FIPS, coalesced across vintages. | 1442 | 0.08 |
| `tract_fips` | string | 11-digit tract FIPS, coalesced across vintages; NaN where suppressed. | 70554 | 4.04 |
| `purchase` | derived | `True`/`False`/missing flag for purchase transactions. See note below. | — | — |
| `program` | string | Source file: `'enterprise'` or `'fha'`. | 0 | 0.00 |

## Additional Documentation

- Enterprise coverage begins in 2013 and FHA coverage begins in 2017. The two files are not symmetric in time span.
- UAD appraisal records only contain mortgage loans requiring traditional appraisals, i.e., when automatic appraisals suffice, the Enterprises waive traditional appraisals.
- UAD appraisal records may include some appraisals related to other lending sources, including FHA and portfolio loans, as well as appraisals not connected to any mortgage loan, such as those associated with a denied loan application.
    - UAD appraisal records include appraisals not connected to any loan, such as appraisals associated with non-transacted loans. 
- Includes only final appraisals
- Appraisals for single-family properties appraised using Fannie Mae Form 1004 or Freddie Mac Form 70 are included, and condominiums, manufactured homes, and small multifamily rental property appraisals as well as other appraisals are excluded. 
- For appraisals with purchase transaction type, only appraisals for arm’s length transactions are included, and appraisals for real estate owned (REO), short sale, and foreclosure purchase transactions are excluded. 

## Quality & Limitations

**Sample design & weighting:** 
- This is a stratified 5% random sample of final appraisals per year, not a census of all appraisals. The `weight` field was a constant 20 for every record, therefore useful only for variance estimation, not for means/medians/regressions.

**Disclosure avoidance:** 
- FHFA applied several techniques that explain interesting attributes of the data. 
- PII and precise location were fully removed. 
- Census tracts and counties are suppressed when fewer than 11 appraisals exist in that geography-year.
- Dollar values (`contract_price`, `appraised_value`) are rounded to $10,000 midpoints. 
- Several continuous fields (`lot_size`, `gross_living_area`) are binned. 
- Some categorical fields were recoded to fewer categories (e.g. `quality`/`condition` merge their top two grades into one code), and dollar fields are top/bottom-coded, with `contract_price` capped at $1.7M in high-cost areas and $720k elsewhere.

FHFA separately publishes aggregate UAD statistics computed from 100% of a broader eligible population. Estimates from this PUF will not match those statistics, and the two shouldn't be benchmarked against each other.

FHFA states this data is intended to show patterns and geographic variation in appraisals. It explicitly advises against using it to appraise individual properties, judge individual appraiser quality, or infer the prevalence of specific property characteristics among all properties in an area, since the file reflects only appraisals actually performed in a period, not a census of properties.

## Relevant Variables
- `record_id`
- `year`
- `state_fips_2010` / `county_fips_2010` / `tract_fips_2010`
- `state_fips_2020` / `county_fips_2020` / `tract_fips_2020`
- `purpose`
- `contract_price`
- `appraised_value`
- `appraisal_to_contract`
- `owner_occupied`
- `quality`
- `condition`
- `gross_living_area`
- `bedrooms` / `bathrooms`
- `lot_size`

## Data Dictionary for UAD Appraisal-Level PUF — Relevant Variables

Enterprise (1,481,868 observations) and FHA (266,474 observations).

| Column Name | Data Type | Description | Example / Allowed Values | Enterprise NaN (Count / %) | FHA NaN (Count / %) |
| :--- | :--- | :--- | :--- | ---: | ---: |
| `record_id` | Character | Unique Appraisal ID. A unique identification value for each appraisal record. FHFA created this data field. It has no relationship to any unique identification data fields in the original UAD appraisal records. | — | 0 / 0.00 | 0 / 0.00 |
| `year` | Numeric | Appraisal Year. The year of the appraisal report effective date. This data field is used to stratify the sample. | 2013, 2014, etc. | 0 / 0.00 | 0 / 0.00 |
| `state_fips_2010` | Character | 2010 Census State FIPS Code. | Characters 1-2: State | 104224 / 7.03 | 37089 / 13.92 |
| `state_fips_2020` | Character | 2020 Census State FIPS Code. Populated only for appraisals conducted in 2022. | Characters 1-2: State | 1377644 / 92.97 | 229385 / 86.08 |
| `county_fips_2010` | Character | 2010 Census County FIPS Code. County is suppressed when fewer than 11 appraisal records exist in that county-year. | Characters 1-2: State; 3-5: County | 105182 / 7.10 | 37487 / 14.07 |
| `county_fips_2020` | Character | 2020 Census County FIPS Code. Populated only for 2022. | Characters 1-2: State; 3-5: County | 1377661 / 92.97 | 229454 / 86.11 |
| `tract_fips_2010` | Character | 2010 Census Tract. For appraisals conducted 2013–2021. Tract is suppressed when fewer than 11 appraisal records exist in that tract-year. | Characters 1-2: State; 3-5: County; 6-11: Tract | 124064 / 8.37 | 76873 / 28.85 |
| `tract_fips_2020` | Character | 2020 Census Tract. Populated only for 2022. | Characters 1-2: State; 3-5: County; 6-11: Tract | 1379126 / 93.07 | 238833 / 89.63 |
| `purpose` | Character | Mortgage Loan Purpose: home purchase, refinance, or other. | '1' = Home Purchase; '2' = Refinance; '3' = Other; '9' = Missing | 0 / 0.00 | 0 / 0.00 |
| `owner_occupied` | Character | Occupancy status at time of appraisal. | '1' = Yes; '2' = No; '9' = Missing | 0 / 0.00 | 0 / 0.00 |
| `contract_price` | Numeric | Contract price, purchase transactions only. | $5,000 - $1,705,000 | 735631 / 49.64 | 56825 / 21.32 |
| `lot_size` | Character | Appraiser-reported site size, in acres, binned. | '1'–'5' bins; '9' = Missing | 0 / 0.00 | 0 / 0.00 |
| `quality` | Character | Construction quality rating. | '1'–'4' = Q1–Q4; '5' = Q5 and Q6; '9' = Missing | 0 / 0.00 | 0 / 0.00 |
| `condition` | Character | Property condition rating. | '1'–'4' = C1–C4; '5' = C5 and C6; '9' = Missing | 0 / 0.00 | 0 / 0.00 |
| `bathrooms` | Character | Total full and half bathrooms. | '1'–'3' = 1–3; '4' = 4+; '9' = Missing | 0 / 0.00 | 0 / 0.00 |
| `bedrooms` | Character | Total bedrooms. | '1' = 0-2; '2' = 3; '3' = 4+; '9' = Missing | 0 / 0.00 | 0 / 0.00 |
| `gross_living_area` | Character | Total inhabitable area, sq. ft., binned. | '1'–'8' bins; '9' = Missing | 0 / 0.00 | 0 / 0.00 |
| `appraised_value` | Numeric | Final reconciled appraised value. | $5,000 to $1,705,000 | 0 / 0.00 | 7209 / 2.71 |
| `appraisal_to_contract` | Numeric | Appraised value as % of contract price. | 50.0% to 150.0% | 735631 / 49.64 | 62344 / 23.40 |