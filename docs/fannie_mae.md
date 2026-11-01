# Documentation for the Fannie Mae Single-Family Loan Performance Dataset (primary dataset)

This data is published here: [Fannie Mae Data Dynamics](https://datadynamics.fanniemae.com) and you are just required to create a free login. The field layout is in the "Single-Family Loan Performance Dataset and Credit Risk Transfer - Glossary and File Layout", and the FAQ is "Single-Family Loan Performance Dataset FAQs".

Each observation (in the raw files) is one loan in one month. Fannie Mae publishes one filer per acquisition quarter (the quarter that they bought the loan), and each file and each file will follow those loans until they leave the datasets or until the latest reporting. The most recent release runs through the second quarter of 2026. Fannie Mae reports about 58.2 million loans acquired from January 2000 to June 2026 in its statistical summary.

The raw files that I have used so far are: 2007Q1, 2010Q1, 2018Q1, 2021Q1 and 2023Q1. Together they total about 45.5 GB.

## Relevant Documentation

- The portal has two datasets: Primary (the one I use here) and HARP.
- The Primary dataset is not every loan Fannie Mae acquired, instead it is fixed-rate, fully amortizing, full documentation, with a term of 5 to under 35 years. It leaves out HARP and Refi Plus loans, interest-only, balloon and prepayment-penalty loans, loans with an LTV above 97%, Alt-A, bulk and similar loans. 
- The format has been the same since October of 2020.
- Of the 114 fields, 41 are marked "NA" for loan performance in the layout which leaves 73 fields that we might care about.
- Old quarters are corrected in each release, so re-downloading a quarter later can change it slightly.
- Fannie Mae's definition of default (statistical summary): zero balance code 02, 03, 09 or 15 with a disposition date. That is what `default_completed` uses.
- Expense and proceeds fields are only filled after a disposition and on a lag of about 90 days. A blank means zero, but the clean file leaves them missing so that "not yet reported" isn't hidden. Treat a missing value as zero only for loans with a completed disposition.

## Quality & Limitations

- **Selected sample.** I explained it a bit above, but the loan counts are not all U.S. mortgages or all of Fannie Mae's book.
- **Right censoring.** Every loan is followed only to mid-2026, so the recent vintages have had little time to default. This means we should compare outcomes at the same loan age, not at the same calendar date.
- **Credit score changes.** `cscore_b` and `cscore_c` (borrower and co-borrower scores) stop being filled in March 2026. `orig_classic_fico` (lowest score among all borrowers) starts in December 2025 and `orig_vantage4` in May 2026. The cleaned `fico_orig` takes `orig_classic_fico` when it is there, and otherwise the lower of `cscore_b` and `cscore_c`.
- **Masked balances.** `current_upb` is masked for the first six months of a loan. Since the October 2020 format, it is 0 on the liquidation record and the removal balance is in `upb_at_removal`. `final_upb` combines them.
- **Last-period fields.** There are many fields only reported in the last active period.
- **Delinquency.** `dlq_status` is text; `00` current, `01`...`98` months, `99` for 99 or more months, `XX` unknown. `dlq_months` is the number, with `XX` set to missing.
- **MSA.** `00000` means not in an MSA. MSA codes are updated over time and MSADs (divisions) were added in December 2025, so a loan's `msa` is the first non-missing value in its history and may be different from HMDA.
- **Loan age** can be -1 (a loan reported before its first payment month). Remaining months to maturity is blank for modified loans. Modification flags only show the first modification.
- **Names.** `seller` and `servicer` are the most recent names, with "Other" for names under 1%.
- **Disclosure avoidance.** `orig_upb` is disclosed rounded, and the geography stops at MSA, 3-digit ZIP and state.

## Relevant Variables

- IDs and time: `loan_id`, `act_period`, `acq_quarter`, `orig_date`, `first_pay_date`, `loan_age`
- Loan characteristics: `channel`, `seller`, `orig_rate`, `orig_upb`, `orig_term`, `purpose`, `amort_type`, `mi_pct`, `mi_type`, `special_elig_program`, `high_balance_loan`
- Borrower and property: `oltv`, `ocltv`, `dti`, `fico_orig`, `num_borrowers`, `first_time_buyer`, `prop_type`, `num_units`, `occ_stat`, `prop_valuation_method`
- Geography: `state`, `msa`, `zip3`
- Performance: `dlq_status`, `dlq_months`, `current_upb`, `curr_rate`, `mod_flag`, `borrower_assist_plan`, `zero_bal_code`, `zero_bal_date`, `foreclosure_date`, `disposition_date`
- Loss: `foreclosure_costs`, `pres_repair_costs`, `asset_recovery_costs`, `misc_holding_exp`, `holding_taxes`, `net_sales_proceeds`, `credit_enh_proceeds`, `repurch_whole_proceeds`, `other_fc_proceeds`, `fc_principal_writeoff`, `principal_forgiveness`

## Data Dictionary: Zero Balance Codes

| Code | Meaning | Used in |
| :--- | :--- | :--- |
| `01` | Prepaid or matured | `prepaid` |
| `02` | Third-party sale | `credit_event` |
| `03` | Short sale | `credit_event` |
| `06` | Repurchased | `repurchased` |
| `09` | Deed in lieu / REO disposition | `credit_event` |
| `15` | Non-performing note sale | `credit_event` |
| `16` | Reperforming note sale | `terminated` only |
| `96` | Removal for non-credit reasons | `terminated` only |

## Data Dictionary: Loan-Level File (`fannie_mae_loans_{quarter}`)

| Column Name | Description |
| :--- | :--- |
| `loan_id`, `acq_quarter`, `acq_year`, `acq_qtr` | Loan ID (12 characters) and the quarter Fannie Mae acquired it |
| `orig_year`, `orig_qtr` | Origination year and quarter, from `orig_date` |
| `channel` | R retail, C correspondent, B broker |
| `seller` | Seller name ("Other" if under 1%) |
| `orig_rate`, `orig_upb`, `orig_term` | Note rate (%), original balance (rounded), term in months |
| `orig_date`, `first_pay_date` | Dates, first of the month |
| `oltv`, `ocltv`, `dti` | Original LTV, combined LTV, debt-to-income (%) |
| `cscore_b`, `cscore_c`, `orig_classic_fico`, `orig_vantage4` | Credit scores as published (see Quality & Limitations) |
| `fico_orig` | `orig_classic_fico`, else the lower of `cscore_b` and `cscore_c` |
| `num_borrowers`, `first_time_buyer`, `purpose`, `prop_type`, `num_units`, `occ_stat` | Borrower, purpose (P purchase, R refinance, C cash-out, U unspecified), property type (SF, PU, CO, CP, MH), units, occupancy (P, S, I, U) |
| `state`, `msa`, `zip3` | Geography (`msa` `00000` = not in an MSA) |
| `mi_pct`, `mi_type`, `amort_type`, `ppmt_flag`, `io_flag`, `first_pay_io_date` | Mortgage insurance and product flags |
| `special_elig_program`, `relocation_mortgage`, `prop_valuation_method`, `high_balance_loan`, `hltv_refi_option` | Program and valuation flags |
| `n_months_obs`, `first_act_period`, `last_act_period` | Months observed and first and last reporting month |
| `max_dlq_months` | Worst delinquency in months (`XX` ignored) |
| `ever_dlq30`, `ever_dlq60`, `ever_dlq90`, `ever_dlq180` | 1 if ever 1, 2, 3 or 6+ months delinquent |
| `first_dlq90_date`, `first_dlq180_date` | First reporting month at that severity |
| `ever_modified`, `first_mod_date`, `ever_forbearance`, `ever_assist_plan`, `ever_payment_deferral` | Modification and assistance flags |
| `zero_bal_code`, `zero_bal_date` | How and when the loan left the data (blank = still active) |
| `terminated`, `prepaid`, `repurchased` | Flags from `zero_bal_code` (all 0 for active loans) |
| `credit_event` | 1 if `zero_bal_code` is 02, 03, 09 or 15 |
| `default_completed` | 1 if `credit_event` and `disposition_date` is present (Fannie Mae's default) |
| `repurch_or_made_whole` | 1 if code 06, or code 02/03/09 with repurchase or make-whole proceeds |
| `liquidation_date` | `disposition_date` for credit events, otherwise `zero_bal_date` |
| `upb_at_removal`, `last_current_upb`, `final_upb` | Removal balance, last reported balance, and the one that applies |
| `foreclosure_date`, `disposition_date` | Foreclosure and disposition dates |
| `foreclosure_costs` ... `principal_forgiveness`, `non_int_bearing_upb` | Cost, proceeds and write-off fields as reported |

## Data Dictionary: Monthly Panel (`fannie_mae_monthly_{quarter}`)

One row per loan-month with 39 columns: `loan_id`, `act_period`, then the time-varying fields (`servicer`, `curr_rate`, `current_upb`, `loan_age`, `rem_months`, `adj_rem_months`, `maturity_date`, `months_to_amort_io`, `dlq_status`, `dlq_months`, `mod_flag`, the zero-balance and foreclosure fields above, `serv_activity_ind`, `borrower_assist_plan`, `repurch_whole_flag`, `adr_type`, `adr_count`, `total_deferral_amt`, `pmt_deferral_mod_flag`).

## Access & Redistribution

Fannie Mae's terms do not allow redistribution without its written consent and they also do not allow correlating the data to identify borrowers or loans.

## Cleaned Dataset

All five quarters through June 2026 reporting. Shares are the percentage of loans in that file.

| Acq. quarter | Loans | Loan-months | Mean UPB ($) | OLTV | DTI | Rate (%) | FICO | Prepaid | Completed default | Ever 90+ | Ever modified | Purchase |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2007Q1 | 253,279 | 16,804,063 | 192,780 | 69.2 | 37.6 | 6.22 | 717.4 | 86.3 | 8.53 | 16.4 | 7.1 | 32.9 |
| 2010Q1 | 323,174 | 21,032,502 | 218,182 | 65.3 | 33.4 | 4.89 | 758.4 | 94.1 | 0.64 | 2.7 | 0.8 | 30.3 |
| 2018Q1 | 458,830 | 23,902,313 | 234,667 | 74.8 | 36.4 | 4.25 | 741.6 | 75.2 | 0.21 | 6.6 | 1.4 | 53.7 |
| 2021Q1 | 1,413,390 | 80,080,858 | 282,748 | 67.0 | 32.9 | 2.79 | 760.7 | 23.0 | 0.03 | 1.6 | 0.4 | 24.0 |
| 2023Q1 | 210,810 | 7,686,914 | 312,829 | 75.3 | 37.5 | 6.33 | 749.0 | 26.1 | 0.10 | 2.9 | 0.9 | 78.9 |

## Linking

- **With HMDA at MSA x year.** `fannie_mae_msa_year.dta` has one row per `msa` x `orig_year`. HMDA has `derived_msa_md`, so we could join them on MSA and year but we need to check that the vintages agree.
- **With the UAD PUF.** The UAD PUF has census tracts, Fannie Mae has MSA, 3-digit ZIP and state, so the join would have to be MSA x year.

## Summary & Research Possibilities

Here are some ideas that I had:

- You could look at default and prepayment using HMDA lending patterns and UAD appraisal measures.
- You could study delinquency transitions using `borrower_assist_plan` and `adr_type`.
- You could measure loss severity for completed defaults by state and year, using the cost and proceeds fields.
- You could test how credit score, LTV, and DTI at origination predict default, and compare at the same loan age.
