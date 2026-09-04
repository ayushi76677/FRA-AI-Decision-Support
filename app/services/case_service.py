"""Case presentation service. A case is a one-to-one view of a claim."""
from __future__ import annotations
from . import evidence_service, timeline_service
from .satellite_change_service import get_change_evidence
from .review_rules import evaluate
from .spatial_service import area_hectares, geometry_valid, distance_m, overlap_percent, intersects
from ..demo_repository import repo

FUTURE_COLLECTIONS=("timeline","documents","evidence","spatial_evidence","satellite_observations","review_signals","field_verification","community_reviews","ledger","anomalies","provenance")

def build_case(claim_summary: dict) -> dict:
    """Populate the Step 3 evidence and timeline modules only."""
    result={"case_id":claim_summary["claim_id"],"claim":claim_summary}
    result.update({name:[] for name in FUTURE_COLLECTIONS})
    claim_id=claim_summary['claim_id']
    result['evidence']=evidence_service.list_for_claim(claim_id,page_size=100)['items']
    result['timeline']=timeline_service.list_for_claim(claim_id,page_size=100)['items']
    # Spatial detail is a deterministic observation of synthetic demo geometry.
    geometry=claim_summary.get('geometry')
    nearby=[]
    for other in repo.list():
        if other['claim_id']==claim_id or not geometry or not other.get('geometry'): continue
        distance=distance_m(geometry,other['geometry'])
        if distance is not None and distance<=2000: nearby.append({'claim_id':other['claim_id'],'distance_m':distance,'overlap_percentage':overlap_percent(geometry,other['geometry'])})
    flags=[]
    if geometry_valid(geometry): flags.append({'code':'CLAIM_GEOMETRY_VALID','message':'Synthetic demo claim geometry is valid.','action':'Use as spatial context only.'})
    if nearby: flags.append({'code':'NEARBY_CLAIM','message':'Nearby demo claim geometry detected.','action':'Spatial relationship requires verification.'})
    if any(item['overlap_percentage']>0 for item in nearby): flags.append({'code':'CLAIM_OVERLAP','message':'Claim geometry overlaps another demo claim.','action':'Requires verification.'})
    if geometry and intersects(geometry,repo.forest_boundary): flags.append({'code':'FOREST_BOUNDARY_INTERSECTION','message':'Forest-boundary relationship detected in synthetic demo data.','action':'Requires human review.'})
    result['spatial_evidence']={'claim_id':claim_id,'geometry':geometry,'area_hectares':area_hectares(geometry),'nearby_claims':nearby,'spatial_flags':flags,'limitations':['Geometry is synthetic demo data. Spatial relationships do not establish legal validity or wrongdoing.']}
    result['satellite_observations']=[get_change_evidence(claim_id)]
    # Case detail exposes the same object returned by /review; it never re-runs
    # a presentation-specific set of alert rules.
    full_claim=repo.get(claim_id)
    result['review_result']=evaluate(full_claim, full_claim['evidence'], full_claim['timeline'], full_claim['anomalies'])
    result['review_signals']=result['review_result']['signals']
    result['field_verification']=full_claim['field_verification']
    result['community_reviews']=full_claim['community_reviews']
    result['ledger']=full_claim['ledger']
    result['provenance']=full_claim['provenance']
    return result
