"""Human-readable evidence summaries based on measured light-curve features."""
def build_evidence(features: dict[str, float], category: str):
    evidence = []
    depth = features["estimated_dip_depth"]
    scatter = features["robust_scatter"]
    periodicity = features["periodicity_score"]
    snr = features["signal_to_noise"]
    dip_fraction = features["dip_fraction"]
    odd_even = features["odd_even_depth_difference"]

    evidence.append({
        "title": "Transit-like brightness decrease",
        "detail": f"Estimated lower-tail dip depth is {depth:.4f} relative to normalized flux.",
        "status": "supporting" if depth > 0.003 else "caution"
    })
    evidence.append({
        "title": "Signal repeatability proxy",
        "detail": f"Autocorrelation-based periodicity score is {periodicity:.2f}. This is a rough periodicity indicator, not an orbital-period measurement.",
        "status": "supporting" if periodicity > 0.25 else "caution"
    })
    evidence.append({
        "title": "Signal-to-noise proxy",
        "detail": f"Estimated dip-to-robust-scatter ratio is {snr:.1f}.",
        "status": "supporting" if snr > 3 else "caution"
    })
    evidence.append({
        "title": "Event duration proxy",
        "detail": f"Approximately {dip_fraction * 100:.1f}% of samples fall below the adaptive low-flux threshold.",
        "status": "neutral"
    })
    evidence.append({
        "title": "Odd/even and secondary-event check",
        "detail": f"Alternating-window difference proxy is {odd_even:.4f}; secondary-dip proxy is {features['secondary_dip_strength']:.2f}. These coarse checks can flag signals needing closer inspection.",
        "status": "caution" if odd_even > 0.01 else "neutral"
    })
    if category == "Planet candidate":
        summary = "The model found a signal resembling patterns in the planet-candidate training class. Treat this as a candidate signal for review, not a confirmed planet."
    else:
        summary = "The model found the signal more similar to the false-positive examples in its training data. This does not prove that no planet is present."
    return summary, evidence
