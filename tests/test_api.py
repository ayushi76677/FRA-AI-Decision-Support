from fastapi.testclient import TestClient
from copy import deepcopy
from app.main import app
from app.demo_repository import repo
from app.services.review_rules import evaluate

client=TestClient(app)
def test_health():
 r=client.get('/health'); assert r.status_code==200 and r.json()['database']=='demo'
def test_claims_and_map():
 body=client.get('/api/claims').json(); assert body['total']>=15 and len(body['items'])<=body['page_size']
 r=client.get('/api/map/claims'); assert r.status_code==200 and r.json()['type']=='FeatureCollection' and r.json()['features'][0]['geometry']

def test_claim_crud_filters_and_validation():
 payload={'claimant_reference':'SYNTHETIC-TEST-001','claim_type':'INDIVIDUAL','village':'Demo Village','gram_panchayat':'Demo Panchayat','district':'Demo District','state':'Demo State','area_hectares':1.5,'status':'PENDING','priority':'HIGH'}
 created=client.post('/api/claims',json=payload); assert created.status_code==201
 cid=created.json()['claim_id']
 updated=client.patch('/api/claims/'+cid,json={'status':'UNDER_REVIEW'}); assert updated.status_code==200 and updated.json()['status']=='UNDER_REVIEW'
 filtered=client.get('/api/claims',params={'status':'UNDER_REVIEW','search':'SYNTHETIC-TEST-001','page':1,'page_size':1,'sort_by':'claim_id','sort_order':'asc'}).json()
 assert filtered['total']==1 and filtered['items'][0]['claim_id']==cid
 assert client.get('/api/claims/NO-SUCH-CLAIM').status_code==404
 assert client.post('/api/claims',json={**payload,'status':'NOT_A_STATUS'}).status_code==422

def test_case_endpoints_reference_claims_only():
 listing=client.get('/api/cases',params={'priority':'HIGH','page_size':5}); assert listing.status_code==200 and 'items' in listing.json()
 body=client.get('/api/cases/DEMO-CLAIM-001').json()
 assert body['case_id']=='DEMO-CLAIM-001' and body['claim']['claim_id']=='DEMO-CLAIM-001'
 assert body['evidence'] and body['timeline']

def test_evidence_and_timeline_subsystem():
 claim_payload={'claimant_reference':'SYNTHETIC-EVIDENCE-TEST','claim_type':'INDIVIDUAL','village':'Demo Village','gram_panchayat':'Demo Panchayat','district':'Demo District','state':'Demo State','area_hectares':1.5,'status':'PENDING','priority':'LOW'}
 claim_id=client.post('/api/claims',json=claim_payload).json()['claim_id']
 evidence_payload={'claim_id':claim_id,'evidence_type':'DOCUMENT','title':'Synthetic supporting record','visibility':'PUBLIC','verification_status':'REVIEWED'}
 created=client.post('/api/evidence',json=evidence_payload); assert created.status_code==201
 evidence_id=created.json()['evidence_id']
 assert client.patch('/api/evidence/'+evidence_id,json={'verification_status':'HUMAN_VERIFIED'}).json()['verification_status']=='HUMAN_VERIFIED'
 evidence_page=client.get('/api/claims/'+claim_id+'/evidence',params={'visibility':'PUBLIC'}).json(); assert evidence_page['total']>=1 and evidence_page['items'][0]['claim_id']==claim_id
 restricted=client.post('/api/evidence',json={**evidence_payload,'title':'Restricted synthetic record','visibility':'RESTRICTED'}).json()
 assert client.get('/api/evidence/'+restricted['evidence_id']).status_code==404
 assert client.get('/api/evidence/'+restricted['evidence_id'],params={'include_restricted':'true'}).status_code==200
 timeline_payload={'claim_id':claim_id,'event_type':'DOCUMENT_SUBMITTED','title':'Synthetic submission','event_time':'2026-09-01T10:00:00Z','evidence_id':evidence_id}
 event=client.post('/api/timeline',json=timeline_payload); assert event.status_code==201
 assert client.get('/api/timeline/'+event.json()['event_id']).status_code==200
 timeline=client.get('/api/claims/'+claim_id+'/timeline').json(); assert timeline['items']==sorted(timeline['items'],key=lambda item:(item['event_time'],item['created_at'],item['event_id']))
 assert client.post('/api/evidence',json={**evidence_payload,'evidence_type':'INVALID'}).status_code==422
 assert client.post('/api/timeline',json={**timeline_payload,'evidence_id':'MISSING'}).status_code==404
