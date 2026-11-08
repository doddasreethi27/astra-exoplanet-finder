
"""Download the uniformly vetted Kepler Q1-Q17 DR25 KOI catalogue."""

from pathlib import Path
import requests

OUT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "dr25_koi_catalog.csv"
)

URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

QUERY = """
SELECT
    kepid,
    kepoi_name,
    koi_disposition,
    koi_period,
    koi_depth,
    koi_duration,
    koi_model_snr
FROM q1_q17_dr25_koi
"""

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(
        URL,
        params={"query": QUERY, "format": "csv"},
        timeout=120,
    )
    response.raise_for_status()

    OUT.write_bytes(response.content)

    print(f"Saved DR25 catalogue to: {OUT}")
    print(f"File size: {len(response.content):,} bytes")
    print("Next: inspect schema, labels and missing values.")

if __name__ == "__main__":
    main()
