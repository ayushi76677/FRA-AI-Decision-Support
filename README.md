# FRA Evidence Ledger

FastAPI decision-support backend for FRA evidence workflows. It uses deterministic rules only: no LLM, autonomous adjudication, legal conclusions, or claimed scientific accuracy.

## Run in demo mode

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DATABASE_MODE='demo'
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

```powershell
cd frontend
npm install
npm run dev
```

## Public deployment

The Render blueprint builds the frontend and serves it from the same origin as
the FastAPI API. Deploy the `fra-evidence-map` Blueprint in Render first, then
use:

`https://fra-evidence-map.onrender.com`

The public dashboard uses relative `/api/...` requests, so its data is loaded
from that deployed service. For a separately hosted frontend, set
`VITE_API_URL` at build time to the public API origin (without a trailing slash).

The supplied CSVs remain immutable state aggregates. Demo mode contains 20 clearly synthetic, deterministic cases so case, map, evidence, ledger, review, workflow, field, community, sync, and analytics APIs can be exercised without credentials. It does not represent real claims, imagery, or verified observations.

The original frontend is retained through `/api/v1` routes. Set `VITE_API_URL=http://127.0.0.1:8000` if required.

Satellite/change records are labelled `DEMO DATA` and indicate only possible land-cover change requiring human verification. Delay Genome is operational workflow analysis, not a legal-deadline determination. `DATABASE_MODE=postgres` is configured as an environment option, with `DATABASE_URL` reserved for a future PostGIS repository integration.