def test_case_review_ledger_and_spatial():
 cid='DEMO-CLAIM-003'
 assert client.get('/api/cases/'+cid).status_code==200
 assert client.get('/api/claims/'+cid+'/review').json()['priority']=='REVIEW'
 events=client.get('/api/claims/'+cid+'/ledger').json()['data']; assert events[0]['event_hash']
 assert client.get('/api/claims/'+cid+'/spatial-analysis').status_code==200
def test_spatial_evidence_response_and_flags():
 body=client.get('/api/claims/DEMO-CLAIM-003/spatial-analysis').json()
 assert body['geometry_valid'] and body['area_hectares']>0 and body['geometry']['type']=='Polygon'
 assert any(flag['code']=='CLAIM_GEOMETRY_VALID' for flag in body['spatial_flags'])
 assert client.get('/api/claims/NO-SUCH-CLAIM/spatial-analysis').status_code==404
 assert client.get('/api/map/forest-boundary').json()['features'][0]['properties']['data_label']=='DEMO DATA'
def test_satellite_change_evidence_is_neutral_and_deterministic():
 no_change=client.get('/api/claims/DEMO-CLAIM-001/satellite-change').json(); assert no_change['status']=='NO_CHANGE' and no_change['data_label']=='SYNTHETIC DEMO DATA'
 change=client.get('/api/claims/DEMO-CLAIM-003/satellite-change').json(); assert change['status']=='CHANGE_REQUIRES_VERIFICATION' and change['claim_intersection'] and change['change_geometry']['type']=='Polygon'
 assert change['provenance'] and change['limitations'] and 'illegal' not in change['observation'].lower()
 assert client.get('/api/claims/UNKNOWN/satellite-change').status_code==404
def test_sync_is_idempotent():
 p={'local_id':'pytest-local-1','claim_id':'DEMO-CLAIM-002','evidence':{'title':'test'}}
 assert client.post('/api/sync/evidence',json=p).json()['status']=='SYNCED'
 assert client.post('/api/sync/evidence',json=p).json()['status']=='DUPLICATE'

def test_review_explanations_are_deterministic_and_case_integrated():
 normal=client.get('/api/claims/DEMO-CLAIM-001/review').json()
 change=client.get('/api/claims/DEMO-CLAIM-003/review').json()
 incomplete=client.get('/api/claims/DEMO-CLAIM-006/review').json()
 multiple=client.get('/api/claims/DEMO-CLAIM-007/review').json()
 assert normal['priority']=='NORMAL' and normal['signals']==[]
 assert change['priority']=='REVIEW' and any(x['code']=='POSSIBLE_CHANGE_INTERSECTION' for x in change['signals'])
 assert incomplete['priority']=='REVIEW' and any(x['code']=='INCOMPLETE_EVIDENCE' for x in incomplete['signals'])
 assert multiple['priority']=='HIGH_PRIORITY' and len(multiple['signals'])>=3
 assert client.get('/api/claims/DEMO-CLAIM-003/review').json()==change
 signal=change['signals'][0]
 assert signal['source'] in {'CLAIM','EVIDENCE','SATELLITE_CHANGE','SPATIAL_ANALYSIS','TIMELINE','FIELD_VERIFICATION','COMMUNITY_REVIEW','WORKFLOW','OTHER'} and signal['deterministic'] is True
 assert 'confidence' not in change and 'illegal' not in signal['explanation'].lower()
 detail=client.get('/api/cases/DEMO-CLAIM-003').json()
 assert detail['review_result']==change and detail['review_signals']==change['signals']
 alert=client.get('/api/claims/DEMO-CLAIM-003/alert-card').json()
 assert alert['review_result']==change and alert['signals']==change['signals']
 assert client.get('/api/claims/NO-SUCH-CLAIM/review').status_code==404

