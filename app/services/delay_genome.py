from datetime import datetime
def analyse(events):
    ordered = sorted(events, key=lambda x: x["timestamp"])
    durations=[]
    for earlier, later in zip(ordered, ordered[1:]):
        try: days=(datetime.fromisoformat(later["timestamp"])-datetime.fromisoformat(earlier["timestamp"])).days
        except ValueError: days=0
        durations.append({"from":earlier["stage"],"to":later["stage"],"days":days})
    return {"sequence":[x["stage"] for x in ordered],"stage_intervals":durations,"total_elapsed_days":sum(x["days"] for x in durations),"inactivity_intervals":[x for x in durations if x["days"] >= 90],"repeated_stages":sorted({x["stage"] for x in ordered if sum(y["stage"]==x["stage"] for y in ordered)>1}),"limitation":"Operational workflow analysis; not a legal deadline determination."}
