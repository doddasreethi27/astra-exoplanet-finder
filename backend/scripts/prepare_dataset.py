"""Combine curated per-target files into the labelled training table.

Expected inputs:
  data/raw/lightcurves/kic_<target_id>.csv
  data/raw/labels.csv with columns target_id,label (PC or FP)

The labels file should be curated from a documented catalogue snapshot.
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
CURVES = BASE / "data" / "raw" / "lightcurves"
LABELS = BASE / "data" / "raw" / "labels.csv"
OUT = BASE / "data" / "processed" / "lightcurves.csv"

def main():
    if not LABELS.exists():
        raise SystemExit(f"Create {LABELS} with columns target_id,label (PC or FP).")
    labels = pd.read_csv(LABELS, dtype={"target_id": str})
    labels["label"] = labels["label"].str.upper().str.strip()
    labels = labels[labels["label"].isin(["PC", "FP"])]
    rows = []
    for row in labels.itertuples(index=False):
        path = CURVES / f"kic_{row.target_id}.csv"
        if not path.exists():
            print(f"Missing light curve for {row.target_id}; skipped")
            continue
        curve = pd.read_csv(path)
        curve["target_id"] = str(row.target_id)
        curve["label"] = row.label
        rows.append(curve[["target_id", "time", "flux", "label"]])
    if not rows:
        raise SystemExit("No labelled light curves found.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.concat(rows, ignore_index=True).to_csv(OUT, index=False)
    print(f"Saved {sum(map(len, rows))} observations for {len(rows)} targets to {OUT}")

if __name__ == "__main__":
    main()
