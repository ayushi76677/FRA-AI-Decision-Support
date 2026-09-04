from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"
PROGRESS_FILES = {
    2022: DATA_DIRECTORY / "fra_state_progress_2022.csv",
    2024: DATA_DIRECTORY / "fra_state_progress_2024.csv",
}
LAND_USE_FILE = DATA_DIRECTORY / "states_land_use_pattern.csv"


def _as_int(value: str) -> int:
    if value is None:
        return 0
    v = value.replace(",", "").strip()
    if v == "" or v.upper() == "NA":
        return 0
    return int(v)


def _progress_field(row: dict[str, str], suffix: str) -> int:
    field_name = next(name for name in row if name.endswith(suffix))
    return _as_int(row[field_name])


@lru_cache
def load_progress(year: int) -> list[dict[str, Any]]:
    if year not in PROGRESS_FILES:
        raise ValueError(f"Unsupported year: {year}")

    with PROGRESS_FILES[year].open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    state_field = "State" if "State" in rows[0] else "States"
    records = []
    for row in rows:
        state = row[state_field].strip()
        if state.casefold() == "total":
            continue

        # Find the specific columns for claims and titles to avoid relying on column order
        def _find(col_contains: str, suffix: str) -> str:
            return next(name for name in row if col_contains in name and name.endswith(suffix))

        claims_ind_key = _find("Claims Received", "- Individual")
        claims_comm_key = _find("Claims Received", "- Community")
        claims_total_key = _find("Claims Received", "- Total")

        titles_ind_key = _find("Titles Distributed", "- Individual")
        titles_comm_key = _find("Titles Distributed", "- Community")
        titles_total_key = _find("Titles Distributed", "- Total")

        claims_ind = _as_int(row[claims_ind_key])
        claims_comm = _as_int(row[claims_comm_key])
        claims_total = _as_int(row[claims_total_key])

        titles_ind = _as_int(row[titles_ind_key])
        titles_comm = _as_int(row[titles_comm_key])
        titles_total = _as_int(row[titles_total_key])

        records.append(
            {
                "state": state,
                "year": year,
                "claims_received": {
                    "individual": claims_ind,
                    "community": claims_comm,
                    "total": claims_total,
                },
                "titles_distributed": {
                    "individual": titles_ind,
                    "community": titles_comm,
                    "total": titles_total,
                },
            }
        )
    return records


@lru_cache
def load_land_use() -> dict[str, dict[str, float | None]]:
    with LAND_USE_FILE.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    records: dict[str, dict[str, float | None]] = {}
    for row in rows:
        if row["Category"].strip() != "Percentage to Geographical Area":
            continue
        state = row["States/UTs"].strip()
        if state.casefold() == "all india":
            continue
        forest_value = row["Forests"].strip()
        records[state] = {
            "forest_area_percent": None if forest_value == "NA" else float(forest_value),
        }
    return records


def state_records(year: int) -> list[dict[str, Any]]:
    land_use = load_land_use()
    records = []
    for record in load_progress(year):
        claims_total = record["claims_received"]["total"]
        titles_total = record["titles_distributed"]["total"]
        completion_rate = round((titles_total / claims_total) * 100, 2) if claims_total else None
        pending_claims = max(claims_total - titles_total, 0)
        records.append(
            {
                **record,
                "pending_claims": pending_claims,
                "title_distribution_rate_percent": completion_rate,
                "land_use": land_use.get(record["state"], {"forest_area_percent": None}),
            }
        )
    return records
