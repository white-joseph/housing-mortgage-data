"""
Check the raw Fannie Mae Single-Family Loan Performance files before cleaning.

Run from anywhere inside the repo:  python src/fannie_mae/check_fannie_mae.py

There is no download script for this dataset because Fannie Mae requires a login.
Download the files by hand (see docs/fannie_mae.md), then use this to check them.

Input : data/raw/fannie-mae/{year}Q{quarter}.csv   (one file per acquisition quarter, e.g. 2010Q1.csv)
For every file it checks that
  - the name looks like 2010Q1.csv
  - the first line has exactly 114 pipe-delimited fields (the current layout). A file with
    113 fields comes from an older release (it has no VantageScore field), so re-download it
  - the first line looks like a loan record (12-character loan id, MMYYYY reporting period)
and prints the size of each file and the free disk space. It exits with an error if any
file fails, so it can be used before a long cleaning run.
"""
from pyprojroot.here import here
import re
import shutil
import sys

# setting
N_FIELDS = 114                      # fields per line in the current layout
MIN_FREE_GB = 40                    # warn when the drive holding the data has less free space

raw_path = here("data/raw/fannie-mae")
NAME_RE = re.compile(r"^(\d{4})Q([1-4])\.csv$")


def first_line(path):
    """Read just the first line (the files are far too big to read whole)."""
    with open(path, "r", encoding="latin-1", newline="") as f:
        return f.readline().rstrip("\r\n")


def check_file(path):
    """Return a list of problems with one raw file (an empty list means it passed)."""
    problems = []
    m = NAME_RE.match(path.name)
    if not m:
        return [f"name should look like 2010Q1.csv, got {path.name}"]

    line = first_line(path)
    n = len(line.split("|"))
    if n != N_FIELDS:
        hint = " (older release: re-download it)" if n == N_FIELDS - 1 else ""
        problems.append(f"first line has {n} fields, expected {N_FIELDS}{hint}")
        return problems

    parts = line.split("|")
    loan_id, period = parts[1], parts[2]
    if len(loan_id) != 12:
        problems.append(f"loan id {loan_id!r} is not 12 characters")
    if not re.fullmatch(r"(0[1-9]|1[0-2])\d{4}", period):
        problems.append(f"reporting period {period!r} is not MMYYYY")
    elif period[2:] != m.group(1):
        # not an error: a loan acquired in January can first appear in the previous year
        print(f"    note: first reporting period is {period}, file is {path.name}")
    return problems


# run
if not raw_path.exists():
    sys.exit(f"{raw_path} does not exist. Create it and put the quarterly CSVs in it.")

leftovers = [p.name for p in raw_path.iterdir()
             if p.is_file() and p.suffix.lower() in (".zip", ".part", ".crdownload")]
if leftovers:
    print(f"Unfinished or zipped downloads in {raw_path}: {leftovers}\n"
          "  Unzip them (and rename the CSV to e.g. 2010Q1.csv) or delete them.\n")

files = sorted(p for p in raw_path.iterdir() if p.is_file() and p.suffix.lower() == ".csv")
if not files:
    sys.exit(f"No CSV files in {raw_path}")

bad = 0
total_gb = 0.0
for path in files:
    gb = path.stat().st_size / 1e9
    total_gb += gb
    print(f"{path.name:<12} {gb:7.2f} GB")
    problems = check_file(path)
    for p in problems:
        print(f"    PROBLEM: {p}")
    bad += bool(problems)

free_gb = shutil.disk_usage(raw_path).free / 1e9
print(f"\n{len(files)} files, {total_gb:.1f} GB. Free disk space: {free_gb:.0f} GB.")
if free_gb < MIN_FREE_GB:
    print(f"WARNING: less than {MIN_FREE_GB} GB free. The clean step needs room for the Parquet and .dta outputs.")

if bad:
    sys.exit(f"{bad} file(s) failed the check.")
print("All files passed.")
