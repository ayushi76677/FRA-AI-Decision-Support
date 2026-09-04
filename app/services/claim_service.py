"""Claim-domain operations over the demo repository boundary."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from ..demo_repository import repo
from ..config import settings
from ..database import get_engine
from ..models import Claim
from ..repositories.claim_repository import ClaimRepository
from sqlalchemy.orm import Session

SORTABLE_FIELDS={'claim_id','claimant_reference','claim_type','village','gram_panchayat','district','state','area_hectares','status','priority','verification_status','community_review_status','evidence_completeness','created_at','updated_at'}
def _sql_dict(claim: Claim) -> dict[str, Any]:
    return {field:(getattr(claim,field).isoformat() if field in {'created_at','updated_at'} else getattr(claim,field)) for field in SORTABLE_FIELDS | {'geometry','is_active'}}
def _session() -> Session: return Session(get_engine())
def summary(claim: dict[str, Any] | Claim) -> dict[str, Any]:
    if isinstance(claim, dict): return repo.copy_claim(claim) if settings.database_mode=='demo' else claim
    return _sql_dict(claim)
def get_claim(claim_id: str) -> dict[str, Any] | None:
    if settings.database_mode=='postgres':
        with _session() as session:
            claim=ClaimRepository(session).get(claim_id)
            return _sql_dict(claim) if claim else None
    claim=repo.get(claim_id)
    return claim if claim and claim.get('is_active',True) else None
def list_claims(*,search=None,status=None,district=None,state=None,claim_type=None,priority=None,verification_status=None,community_review_status=None,sort_by='updated_at',sort_order='desc',page=1,page_size=20):
    if settings.database_mode=='postgres':
        with _session() as session: rows=[_sql_dict(row) for row in ClaimRepository(session).list(state=state,district=district)]
    else:
        rows=[claim for claim in repo.list() if claim.get('is_active',True)]
    for field,value in {'status':status,'district':district,'state':state,'claim_type':claim_type,'priority':priority,'verification_status':verification_status,'community_review_status':community_review_status}.items():
        if value: rows=[row for row in rows if str(row.get(field,'')).casefold()==value.casefold()]
    if search:
        fields=('claim_id','claimant_reference','claim_type','village','gram_panchayat','district','state'); needle=search.casefold()
        rows=[row for row in rows if any(needle in str(row.get(field,'')).casefold() for field in fields)]
    field=sort_by if sort_by in SORTABLE_FIELDS else 'updated_at'
    rows.sort(key=lambda row:(row.get(field) is None,str(row.get(field,'')).casefold()),reverse=sort_order=='desc')
    total=len(rows); start=(page-1)*page_size
    return {'items':[summary(row) for row in rows[start:start+page_size]],'page':page,'page_size':page_size,'total':total}
def create_claim(payload: dict[str, Any]) -> dict[str, Any]:
    if settings.database_mode=='postgres':
        with _session() as session:
            claim=Claim(**payload,verification_status='NOT_REQUIRED',community_review_status='NOT_REVIEWED',evidence_completeness=0,is_active=True)
            ClaimRepository(session).add(claim); session.commit(); session.refresh(claim); return _sql_dict(claim)
    numbers=(int(key.rsplit('-',1)[-1]) for key in repo.claims if key.startswith('DEMO-CLAIM-') and key.rsplit('-',1)[-1].isdigit()); claim_id=f'DEMO-CLAIM-{max(numbers,default=0)+1:03d}'; now=datetime.now(timezone.utc).isoformat()
    claim={**payload,'claim_id':claim_id,'case_id':claim_id,'verification_status':'NOT_REQUIRED','community_review_status':'NOT_REVIEWED','evidence_completeness':0,'created_at':now,'updated_at':now,'is_active':True,'data_label':'DEMO DATA','days_since_last_action':0,'timeline':[],'evidence':[],'provenance':[],'change_detection':[],'field_verification':[],'community_reviews':[],'ledger':[],'anomalies':[]}
    repo.claims[claim_id]=claim
    return claim
def update_claim(claim: dict[str, Any],changes:dict[str,Any]) -> dict[str,Any]:
    if settings.database_mode=='postgres':
        with _session() as session:
            stored=ClaimRepository(session).get(claim['claim_id'])
            if stored is None: raise KeyError(claim['claim_id'])
            for key,value in changes.items(): setattr(stored,key,value)
            session.commit(); session.refresh(stored); return _sql_dict(stored)
    claim.update(changes); claim['updated_at']=datetime.now(timezone.utc).isoformat(); return claim
def archive_claim(claim:dict[str,Any]) -> None:
    """Hide rather than destroy an evidence-bearing record."""
    if settings.database_mode=='postgres':
        with _session() as session:
            stored=ClaimRepository(session).get(claim['claim_id'])
            if stored: ClaimRepository(session).archive(stored); session.commit()
    else: claim['is_active']=False; claim['updated_at']=datetime.now(timezone.utc).isoformat()
