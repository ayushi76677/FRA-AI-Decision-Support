from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

TimelineEventType=Literal['APPLICATION_RECEIVED','DOCUMENT_SUBMITTED','DOCUMENT_REVIEWED','SITE_VERIFICATION','COMMITTEE_REVIEW','DECISION','APPEAL','SATELLITE_OBSERVATION','CHANGE_ALERT','FIELD_VERIFICATION','COMMUNITY_REVIEW','CORRECTION','OTHER']

class TimelineEventCreate(BaseModel):
    claim_id:str=Field(min_length=1,max_length=64)
    event_type:TimelineEventType
    title:str=Field(min_length=1,max_length=256)
    description:str=''
    event_time:datetime
    source:str=Field(default='USER_SUBMITTED',min_length=1,max_length=128)
    evidence_id:str|None=None
    metadata:dict[str,Any]=Field(default_factory=dict)

class TimelineEventUpdate(BaseModel):
    event_type:TimelineEventType|None=None
    title:str|None=Field(default=None,min_length=1,max_length=256)
    description:str|None=None
    event_time:datetime|None=None
    source:str|None=Field(default=None,min_length=1,max_length=128)
    evidence_id:str|None=None
    metadata:dict[str,Any]|None=None

class TimelineEventResponse(TimelineEventCreate):
    event_id:str
    created_at:datetime

class TimelinePage(BaseModel):
    items:list[TimelineEventResponse]
    page:int
    page_size:int
    total:int

TimelineEventRead=TimelineEventResponse
