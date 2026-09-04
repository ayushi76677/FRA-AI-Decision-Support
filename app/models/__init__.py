"""Compact SQLAlchemy domain models for the PostgreSQL/PostGIS repository."""
from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

def uid() -> str: return str(uuid4())
def now() -> datetime: return datetime.utcnow()

class Claim(Base):
    __tablename__='claims'
    claim_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid)
    claimant_reference: Mapped[str]=mapped_column(String(128),index=True)
    claim_type: Mapped[str]=mapped_column(String(32)); village: Mapped[str]=mapped_column(String(128))
    gram_panchayat: Mapped[str]=mapped_column(String(128)); district: Mapped[str]=mapped_column(String(128),index=True); state: Mapped[str]=mapped_column(String(128),index=True)
    area_hectares: Mapped[float|None]=mapped_column(Float,nullable=True); status: Mapped[str]=mapped_column(String(32),index=True); priority: Mapped[str]=mapped_column(String(32),index=True)
    verification_status: Mapped[str]=mapped_column(String(32)); community_review_status: Mapped[str]=mapped_column(String(32)); evidence_completeness: Mapped[int]=mapped_column(Integer,default=0)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now); updated_at: Mapped[datetime]=mapped_column(DateTime,default=now,onupdate=now)
    geometry: Mapped[dict|None]=mapped_column(JSON,nullable=True,comment='EPSG:4326 GeoJSON; replace with GeoAlchemy Geometry in PostGIS deployment')
    is_active: Mapped[bool]=mapped_column(Boolean,default=True,index=True)

class CaseTimelineEvent(Base):
    __tablename__='case_timeline_events'; event_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); event_type: Mapped[str]=mapped_column(String(64)); title: Mapped[str]=mapped_column(String(256)); event_time: Mapped[datetime]=mapped_column(DateTime,index=True); description: Mapped[str]=mapped_column(Text,default=''); source: Mapped[str]=mapped_column(String(128)); evidence_id: Mapped[str|None]=mapped_column(ForeignKey('evidence_items.evidence_id'),nullable=True); metadata_json: Mapped[dict]=mapped_column(JSON,default=dict); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class Document(Base):
    __tablename__='documents'; document_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); title: Mapped[str]=mapped_column(String(256)); document_type: Mapped[str]=mapped_column(String(64)); reference: Mapped[str|None]=mapped_column(String(256)); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class EvidenceItem(Base):
    __tablename__='evidence_items'; evidence_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); evidence_type: Mapped[str]=mapped_column(String(64),index=True); title: Mapped[str]=mapped_column(String(256)); description: Mapped[str]=mapped_column(Text,default=''); source: Mapped[str]=mapped_column(String(128)); captured_at: Mapped[datetime|None]=mapped_column(DateTime,nullable=True); uploaded_at: Mapped[datetime]=mapped_column(DateTime,default=now); location: Mapped[dict|None]=mapped_column(JSON,nullable=True); visibility: Mapped[str]=mapped_column(String(32),default='AUTHORIZED',index=True); verification_status: Mapped[str]=mapped_column(String(32),default='UNVERIFIED',index=True); provenance_id: Mapped[str|None]=mapped_column(String(64),nullable=True); metadata_json: Mapped[dict]=mapped_column(JSON,default=dict); created_at: Mapped[datetime]=mapped_column(DateTime,default=now); updated_at: Mapped[datetime]=mapped_column(DateTime,default=now,onupdate=now)
class SatelliteObservation(Base):
    __tablename__='satellite_observations'; observation_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); source: Mapped[str]=mapped_column(String(128)); observed_at: Mapped[datetime]=mapped_column(DateTime); metadata_json: Mapped[dict]=mapped_column(JSON,default=dict)
class ChangeDetectionResult(Base):
    __tablename__='change_detection_results'; change_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); change_detected: Mapped[bool]=mapped_column(default=False); method: Mapped[str]=mapped_column(String(128)); geometry: Mapped[dict|None]=mapped_column(JSON); limitations: Mapped[str]=mapped_column(Text)
class FieldVerification(Base):
    __tablename__='field_verifications'; verification_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); assigned_to: Mapped[str]=mapped_column(String(128)); result: Mapped[str]=mapped_column(String(64),default='PENDING'); observation: Mapped[str]=mapped_column(Text,default=''); gps_location: Mapped[dict|None]=mapped_column(JSON)
class CommunityReview(Base):
    __tablename__='community_reviews'; review_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); reviewer_role: Mapped[str]=mapped_column(String(64)); action: Mapped[str]=mapped_column(String(64)); statement: Mapped[str]=mapped_column(Text); visibility: Mapped[str]=mapped_column(String(32),default='AUTHORIZED')
class LedgerEvent(Base):
    __tablename__='ledger_events'; ledger_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); timestamp: Mapped[datetime]=mapped_column(DateTime,default=now); event_type: Mapped[str]=mapped_column(String(64)); actor: Mapped[str]=mapped_column(String(128)); description: Mapped[str]=mapped_column(Text); previous_event_hash: Mapped[str|None]=mapped_column(String(128)); event_hash: Mapped[str]=mapped_column(String(128))
class AnomalyRecord(Base):
    __tablename__='anomaly_records'; anomaly_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); anomaly_type: Mapped[str]=mapped_column(String(64)); severity: Mapped[str]=mapped_column(String(32)); reason: Mapped[str]=mapped_column(Text)
class WorkflowEvent(Base):
    __tablename__='workflow_events'; workflow_event_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); stage: Mapped[str]=mapped_column(String(64)); occurred_at: Mapped[datetime]=mapped_column(DateTime,default=now); details: Mapped[dict]=mapped_column(JSON,default=dict)
class ModelRun(Base):
    __tablename__='model_runs'; model_run_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); model_name: Mapped[str]=mapped_column(String(128)); version: Mapped[str]=mapped_column(String(64)); status: Mapped[str]=mapped_column(String(32)); metrics: Mapped[dict|None]=mapped_column(JSON)
class DataProvenance(Base):
    __tablename__='data_provenance'; provenance_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); source: Mapped[str]=mapped_column(String(256)); provider: Mapped[str|None]=mapped_column(String(128)); method: Mapped[str|None]=mapped_column(String(256)); limitations: Mapped[str|None]=mapped_column(Text); details: Mapped[dict]=mapped_column(JSON,default=dict)
class AuditLog(Base):
    __tablename__='audit_logs'; audit_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); actor: Mapped[str]=mapped_column(String(128)); action: Mapped[str]=mapped_column(String(128)); entity: Mapped[str]=mapped_column(String(256)); timestamp: Mapped[datetime]=mapped_column(DateTime,default=now); request_id: Mapped[str]=mapped_column(String(64))
class SyncEvent(Base):
    __tablename__='sync_events'; sync_event_id: Mapped[str]=mapped_column(String(64),primary_key=True,default=uid); local_id: Mapped[str]=mapped_column(String(128),unique=True,index=True); claim_id: Mapped[str]=mapped_column(ForeignKey('claims.claim_id'),index=True); checksum: Mapped[str|None]=mapped_column(String(128)); status: Mapped[str]=mapped_column(String(32)); received_at: Mapped[datetime]=mapped_column(DateTime,default=now)
