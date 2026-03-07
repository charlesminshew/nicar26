import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import urllib3
import time

# Suppress SSL warning when verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://www.flycou.com/passenger-load-data/?ParamYear={year}"
YEARS = range(2002, 2025)

MONTHS = {
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
}

def clean_int(value):
    value = value.strip().replace(",", "")
    return int(value) if value else None

def clean_pct(value):
    value = value.strip().replace("%", "").replace(",", "")
    return float(value) if value else None

rows_out = []

for year in YEARS:
    url = BASE_URL.format(year=year)
    print(f"Scraping {year}: {url}")

    resp = requests.get(url, verify=False, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.select_one("table.passengerdata")

    if table is None:
        print(f"No table found for {year}")
        continue

    for tr in table.select("tr"):
        cells = tr.find_all(["td", "th"])
        if len(cells) < 5:
            continue

        first_cell = cells[0].get_text(strip=True)

        if first_cell not in MONTHS:
            continue

        row = {
            "year": year,
            "month": first_cell,
            "enplanements": clean_int(cells[1].get_text()),
            "deplanements": clean_int(cells[2].get_text()),
            "monthly_total": clean_int(cells[3].get_text()),
            "pct_change_previous_year": clean_pct(cells[4].get_text())
        }

        rows_out.append(row)

    # Wait 2 seconds before scraping the next year
    time.sleep(2)

df = pd.DataFrame(rows_out)

month_order = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)
df = df.sort_values(["year","month"])

Path("data").mkdir(exist_ok=True)
df.to_csv("data/flycou_passenger_load.csv", index=False)

print("Saved:", len(df), "rows")