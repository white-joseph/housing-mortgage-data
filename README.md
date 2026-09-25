# housing-mortgage-data

Micro-level housing and mortgage dataset exploration for Dr. Nam Vu, Miami University. This repo downloads, cleans, and documents several public housing/mortgage datasets, with the goal of producing research-ready files and identifying opportunities to link them together.

Datasets covered so far:
- **UAD PUF** (FHFA Uniform Appraisal Dataset, Appraisal-Level Public Use File) — complete

Planned: Fannie Mae Single-Family Loan Performance Data, HMDA, ZTRAX.

## Repo structure

```
├── data/                # gitignored — raw and cleaned data live here locally, not in git
│   ├── raw/             # as downloaded, untouched
│   └── clean/           # cleaned, research-ready output (.dta)
├── docs/                # per-dataset documentation (one .md file per dataset)
├── src/                 # Python — download and cleaning scripts
│   └── uad/
│       ├── download_uad.py
│       └── clean_uad.py
├── r/                   # R — summary statistics and figures (R Markdown)
├── notebooks/           # gitignored — exploratory notebooks, not part of the reproducible pipeline
├── outputs/             # exported tables/figures (currently unused — output lives in the knitted .Rmd)
└── environment.yml      # conda environment
```

## Setup

```
conda env create -f environment.yml
conda activate housing-data
```

## Reproducing the UAD PUF pipeline

1. `python src/uad/download_uad.py` — downloads the raw Enterprise and FHA UAD PUF files into `data/raw/uad/`
2. `python src/uad/clean_uad.py` — cleans and combines both files into `data/clean/uad_clean.dta`
3. Open `r/uad_puf_sumstats.Rmd` in RStudio (via `housing-mortgage-data.Rproj`) and click **Knit** — produces summary statistics and figures from the cleaned data

See `docs/uad_puf.md` for full documentation of the dataset itself: variable definitions, known limitations, and research notes.