def test_review_rule_edge_cases_are_explicit_and_neutral():
 base=deepcopy(repo.get('DEMO-CLAIM-001'))
 base['change_detection']=[deepcopy(repo.get('DEMO-CLAIM-003')['change_detection'][0])]
 base['change_detection'][0]['geometry']['coordinates'][0][0]=[0,0]
 outside=evaluate(base)
 assert 'POSSIBLE_CHANGE_INTERSECTION' not in {x['code'] for x in outside['signals']}
 assert any('outside the claim geometry' in item for item in outside['limitations'])
 assert evaluate(deepcopy(repo.get('DEMO-CLAIM-001')))['signals']==[]
 base['verification_status']='PENDING'; base['community_review_status']='PENDING'
 base['spatial_overlaps']=[{'overlap_percentage':1}]; base['forest_boundary_intersection']=True
 base['workflow_inactivity_benchmark_days']=10; base['days_since_last_action']=10
 result=evaluate(base); codes={x['code'] for x in result['signals']}
 assert {'FIELD_VERIFICATION_PENDING','COMMUNITY_REVIEW_PENDING','SPATIAL_OVERLAP','FOREST_BOUNDARY_INTERSECTION','WORKFLOW_INACTIVITY'}<=codes
 assert result['priority']=='HIGH_PRIORITY' and result['evidence_for'] and result['recommended_next_action']
 base.pop('workflow_inactivity_benchmark_days')
 assert any('no configured benchmark' in item for item in evaluate(base)['limitations'])
 base['community_reviews']=[{'action':'COMMENT'}]
 assert 'CONFLICTING_COMMUNITY_EVIDENCE' not in {x['code'] for x in evaluate(base)['signals']}
 base['community_reviews']=[{'action':'REPORT_CONFLICT'}]
 assert 'CONFLICTING_COMMUNITY_EVIDENCE' in {x['code'] for x in evaluate(base)['signals']}

def test_field_verification_task_and_evidence_capture_are_claim_scoped():
 task=client.post('/api/claims/DEMO-CLAIM-003/field-verification/tasks',json={'assigned_to':'FIELD_OFFICER_DEMO','status':'ASSIGNED','reason':'Possible change requires verification.','latitude':22.18,'longitude':80.29}).json()
 assert task['claim_id']=='DEMO-CLAIM-003' and task['status']=='ASSIGNED' and task['location']['type']=='Point'
 payload={'evidence_type':'FIELD_PHOTO','photo_reference':'DEMO-PHOTO-001','photo_metadata':{'data_label':'SYNTHETIC DEMO DATA'},'latitude':22.18,'longitude':80.29,'captured_at':'2026-09-05T10:00:00Z','observation':'Synthetic field observation for human review.','notes':'Demo only.','submitted_by':'FIELD_OFFICER_DEMO'}
 evidence=client.post(f"/api/claims/DEMO-CLAIM-003/field-verification/{task['verification_id']}/evidence",json=payload)
 assert evidence.status_code==201 and evidence.json()['metadata']['verification_id']==task['verification_id']
 assert client.post(f"/api/claims/DEMO-CLAIM-001/field-verification/{task['verification_id']}/evidence",json=payload).status_code==404
 assert client.post('/api/claims/DEMO-CLAIM-003/field-verification/tasks',json={'assigned_to':'FIELD_OFFICER_DEMO','latitude':91}).status_code==422

def test_evidence_ledger_is_append_only_and_traceable():
 before=client.get('/api/claims/DEMO-CLAIM-003/ledger').json()['data']
 created=client.post('/api/claims/DEMO-CLAIM-003/ledger',json={'event_type':'REVIEW_SIGNAL','description':'Deterministic review signal recorded.','source':'WORKFLOW','related_id':'POSSIBLE_CHANGE_INTERSECTION'}).json()
 after=client.get('/api/claims/DEMO-CLAIM-003/ledger').json()['data']
 assert len(after)==len(before)+1 and after[-1]['event_id']==created['event_id']
 assert created['source']=='WORKFLOW' and created['related_id']=='POSSIBLE_CHANGE_INTERSECTION' and created['synthetic_demo'] is True
 assert created['previous_event_hash']==before[-1]['event_hash'] and created['event_hash']
