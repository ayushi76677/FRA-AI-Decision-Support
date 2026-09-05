from __future__ import annotations
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .config import settings
from .data_repository import PROGRESS_FILES, state_records
from .demo_repository import repo
from .services.spatial_service import area_hectares, distance_m, overlap_percent, geometry_valid, intersects
from .services.review_rules import evaluate
from .services.delay_genome import analyse
from .schemas.claim import ClaimCreate, ClaimUpdate, ClaimPage
from .schemas.evidence import EvidenceCreate, EvidenceUpdate, EvidencePage
from .schemas.timeline import TimelineEventCreate, TimelinePage
from .services import claim_service
from .services.case_service import build_case
from .services import evidence_service, timeline_service
from .services.satellite_change_service import get_change_evidence
from .schemas.verification import FieldVerificationCreate, FieldVerificationUpdate, FieldEvidenceCreate
from .services import field_verification_service

app=FastAPI(title="FRA Evidence Ledger API",version="1.0.0",description="Deterministic FRA evidence decision support. Demo records are synthetic; no LLM runtime.")
app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_origins),allow_methods=["GET","POST","PATCH","DELETE"],allow_headers=["*"])
class EvidenceInput(BaseModel): evidence_type:str; title:str; description:str=""; source:str="USER_SUBMITTED"; captured_at:datetime|None=None; location:dict|None=None; visibility:Literal['PUBLIC','AUTHORIZED','RESTRICTED','SENSITIVE']='AUTHORIZED'; metadata:dict={}
class TimelineInput(BaseModel): event_type:str; timestamp:datetime; stage:str="OTHER"; actor_role:str="AUTHORITY"; description:str; source:str="USER_SUBMITTED"; metadata:dict={}
class LedgerInput(BaseModel): event_type:Literal['CLAIM_APPLICATION','DOCUMENT','TIMELINE_EVENT','SPATIAL_ANALYSIS','SATELLITE_CHANGE','REVIEW_SIGNAL','FIELD_VERIFICATION','FIELD_PHOTO','FIELD_OBSERVATION','COMMUNITY_REVIEW','COMMUNITY_EVIDENCE','STATUS_CHANGE','OTHER']; description:str; evidence_reference:str|None=None; provenance_reference:str|None=None; source:str='SYNTHETIC DEMO DATA'; related_id:str|None=None
class FieldInput(BaseModel): assigned_to:str; scheduled_at:datetime|None=None; gps_location:dict|None=None; photos:list=[]; observation:str=""; result:str="PENDING"; notes:str=""
class CommunityInput(BaseModel): reviewer_role:str="COMMUNITY_REVIEWER"; action:str; statement:str; evidence_reference:str|None=None; visibility:str="AUTHORIZED"
def actor(x): return x or 'VIEWER'
def dump(x): return x.model_dump() if hasattr(x,'model_dump') else x.dict()
def getc(cid):
 c=claim_service.get_claim(cid)
 if not c: raise HTTPException(404,'Claim not found')
 return c
def slim(c): return claim_service.summary(c)
def fc(rows): return {'type':'FeatureCollection','features':rows}
def feature(c,props={}): return {'type':'Feature','geometry':c.get('geometry'),'properties':{**slim(c),**props}}
@app.exception_handler(HTTPException)
async def error(_:Request,e:HTTPException):
 message=str(e.detail)
 code='CLAIM_NOT_FOUND' if e.status_code==404 and message=='Claim not found' else ('NOT_FOUND' if e.status_code==404 else ('FORBIDDEN' if e.status_code==403 else 'VALIDATION_ERROR' if e.status_code==422 else 'REQUEST_ERROR'))
 return JSONResponse(status_code=e.status_code,content={'error':{'code':code,'message':message,'request_id':str(uuid4())}})
FRONTEND_DIST = Path(__file__).resolve().parent.parent / 'frontend' / 'dist'

@app.get('/', include_in_schema=False)
def root():
 if (FRONTEND_DIST / 'index.html').is_file(): return FileResponse(FRONTEND_DIST / 'index.html')
 return RedirectResponse('/docs')
@app.get('/health',tags=['Health'])
def health(): return {'status':'ok','database':settings.database_mode,'version':'1.0.0','environment':settings.app_env,'data_years':sorted(PROGRESS_FILES),'demo_data':settings.database_mode=='demo'}

