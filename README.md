# housing-mortgage-data

This repo downloads, cleans, and documents several public housing/mortgage datasets, with the goal of identifying opportunities to link them together.

Datasets covered so far:
- **UAD PUF** (FHFA Uniform Appraisal Dataset, Appraisal-Level Public Use File), 2013-2022: [`docs/uad_puf.md`](docs/uad_puf.md)
- **HMDA** (FFIEC Home Mortgage Disclosure Act Snapshot National Loan-Level Dataset), 2018-2025: [`docs/hmda.md`](docs/hmda.md)

## Repo structure

```
├── data/                # gitignored
│   ├── raw/             # as downloaded, untouched
│   │   ├── uad/
│   │   └── hmda/        # ~53 GB of CSVs
│   ├── clean/           # cleaned outputs
│       ├── uad_clean.dta
│       └── hmda/        # one loan-level .dta per year + hmda_tract_year.dta
│   └── combined/        # linked datasets (hmda_uad_tract_year.dta)
├── docs/                # dataset documentation (one .md per dataset)
├── src/                 # source code for download and cleaning scripts
│   ├── uad/
│   │   ├── download_uad.py
│   │   └── clean_uad.py
│   ├── hmda/
│   │   ├── download_hmda.py
│   │   └── clean_hmda.py
│   └── combined/
│       └── link_hmda_uad.py
├── r/                   # summary statistics and figures
├── outputs/             # exported tables/figures and cleaning logs
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
3. Open `r/uad_puf_sumstats.Rmd` in RStudio and knit to produce summary statistics and figures

## Reproducing the HMDA pipeline

The raw files are large (4-10 GB per year, about 53 GB in total), so check your free disk space first. Both scripts can be re-run safely: finished years are skipped by the download, and an interrupted download resumes.

1. `python src/hmda/download_hmda.py` — downloads the 2018-2025 Snapshot LAR files into `data/raw/hmda/`
2. `python src/hmda/clean_hmda.py` — restricts to originated home-purchase loans, cleans them, and writes:
   - `data/clean/hmda/hmda_clean_{year}.dta` (loan level, one file per year)
   - `data/clean/hmda/hmda_tract_year.dta` (census tract x year aggregates, used for linking)
3. Open `r/hmda_sumstats.Rmd` in RStudio and knit to produce summary statistics and figures

## Linking HMDA and the UAD PUF

After both datasets are cleaned, run `python src/combined/link_hmda_uad.py`. It joins the two at the census tract x year level (2018-2022) and writes `data/combined/hmda_uad_tract_year.dta`. See the "Linked HMDA-UAD File" section of [`docs/hmda.md`](docs/hmda.md).
