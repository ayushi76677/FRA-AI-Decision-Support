"""Deterministic, explainable review rules for a claim."""
from __future__ import annotations

from .spatial_service import geometry_valid, intersects


def _signal(code, severity, explanation, source, evidence_for=(), evidence_against=()):
    return {"code":code,"title":code,"severity":severity,"explanation":explanation,"source":source,"deterministic":True,"evidence_for":list(evidence_for),"evidence_against":list(evidence_against)}


def _change_intersects_claim(claim, change):
    claim_geometry=claim.get("geometry")
    change_geometry=change.get("geometry")
    return bool(
        geometry_valid(claim_geometry)
        and geometry_valid(change_geometry)
        and intersects(claim_geometry, change_geometry)
    )


def evaluate(claim, evidence=None, timeline=None, anomalies=None):
    """Return the single, reproducible review result used by every presentation."""
    signals=[]
    limitations=["Decision support only; authorized humans make FRA determinations.","Demo records are synthetic and imagery observations are not real provider data."]
    changes=claim.get("change_detection", [])
    intersecting_changes=[item for item in changes if item.get("change_detected") and _change_intersects_claim(claim,item)]
    if intersecting_changes:
        signals.append(_signal("POSSIBLE_CHANGE_INTERSECTION","MEDIUM","Possible land-cover change intersects the claim area. Field verification is recommended.","SATELLITE_CHANGE",["A deterministic possible-change observation intersects the claim geometry."]))
    elif any(item.get("change_detected") for item in changes):
        limitations.append("A possible change observation is outside the claim geometry and is not treated as a claim review signal.")
    completeness=claim.get("evidence_completeness")
    if completeness is not None and completeness<70:
        signals.append(_signal("INCOMPLETE_EVIDENCE","MEDIUM","The available evidence set is below the configured completeness threshold and should be completed before a human decision.","EVIDENCE",[f"Evidence completeness is {completeness}% (threshold: 70%)."]))
    field_status=claim.get("field_verification_status",claim.get("verification_status"))
    if field_status=="PENDING":
        signals.append(_signal("FIELD_VERIFICATION_PENDING","MEDIUM","Field verification is pending; its observation should be considered before a human decision.","FIELD_VERIFICATION",["A field-verification record has result PENDING."]))
    elif field_status=="CHANGE_NOT_CONFIRMED": limitations.append("Field verification did not confirm the possible-change observation.")
    community_status=claim.get("community_review_status","NOT_REVIEWED")
    if community_status=="PENDING":
        signals.append(_signal("COMMUNITY_REVIEW_PENDING","LOW","Community review is pending and may provide relevant local context.","COMMUNITY_REVIEW",["Community review status is PENDING."]))
    if any(review.get("action") in {"CONTEST","REPORT_CONFLICT"} for review in claim.get("community_reviews",[])):
        signals.append(_signal("CONFLICTING_COMMUNITY_EVIDENCE","HIGH","Community evidence contains a recorded conflict that requires human review.","COMMUNITY_REVIEW",["A community review explicitly reported a conflict."]))
    if any((item.get("overlap_percentage") or item.get("percentage") or 0)>0 for item in claim.get("spatial_overlaps",[])):
        signals.append(_signal("SPATIAL_OVERLAP","HIGH","The claim geometry overlaps another supplied claim geometry and requires human review.","SPATIAL_ANALYSIS",["A supplied spatial analysis reports positive claim overlap."]))
    if claim.get("forest_boundary_intersection") is True:
        signals.append(_signal("FOREST_BOUNDARY_INTERSECTION","MEDIUM","The claim geometry intersects a supplied forest-boundary layer and requires human review.","SPATIAL_ANALYSIS",["A supplied spatial analysis reports a forest-boundary intersection."]))
    benchmark,days=claim.get("workflow_inactivity_benchmark_days"),claim.get("days_since_last_action")
    if isinstance(benchmark,(int,float)) and isinstance(days,(int,float)) and days>=benchmark:
        signals.append(_signal("WORKFLOW_INACTIVITY","MEDIUM","Operational inactivity meets the configured workflow benchmark; this is not a legal deadline finding.","WORKFLOW",[f"Days since last action: {days}; configured benchmark: {benchmark}."],["The benchmark is an operational review rule, not a legal deadline."]))
    elif days is not None and benchmark is None: limitations.append("Workflow inactivity cannot be assessed because no configured benchmark is available.")
    against=[]
    if field_status=="CHANGE_NOT_CONFIRMED": against.append("Field verification did not confirm the possible-change observation.")
    if community_status=="CONFIRM": against.append("Community review provided contextual confirmation; it is not an automatic decision.")
    against.extend(item for signal in signals for item in signal["evidence_against"])
    codes={signal["code"] for signal in signals}
    if "CONFLICTING_COMMUNITY_EVIDENCE" in codes or len(signals)>=3 or ({"INCOMPLETE_EVIDENCE","WORKFLOW_INACTIVITY"}<=codes): priority,reason="HIGH_PRIORITY","Multiple or high-severity deterministic review signals require coordinated human review."
    elif "POSSIBLE_CHANGE_INTERSECTION" in codes: priority,reason="REVIEW","A possible land-cover change intersects the claim area and requires field verification."
    elif signals: priority,reason="REVIEW","At least one deterministic review signal requires human attention."
    else: priority,reason="NORMAL","No significant deterministic review signal currently meets the configured rules."
    if "POSSIBLE_CHANGE_INTERSECTION" in codes or "FIELD_VERIFICATION_PENDING" in codes: action="Complete field verification and record the human observation."
    elif "INCOMPLETE_EVIDENCE" in codes: action="Request and review the missing documentary evidence."
    elif "COMMUNITY_REVIEW_PENDING" in codes or "CONFLICTING_COMMUNITY_EVIDENCE" in codes: action="Complete community review and record the human assessment."
    elif "SPATIAL_OVERLAP" in codes or "FOREST_BOUNDARY_INTERSECTION" in codes: action="Review the supplied spatial evidence with an authorized human reviewer."
    else: action="Continue normal human review."
    return {"priority":priority,"priority_reason":reason,"signals":signals,"evidence_for":[item for signal in signals for item in signal["evidence_for"]],"evidence_against":against,"limitations":limitations,"recommended_next_action":action,"deterministic":True}
