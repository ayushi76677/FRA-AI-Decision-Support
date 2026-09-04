"""Persistence operations for chronological case events."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import CaseTimelineEvent

class TimelineRepository:
    def __init__(self,session:Session): self.session=session
    def create(self,event:CaseTimelineEvent): self.session.add(event); self.session.flush(); return event
    def get_by_id(self,event_id:str): return self.session.get(CaseTimelineEvent,event_id)
    def list_by_claim(self,claim_id:str): return list(self.session.scalars(select(CaseTimelineEvent).where(CaseTimelineEvent.claim_id==claim_id).order_by(CaseTimelineEvent.event_time,CaseTimelineEvent.created_at,CaseTimelineEvent.event_id)))
    def update(self,event:CaseTimelineEvent,changes:dict):
        for field,value in changes.items(): setattr(event,field,value)
        self.session.flush(); return event
