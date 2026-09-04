from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import RedirectResponse # type: ignore

# Import `data_repository` in a way that works both when this module is
# executed as a package (relative import) and when run directly as a script
# (absolute import from the same directory).
try:
    from .data_repository import PROGRESS_FILES, state_records
except Exception:
    # Running as a script: the package-relative import will fail, so fall back
    # to importing the module by name. This makes `python app/main.py` usable
    # when invoked from the project root.
    from data_repository import PROGRESS_FILES, state_records  # type: ignore


app = FastAPI(
    title="FRA Monitoring Decision Support API",
    version="0.1.0",
    description="Read-only, rule-based state-level FRA monitoring API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def records_for_year(year: int) -> list[dict]:
    if year not in PROGRESS_FILES:
        raise HTTPException(status_code=400, detail=f"year must be one of {sorted(PROGRESS_FILES)}")
    return state_records(year)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Send browser visits to the interactive API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "data_years": sorted(PROGRESS_FILES), "scope": "state-level"}


@app.get("/api/v1/states")
def list_states(year: int = Query(2024)) -> dict:
    return {"year": year, "data": records_for_year(year)}


@app.get("/api/v1/states/{state_name}")
def get_state(state_name: str, year: int = Query(2024)) -> dict:
    record = next(
        (item for item in records_for_year(year) if item["state"].casefold() == state_name.casefold()),
        None,
    )
    if record is None:
        raise HTTPException(status_code=404, detail="State not found")
    return record


@app.get("/api/v1/statistics/states")
def state_statistics(year: int = Query(2024)) -> dict:
    records = records_for_year(year)
    claims = sum(item["claims_received"]["total"] for item in records)
    titles = sum(item["titles_distributed"]["total"] for item in records)
    return {
        "year": year,
        "state_count": len(records),
        "claims_received_total": claims,
        "titles_distributed_total": titles,
        "pending_claims_total": max(claims - titles, 0),
        "title_distribution_rate_percent": round((titles / claims) * 100, 2) if claims else None,
    }


@app.get("/api/v1/anomalies")
def anomalies(
    year: int = Query(2024),
    minimum_pending_rate_percent: float = Query(40, ge=0, le=100),
) -> dict:
    findings = []
    for record in records_for_year(year):
        completion_rate = record["title_distribution_rate_percent"]
        pending_rate = 100 - completion_rate if completion_rate is not None else None
        if pending_rate is not None and pending_rate >= minimum_pending_rate_percent:
            findings.append(
                {
                    "rule_id": "HIGH_PENDING_CLAIMS",
                    "severity": "high" if pending_rate >= 60 else "medium",
                    "state": record["state"],
                    "year": year,
                    "pending_claims": record["pending_claims"],
                    "pending_rate_percent": round(pending_rate, 2),
                    "explanation": "Pending-claim rate meets or exceeds the configured threshold.",
                }
            )
    return {
        "year": year,
        "rules": [{"rule_id": "HIGH_PENDING_CLAIMS", "threshold_percent": minimum_pending_rate_percent}],
        "limitations": [
            "Delayed-claim detection needs claim submission and decision dates.",
            "Land-record mismatch detection needs parcel or land-record identifiers and areas.",
        ],
        "data": findings,
    }


@app.get("/api/v1/map/states")
def map_states(year: int = Query(2024)) -> dict:
    return {
        "type": "FeatureCollection",
        "geometry_note": "This source has no boundary geometries. Join features to a frontend state-boundary layer using properties.state.",
        "features": [
            {"type": "Feature", "geometry": None, "properties": record}
            for record in records_for_year(year)
        ],
    }


if __name__ == "__main__":
    try:
        import uvicorn # type: ignore
    except Exception:
        print(
            "uvicorn is not installed. Install it with: pip install uvicorn[standard]"
        )
        print("Then run: uvicorn app.main:app --reload")
    else:
        uvicorn.run(app, host="127.0.0.1", port=8000)
