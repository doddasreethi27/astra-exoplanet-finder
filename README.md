# ASTRA — Exoplanet Finder

An end-to-end portfolio project for analysing stellar light curves and classifying transit-like signals.

**Stack:** React + TypeScript + Vite, FastAPI, NumPy, Pandas, scikit-learn, optional TensorFlow/Keras.

> Scientific scope: the application classifies light-curve signals using labels supplied by a training dataset. A model prediction is not an astronomical confirmation. Candidate validation requires independent scientific review and often follow-up observations.

## Features

- Responsive astronomy-inspired React dashboard.
- Upload a CSV light curve (`time,flux`) and analyse it.
- Demo analysis mode, clearly labelled as simulated.
- Feature extraction and evidence-based explanations.
- Random Forest baseline training pipeline.
- Optional 1D CNN training pipeline (TensorFlow).
- Model metrics endpoint and evaluation report.
- NASA KOI catalogue downloader and Lightkurve data-fetch helper.
- Clear separation between raw data, processed data, models and application code.

## Repository layout

```text
astra-exoplanet-finder/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── features.py
│   │   ├── explain.py
│   │   ├── predictor.py
│   │   └── demo.py
│   ├── scripts/
│   │   ├── download_koi_catalog.py
│   │   ├── fetch_lightcurves.py
│   │   ├── prepare_dataset.py
│   │   ├── train_baseline.py
│   │   └── train_cnn.py
│   ├── data/raw/
│   ├── data/processed/
│   ├── models/
│   ├── reports/
│   ├── requirements.txt
│   └── requirements-cnn.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── App.tsx
    │   ├── main.tsx
    │   ├── api.ts
    │   ├── types.ts
    │   └── styles.css
    ├── index.html
    ├── package.json
    └── vite.config.ts
```

## 1. Requirements

- Python 3.10 or 3.11 recommended.
- Node.js 20 or newer.
- npm.
- Git.
- Internet connection for NASA data downloads.

## 2. Start the backend

From the project root:

### Windows PowerShell

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend: http://localhost:8000  
Interactive API docs: http://localhost:8000/docs

### Start the frontend (second terminal)

```powershell
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

The frontend uses the API at `http://localhost:8000`. Override it with `VITE_API_URL` if needed.

## 3. Try the application

The dashboard works in demo mode immediately. Demo outputs are simulated and are never presented as a trained model prediction.

For a real analysis:
1. Open **Analyze**.
2. Upload a CSV with two columns named `time` and `flux`.
3. The backend validates and preprocesses the measurements.
4. If a trained model exists, the API uses it.
5. Otherwise, the API returns a clear "model not trained" response rather than inventing a prediction.

You can download the sample CSV from `backend/data/sample_lightcurve.csv`.

## 4. Real NASA data workflow

### A. Download the KOI catalogue

```powershell
cd backend
python scripts/download_koi_catalog.py
```

This downloads the Kepler Objects of Interest table from the NASA Exoplanet Archive TAP service. The catalogue provides identifiers and dispositions, not the raw light-curve flux time series.

### B. Fetch selected Kepler light curves

Install the optional astronomy package:

```powershell
pip install lightkurve
```

Then fetch a small, curated set of target IDs:

```powershell
python scripts/fetch_lightcurves.py --target-ids 11446443 11904151 10984090
```

The script saves one CSV per target under `data/raw/lightcurves/`. Target availability varies; a missing target is logged and skipped.

### C. Prepare labelled sequences

The training pipeline expects one CSV with columns:

- `target_id`: stable target identifier
- `time`: observation time
- `flux`: measured flux
- `label`: `PC` (planet candidate) or `FP` (false positive)

For a first experiment, manually curate a small set of targets from the downloaded KOI catalogue and matching light curves. Do not assume every KOI has a usable light curve or that the catalogue label is a final scientific truth.

Combine the per-target CSVs into `data/processed/lightcurves.csv` with the four columns above. Keep all observations for a target together. Do not split observations from the same target across train and test.

### D. Train the baseline model

```powershell
python scripts/train_baseline.py --data data/processed/lightcurves.csv
```

This creates:
- `models/random_forest.joblib`
- `models/feature_names.json`
- `reports/baseline_metrics.json`

### E. Train the optional 1D CNN

Install TensorFlow separately:

```powershell
pip install -r requirements-cnn.txt
```

Then:

```powershell
python scripts/train_cnn.py --data data/processed/lightcurves.csv
```

The CNN uses fixed-length normalized light-curve sequences and saves `models/exoplanet_cnn.keras`.

## 5. Dataset and scientific methodology

- NASA Exoplanet Archive: https://exoplanetarchive.ipac.caltech.edu/
- MAST Kepler data: https://archive.stsci.edu/missions-and-data/kepler
- Lightkurve: https://lightkurve.org/
- Kepler mission overview: https://science.nasa.gov/mission/kepler/

The included feature-based explanations describe measurable signal characteristics (e.g. estimated dip depth, variability and periodicity proxy). They are evidence summaries, not causal explanations of the neural network's internal reasoning. For a stronger research extension, add Integrated Gradients or occlusion-based saliency for the 1D CNN.

## 6. Important modelling cautions

- A KOI "planet candidate" is not the same thing as a confirmed exoplanet.
- A classifier trained on PC/FP catalogue labels learns the catalogue's label definitions and selection biases.
- Avoid target leakage: split by `target_id`, not by individual rows or windows.
- Evaluate precision and recall, not accuracy alone.
- Calibrate probabilities before interpreting them as confidence.
- The feature extraction in this starter implementation is a transparent baseline, not a replacement for expert vetting.
- Real-time "NASA discovery" claims are intentionally not made.

## 7. Next portfolio upgrades

1. Add a MAST API search page for target lookup.
2. Add a target metadata panel (stellar parameters and catalogue disposition).
3. Add CNN Integrated Gradients visualizations.
4. Add model versioning and experiment tracking.
5. Add automated tests and CI.
6. Deploy frontend and backend separately.
7. Add an explicit "data provenance" panel with source, cadence, sector/quarter and download timestamp.
