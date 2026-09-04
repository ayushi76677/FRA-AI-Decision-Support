"""Evidence business rules and demo-mode storage adapter."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from ..config import settings
from ..demo_repository import repo
from ..models import EvidenceItem
from ..repositories.evidence_repository import EvidenceRepository
from ..repositories.claim_repository import ClaimRepository
from . import claim_service

PUBLIC_VISIBILITIES={'PUBLIC','AUTHORIZED'}

def _now(): return datetime.now(timezone.utc).isoformat()
def _demo_response(item):
    result=dict(item)
    result.setdefault('created_at',result.get('uploaded_at'))
    result.setdefault('updated_at',result.get('created_at'))
    return result
def _sql_response(item):
    return {'evidence_id':item.evidence_id,'claim_id':item.claim_id,'evidence_type':item.evidence_type,'title':item.title,'description':item.description,'source':item.source,'captured_at':item.captured_at,'uploaded_at':item.uploaded_at,'location':item.location,'visibility':item.visibility,'verification_status':item.verification_status,'provenance_id':item.provenance_id,'metadata':item.metadata_json,'created_at':item.created_at,'updated_at':item.updated_at}
def _session(): return claim_service._session()
def _require_claim(claim_id):
    claim=claim_service.get_claim(claim_id)
    if not claim: raise LookupError('Claim not found')
    return claim
def calculate_completeness(claim_id):
    """A transparent record-count indicator, not a legal or eligibility assessment."""
    if settings.database_mode=='demo':
        claim=repo.get(claim_id); claim['evidence_completeness']=min(100,len(claim['evidence'])*20); return claim['evidence_completeness']
    with _session() as session:
        claim=ClaimRepository(session).get(claim_id)
        count=len(EvidenceRepository(session).list_by_claim(claim_id))
        claim.evidence_completeness=min(100,count*20); session.commit(); return claim.evidence_completeness
def create(payload):
    _require_claim(payload['claim_id'])
    if settings.database_mode=='demo':
        now=_now(); item={**payload,'evidence_id':str(uuid4()),'uploaded_at':now,'created_at':now,'updated_at':now}; repo.get(payload['claim_id'])['evidence'].append(item); calculate_completeness(payload['claim_id']); return _demo_response(item)
    with _session() as session:
        item=EvidenceRepository(session).create(EvidenceItem(**{**payload,'metadata_json':payload.pop('metadata')})); session.commit(); session.refresh(item); calculate_completeness(payload['claim_id']); return _sql_response(item)
def get(evidence_id,*,include_restricted=False):
    if settings.database_mode=='demo':
        item=next((e for c in repo.list() for e in c['evidence'] if e['evidence_id']==evidence_id),None)
        result=_demo_response(item) if item else None
    else:
        with _session() as session:
            item=EvidenceRepository(session).get_by_id(evidence_id); result=_sql_response(item) if item else None
    if result and result['visibility'] not in PUBLIC_VISIBILITIES and not include_restricted: return None
    return result
def list_for_claim(claim_id,*,evidence_type=None,verification_status=None,visibility=None,include_restricted=False,page=1,page_size=20):
    _require_claim(claim_id)
    if visibility in {'RESTRICTED','SENSITIVE'} and not include_restricted: return {'items':[],'page':page,'page_size':page_size,'total':0}
    if settings.database_mode=='demo': rows=[_demo_response(e) for e in repo.get(claim_id)['evidence']]
    else:
        with _session() as session: rows=[_sql_response(e) for e in EvidenceRepository(session).list_by_claim(claim_id,evidence_type=evidence_type,verification_status=verification_status,visibility=visibility)]
    if settings.database_mode=='demo':
        for field,value in {'evidence_type':evidence_type,'verification_status':verification_status,'visibility':visibility}.items():
            if value: rows=[row for row in rows if row[field]==value]
    if not include_restricted: rows=[row for row in rows if row['visibility'] in PUBLIC_VISIBILITIES]
    total=len(rows); start=(page-1)*page_size
    return {'items':rows[start:start+page_size],'page':page,'page_size':page_size,'total':total}
def update(evidence_id,changes,*,include_restricted=False):
    item=get(evidence_id,include_restricted=include_restricted)
    if not item: return None
    if settings.database_mode=='demo':
        raw=next(e for c in repo.list() for e in c['evidence'] if e['evidence_id']==evidence_id); raw.update(changes); raw['updated_at']=_now(); calculate_completeness(raw['claim_id']); return _demo_response(raw)
    with _session() as session:
        raw=EvidenceRepository(session).get_by_id(evidence_id); fields={('metadata_json' if k=='metadata' else k):v for k,v in changes.items()}; EvidenceRepository(session).update(raw,fields); session.commit(); session.refresh(raw); return _sql_response(raw)
