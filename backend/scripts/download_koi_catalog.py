"""Download a Kepler Objects of Interest catalogue snapshot from NASA Exoplanet Archive TAP."""
from pathlib import Path
import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "koi_catalog.csv"
URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
QUERY = "select kepid,kepoi_name,kepler_name,koi_disposition,koi_period,koi_depth,koi_duration,koi_prad,koi_model_snr from cumulative"

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL, params={"query": QUERY, "format": "csv"}, timeout=120)
    response.raise_for_status()
    OUT.write_bytes(response.content)
    print(f"Saved catalogue snapshot to {OUT} ({len(response.content):,} bytes)")
    print("Check the archive's current table schema and disposition definitions before research use.")

if __name__ == "__main__":
    main()
