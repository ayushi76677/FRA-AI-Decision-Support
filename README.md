# FRA Monitoring Decision Support API

This backend provides read-only, state-level FRA monitoring data from the supplied CSV files. It uses deterministic rules only—no LLM and no predictive model.

## Data

- `data/fra_state_progress_2024.csv`: claims received and titles distributed up to 30 June 2024.
- `data/fra_state_progress_2022.csv`: claims received and titles distributed up to 31 March 2022.
- `data/states_land_use_pattern.csv`: state/UT land-use context, including forest area percentage.

The source data is state-level. It does not contain district boundaries, claim dates, individual claim records, parcel IDs, land-record areas, or geometries. Therefore the API does not infer delayed claims or land-record mismatches.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python start.py
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Endpoints

- `GET /health`
- `GET /api/v1/states?year=2024`
- `GET /api/v1/states/{state_name}?year=2024`
- `GET /api/v1/statistics/states?year=2024`
- `GET /api/v1/anomalies?year=2024&minimum_pending_rate_percent=40`
- `GET /api/v1/map/states?year=2024`

`/api/v1/anomalies` flags `HIGH_PENDING_CLAIMS` when the percentage of claims without distributed titles meets the supplied threshold. It returns a direct explanation and threshold for each finding.

For a district WebGIS view and the remaining FRA anomaly rules, add a dataset with: district/state codes, claim ID, submission and decision dates, claim status, claimed/approved area, parcel/land-record identifiers, and district geometries or a joinable district code.
