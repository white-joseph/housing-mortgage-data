"""
Field layout of the Fannie Mae Single-Family Loan Performance files.

clean_fannie_mae.py imports this file since it is the only place that says what each column is
and how it should be treated. The raw files don't have column headers so this is the solution.

The FIELDS rows are (position, name, type, role). and the names are at most 32 characters so they
also work as Stata variable names.
"""

N_FIELDS = 114

FIELDS = [
    (1,   "pool_id",                 "str",  "na"),
    (2,   "loan_id",                 "str",  "key"),
    (3,   "act_period",              "date", "key"),
    (4,   "channel",                 "str",  "orig"),     # R retail, C correspondent, B broker
    (5,   "seller",                  "str",  "orig"),     # "Other" if under 1% of the quarter's volume
    (6,   "servicer",                "str",  "monthly"),  # blank before Dec 2001; "Other" if small
    (7,   "master_servicer",         "str",  "na"),
    (8,   "orig_rate",               "num",  "orig"),
    (9,   "curr_rate",               "num",  "monthly"),
    (10,  "orig_upb",                "num",  "orig"),     # disclosed rounded
    (11,  "issuance_upb",            "num",  "na"),
    (12,  "current_upb",             "num",  "monthly"),  # masked for the first six months of a loan
    (13,  "orig_term",               "int",  "orig"),
    (14,  "orig_date",               "date", "orig"),
    (15,  "first_pay_date",          "date", "orig"),
    (16,  "loan_age",                "int",  "monthly"),  # can be -1 when a loan is reported before its first payment month
    (17,  "rem_months",              "int",  "monthly"),  # remaining months to legal maturity
    (18,  "adj_rem_months",          "int",  "monthly"),  # remaining months to maturity given the balance
    (19,  "maturity_date",           "date", "monthly"),  # changes if the loan is modified
    (20,  "oltv",                    "num",  "orig"),     # blank for some HARP loans
    (21,  "ocltv",                   "num",  "orig"),
    (22,  "num_borrowers",           "int",  "orig"),
    (23,  "dti",                     "num",  "orig"),     # blank for all HARP loans and out-of-range values
    (24,  "cscore_b",                "int",  "orig"),     # not populated from the March 2026 activity period
    (25,  "cscore_c",                "int",  "orig"),     # not populated from the March 2026 activity period
    (26,  "first_time_buyer",        "str",  "orig"),
    (27,  "purpose",                 "str",  "orig"),     # P purchase, R refinance, C cash-out, U not specified
    (28,  "prop_type",               "str",  "orig"),     # SF, PU, CO, CP, MH
    (29,  "num_units",               "int",  "orig"),
    (30,  "occ_stat",                "str",  "orig"),     # P principal, S second, I investor, U unknown
    (31,  "state",                   "str",  "orig"),
    (32,  "msa",                     "str",  "orig"),     # 00000 = not in an MSA/MSAD. Updated over time, MSADs added Dec 2025
    (33,  "zip3",                    "str",  "orig"),
    (34,  "mi_pct",                  "num",  "orig"),
    (35,  "amort_type",              "str",  "orig"),     # FRM in the primary dataset
    (36,  "ppmt_flag",               "str",  "orig"),
    (37,  "io_flag",                 "str",  "orig"),
    (38,  "first_pay_io_date",       "date", "orig"),
    (39,  "months_to_amort_io",      "int",  "monthly"),
    (40,  "dlq_status",              "str",  "monthly"),  # 00 current ... 99 = 99+ months, XX unknown
    # 41 Loan Payment History: the delinquency status for the last 24 months in one string.
    # It repeats what dlq_status already gives month by month, and it is 48 characters per
    # row, so I don't keep it.
    (41,  "pmt_history",             "str",  "skip"),
    (42,  "mod_flag",                "str",  "monthly"),  # Y from the first modification onward
    (43,  "mi_cancel_flag",          "str",  "na"),
    (44,  "zero_bal_code",           "str",  "monthly"),  # 01 prepaid, 02 third party sale, 03 short sale, 06 repurchased, 09 REO, 15 NPL sale, 16 RPL sale, 96 non-credit removal
    (45,  "zero_bal_date",           "date", "monthly"),
    (46,  "upb_at_removal",          "num",  "monthly"),
    (47,  "repurchase_date",         "date", "na"),
    (48,  "sched_principal_current", "num",  "na"),
    (49,  "total_principal_current", "num",  "monthly"),
    (50,  "unsched_principal_current", "num", "na"),
    (51,  "last_paid_inst_date",     "date", "monthly"),
    (52,  "foreclosure_date",        "date", "monthly"),
    (53,  "disposition_date",        "date", "monthly"),
    (54,  "foreclosure_costs",       "num",  "monthly"),
    (55,  "pres_repair_costs",       "num",  "monthly"),
    (56,  "asset_recovery_costs",    "num",  "monthly"),
    (57,  "misc_holding_exp",        "num",  "monthly"),
    (58,  "holding_taxes",           "num",  "monthly"),
    (59,  "net_sales_proceeds",      "num",  "monthly"),
    (60,  "credit_enh_proceeds",     "num",  "monthly"),
    (61,  "repurch_whole_proceeds",  "num",  "monthly"),
    (62,  "other_fc_proceeds",       "num",  "monthly"),
    (63,  "non_int_bearing_upb",     "num",  "monthly"),
    (64,  "principal_forgiveness",   "num",  "monthly"),
    (65,  "orig_list_start_date",    "date", "na"),
    (66,  "orig_list_price",         "num",  "na"),
    (67,  "curr_list_start_date",    "date", "na"),
    (68,  "curr_list_price",         "num",  "na"),
    (69,  "issue_score_b",           "int",  "na"),
    (70,  "issue_score_c",           "int",  "na"),
    (71,  "curr_score_b",            "int",  "na"),
    (72,  "curr_score_c",            "int",  "na"),
    (73,  "mi_type",                 "str",  "orig"),
    (74,  "serv_activity_ind",       "str",  "monthly"),
    (75,  "cur_mod_loss",            "num",  "na"),
    (76,  "cum_mod_loss",            "num",  "na"),
    (77,  "cur_credit_event_gl",     "num",  "na"),
    (78,  "cum_credit_event_gl",     "num",  "na"),
    (79,  "special_elig_program",    "str",  "orig"),     # F HFA Preferred, H HomeReady/Home Possible, R RefiNow, O other, 7 N/A, 9 not available
    (80,  "fc_principal_writeoff",   "num",  "monthly"),
    (81,  "relocation_mortgage",     "str",  "orig"),
    (82,  "zb_code_change_date",     "date", "na"),
    (83,  "holdback_ind",            "str",  "na"),
    (84,  "holdback_eff_date",       "date", "na"),
    (85,  "delinq_accrued_int",      "num",  "na"),
    (86,  "prop_valuation_method",   "str",  "orig"),     # A appraisal, W waiver, C/P/R/O ... (from 2017 acquisitions)
    (87,  "high_balance_loan",       "str",  "orig"),
    (88,  "arm_5yr_ind",             "str",  "na"),
    (89,  "arm_product_type",        "str",  "na"),
    (90,  "arm_init_fixed_period",   "int",  "na"),
    (91,  "arm_adj_frequency",       "int",  "na"),
    (92,  "arm_next_rate_adj_date",  "date", "na"),
    (93,  "arm_next_pmt_chg_date",   "date", "na"),
    (94,  "arm_index",               "str",  "na"),
    (95,  "arm_cap_structure",       "str",  "na"),
    (96,  "arm_init_rate_cap",       "num",  "na"),
    (97,  "arm_periodic_cap",        "num",  "na"),
    (98,  "arm_lifetime_cap",        "num",  "na"),
    (99,  "arm_margin",              "num",  "na"),
    (100, "arm_balloon_ind",         "str",  "na"),
    (101, "arm_plan_number",         "int",  "na"),
    (102, "borrower_assist_plan",    "str",  "monthly"),  # F forbearance, R repayment, T trial, O other, N none, 7 N/A, 9 not available
    (103, "hltv_refi_option",        "str",  "orig"),
    (104, "deal_name",               "str",  "na"),
    (105, "repurch_whole_flag",      "str",  "monthly"),
    (106, "adr_type",                "str",  "monthly"),  # alternative delinquency resolution: P/C/D payment deferral, 7 N/A, 9 not available
    (107, "adr_count",               "int",  "monthly"),
    (108, "total_deferral_amt",      "num",  "monthly"),
    (109, "pmt_deferral_mod_flag",   "str",  "monthly"),  # always 7 (not applicable) in the loan performance data
    (110, "int_bearing_upb",         "num",  "na"),
    (111, "orig_classic_fico",       "int",  "orig"),     # populated from the December 2025 activity period
    (112, "issue_classic_fico",      "int",  "na"),
    (113, "curr_classic_fico",       "int",  "na"),
    (114, "orig_vantage4",           "int",  "orig"),     # populated from the May 2026 activity period
]

assert len(FIELDS) == N_FIELDS
assert [f[0] for f in FIELDS] == list(range(1, N_FIELDS + 1))
assert len({f[1] for f in FIELDS}) == N_FIELDS
assert all(len(f[1]) <= 32 for f in FIELDS)

# name -> (type, role)
FIELD_INFO = {name: (kind, role) for _, name, kind, role in FIELDS}
COLUMN_NAMES = [name for _, name, _, _ in FIELDS]

NA_COLS = [name for _, name, _, role in FIELDS if role == "na"]
ORIG_COLS = [name for _, name, _, role in FIELDS if role == "orig"]
MONTHLY_COLS = [name for _, name, _, role in FIELDS if role == "monthly"]