# Original aggregate API retained for existing frontend compatibility.
def year_records(y):
 if y not in PROGRESS_FILES: raise HTTPException(400,f'year must be one of {sorted(PROGRESS_FILES)}')
 return state_records(y)
@app.get('/api/v1/states',tags=['Legacy state aggregates'])
def states(year:int=2024): return {'year':year,'data':year_records(year)}
@app.get('/api/v1/states/{state_name}',tags=['Legacy state aggregates'])
def state(state_name:str,year:int=2024):
 x=next((r for r in year_records(year) if r['state'].casefold()==state_name.casefold()),None)
 if not x: raise HTTPException(404,'State not found')
 return x
@app.get('/api/v1/statistics/states',tags=['Legacy state aggregates'])
def statistics(year:int=2024):
 r=year_records(year); claims=sum(x['claims_received']['total'] for x in r); titles=sum(x['titles_distributed']['total'] for x in r)
 return {'year':year,'state_count':len(r),'claims_received_total':claims,'titles_distributed_total':titles,'pending_claims_total':max(claims-titles,0),'title_distribution_rate_percent':round(titles/claims*100,2) if claims else None}
@app.get('/api/v1/anomalies',tags=['Legacy state aggregates'])
def state_anomalies(year:int=2024,minimum_pending_rate_percent:float=Query(40,ge=0,le=100)):
 data=[]
 for x in year_records(year):
  pending=100-x['title_distribution_rate_percent'] if x['title_distribution_rate_percent'] is not None else None
  if pending is not None and pending>=minimum_pending_rate_percent:data.append({'rule_id':'HIGH_PENDING_CLAIMS','severity':'high' if pending>=60 else 'medium','state':x['state'],'year':year,'pending_claims':x['pending_claims'],'pending_rate_percent':round(pending,2),'explanation':'Pending-claim rate meets the configured operational threshold.'})
 return {'year':year,'data':data,'limitations':['State aggregates cannot establish individual claim delay or legal findings.']}
@app.get('/api/v1/map/states',tags=['Legacy state aggregates'])
def old_map(year:int=2024): return {'type':'FeatureCollection','geometry_note':'Supplied source has no boundary geometry.','features':[{'type':'Feature','geometry':None,'properties':x} for x in year_records(year)]}

@app.get('/api/claims',tags=['Claims'],response_model=ClaimPage,summary='List claims')
def claims(search:str|None=None,status:str|None=None,district:str|None=None,state:str|None=None,claim_type:str|None=None,priority:str|None=None,verification_status:str|None=None,community_review_status:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),sort_by:str=Query('updated_at',pattern='^(claim_id|claimant_reference|claim_type|village|gram_panchayat|district|state|area_hectares|status|priority|verification_status|community_review_status|evidence_completeness|created_at|updated_at)$'),sort_order:Literal['asc','desc']='desc'):
 return claim_service.list_claims(search=search,status=status,district=district,state=state,claim_type=claim_type,priority=priority,verification_status=verification_status,community_review_status=community_review_status,page=page,page_size=page_size,sort_by=sort_by,sort_order=sort_order)
@app.post('/api/claims',status_code=201,tags=['Claims'],summary='Create a synthetic demo claim')
def create_claim(b:ClaimCreate,x_role:str|None=Header(None)):
 payload=dump(b); payload['area_hectares']=b.area_hectares if b.area_hectares is not None else area_hectares(b.geometry)
 c=claim_service.create_claim(payload)
 if settings.database_mode=='demo': repo.append_ledger(c['claim_id'],{'event_type':'claim submitted','actor':actor(x_role),'evidence_reference':None,'description':'Demo claim created through API.','provenance_reference':None}); repo.log(actor(x_role),'CREATE','Claim:'+c['claim_id'])
 return slim(c)
@app.get('/api/claims/{claim_id}',tags=['Claims'],summary='Get claim detail')
def claim(claim_id:str): return slim(getc(claim_id))
@app.patch('/api/claims/{claim_id}',tags=['Claims'],summary='Update a claim')
def patch_claim(claim_id:str,b:ClaimUpdate,x_role:str|None=Header(None)):
 c=claim_service.update_claim(getc(claim_id),b.model_dump(exclude_unset=True))
 if settings.database_mode=='demo': repo.log(actor(x_role),'UPDATE','Claim:'+claim_id)
 return slim(c)
