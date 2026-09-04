from pydantic import BaseModel
class ProvenanceRead(BaseModel): provenance_id:str; source:str; provider:str|None=None; method:str|None=None; limitations:str|None=None; details:dict={}
