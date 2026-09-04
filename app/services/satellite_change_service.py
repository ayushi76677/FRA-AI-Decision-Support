"""Offline deterministic satellite-change evidence built from demo observations."""
from __future__ import annotations
from datetime import datetime, timezone
from ..demo_repository import repo
from .spatial_service import area_hectares, intersection_bbox, intersects, overlap_percent

LIMITATIONS=['SYNTHETIC DEMO DATA: no real satellite ingestion is performed.','Satellite change does not establish illegality, ownership, intent, or a violation.','Resolution, seasonal variation, temporal gaps, and classification uncertainty require human caution.']
def get_change_evidence(claim_id):
    claim=repo.get(claim_id)
    if not claim or not claim.get('is_active',True): return None
    observation=claim['change_detection'][0] if claim['change_detection'] else None
    now=datetime.now(timezone.utc).isoformat()
    if not observation:
        return {'claim_id':claim_id,'change_id':None,'source':'DEMO / SYNTHETIC','source_type':'SYNTHETIC_DEMO','before_date':None,'after_date':None,'before_image':None,'after_image':None,'change_detected':False,'status':'NO_CHANGE','change_area_hectares':0.0,'change_geometry':None,'claim_intersection':False,'intersection_area_hectares':0.0,'intersection_percentage':0.0,'observation':'No possible land-cover change is recorded in the deterministic demo comparison.','evidence_for_review':[],'limitations':LIMITATIONS,'recommended_action':'Continue normal human review.','provenance':None,'created_at':now,'updated_at':now,'data_label':'SYNTHETIC DEMO DATA'}
    geometry=observation.get('geometry'); intersection=intersection_bbox(claim.get('geometry'),geometry); has_intersection=bool(intersection)
    intersection_area=area_hectares(intersection); percentage=overlap_percent(claim.get('geometry'),geometry)
    status='CHANGE_REQUIRES_VERIFICATION' if has_intersection else 'POSSIBLE_CHANGE'
    return {'claim_id':claim_id,'change_id':observation['change_id'],'source':observation.get('source','DEMO DATA'),'source_type':'SYNTHETIC_DEMO','before_date':observation.get('before_date'),'after_date':observation.get('after_date'),'before_image':None,'after_image':None,'change_detected':True,'status':status,'change_area_hectares':area_hectares(geometry),'change_geometry':geometry,'claim_intersection':has_intersection,'intersection_area_hectares':intersection_area,'intersection_percentage':percentage,'observation':'Possible land-cover change intersects the claim area and requires field verification.' if has_intersection else 'Possible land-cover change was observed outside the claim geometry; it does not establish a claim-specific issue.','evidence_for_review':['Deterministic temporal comparison indicates a possible land-cover transition.','Change geometry and affected area are available as synthetic demo evidence.']+(['Change polygon intersects the claim geometry.'] if has_intersection else []),'limitations':LIMITATIONS+list(filter(None,[observation.get('limitations')])),'recommended_action':'Field verification recommended.' if has_intersection else 'Review spatial context; field verification may be considered.','provenance':next((p for p in claim['provenance'] if p['provenance_id']==observation.get('provenance_id')),None),'created_at':now,'updated_at':now,'data_label':'SYNTHETIC DEMO DATA'}
