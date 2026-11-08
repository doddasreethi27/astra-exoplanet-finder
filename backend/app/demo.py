import numpy as np

def make_demo_curve(seed=14, n=900):
    rng = np.random.default_rng(seed)
    time = np.linspace(0, 18, n)
    flux = 1.0 + rng.normal(0, 0.0018, n)
    # Synthetic recurring transit-like dips. This is deliberately demo data.
    for center in [3.0, 8.0, 13.0]:
        phase = np.abs(time - center)
        dip = phase < 0.16
        shape = np.clip(1 - (phase[dip] / 0.16) ** 2, 0, 1)
        flux[dip] -= 0.012 * shape
    return time, flux