@app.delete('/api/claims/{claim_id}',status_code=204,tags=['Claims'],summary='Archive a claim without deleting evidence')
def delete_claim(claim_id:str,x_role:str|None=Header(None)):
 claim_service.archive_claim(getc(claim_id))
 if settings.database_mode=='demo': repo.log(actor(x_role),'ARCHIVE','Claim:'+claim_id)

@app.get('/api/cases',tags=['Cases'],summary='List cases')
def cases(search:str|None=None,status:str|None=None,district:str|None=None,priority:str|None=None,verification_status:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),sort_by:str='updated_at',sort_order:Literal['asc','desc']='desc'):
 return claim_service.list_claims(search=search,status=status,district=district,priority=priority,verification_status=verification_status,page=page,page_size=page_size,sort_by=sort_by,sort_order=sort_order)
@app.post('/api/cases',status_code=201,tags=['Cases'],summary='Create a case and its one linked claim')
def create_case(b:ClaimCreate,x_role:str|None=Header(None)): return build_case(create_claim(b,x_role))
@app.get('/api/cases/{case_id}',tags=['Cases'],summary='Get a case by its linked claim identifier')
def case(case_id:str): return build_case(slim(getc(case_id)))
@app.patch('/api/cases/{case_id}',tags=['Cases'])
def patch_case(case_id:str,b:ClaimUpdate,x_role:str|None=Header(None)): return patch_claim(case_id,b,x_role)

