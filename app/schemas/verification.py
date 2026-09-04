from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator

VerificationStatus=Literal['PENDING','ASSIGNED','IN_PROGRESS','SUBMITTED','REQUIRES_FURTHER_VERIFICATION','COMPLETED']
VerificationResult=Literal['CHANGE_CONFIRMED','CHANGE_NOT_CONFIRMED','FURTHER_VERIFICATION_REQUIRED','INCONCLUSIVE']

class FieldVerificationCreate(BaseModel):
    assigned_to:str=Field(min_length=1)
    status:VerificationStatus='PENDING'
    reason:str='Evidence requires verification.'
    location:dict|None=None
    latitude:float|None=None
    longitude:float|None=None
    scheduled_at:datetime|None=None
    observation:str=''
    result:VerificationResult|None=None
    photos:list[dict]=Field(default_factory=list)
    notes:str=''
    @field_validator('latitude')
    @classmethod
    def valid_latitude(cls,value):
        if value is not None and not -90<=value<=90: raise ValueError('latitude must be between -90 and 90')
        return value
    @field_validator('longitude')
    @classmethod
    def valid_longitude(cls,value):
        if value is not None and not -180<=value<=180: raise ValueError('longitude must be between -180 and 180')
        return value

class FieldEvidenceCreate(BaseModel):
    evidence_type:Literal['FIELD_PHOTO','FIELD_OBSERVATION','GPS','VERIFICATION_REPORT']
    photo_reference:str|None=None
    photo_metadata:dict=Field(default_factory=dict)
    latitude:float|None=None
    longitude:float|None=None
    captured_at:datetime
    observation:str=Field(min_length=1)
    notes:str=''
    submitted_by:str=Field(min_length=1)
    @field_validator('latitude')
    @classmethod
    def evidence_latitude(cls,value):
        if value is not None and not -90<=value<=90: raise ValueError('latitude must be between -90 and 90')
        return value
    @field_validator('longitude')
    @classmethod
    def evidence_longitude(cls,value):
        if value is not None and not -180<=value<=180: raise ValueError('longitude must be between -180 and 180')
        return value

class FieldVerificationUpdate(BaseModel):
    status:VerificationStatus|None=None
    observation:str|None=None
    result:VerificationResult|None=None
    notes:str|None=None
