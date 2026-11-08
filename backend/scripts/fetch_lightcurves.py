"""Fetch a small set of Kepler light curves with Lightkurve."""
import argparse
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "data" / "raw" / "lightcurves"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-ids", nargs="+", required=True, help="Kepler Input Catalog IDs")
    args = parser.parse_args()
    try:
        import lightkurve as lk
    except ImportError:
        raise SystemExit("Install Lightkurve first: pip install lightkurve")
    OUT.mkdir(parents=True, exist_ok=True)
    for target in args.target_ids:
        try:
            search = lk.search_lightcurve(f"KIC {target}", mission="Kepler", author="Kepler")
            if len(search) == 0:
                print(f"No Kepler light curve found for KIC {target}")
                continue
            collection = search.download_all()
            if collection is None or len(collection) == 0:
                print(f"Download returned no data for KIC {target}")
                continue
            curve = collection.stitch().remove_nans()
            # Use PDCSAP flux where available; normalize before saving.
            normalized = curve.normalize()
            frame = pd.DataFrame({
                "time": normalized.time.value,
                "flux": normalized.flux.value
            }).dropna()
            destination = OUT / f"kic_{target}.csv"
            frame.to_csv(destination, index=False)
            print(f"Saved {len(frame)} points: {destination}")
        except Exception as exc:
            print(f"Skipped KIC {target}: {exc}")

if __name__ == "__main__":
    main()
