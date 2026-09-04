from datetime import datetime
from pydantic import BaseModel
class SatelliteObservationRead(BaseModel): observation_id:str; claim_id:str; source:str; observed_at:datetime; metadata:dict={}
