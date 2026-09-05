"""In-memory deterministic fixture repository used exclusively in DATABASE_MODE=demo."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from .services.ledger_service import event_hash, normalize_event

NOW = datetime(2026, 9, 5, tzinfo=timezone.utc)
def iso(days): return (NOW - timedelta(days=days)).isoformat()
def polygon(x, y, d=.006): return {"type":"Polygon","coordinates":[[[x,y],[x+d,y],[x+d,y+d],[x,y+d],[x,y]]]}

class DemoRepository:
    def __init__(self):
        self.claims={}; self.audit=[]; self.sync_keys=set()
        # Clearly synthetic boundary used solely for the local GIS demonstration.
        self.forest_boundary={"type":"Polygon","coordinates":[[[80.262,22.162],[80.296,22.162],[80.296,22.196],[80.262,22.196],[80.262,22.162]]],"data_label":"DEMO DATA","name":"Synthetic forest-boundary demonstration"}
        # India-wide synthetic locations make the global evidence-map overview
        # demonstrably multi-case; they are not real claims or boundaries.
        locations=[
            ("Assam", "Kamrup Metropolitan", "Demo Village Assam", 91.73, 26.14),
            ("Madhya Pradesh", "Jabalpur", "Demo Village Jabalpur", 79.95, 23.18),
            ("Rajasthan", "Udaipur", "Demo Village Udaipur", 73.68, 24.58),
            ("Maharashtra", "Nagpur", "Demo Village Nagpur", 79.09, 21.15),
            ("Odisha", "Khordha", "Demo Village Odisha", 85.82, 20.29),
            ("Karnataka", "Mysuru", "Demo Village Mysuru", 76.64, 12.29),
            ("Gujarat", "Ahmedabad", "Demo Village Gujarat", 72.58, 23.03),
            ("Uttar Pradesh", "Lucknow", "Demo Village Lucknow", 80.95, 26.85),
            ("Jharkhand", "Ranchi", "Demo Village Ranchi", 85.31, 23.34),
            ("Chhattisgarh", "Raipur", "Demo Village Raipur", 81.63, 21.25),
        ]
        statuses=["PENDING","UNDER_REVIEW","FIELD_VERIFICATION","COMMUNITY_REVIEW","VERIFIED","COMPLETED"]
        for n in range(1, 21):
            cid=f"DEMO-CLAIM-{n:03d}"; change=n in (3,7,11,16); conflict=n in (7,14); pending=n in (3,6,7,11,14,16)
            state,district,village,longitude,latitude=locations[(n-1)%len(locations)]
            group=(n-1)//len(locations)
            geom=polygon(longitude+(group*.18),latitude+(group*.13),.10)
            timeline=[self.timeline(cid,"APPLICATION_RECEIVED",iso(220-n*3),"APPLICATION","Application received."),self.timeline(cid,"DOCUMENT_REVIEWED",iso(130-n*2),"DOCUMENT_REVIEW","Documents reviewed.")]
            if n % 3: timeline.append(self.timeline(cid,"SITE_VERIFICATION",iso(30+n),"SITE_VERIFICATION","Site review queued or completed."))
            community=[] if not conflict else [{"review_id":f"CR-{n}","claim_id":cid,"reviewer_role":"COMMUNITY_REVIEWER","action":"REPORT_CONFLICT","statement":"Synthetic contextual conflict for human review.","evidence_reference":None,"submitted_at":iso(20),"visibility":"AUTHORIZED"}]
            verification=[] if not change else [{"verification_id":f"FV-{n}","claim_id":cid,"assigned_to":"FIELD_OFFICER_DEMO","scheduled_at":iso(-5),"gps_location":{"type":"Point","coordinates":[geom['coordinates'][0][0][0]+.002,geom['coordinates'][0][0][1]+.002]},"photos":[],"observation":"Demo verification appointment.","result":"PENDING","notes":"Synthetic demo record.","created_at":iso(8),"completed_at":None}]
            provenance={"provenance_id":f"PROV-{n}","source":"DEMO DATA / deterministic fixture","provider":"Local demo provider","acquisition_date":iso(60),"processing_date":iso(2),"processing_method":"Deterministic temporal comparison","model_or_method":"NDVI-style fixture comparison","parameters":{"threshold":"demo"},"transformation_steps":["fixture generation"],"operator":"system","hash":None,"limitations":"Not real satellite imagery or a measured scientific result."}
            detection=[] if not change else [{"change_id":f"CHANGE-{n}","claim_id":cid,"before_date":iso(120),"after_date":iso(20),"change_detected":True,"estimated_change_area":round(.15+n*.01,2),"percentage_change":round(8+n*.3,1),"geometry":polygon(geom['coordinates'][0][0][0]+.001,geom['coordinates'][0][0][1]+.001,.003),"method":"DEMO deterministic temporal comparison","source":"DEMO DATA","limitations":"Possible land-cover change does not establish cause, legality, or claim validity.","provenance_id":provenance['provenance_id']}]
            evidence=[{"evidence_id":f"EV-{n}-DOC","claim_id":cid,"evidence_type":"DOCUMENT","title":"Demo application record","description":"Synthetic document register entry.","source":"DEMO DATA","captured_at":iso(210),"uploaded_at":iso(209),"location":None,"visibility":"AUTHORIZED","verification_status":"UNVERIFIED","provenance_id":provenance['provenance_id'],"metadata":{"origin":"demo"}}]
            if change: evidence.append({"evidence_id":f"EV-{n}-SAT","claim_id":cid,"evidence_type":"SATELLITE","title":"Demo possible change observation","description":"Synthetic deterministic alert.","source":"DEMO DATA","captured_at":iso(20),"uploaded_at":iso(19),"location":detection[0]['geometry'],"visibility":"AUTHORIZED","verification_status":"REQUIRES_VERIFICATION","provenance_id":provenance['provenance_id'],"metadata":{"change_id":detection[0]['change_id']}})
            # The first four fixtures deliberately demonstrate Normal, change review,
            # incomplete evidence, and multiple-signal review situations.
            completeness=55 if pending else 85; inactive_days=120 if pending else 18
            if n in (3,6): completeness=85 if n==3 else 55; inactive_days=18
            priority="REQUIRES_VERIFICATION" if change else ("HIGH" if pending else ("MEDIUM" if n%3==0 else "LOW"))
            self.claims[cid]={"claim_id":cid,"case_id":cid,"claimant_reference":f"SYNTHETIC-REF-{n:03d}","claim_type":"COMMUNITY" if n%4==0 else "INDIVIDUAL","village":village,"gram_panchayat":f"Demo Panchayat {(n-1)//4+1}","district":district,"state":state,"latitude":latitude+(group*.13)+.05,"longitude":longitude+(group*.18)+.05,"area_hectares":round(1.1+(n*.17),2),"status":statuses[n%len(statuses)],"priority":priority,"verification_status":verification[0]['result'] if verification else "NOT_REQUIRED","community_review_status":community[0]['action'] if community else "NOT_REVIEWED","evidence_completeness":completeness,"workflow_inactivity_benchmark_days":90,"created_at":iso(220-n*3),"updated_at":iso(n+2),"geometry":geom,"is_active":True,"data_label":"DEMO DATA","days_since_last_action":inactive_days,"timeline":timeline,"evidence":evidence,"provenance":[provenance],"change_detection":detection,"field_verification":verification,"community_reviews":community,"ledger":[],"anomalies":[]}
            self.append_ledger(cid,{"event_type":"CLAIM_APPLICATION","actor":"SYSTEM_DEMO","source":"CLAIM","description":"Synthetic demo claim fixture initialized.","provenance_reference":provenance['provenance_id']})
            self.append_ledger(cid,{"event_type":"DOCUMENT","actor":"SYSTEM_DEMO","source":"CLAIM","evidence_reference":evidence[0]['evidence_id'],"description":"Synthetic demo application record added.","provenance_reference":provenance['provenance_id']})
            if change: self.append_ledger(cid,{"event_type":"SATELLITE_CHANGE","actor":"SYSTEM_DEMO","source":"SATELLITE_CHANGE","evidence_reference":evidence[-1]['evidence_id'],"description":"Synthetic possible-change observation recorded.","provenance_reference":provenance['provenance_id']})
            if verification: self.append_ledger(cid,{"event_type":"FIELD_VERIFICATION","actor":"SYSTEM_DEMO","source":"FIELD_VERIFICATION","verification_id":verification[0]['verification_id'],"description":"Synthetic field verification task created.","provenance_reference":provenance['provenance_id']})
            if community: self.append_ledger(cid,{"event_type":"COMMUNITY_REVIEW","actor":"SYSTEM_DEMO","source":"COMMUNITY_REVIEW","review_id":community[0]['review_id'],"description":"Synthetic community review recorded.","provenance_reference":provenance['provenance_id']})
    def timeline(self,cid,event_type,timestamp,stage,description): return {"event_id":str(uuid4()),"claim_id":cid,"event_type":event_type,"timestamp":timestamp,"stage":stage,"actor_role":"SYSTEM_DEMO","description":description,"source":"DEMO DATA","metadata":{}}
    def get(self,cid): return self.claims.get(cid)
    def list(self): return list(self.claims.values())
    def append_ledger(self,cid, data):
        claim=self.claims[cid]; previous=claim['ledger'][-1]['event_hash'] if claim['ledger'] else "GENESIS"
        event={**normalize_event(cid,data,NOW.isoformat()),"previous_event_hash":previous}; event['event_hash']=event_hash(event,previous); claim['ledger'].append(event); return event
    def log(self,actor,action,entity): self.audit.append({"audit_id":str(uuid4()),"actor":actor,"action":action,"entity":entity,"timestamp":NOW.isoformat(),"request_id":str(uuid4())})
    def copy_claim(self,c):
        result=deepcopy(c)
        for k in ('timeline','evidence','provenance','change_detection','field_verification','community_reviews','ledger','anomalies'): result.pop(k,None)
        return result

repo=DemoRepository()
