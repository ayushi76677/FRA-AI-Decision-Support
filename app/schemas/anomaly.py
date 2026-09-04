from pydantic import BaseModel
class AnomalyRead(BaseModel): anomaly_id:str; claim_id:str; anomaly_type:str; severity:str; reason:str
