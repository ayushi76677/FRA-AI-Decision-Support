from datetime import datetime
from pydantic import BaseModel
class LedgerEventRead(BaseModel):
 event_id:str; ledger_id:str; claim_id:str; timestamp:datetime; event_type:str; actor:str; role:str|None=None; source:str; description:str; provenance:str|None=None; related_id:str|None=None; evidence_reference:str|None=None; synthetic_demo:bool=True; previous_event_hash:str|None=None; event_hash:str
