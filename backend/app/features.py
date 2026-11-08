"""Transparent, compact feature extraction for normalized stellar light curves."""
from __future__ import annotations
import numpy as np
from scipy.signal import find_peaks

FEATURE_NAMES = [
    "median_flux", "robust_scatter", "min_flux", "max_flux",
    "estimated_dip_depth", "dip_fraction", "dip_count",
    "periodicity_score", "odd_even_depth_difference",
    "secondary_dip_strength", "signal_to_noise", "flux_skewness",
]

def clean_lightcurve(time, flux):
    t = np.asarray(time, dtype=float)
    f = np.asarray(flux, dtype=float)
    valid = np.isfinite(t) & np.isfinite(f)
    t, f = t[valid], f[valid]
    if len(f) < 40:
        raise ValueError("At least 40 valid time/flux measurements are required.")
    order = np.argsort(t)
    t, f = t[order], f[order]
    # Collapse duplicate timestamps by retaining the first occurrence.
    unique = np.concatenate(([True], np.diff(t) > 0))
    t, f = t[unique], f[unique]
    if len(f) < 40:
        raise ValueError("At least 40 unique time measurements are required.")
    median = np.median(f)
    if not np.isfinite(median) or median == 0:
        raise ValueError("Flux median must be finite and non-zero.")
    f = f / median
    # Clip only extreme numerical outliers; do not flatten or erase transit dips.
    q1, q3 = np.percentile(f, [1, 99])
    f = np.clip(f, q1, q3)
    return t, f

def _periodicity_score(f):
    centered = f - np.median(f)
    centered = centered - np.mean(centered)
    if np.std(centered) < 1e-8:
        return 0.0
    corr = np.correlate(centered, centered, mode="full")[len(centered)-1:]
    corr = corr / max(corr[0], 1e-12)
    # Ignore very short lags; use the strongest later autocorrelation peak.
    if len(corr) < 12:
        return 0.0
    peaks, _ = find_peaks(corr[3:])
    if len(peaks) == 0:
        return float(np.max(corr[3:]))
    return float(np.clip(np.max(corr[peaks + 3]), 0, 1))

def extract_features(time, flux):
    t, f = clean_lightcurve(time, flux)
    med = float(np.median(f))
    mad = float(1.4826 * np.median(np.abs(f - med)) + 1e-9)
    q01, q05, q95, q99 = np.percentile(f, [1, 5, 95, 99])
    baseline = float(np.percentile(f, 90))
    threshold = baseline - max(2.5 * mad, 0.001)
    in_dip = f < threshold
    dip_fraction = float(np.mean(in_dip))
    dip_depth = float(max(0.0, baseline - q01))
    # Count separated low-flux regions as a simple dip proxy.
    transitions = np.diff(np.r_[False, in_dip, False].astype(int))
    dip_count = int(np.sum(transitions == 1))
    # Compare alternating low-flux windows as a rough odd/even diagnostic.
    chunks = np.array_split(f, 8)
    chunk_medians = np.array([np.median(c) for c in chunks if len(c)])
    odd_even = float(abs(np.mean(chunk_medians[::2]) - np.mean(chunk_medians[1::2]))) if len(chunk_medians) > 1 else 0.0
    secondary = float(max(0.0, baseline - q05) / max(dip_depth, 1e-9))
    signal_to_noise = float(dip_depth / mad)
    centered = (f - np.mean(f)) / (np.std(f) + 1e-9)
    skew = float(np.mean(centered ** 3))
    return {
        "median_flux": med,
        "robust_scatter": mad,
        "min_flux": float(np.min(f)),
        "max_flux": float(np.max(f)),
        "estimated_dip_depth": dip_depth,
        "dip_fraction": dip_fraction,
        "dip_count": float(dip_count),
        "periodicity_score": _periodicity_score(f),
        "odd_even_depth_difference": odd_even,
        "secondary_dip_strength": secondary,
        "signal_to_noise": signal_to_noise,
        "flux_skewness": skew,
    }

def resample_sequence(time, flux, length=1024):
    t, f = clean_lightcurve(time, flux)
    grid = np.linspace(t.min(), t.max(), length)
    seq = np.interp(grid, t, f)
    seq = seq - np.median(seq)
    scale = np.std(seq)
    if scale > 1e-8:
        seq = seq / scale
    return seq.astype("float32")
