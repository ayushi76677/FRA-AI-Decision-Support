import hashlib, json
from uuid import uuid4

EVENT_TYPES={'CLAIM_APPLICATION','DOCUMENT','TIMELINE_EVENT','SPATIAL_ANALYSIS','SATELLITE_CHANGE','REVIEW_SIGNAL','FIELD_VERIFICATION','FIELD_PHOTO','FIELD_OBSERVATION','COMMUNITY_REVIEW','COMMUNITY_EVIDENCE','STATUS_CHANGE','OTHER'}
EVENT_ALIASES={'claim submitted':'CLAIM_APPLICATION','claim application':'CLAIM_APPLICATION','field verification':'FIELD_VERIFICATION','field verification task created':'FIELD_VERIFICATION','field verification task updated':'FIELD_VERIFICATION','field evidence submitted':'FIELD_OBSERVATION','community review':'COMMUNITY_REVIEW','offline evidence sync':'FIELD_OBSERVATION'}

def normalize_event(claim_id, data, timestamp):
    """Build an append-only, display-ready ledger event without altering history."""
    raw=data.get('event_type','OTHER')
    event_type=EVENT_ALIASES.get(raw, raw if raw in EVENT_TYPES else 'OTHER')
    event_id=data.get('event_id') or data.get('ledger_id') or str(uuid4())
    related_id=data.get('related_id') or data.get('evidence_reference') or data.get('verification_id') or data.get('review_id')
    return {'event_id':event_id,'ledger_id':event_id,'claim_id':claim_id,'event_type':event_type,'timestamp':data.get('timestamp',timestamp),'actor':data.get('actor','SYSTEM'),'role':data.get('role'),'source':data.get('source','SYNTHETIC DEMO DATA'),'description':data.get('description',''),'provenance':data.get('provenance') or data.get('provenance_reference'),'related_id':related_id,'evidence_reference':data.get('evidence_reference'),'synthetic_demo':data.get('synthetic_demo',True)}
def event_hash(event, previous):
    payload = json.dumps({k:v for k,v in event.items() if k not in ("event_hash", "previous_event_hash")}, sort_keys=True, default=str)
    return hashlib.sha256((previous + payload).encode()).hexdigest()
