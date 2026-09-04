from pydantic import BaseModel
class CommunityReviewCreate(BaseModel): reviewer_role:str; action:str; statement:str; evidence_reference:str|None=None; visibility:str='AUTHORIZED'
