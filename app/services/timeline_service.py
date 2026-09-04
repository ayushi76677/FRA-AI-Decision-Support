"""Chronological timeline operations with optional evidence association."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from ..config import settings
from ..demo_repository import repo
from ..models import CaseTimelineEvent
from ..repositories.timeline_repository import TimelineRepository
from . import claim_service, evidence_service

def _normalise(event):
    result=dict(event); result['event_time']=result.get('event_time',result.get('timestamp')); result.setdefault('title',result['event_type'].replace('_',' ').title()); result.setdefault('evidence_id',None); result.setdefault('created_at',result.get('timestamp')); return result
def _sql(event): return {'event_id':event.event_id,'claim_id':event.claim_id,'event_type':event.event_type,'title':event.title,'description':event.description,'event_time':event.event_time,'source':event.source,'evidence_id':event.evidence_id,'metadata':event.metadata_json,'created_at':event.created_at}
def _require_claim(claim_id):
    if not claim_service.get_claim(claim_id): raise LookupError('Claim not found')
def create(payload):
    _require_claim(payload['claim_id'])
    if payload.get('evidence_id'):
        evidence=evidence_service.get(payload['evidence_id'],include_restricted=True)
        if not evidence or evidence['claim_id']!=payload['claim_id']: raise LookupError('Evidence not found for claim')
    if settings.database_mode=='demo':
        now=datetime.now(timezone.utc).isoformat(); event={**payload,'event_id':str(uuid4()),'created_at':now,'timestamp':payload['event_time'].isoformat()}; repo.get(payload['claim_id'])['timeline'].append(event); return _normalise(event)
    with claim_service._session() as session:
        event=TimelineRepository(session).create(CaseTimelineEvent(**{**payload,'metadata_json':payload.pop('metadata')})); session.commit(); session.refresh(event); return _sql(event)
def get(event_id):
    if settings.database_mode=='demo':
        event=next((e for c in repo.list() for e in c['timeline'] if e['event_id']==event_id),None); return _normalise(event) if event else None
    with claim_service._session() as session:
        event=TimelineRepository(session).get_by_id(event_id); return _sql(event) if event else None
def list_for_claim(claim_id,*,page=1,page_size=20):
    _require_claim(claim_id)
    if settings.database_mode=='demo': rows=[_normalise(e) for e in repo.get(claim_id)['timeline']]
    else:
        with claim_service._session() as session: rows=[_sql(e) for e in TimelineRepository(session).list_by_claim(claim_id)]
    rows.sort(key=lambda e:(str(e['event_time']),str(e.get('created_at','')),e['event_id']))
    total=len(rows); start=(page-1)*page_size
    return {'items':rows[start:start+page_size],'page':page,'page_size':page_size,'total':total}
