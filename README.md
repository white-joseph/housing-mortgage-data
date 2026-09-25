# housing-mortgage-data

This repo downloads, cleans, and documents several public housing/mortgage datasets, with the goal of identifying opportunities to link them together.

Datasets covered so far:
- **UAD PUF** (FHFA Uniform Appraisal Dataset, Appraisal-Level Public Use File)

## Repo structure

```
├── data/                # gitignored
│   ├── raw/             # as downloaded, untouched
│   └── clean/           # cleaned outputs
├── docs/                # dataset documentation 
├── src/                 # source code for download and cleaning scripts
│   └── uad/
│       ├── download_uad.py
│       └── clean_uad.py
├── r/                   # summary statistics and figures
├── outputs/             # exported tables/figures
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
3. Open `r/uad_puf_sumstats.Rmd` in RStudio and knit to produces summary statistics and figures