@app.get('/api/claims/{claim_id}/timeline',tags=['Timeline'],response_model=TimelinePage,summary='List a claim timeline in chronological order')
def timeline(claim_id:str,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
 try: return timeline_service.list_for_claim(claim_id,page=page,page_size=page_size)
 except LookupError as error: raise HTTPException(404,str(error))
@app.post('/api/claims/{claim_id}/timeline',status_code=201,tags=['Timeline'])
def add_timeline(claim_id:str,b:TimelineInput,x_role:str|None=Header(None)):
 payload={'claim_id':claim_id,'event_type':b.event_type,'title':b.event_type.replace('_',' ').title(),'description':b.description,'event_time':b.timestamp,'source':b.source,'metadata':{**b.metadata,'stage':b.stage,'actor_role':b.actor_role}}
 try: return timeline_service.create(payload)
 except LookupError as error: raise HTTPException(404,str(error))
@app.post('/api/timeline',status_code=201,tags=['Timeline'],summary='Create a timeline event')
def create_timeline(b:TimelineEventCreate):
 try: return timeline_service.create(dump(b))
 except LookupError as error: raise HTTPException(404,str(error))
@app.get('/api/timeline/{event_id}',tags=['Timeline'],summary='Get a timeline event')
def timeline_by_id(event_id:str):
 event=timeline_service.get(event_id)
 if not event: raise HTTPException(404,'Timeline event not found')
 return event
@app.get('/api/claims/{claim_id}/evidence',tags=['Evidence'],response_model=EvidencePage,summary='List evidence for a claim')
def evidence(claim_id:str,evidence_type:str|None=None,verification_status:str|None=None,visibility:str|None=None,include_restricted:bool=False,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
 try: return evidence_service.list_for_claim(claim_id,evidence_type=evidence_type,verification_status=verification_status,visibility=visibility,include_restricted=include_restricted,page=page,page_size=page_size)
 except LookupError as error: raise HTTPException(404,str(error))
@app.post('/api/claims/{claim_id}/evidence',status_code=201,tags=['Evidence'])
def add_evidence(claim_id:str,b:EvidenceInput,x_role:str|None=Header(None)):
 payload=EvidenceCreate(claim_id=claim_id,**dump(b))
 try: return evidence_service.create(dump(payload))
 except LookupError as error: raise HTTPException(404,str(error))
@app.post('/api/evidence',status_code=201,tags=['Evidence'],summary='Create evidence for a claim')
def create_evidence(b:EvidenceCreate):
 try: return evidence_service.create(dump(b))
 except LookupError as error: raise HTTPException(404,str(error))
@app.get('/api/evidence/{evidence_id}',tags=['Evidence'])
def evidence_by_id(evidence_id:str,include_restricted:bool=False):
 item=evidence_service.get(evidence_id,include_restricted=include_restricted)
 if not item: raise HTTPException(404,'Evidence not found or not available at this visibility scope')
 return item
@app.patch('/api/evidence/{evidence_id}',tags=['Evidence'],summary='Update mutable evidence fields')
def patch_evidence(evidence_id:str,b:EvidenceUpdate,include_restricted:bool=False):
 item=evidence_service.update(evidence_id,b.model_dump(exclude_unset=True),include_restricted=include_restricted)
 if not item: raise HTTPException(404,'Evidence not found or not available at this visibility scope')
 return item
@app.get('/api/claims/{claim_id}/ledger',tags=['Ledger'])
def ledger(claim_id:str): return {'data':getc(claim_id)['ledger']}
@app.post('/api/claims/{claim_id}/ledger',status_code=201,tags=['Ledger'])
def add_ledger(claim_id:str,b:LedgerInput,x_role:str|None=Header(None)): getc(claim_id); return repo.append_ledger(claim_id,{**dump(b),'actor':actor(x_role)})

@app.get('/api/claims/{claim_id}/review',tags=['Review'])
@app.get('/api/cases/{claim_id}/review',tags=['Review'])
def review(claim_id:str):
 c=getc(claim_id); return evaluate(c,c['evidence'],c['timeline'],c['anomalies'])
@app.post('/api/claims/{claim_id}/review/recalculate',tags=['Review'])
def recalc(claim_id:str): return review(claim_id)
@app.get('/api/claims/{claim_id}/alert-card',tags=['Satellite'])
def alert(claim_id:str):
 c=getc(claim_id); ch=c['change_detection'][0] if c['change_detection'] else None; result=evaluate(c,c['evidence'],c['timeline'],c['anomalies'])
 return {'claim_id':claim_id,'observation':'DEMO DATA: deterministic possible change observation' if ch else 'No demo change observation.','before':{'date':ch['before_date']} if ch else {},'after':{'date':ch['after_date']} if ch else {},'change':ch or {'change_detected':False},'spatial_extent':ch.get('geometry') if ch else c['geometry'],'review_result':result,'priority':result['priority'],'priority_reason':result['priority_reason'],'signals':result['signals'],'evidence_for':result['evidence_for'],'evidence_against':result['evidence_against'],'limitations':result['limitations'],'recommended_action':result['recommended_next_action'],'provenance':c['provenance'][0] if c['provenance'] else None}
@app.get('/api/claims/{claim_id}/satellite-change',tags=['Satellite'],summary='Get deterministic satellite change evidence')
def satellite_change(claim_id:str):
 if not getc(claim_id): raise HTTPException(404,'Claim not found')
 return get_change_evidence(claim_id)
@app.get('/api/claims/{claim_id}/delay-genome',tags=['Workflow'])
def delay(claim_id:str): return analyse(getc(claim_id)['timeline'])
@app.get('/api/analytics/delay-genome',tags=['Workflow'])
def delay_all(): return {'data':[{'claim_id':c['claim_id'],**analyse(c['timeline'])} for c in repo.list()]}

@app.get('/api/claims/{claim_id}/nearby',tags=['Spatial'])
def nearby(claim_id:str,radius_m:float=Query(2000,gt=0,le=50000)):
 c=getc(claim_id); out=[]
 for o in repo.list():
  if o['claim_id']!=claim_id:
   d=distance_m(c['geometry'],o['geometry'])
   if d is not None and d<=radius_m: out.append({'claim_id':o['claim_id'],'distance_m':d,'overlap_percentage':overlap_percent(c['geometry'],o['geometry']),'status':o['status'],'geometry':o['geometry']})
 return {'data':out}
@app.get('/api/claims/{claim_id}/spatial-analysis',tags=['Spatial'])
def spatial(claim_id:str):
 c=getc(claim_id); geometry=c.get('geometry'); n=nearby(claim_id,50000)['data'] if geometry_valid(geometry) else []; overlap=[x for x in n if x['overlap_percentage']>0]
 change_intersections=[x for x in c['change_detection'] if geometry and x.get('geometry') and intersects(geometry,x['geometry'])]
 forest=repo.forest_boundary if settings.database_mode=='demo' else None; flags=[]
 if geometry_valid(geometry): flags.append({'code':'CLAIM_GEOMETRY_VALID','message':'Synthetic demo claim geometry is valid.','action':'Use as spatial context only.'})
 else: flags.append({'code':'CLAIM_GEOMETRY_UNAVAILABLE','message':'Spatial geometry is unavailable or invalid for this claim.','action':'Add or correct geometry before spatial review.'})
 if n: flags.append({'code':'NEARBY_CLAIM','message':'Nearby demo claim geometry detected.','action':'Spatial relationship requires verification.'})
 if overlap: flags.append({'code':'CLAIM_OVERLAP','message':'Claim geometry overlaps another demo claim.','action':'Requires verification.'})
 if forest and geometry and intersects(geometry,forest): flags.append({'code':'FOREST_BOUNDARY_INTERSECTION','message':'Forest-boundary relationship detected in synthetic demo data.','action':'Requires human review.'})
 if change_intersections: flags.append({'code':'POSSIBLE_CHANGE_INTERSECTION','message':'Possible change area intersects the claim geometry.','action':'Requires verification.'})
 return {'claim_id':claim_id,'geometry':geometry,'area_hectares':area_hectares(geometry),'geometry_valid':geometry_valid(geometry),'forest_boundary':forest,'nearby_claims':n,'overlaps':overlap,'change_intersections':change_intersections,'spatial_flags':flags,'limitations':['Geometry and boundary are synthetic demo data.','Spatial overlap does not establish legal ownership.','Boundary intersection is an observation requiring human review.','Possible change does not establish cause or legality.','Production deployment requires authoritative spatial datasets.']}
@app.get('/api/claims/{claim_id}/field-verification',tags=['Field Verification'])
def field_list(claim_id:str): return {'data':getc(claim_id)['field_verification']}
@app.post('/api/claims/{claim_id}/field-verification/tasks',status_code=201,tags=['Field Verification'],summary='Create a deterministic field verification task')
def field_task_create(claim_id:str,b:FieldVerificationCreate,x_role:str|None=Header(None)):
 try:
  task=field_verification_service.create_task(claim_id,dump(b)); repo.append_ledger(claim_id,{'event_type':'field verification task created','actor':actor(x_role),'evidence_reference':None,'description':task['reason'],'provenance_reference':None}); return task
 except LookupError as error: raise HTTPException(404,str(error))
@app.get('/api/claims/{claim_id}/field-verification/{verification_id}',tags=['Field Verification'])
def field_task(claim_id:str,verification_id:str):
 try: return field_verification_service.get_task(claim_id,verification_id)
 except LookupError as error: raise HTTPException(404,str(error))
@app.patch('/api/claims/{claim_id}/field-verification/{verification_id}/task',tags=['Field Verification'])
def field_task_update(claim_id:str,verification_id:str,b:FieldVerificationUpdate,x_role:str|None=Header(None)):
 try:
  task=field_verification_service.update_task(claim_id,verification_id,b.model_dump(exclude_unset=True)); repo.append_ledger(claim_id,{'event_type':'field verification task updated','actor':actor(x_role),'evidence_reference':None,'description':task.get('observation') or task['status'],'provenance_reference':None}); return task
 except LookupError as error: raise HTTPException(404,str(error))
@app.post('/api/claims/{claim_id}/field-verification/{verification_id}/evidence',status_code=201,tags=['Field Verification'],summary='Submit synthetic field evidence metadata')
def field_evidence(claim_id:str,verification_id:str,b:FieldEvidenceCreate,x_role:str|None=Header(None)):
 try:
  item=field_verification_service.submit_evidence(claim_id,verification_id,dump(b)); repo.append_ledger(claim_id,{'event_type':'field evidence submitted','actor':actor(x_role or b.submitted_by),'evidence_reference':item['evidence_id'],'description':b.observation,'provenance_reference':None}); return item
 except LookupError as error: raise HTTPException(404,str(error))
@app.post('/api/claims/{claim_id}/field-verification',status_code=201,tags=['Field Verification'])
def field_add(claim_id:str,b:FieldInput,x_role:str|None=Header(None)):
 c=getc(claim_id); v={'verification_id':str(uuid4()),'claim_id':claim_id,**dump(b),'scheduled_at':b.scheduled_at.isoformat() if b.scheduled_at else None,'created_at':datetime.now(timezone.utc).isoformat(),'completed_at':None}; c['field_verification'].append(v); c['verification_status']=b.result; repo.append_ledger(claim_id,{'event_type':'field verification','actor':actor(x_role),'evidence_reference':None,'description':b.observation,'provenance_reference':None}); return v
@app.patch('/api/field-verification/{verification_id}',tags=['Field Verification'])
def field_patch(verification_id:str,b:dict):
 for c in repo.list():
  for v in c['field_verification']:
   if v['verification_id']==verification_id:
    v.update(b); v['completed_at']=datetime.now(timezone.utc).isoformat() if b.get('result') not in (None,'PENDING') else v['completed_at']; c['verification_status']=v.get('result',c['verification_status']); return v
 raise HTTPException(404,'Field verification not found')
@app.get('/api/claims/{claim_id}/community-reviews',tags=['Community'])
def community_list(claim_id:str): return {'data':getc(claim_id)['community_reviews']}
@app.post('/api/claims/{claim_id}/community-reviews',status_code=201,tags=['Community'])
def community_add(claim_id:str,b:CommunityInput,x_role:str|None=Header(None)):
 c=getc(claim_id); r={'review_id':str(uuid4()),'claim_id':claim_id,**dump(b),'submitted_at':datetime.now(timezone.utc).isoformat()}; c['community_reviews'].append(r); c['community_review_status']=b.action; repo.append_ledger(claim_id,{'event_type':'community review','actor':actor(x_role),'evidence_reference':b.evidence_reference,'description':b.statement,'provenance_reference':None}); return r

@app.get('/api/map/claims',tags=['Map'])
def map_claims(state:str|None=None): return fc([feature(c) for c in repo.list() if not state or c['state'].casefold()==state.casefold()])
@app.get('/api/map/claims/{claim_id}',tags=['Map'])
def map_claim(claim_id:str): return feature(getc(claim_id))
@app.get('/api/map/change-alerts',tags=['Map'])
def map_changes(): return fc([{'type':'Feature','geometry':x['geometry'],'properties':{k:v for k,v in x.items() if k!='geometry'}} for c in repo.list() for x in c['change_detection']])
@app.get('/api/map/anomalies',tags=['Map'])
def map_anomalies(): return fc([feature(c,{'anomaly_type':'OPERATIONAL_INACTIVITY'}) for c in repo.list() if c['days_since_last_action']>=90])
@app.get('/api/map/field-verification',tags=['Map'])
def map_field(): return fc([{'type':'Feature','geometry':v['gps_location'],'properties':{k:x for k,x in v.items() if k!='gps_location'}} for c in repo.list() for v in c['field_verification'] if v['gps_location']])
@app.get('/api/map/community-evidence',tags=['Map'])
def map_community(): return fc([{'type':'Feature','geometry':c['geometry'],'properties':r} for c in repo.list() for r in c['community_reviews']])
@app.get('/api/map/forest-boundary',tags=['Map'])
def map_forest():
 if settings.database_mode!='demo': return fc([])
 return fc([{'type':'Feature','geometry':repo.forest_boundary,'properties':{'layer':'Forest Boundary','data_label':'DEMO DATA','name':repo.forest_boundary['name']}}])
@app.get('/api/map/lulc',tags=['Map'])
def map_lulc(): return fc([])

@app.get('/api/analytics/overview',tags=['Analytics'])
def overview():
 rows=repo.list(); return {'total_claims':len(rows),'by_status':{s:sum(x['status']==s for x in rows) for s in sorted({x['status'] for x in rows})},'priority_review_count':sum(x['priority'] in ('HIGH','REQUIRES_VERIFICATION') for x in rows),'possible_change_alerts':sum(bool(x['change_detection']) for x in rows),'demo_data':True}
@app.get('/api/analytics/status',tags=['Analytics'])
def analytics_status(): return overview()['by_status']
@app.get('/api/analytics/priorities',tags=['Analytics'])
def priorities(): return {'data':[slim(x) for x in repo.list() if x['priority'] in ('HIGH','REQUIRES_VERIFICATION')]}
@app.get('/api/analytics/satellite-alerts',tags=['Analytics'])
def satellite_analytics(): return {'data':[x for c in repo.list() for x in c['change_detection']],'limitations':['DEMO DATA only.']}
@app.get('/api/analytics/verification',tags=['Analytics'])
def verification_analytics(): return {'data':[x for c in repo.list() for x in c['field_verification']]}
@app.get('/api/analytics/community-review',tags=['Analytics'])
def community_analytics(): return {'data':[x for c in repo.list() for x in c['community_reviews']]}
@app.get('/api/analytics/anomalies',tags=['Analytics'])
def anomalies(): return {'data':[{'claim_id':c['claim_id'],'anomaly_type':'OPERATIONAL_INACTIVITY','severity':'MEDIUM','reason':'Operational inactivity detected.','evidence':['days_since_last_action'], 'limitations':['Not a legal deadline determination.']} for c in repo.list() if c['days_since_last_action']>=90]}
@app.get('/api/analytics/workflow',tags=['Analytics'])
def workflow(): return delay_all()

@app.get('/api/provenance/{provenance_id}',tags=['Provenance'])
def provenance(provenance_id:str):
 for c in repo.list():
  for p in c['provenance']:
   if p['provenance_id']==provenance_id:return p
 raise HTTPException(404,'Provenance not found')
@app.get('/api/models',tags=['Models'])
def models(): return {'data':[{'model_id':'RULES-001','model_name':'Deterministic review rules','model_type':'rules','version':'1.0.0','training_dataset':None,'feature_set':['evidence completeness','change flag','workflow interval','community signal'],'metrics':None,'created_at':'2026-09-05T00:00:00+00:00','status':'ACTIVE','limitations':'No ML accuracy metric is claimed.'}]}
@app.get('/api/models/{model_id}',tags=['Models'])
def model(model_id:str):
 if model_id=='RULES-001': return models()['data'][0]
 raise HTTPException(404,'Model not found')
@app.get('/api/audit',tags=['Audit'])
def audit(limit:int=Query(100,ge=1,le=1000)): return {'data':repo.audit[-limit:]}
@app.post('/api/sync/evidence',tags=['Sync'])
def sync_evidence(b:dict,x_role:str|None=Header(None)):
 key=b.get('checksum') or b.get('idempotency_key') or b.get('local_id')
 if not key:return {'status':'SYNC_ERROR','message':'checksum, idempotency_key, or local_id is required'}
 if key in repo.sync_keys:return {'status':'DUPLICATE','local_id':b.get('local_id')}
 cid=b.get('claim_id'); c=getc(cid); repo.sync_keys.add(key); payload=b.get('evidence',{}); now=datetime.now(timezone.utc).isoformat(); e={'evidence_id':str(uuid4()),'claim_id':cid,'evidence_type':payload.get('evidence_type','FIELD_OBSERVATION'),'title':payload.get('title','Offline evidence'),'description':payload.get('description',''),'source':'OFFLINE_SYNC','captured_at':b.get('captured_at',now),'uploaded_at':now,'location':b.get('GPS') or b.get('gps_location'),'visibility':payload.get('visibility','AUTHORIZED'),'verification_status':'UNVERIFIED','provenance_id':None,'metadata':{'local_id':b.get('local_id'),'device_reference':b.get('device_reference'),'sync_attempt':b.get('sync_attempt')}}; c['evidence'].append(e); repo.append_ledger(cid,{'event_type':'offline evidence sync','actor':actor(x_role),'evidence_reference':e['evidence_id'],'description':'Offline evidence synchronized.','provenance_reference':None}); return {'status':'SYNCED','local_id':b.get('local_id'),'evidence_id':e['evidence_id']}
@app.post('/api/sync/batch',tags=['Sync'])
def sync_batch(b:list[dict],x_role:str|None=Header(None)): return {'results':[sync_evidence(x,x_role) for x in b]}

# The desktop launcher serves the production dashboard from the same local
# address as the API. API routes above are registered first and retain priority.
if (FRONTEND_DIST / 'assets').is_dir():
 app.mount('/assets', StaticFiles(directory=FRONTEND_DIST / 'assets'), name='frontend-assets')
