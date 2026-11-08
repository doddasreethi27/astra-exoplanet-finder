
"""Prepare the Kepler DR25 KOI catalogue for a baseline classifier."""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT = BASE_DIR / "data" / "raw" / "dr25_koi_catalog.csv"
OUTPUT = BASE_DIR / "data" / "processed" / "dr25_training_data.csv"

FEATURES = [
    "koi_period",
    "koi_depth",
    "koi_duration",
    "koi_model_snr",
]

def main():
    df = pd.read_csv(INPUT)

    # Keep only the dispositions used in this binary experiment.
    df = df[df["koi_disposition"].isin(
        ["CONFIRMED", "CANDIDATE", "FALSE POSITIVE"]
    )].copy()

    # Create the binary target.
    df["target"] = (
        df["koi_disposition"].isin(["CONFIRMED", "CANDIDATE"])
    ).astype(int)

    # Remove rows missing any required model feature.
    df = df.dropna(subset=FEATURES + ["kepid"])

    # Retain the target-star ID for grouped train/test splitting.
    output_columns = ["kepid"] + FEATURES + ["koi_disposition", "target"]
    df = df[output_columns]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print("Prepared DR25 training dataset.")
    print("Output:", OUTPUT)
    print("Shape:", df.shape)
    print("\nTarget distribution:")
    print(df["target"].value_counts().sort_index())
    print("\nOriginal dispositions:")
    print(df["koi_disposition"].value_counts())

if __name__ == "__main__":
    main()
