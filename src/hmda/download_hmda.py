"""
Download the HMDA Snapshot National Loan-Level Dataset (LAR, CSV) for 2018-2025.

Output: data/raw/hmda/hmda_{year}.csv 

Source: https://ffiec.cfpb.gov/data-publication/snapshot-national-loan-level-dataset/
The Snapshot is the earliest of the FFIEC's static datasets for each year, so later
resubmissions are not included. Each zip is 1-2 GB and each CSV 4-10 GB, 
so this takes a while.The script can be re-run safely since finished years are skipped
and interrupted downloads resume.
"""
from pyprojroot.here import here
import requests
import shutil
import zipfile
import time

# setting 
years = range(2018, 2026)  # end is exclusive, so this includes 2025
KEEP_ZIP = False           # True keeps the zips after extracting

BASE = "https://files.ffiec.cfpb.gov/static-data/snapshot"
urls = {year: f"{BASE}/{year}/{year}_public_lar_csv.zip" for year in years}

# The server rejects requests that do not look like a browser (HTTP 403), so
# must be a browser-style User-Agent and Referer.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer": "https://ffiec.cfpb.gov/data-publication/snapshot-national-loan-level-dataset/",
}

hmda_path = here("data/raw/hmda")
hmda_path.mkdir(parents=True, exist_ok=True)


def download(url, out_file, max_tries=10):
    """Download url to out_file, resuming from a partial file if the connection drops."""
    # Data goes to a ".part" file first and is renamed only when complete, so a
    # half-finished download is never mistaken for a finished one.
    tmp = out_file.with_name(out_file.name + ".part")

    for attempt in range(1, max_tries + 1):
        have = tmp.stat().st_size if tmp.exists() else 0   # bytes already downloaded
        headers = dict(HEADERS)
        if have:
            headers["Range"] = f"bytes={have}-"   # ask the server to resume

        try:
            with requests.get(url, stream=True, timeout=60, headers=headers) as r:
                if r.status_code == 416:           # "range not satisfiable": we already have everything
                    break
                if r.status_code == 200 and have:  # server ignored Range, so start over
                    have = 0
                r.raise_for_status()
                # a blocked request can return an HTML error page with status 200
                if r.headers.get("Content-Type", "").startswith("text/html"):
                    raise RuntimeError(f"Got an HTML page instead of data for {url}")

                mode = "ab" if have else "wb"      # append when resuming, otherwise overwrite
                with open(tmp, mode) as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):   # 1 MB at a time
                        f.write(chunk)
            break                                  # finished without an error
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            # a dropped connection (this happened on the 1.5 GB 2020 file): wait, then resume
            print(f"  attempt {attempt}/{max_tries} failed at "
                  f"{tmp.stat().st_size / 1e6:.0f} MB: {type(e).__name__}. Retrying...")
            time.sleep(5)
    else:
        raise RuntimeError(f"Gave up on {url} after {max_tries} attempts")

    tmp.rename(out_file)


def extract_csv(zip_file, csv_file):
    """Extract the single CSV inside the zip, renaming it to csv_file."""
    tmp = csv_file.with_name(csv_file.name + ".part")   # same ".part" trick as above
    with zipfile.ZipFile(zip_file) as zf:
        members = [m for m in zf.namelist() if m.lower().endswith(".csv")]
        if len(members) != 1:
            raise RuntimeError(f"Expected 1 CSV in {zip_file.name}, found {members}")
        # stream in 1 MB pieces: the CSV is far too large to hold in memory
        with zf.open(members[0]) as src, open(tmp, "wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
    tmp.rename(csv_file)


# run 
for year in years:
    csv_file = hmda_path / f"hmda_{year}.csv"
    zip_file = hmda_path / f"hmda_{year}.zip"

    if csv_file.exists():                  # already done: skip
        print(f"Already have {csv_file.name}, skipping")
        continue

    if not zip_file.exists():              # a manually downloaded zip is used as is
        print(f"Downloading HMDA {year}...")
        download(urls[year], zip_file)

    print(f"Extracting {zip_file.name}...")
    extract_csv(zip_file, csv_file)

    if not KEEP_ZIP:                       # the CSV is all we need; free the disk space
        zip_file.unlink()
    print(f"Saved to {csv_file}")

print("Done.")
