# Documentation for the Home Mortgage Disclosure Act (HMDA) Snapshot National Loan-Level Dataset (LAR)

The data dictionary is [here](https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/lar-data-fields) and the data are published on the [FFIEC Snapshot National Loan-Level Dataset page](https://ffiec.cfpb.gov/data-publication/snapshot-national-loan-level-dataset/). HMDA data are collected under the Home Mortgage Disclosure Act and published by the Federal Financial Institutions Examination Council (FFIEC) and the Consumer Financial Protection Bureau (CFPB). This is the **Snapshot** version of the **Loan/Application Register (LAR)**, from 2018-2025.

Each observation is one covered loan or application reported by a financial institution. The raw files contain 99 fields and 137,678,531 records over eight years. The data covers all 50 U.S. states, DC, and territories. 

## Relevant Documentation

- FFIEC publishes three static versions of each year:
    - Snapshot (about one month after the March 1 filing deadline)
    - One Year (12 months after)
    - Three Year (34 months after, and final). 
    Lenders may resubmit for three years, so the Snapshot is the earliest and least revised version. I chose to download this data because it is the only one of the three that runs over the 2018-2025 timeframe. The Three Year dataset only covers 2017-2022 and the One Year dataset covers 2017-2024.
- There are multiple dates that the snapshots were frozen. The implication of this is that it leaves out any resubmissions or late filings that came afterward. The data were as follows: 
    - 2018: August 7, 2019
    - 2019: April 27, 2020
    - 2020: May 1, 2021
    - 2021: May 1, 2022
    - 2022: May 1, 2023
    - 2023: May 1, 2024
    - 2024: May 19, 2025
    - 2025: June 2, 2026
- The FFIEC Data Browser and API use the latest available static dataset (Three Year for 2018-2022, One Year for 2023-2024), so their counts will not exactly match these Snapshot files.
- The loan-to-value field is `loan_to_value_ratio` in the 2018 file and `combined_loan_to_value_ratio` in 2019-2025.
- The Transmittal Sheet (lender names), Panel, and ARID2017-to-LEI files are published separately.

## Quality & Limitations

- HMDA is not every mortgage in the country. Only institutions that meet HMDA's coverage tests report are included, so the smallest lenders are missing. There are also two rule changes that matter for comparisons across years:
    - The 2015 HMDA rule requires reporting of closed-end loans by institutions that originated at least 25 in each of the two preceding years. In 2020 the CFPB raised this to 100, effective July 1, 2020. In 2022 the 25-loan threshold was restored. Lenders with 25-99 closed-end loans may be missing in the years the higher threshold applied, which could make small-lender coverage differ across roughly 2020-2022.
    - Under the 2018 Economic Growth, Regulatory Relief, and Consumer Protection Act (EGRRCPA), smaller institutions do not have to report certain data points. This is where the `Exempt` and `1111` values come from.

- Since the data is a snapshot of a point in time, 2023-2025 have not reached their final (Three Year) version, so recent years may later be revised.

**Disclosure avoidance:** 
- `property_value` and `loan_amount` are rounded to the midpoint of the nearest $10,000 interval. 
- Applicant age is binned, and the debt-to-income ratio is binned for values below 36% and above 49%.


There are some extreme values that look like reporting errors (for example `rate_spread` from -2046 to 100, `income` below zero or over 200 million dollars, loan terms of 2 or 495 months, and some interest rates of 0).

`discount_points` is missing for 42-71% of loans, which mostly means no points were paid.

Census tracts use 2010 boundaries for 2018-2021 and 2020 boundaries from 2022 (similar to the UAD PUF). Same-year links are straightforward, but a tract-level panel across 2021-2022 needs a crosswalk.

## Relevant Variables

- Identifiers and geography: `activity_year`, `lei`, `derived_msa_md`, `state_code`, `county_code`, `census_tract`
- Loan characteristics: `action_taken`, `loan_purpose`, `loan_type`, `lien_status`, `derived_loan_product_type`, `conforming_loan_limit`, `purchaser_type`, `preapproval`, `hoepa_status`, `reverse_mortgage`, `open_end_line_of_credit`, `business_or_commercial_purpose`, `loan_amount`, `combined_loan_to_value_ratio` (`loan_to_value_ratio` in 2018), `interest_rate`, `rate_spread`, `total_loan_costs`, `discount_points`, `loan_term`
- Property characteristics: `property_value`, `construction_method`, `occupancy_type`, `total_units`, `derived_dwelling_category`
- Borrower characteristics: `derived_ethnicity`, `derived_race`, `derived_sex`, `income`, `debt_to_income_ratio`, `applicant_credit_score_type`, `applicant_age`
- Census tract characteristics: `tract_population`, `tract_minority_population_percent`, `ffiec_msa_md_median_family_income`, `tract_to_msa_income_percentage`, `tract_owner_occupied_units`, `tract_one_to_four_family_homes`, `tract_median_age_of_housing_units`

## Data Dictionary for HMDA LAR: Relevant Variables

| Column Name | Description | Allowed Values |
| :--- | :--- | :--- |
| `activity_year` | Calendar year the submission covers | 2018-2025 |
| `lei` | Lender's Legal Entity Identifier | Varying values |
| `derived_msa_md` | 5-digit derived MSA/MD code | Varying values (99999 appears for loans outside an MSA/MD) |
| `state_code`, `county_code`, `census_tract` | Two-letter state; state-county FIPS; 11-digit census tract | Varying values |
| `conforming_loan_limit` | Whether loan amount exceeds the GSE conforming limit | C, NC, U (undetermined), NA |
| `derived_loan_product_type` | Loan type and lien status combined | Conventional / FHA / VA / FSA-RHS : First or Subordinate Lien |
| `derived_dwelling_category` | Construction method and units combined | Single Family (1-4):Site-Built, Multifamily (5+):Site-Built, Single Family (1-4):Manufactured, Multifamily (5+):Manufactured |
| `derived_ethnicity` | Aggregated ethnicity of applicants | Hispanic or Latino; Not Hispanic or Latino; Joint; Ethnicity Not Available; Free Form Text Only |
| `derived_race` | Aggregated race of applicants | American Indian or Alaska Native; Asian; Black or African American; Native Hawaiian or Other Pacific Islander; White; 2 or more minority races; Joint; Free Form Text Only; Race Not Available |
| `derived_sex` | Aggregated sex of applicants | Male; Female; Joint; Sex Not Available |
| `action_taken` | Action taken on the loan or application | 1 Originated; 2 Approved not accepted; 3 Denied; 4 Withdrawn; 5 Closed for incompleteness; 6 Purchased loan; 7 Preapproval denied; 8 Preapproval approved not accepted |
| `purchaser_type` | Entity purchasing the loan | 0 N/A; 1 Fannie Mae; 2 Ginnie Mae; 3 Freddie Mac; 4 Farmer Mac; 5 Private securitizer; 6 Commercial bank, savings bank or association; 71 Credit union, mortgage or finance company; 72 Life insurance company; 8 Affiliate; 9 Other |
| `preapproval` | Preapproval requested | 1 Requested; 2 Not requested |
| `loan_type` | Loan type | 1 Conventional; 2 FHA; 3 VA; 4 RHS or FSA |
| `loan_purpose` | Loan purpose | 1 Home purchase; 2 Home improvement; 31 Refinancing; 32 Cash-out refinancing; 4 Other; 5 N/A |
| `lien_status` | Lien status | 1 First lien; 2 Subordinate lien |
| `reverse_mortgage`, `open_end_line_of_credit`, `business_or_commercial_purpose` | Reverse mortgage / open-end line / primarily business or commercial | 1 Yes; 2 No; 1111 Exempt |
| `hoepa_status` | High-cost mortgage | 1 High-cost; 2 Not high-cost; 3 N/A |
| `loan_amount` | Amount of the loan or amount applied for ($) | Varying values (observed as $10,000 midpoints) |
| `combined_loan_to_value_ratio` | Total debt secured by the property divided by property value (%) | Varying values |
| `interest_rate` | Interest rate (%) | Varying values |
| `rate_spread` | APR minus average prime offer rate | Varying values |
| `total_loan_costs`, `discount_points` | Total loan costs ($); points paid to reduce the rate ($) | Varying values |
| `loan_term` | Months until the obligation matures | Varying values |
| `property_value` | Value of the property relied on ($) | Varying values, rounded to the midpoint of the nearest $10,000 interval |
| `construction_method` | Construction method | 1 Site-built; 2 Manufactured home |
| `occupancy_type` | Occupancy | 1 Principal residence; 2 Second residence; 3 Investment property |
| `total_units` | Dwelling units in the property | 1, 2, 3, 4, 5-24, 25-49, 50-99, 100-149, >149 |
| `income` | Gross annual income relied on, in $ thousands | Varying values |
| `debt_to_income_ratio` | Total monthly debt over monthly income (%) | Bins: <20%, 20%-<30%, 30%-<36%, single values 36-49 (stored without a % sign), 50%-60%, >60%; NA; Exempt |
| `applicant_credit_score_type` | Credit scoring model used | 1 Equifax Beacon 5.0; 2 Experian Fair Isaac; 3 FICO Classic 04; 4 FICO Classic 98; 5 VantageScore 2.0; 6 VantageScore 3.0; 7 More than one model; 8 Other; 9 N/A; 1111 Exempt |
| `applicant_age` | Age of applicant | <25, 25-34, 35-44, 45-54, 55-64, 65-74, >74, 8888 |
| `tract_population` | Total tract population | Varying values |
| `tract_minority_population_percent` | Minority share of tract population, 2 decimals | Varying values |
| `ffiec_msa_md_median_family_income` | FFIEC median family income of the MSA/MD ($) | Varying values |
| `tract_to_msa_income_percentage` | Tract median family income as % of MSA/MD | Varying values |
| `tract_owner_occupied_units` | Owner-occupied dwellings in tract | Varying values |
| `tract_one_to_four_family_homes` | 1-4 family dwellings in tract | Varying values |
| `tract_median_age_of_housing_units` | Median age of homes in tract | Varying values |

## Access & Redistribution

The data are public and free to download from the FFIEC, with no account, license, or data use agreement. The raw CSVs total about 53 GB. `src/hmda/download_hmda.py` re-downloads them.

## Cleaned Dataset

**Sample:** I kept originated (`action_taken = 1`), first-lien, owner-occupied, site-built, 1-4 unit, closed-end, non-reverse, non-business home-purchase loans. This keeps 27,789,337 of 137,678,531 observations (20%). Refinances are excluded.

| Year | Rows read | Rows kept | % kept tracts missing |
| :--- | ---: | ---: | ---: |
| 2018 | 15,119,651 | 3,591,478 | 0.40 |
| 2019 | 17,545,457 | 3,732,655 | 0.26 |
| 2020 | 25,551,868 | 4,098,299 | 0.18 |
| 2021 | 26,124,552 | 4,369,605 | 0.13 |
| 2022 | 16,080,210 | 3,529,813 | 0.12 |
| 2023 | 11,483,889 | 2,795,089 | 0.15 |
| 2024 | 12,229,298 | 2,819,843 | 0.14 |
| 2025 | 13,543,606 | 2,852,555 | 0.16 |

**Cleaning:** `src/hmda/clean_hmda.py` reads each file in 1,000,000-row chunks as text and then:
- keeps 45 of the 99 variables
- applies the sample filter and drops nine columns that are constant after it
- renames the 2018 loan-to-value field to `combined_loan_to_value_ratio`
- converts numeric fields to numbers (text such as "Exempt" becomes missing) and code fields to integers
- sets tracts that are not 11 digits, and counties that are not 5 digits, to missing
- stores four long text fields as labelled integers, and keeps `lei` as text
- shortens three variable names to fit Stata's 32-character limit (`tract_minority_pct`, `msa_md_median_fam_income`, `tract_median_housing_age`)

**Outputs**:
- `hmda_clean_{year}.dta`: 3-4 million loans per year, 35 variables.
- `hmda_tract_year.dta`: 617,100 tract-year rows (2018-2025) with loan count and mean/median loan amount, mean property value, income, CLTV, and interest rate.
- `data/combined/hmda_uad_tract_year.dta`: the HMDA-UAD linked tract-year file (see below).

**Missing values (% of kept loans):**

| Year | CLTV | Interest rate | Property value | Income | Discount points |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 2018 | 5.5 | 3.2 | 3.1 | 0.9 | 70.6 |
| 2019 | 6.0 | 2.6 | 3.1 | 0.9 | 68.4 |
| 2020 | 4.7 | 2.2 | 2.5 | 0.9 | 67.0 |
| 2021 | 3.8 | 1.4 | 1.7 | 0.9 | 67.7 |
| 2022 | 4.3 | 1.6 | 1.9 | 0.9 | 49.2 |
| 2023 | 4.5 | 1.9 | 2.2 | 0.8 | 42.4 |
| 2024 | 4.7 | 2.1 | 2.4 | 0.7 | 45.6 |
| 2025 | 5.3 | 2.3 | 2.8 | 0.9 | 50.2 |

**Cleaned data dictionary (loan-level, `hmda_clean_{year}.dta`, 35 variables):**

Types: *text* is a string, *int* is a whole number (stored as a float where missing values exist), *num* is a continuous number, *label* is a Stata labelled integer. Text that is missing is stored as an empty string. Raw codes are explained in the raw dictionary above.

| Variable | Type | Description | Values / Notes |
| :--- | :--- | :--- | :--- |
| `activity_year` | int | Year of the file | 2018-2025 |
| `lei` | text | Lender's Legal Entity Identifier | 20 characters |
| `derived_msa_md` | text | 5-digit MSA/MD code | 99999 = outside an MSA/MD |
| `state_code` | text | Two-letter state | |
| `county_code` | text | 5-digit state-county FIPS | Missing if not 5 digits |
| `census_tract` | text | 11-digit tract FIPS | Missing if not 11 digits (0.1-0.4% of loans). 2010 boundaries 2018-2021, 2020 boundaries from 2022 |
| `conforming_loan_limit` | text | Loan amount vs. the GSE conforming limit | C, NC, U, NA |
| `derived_loan_product_type` | label | Loan type and lien status | First-lien only after the filter: Conventional, FHA, VA, FSA/RHS |
| `derived_ethnicity` | label | Aggregated applicant ethnicity | See raw dictionary |
| `derived_race` | label | Aggregated applicant race | See raw dictionary |
| `derived_sex` | label | Aggregated applicant sex | See raw dictionary |
| `purchaser_type` | int | Who bought the loan | 0 N/A (not sold in the year), 1 Fannie Mae, 3 Freddie Mac, etc.; 1111 Exempt |
| `preapproval` | int | Preapproval requested | 1 Requested, 2 Not requested; 1111 Exempt |
| `loan_type` | int | Loan program | 1 Conventional, 2 FHA, 3 VA, 4 RHS/FSA |
| `loan_amount` | num | Loan amount, $ | $10k midpoints |
| `combined_loan_to_value_ratio` | num | Combined LTV, % | The 2018 `loan_to_value_ratio`. Missing for "Exempt" and "NA" |
| `interest_rate` | num | Interest rate, % | 0 is likely an error |
| `rate_spread` | num | APR minus average prime offer rate | Extreme values exist |
| `hoepa_status` | int | High-cost mortgage | 1 High-cost, 2 Not high-cost, 3 N/A |
| `total_loan_costs` | num | Total loan costs, $ | |
| `discount_points` | num | Points paid to lower the rate, $ | Mostly missing (42-71%) |
| `loan_term` | num | Months to maturity | |
| `property_value` | num | Property value relied on, $ | $10k midpoints |
| `total_units` | int | Dwelling units | 1-4 after the filter |
| `income` | num | Gross annual income relied on, $ thousands | Extreme values exist |
| `debt_to_income_ratio` | text | Debt-to-income, binned | Text bins (see raw dictionary); blank, NA or Exempt otherwise |
| `applicant_credit_score_type` | int | Credit scoring model | 1-9; 1111 Exempt |
| `applicant_age` | text | Applicant age bin | <25 ... >74, 8888 |
| `tract_population` | num | Tract population | |
| `tract_minority_pct` | num | Minority share of tract population, % | |
| `msa_md_median_fam_income` | num | FFIEC median family income of the MSA/MD, $ | |
| `tract_to_msa_income_percentage` | num | Tract median family income as % of the MSA/MD | |
| `tract_owner_occupied_units` | num | Owner-occupied dwellings in tract | |
| `tract_one_to_four_family_homes` | num | 1-4 family dwellings in tract | |
| `tract_median_housing_age` | num | Median age of homes in tract, years | |

Dropped after the filter because they are constant: `action_taken`, `lien_status`, `loan_purpose`, `occupancy_type`, `construction_method`, `derived_dwelling_category`, `open_end_line_of_credit`, `reverse_mortgage`, `business_or_commercial_purpose`.

**Cleaned data dictionary (tract-year, `hmda_tract_year.dta`, one row per tract and year):**

| Variable | Description |
| :--- | :--- |
| `census_tract` | 11-digit tract FIPS (loans with no valid tract are dropped) |
| `activity_year` | Year |
| `n_loans` | Number of loans in the cleaned sample (not all HMDA loans in the tract) |
| `loan_amount_mean`, `loan_amount_median` | Loan amount, $ |
| `property_value_mean` | Property value, $ |
| `income_mean` | Income, $ thousands |
| `cltv_mean` | Combined LTV, % |
| `interest_rate_mean` | Interest rate, % |

Means include the extreme values noted above (a few tract means are clearly wrong), so look at medians or trim before using them.

## Linked HMDA-UAD File

`src/combined/link_hmda_uad.py` joins the HMDA tract-year file to the UAD appraisals collapsed to the same level. The output is `data/combined/hmda_uad_tract_year.dta`: 369,452 rows, one per tract and year, 2018-2022 (the years both datasets cover). The join is an outer join and `link_status` says where each row came from.

| Variable | Description |
| :--- | :--- |
| `tract_fips`, `year` | Keys |
| `hmda_n_loans`, `hmda_loan_amount_mean`, `hmda_loan_amount_median`, `hmda_property_value_mean`, `hmda_income_mean`, `hmda_cltv_mean`, `hmda_interest_rate_mean` | From the HMDA tract-year file |
| `uad_n_appraisals`, `uad_appraised_value_mean` | All UAD appraisals in the tract-year |
| `uad_n_purchase`, `uad_contract_price_mean`, `uad_purchase_value_mean`, `uad_appraisal_to_contract_mean` | UAD purchase appraisals only (missing if none) |
| `link_status` | `both`, `hmda_only`, or `uad_only` |

| Year | Both | HMDA only | UAD only | % of HMDA tract-years matched |
| :--- | ---: | ---: | ---: | ---: |
| 2018 | 45,635 | 25,877 | 2 | 63.8 |
| 2019 | 48,802 | 22,790 | 2 | 68.2 |
| 2020 | 54,119 | 17,496 | 11 | 75.6 |
| 2021 | 54,435 | 17,464 | 10 | 75.7 |
| 2022 | 49,146 | 33,662 | 1 | 59.3 |

Things to know before using it:
- Nearly every UAD tract-year is in HMDA, but a quarter to 40% of HMDA tract-years have no UAD match. UAD's public file blanks out the tract for some appraisals, and the file only has a small number of appraisals per tract: the median matched tract-year has 2-3 UAD appraisals (and a median of about 50 HMDA loans). The UAD means are therefore noisy, so keep `uad_n_appraisals` in any filter.
- HMDA covers originated purchase loans, while UAD covers appraisals (Enterprise and FHA) of purchases and refinances. The two samples overlap but are not the same set of loans.
- In matched tract-years the HMDA mean property value is close to the UAD mean purchase appraisal (median ratio about 1.01-1.03, correlation of the logs 0.82-0.89), which suggests the link is working.
- 2022 uses 2020 tract boundaries in both datasets, so it links cleanly, but a panel across 2021 and 2022 needs a crosswalk.

## Summary & Research Possibilities

The two things I think this could be used for are examining the lending side of local housing markets, and using it as source of tract-level controls for the other datasets. This dataset also comes at a very good time for studying how rate cycles change who borrows and where they borrow. The mean interest rate on these loans fell from 4.8% in 2018 to 3.1% in 2021 and then rose to 6.5% in 2023, and the number of purchase loans fell from 4.37 million (2021) to 2.80 million (2023). The mean loan amount rose from about $275k to $404k over the timeframe.

I think the most interesting things about this dataset are the spikes at 80 and 96.5, where the 20%-down and FHA minimum down payment cutoffs are, the conforming loan limit, and how the 2021-2023 rate shock changed the borrower mix (`income`, `derived_race`, `loan_type`) within the same MSA or tract.

After linking to the UAD PUF at the tract-year level, I think something interesting to ask is whether the appraisal-to-contract bunching at 100% is stronger where more buyers are highly leveraged. HMDA `property_value` can also be checked against UAD prices, and UAD's property characteristics could be used to build quality-adjusted tract prices weighted by HMDA volume. The UAD means rest on only 2-3 appraisals per tract-year, so this is better suited to larger tracts. For the other datasets, Fannie Mae can only be linked at the MSA or ZIP3 level, which would let local lending conditions be related to loan outcomes, and HMDA loans sold to Fannie Mae can be used as a quality check. Once we get ZTRAX access, HMDA purchase loans divided by ZTRAX sales would give the share of purchases financed with a mortgage, and one minus that is the cash share.
