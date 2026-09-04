from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

EvidenceType=Literal['DOCUMENT','SATELLITE','GIS','FIELD_PHOTO','FIELD_OBSERVATION','GPS','COMMUNITY','VERIFICATION_REPORT','WORKFLOW_RECORD','OTHER']
EvidenceVisibility=Literal['PUBLIC','AUTHORIZED','RESTRICTED','SENSITIVE']
EvidenceVerificationStatus=Literal['UNVERIFIED','REVIEWED','HUMAN_VERIFIED','CONTESTED']

class EvidenceCreate(BaseModel):
    claim_id:str=Field(min_length=1,max_length=64)
    evidence_type:EvidenceType
    title:str=Field(min_length=1,max_length=256)
    description:str=''
    source:str=Field(default='USER_SUBMITTED',min_length=1,max_length=128)
    captured_at:datetime|None=None
    location:dict[str,Any]|None=None
    visibility:EvidenceVisibility='AUTHORIZED'
    verification_status:EvidenceVerificationStatus='UNVERIFIED'
    provenance_id:str|None=None
    metadata:dict[str,Any]=Field(default_factory=dict)

class EvidenceUpdate(BaseModel):
    evidence_type:EvidenceType|None=None
    title:str|None=Field(default=None,min_length=1,max_length=256)
    description:str|None=None
    source:str|None=Field(default=None,min_length=1,max_length=128)
    captured_at:datetime|None=None
    location:dict[str,Any]|None=None
    visibility:EvidenceVisibility|None=None
    verification_status:EvidenceVerificationStatus|None=None
    provenance_id:str|None=None
    metadata:dict[str,Any]|None=None

class EvidenceResponse(EvidenceCreate):
    evidence_id:str
    uploaded_at:datetime
    created_at:datetime
    updated_at:datetime

class EvidencePage(BaseModel):
    items:list[EvidenceResponse]
    page:int
    page_size:int
    total:int

# Kept as a compatibility alias for earlier callers.
EvidenceRead=EvidenceResponse
