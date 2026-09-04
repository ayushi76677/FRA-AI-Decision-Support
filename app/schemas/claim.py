"""Request and response contracts for the claim domain."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator

ClaimStatus = Literal['PENDING', 'UNDER_REVIEW', 'FIELD_VERIFICATION', 'COMMUNITY_REVIEW', 'VERIFIED', 'COMPLETED']
Priority = Literal['LOW', 'MEDIUM', 'HIGH', 'REQUIRES_VERIFICATION']

def validate_geometry(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None: return value
    if value.get('type') not in {'Polygon', 'MultiPolygon'}: raise ValueError('GeoJSON geometry must be a Polygon or MultiPolygon')
    if not isinstance(value.get('coordinates'), list) or not value['coordinates']: raise ValueError('GeoJSON geometry must include coordinates')
    return value

class ClaimCreate(BaseModel):
    claimant_reference: str = Field(min_length=3,max_length=128)
    claim_type: str = Field(min_length=1,max_length=64)
    village: str = Field(min_length=1,max_length=128)
    gram_panchayat: str = Field(min_length=1,max_length=128)
    district: str = Field(min_length=1,max_length=128)
    state: str = Field(min_length=1,max_length=128)
    area_hectares: float | None = Field(None,ge=0)
    status: ClaimStatus = 'PENDING'
    priority: Priority = 'MEDIUM'
    geometry: dict[str, Any] | None = None
    @field_validator('geometry')
    @classmethod
    def geometry_is_geojson(cls, value): return validate_geometry(value)

class ClaimUpdate(BaseModel):
    claim_type: str | None = Field(None,min_length=1,max_length=64)
    village: str | None = Field(None,min_length=1,max_length=128)
    gram_panchayat: str | None = Field(None,min_length=1,max_length=128)
    district: str | None = Field(None,min_length=1,max_length=128)
    state: str | None = Field(None,min_length=1,max_length=128)
    area_hectares: float | None = Field(None,ge=0)
    status: ClaimStatus | None = None
    priority: Priority | None = None
    verification_status: str | None = Field(None,min_length=1,max_length=64)
    community_review_status: str | None = Field(None,min_length=1,max_length=64)
    geometry: dict[str, Any] | None = None
    @field_validator('geometry')
    @classmethod
    def geometry_is_geojson(cls, value): return validate_geometry(value)

class ClaimRead(ClaimCreate):
    claim_id: str
    verification_status: str
    community_review_status: str
    evidence_completeness: int = Field(ge=0,le=100)
    created_at: datetime
    updated_at: datetime
    data_label: str | None = None

class ClaimPage(BaseModel):
    items: list[dict[str, Any]]
    page: int
    page_size: int
    total: int
