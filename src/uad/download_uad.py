from pyprojroot.here import here
import requests
import zipfile
import io
import pandas as pd

# Create necessary folders

paths = (here("data"), here("data/clean"), here("data/raw"), here("data/raw/uad"))

for path in paths:
    path.mkdir(parents=True, exist_ok=True)

# URL's
enterprise_url = "https://www.fhfa.gov/document/d/uad-al/ent_uad_puf_combined_csv_v2_1.zip" # currently version 2.1
fha_url = "https://www.fhfa.gov/document/d/uad-al/fha_uad_puf_combined_v1_0_csv.zip" # currently version 1.0

# Load Enterprise Uniform Appraisal Dataset (UAD) Appraisal-Level Public Use File (PUF)

ent_response = requests.get(enterprise_url)
ent_response.raise_for_status()

df_enterprise = pd.read_csv(io.BytesIO(ent_response.content), compression = 'zip')

# Load FHA Uniform Appraisal Dataset (UAD) Appraisal-Level Public Use File (PUF)

fha_response = requests.get(fha_url)
fha_response.raise_for_status()

df_fha = pd.read_csv(io.BytesIO(fha_response.content), compression = 'zip')

# Save locally

df_enterprise.to_csv(here("data/raw/uad/enterprise_uad.csv"), index=False)
print(f"Saving Enterprise UAD PUF to {here("data/raw/uad/enterprise_uad.csv")}")
df_fha.to_csv(here("data/raw/uad/fha_uad.csv"), index=False)
print(f"Saving FAH UAD PUF to {here("data/raw/uad/fha_uad.csv")}")

print(f"Done.")