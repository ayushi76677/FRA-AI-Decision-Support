"""Persistence operations for evidence; no FastAPI concerns live here."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import EvidenceItem

class EvidenceRepository:
    def __init__(self,session:Session): self.session=session
    def create(self,item:EvidenceItem): self.session.add(item); self.session.flush(); return item
    def get_by_id(self,evidence_id:str): return self.session.get(EvidenceItem,evidence_id)
    def list_by_claim(self,claim_id:str,**filters):
        query=select(EvidenceItem).where(EvidenceItem.claim_id==claim_id)
        for field,value in filters.items():
            if value is not None: query=query.where(getattr(EvidenceItem,field)==value)
        return list(self.session.scalars(query.order_by(EvidenceItem.created_at,EvidenceItem.evidence_id)))
    def update(self,item:EvidenceItem,changes:dict):
        for field,value in changes.items(): setattr(item,field,value)
        self.session.flush(); return item
