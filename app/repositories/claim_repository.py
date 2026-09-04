"""Database repository boundary; demo repository remains separate and in-memory."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Claim

class ClaimRepository:
    def __init__(self, session: Session): self.session=session
    def get(self, claim_id:str) -> Claim|None:
        claim=self.session.get(Claim,claim_id)
        return claim if claim and claim.is_active else None
    def list(self, *, state:str|None=None, district:str|None=None) -> list[Claim]:
        query=select(Claim).where(Claim.is_active.is_(True))
        if state: query=query.where(Claim.state==state)
        if district: query=query.where(Claim.district==district)
        return list(self.session.scalars(query))
    def add(self, claim:Claim) -> Claim: self.session.add(claim); self.session.flush(); return claim
    def archive(self, claim:Claim) -> None:
        claim.is_active=False
        self.session.flush()
