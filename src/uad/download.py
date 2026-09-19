"""
Download UAD Appraisal-Level Public Use File (PUF) data from FHFA.

Source page (check here if a URL below returns a 404):
https://www.fhfa.gov/data/uad/puf

Downloads the combined CSV files (Enterprise + FHA) and unzips them
into data/raw/uad/. Re-running this script is safe — it just
re-downloads and overwrites.
"""

import zipfile
import requests
from pathlib import Path

# --- Paths -------------------------------------------------------------
# Adjust this if your notebook/script isn't run from the repo root.
RAW_DIR = Path("data/raw/uad")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# --- Source files --------------------------------------------------------
# Combined files (all years in one CSV) are simplest to start with.
# Swap these for the *_annual_* URLs if you want one file per year instead.
FILES = {
    "ent_uad_puf_combined_csv_v2_1.zip": (
        "https://www.fhfa.gov/document/d/uad-al/"
        "ent_uad_puf_combined_csv_v2_1.zip"
    ),
    "fha_uad_puf_combined_v1_0_csv.zip": (
        "https://www.fhfa.gov/document/d/uad-al/"
        "fha_uad_puf_combined_v1_0_csv.zip"
    ),
}


def download_file(filename: str, url: str, dest_dir: Path) -> Path:
    """Download one file, failing loudly if FHFA has moved it."""
    dest_path = dest_dir / filename
    print(f"Downloading {filename} ...")

    response = requests.get(url, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(
            f"Download failed for {filename} "
            f"(status {response.status_code}). "
            "FHFA may have moved the file — check "
            "https://www.fhfa.gov/data/uad/puf for the current link "
            "and update the URL in this script."
        )

    # A 200 status with a tiny HTML body usually means we got an error
    # page, not the actual zip — catch that case too.
    if response.headers.get("Content-Type", "").startswith("text/html"):
        raise RuntimeError(
            f"Expected a zip file for {filename} but got an HTML page "
            "instead. The download link has likely changed — check "
            "https://www.fhfa.gov/data/uad/puf"
        )

    dest_path.write_bytes(response.content)
    print(f"  Saved to {dest_path} ({len(response.content):,} bytes)")
    return dest_path


def unzip_file(zip_path: Path, dest_dir: Path) -> None:
    print(f"Unzipping {zip_path.name} ...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)


def main():
    for filename, url in FILES.items():
        zip_path = download_file(filename, url, RAW_DIR)
        unzip_file(zip_path, RAW_DIR)
    print("Done. Raw UAD files are in", RAW_DIR)


if __name__ == "__main__":
    main()
