"""Deterministic field-verification task and evidence operations for demo mode."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from ..demo_repository import repo
from . import claim_service, evidence_service

def _claim(claim_id):
    claim=claim_service.get_claim(claim_id)
    if not claim: raise LookupError('Claim not found')
    return claim
def _location(latitude, longitude, fallback=None):
    return {'type':'Point','coordinates':[longitude,latitude]} if latitude is not None and longitude is not None else fallback
def list_for_claim(claim_id): return _claim(claim_id)['field_verification']
def create_task(claim_id, payload):
    claim=_claim(claim_id); now=datetime.now(timezone.utc).isoformat(); location=_location(payload.get('latitude'),payload.get('longitude'),payload.get('location'))
    task={'verification_id':str(uuid4()),'claim_id':claim_id,'assigned_to':payload['assigned_to'],'status':payload.get('status','PENDING'),'reason':payload.get('reason','Evidence requires verification.'),'location':location,'latitude':payload.get('latitude'),'longitude':payload.get('longitude'),'scheduled_at':payload.get('scheduled_at').isoformat() if payload.get('scheduled_at') else None,'created_at':now,'updated_at':now,'observation':payload.get('observation',''),'result':payload.get('result'),'photos':payload.get('photos',[]),'notes':payload.get('notes',''),'data_label':'SYNTHETIC DEMO DATA'}
    claim['field_verification'].append(task); claim['verification_status']=task['status']; return task
def get_task(claim_id, verification_id):
    _claim(claim_id); task=next((item for item in repo.get(claim_id)['field_verification'] if item['verification_id']==verification_id),None)
    if not task: raise LookupError('Field verification not found')
    return task
def update_task(claim_id, verification_id, changes):
    task=get_task(claim_id,verification_id); task.update({key:value for key,value in changes.items() if value is not None}); task['updated_at']=datetime.now(timezone.utc).isoformat(); repo.get(claim_id)['verification_status']=task['status']; return task
def submit_evidence(claim_id, verification_id, payload):
    task=get_task(claim_id,verification_id); location=_location(payload.get('latitude'),payload.get('longitude'))
    item=evidence_service.create({'claim_id':claim_id,'evidence_type':payload['evidence_type'],'title':f"Field evidence for {verification_id}",'description':payload['observation'],'source':'FIELD_VERIFICATION_DEMO','captured_at':payload['captured_at'],'location':location,'visibility':'AUTHORIZED','verification_status':'UNVERIFIED','metadata':{'verification_id':verification_id,'photo_reference':payload.get('photo_reference'),'photo_metadata':payload.get('photo_metadata',{}),'latitude':payload.get('latitude'),'longitude':payload.get('longitude'),'notes':payload.get('notes',''),'submitted_by':payload['submitted_by'],'data_label':'SYNTHETIC DEMO DATA'}})
    task['status']='SUBMITTED'; task['observation']=payload['observation']; task['updated_at']=datetime.now(timezone.utc).isoformat(); return item
