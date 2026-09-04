from pydantic import BaseModel
class GeoJSONFeature(BaseModel): type:str='Feature'; geometry:dict|None=None; properties:dict={}
class GeoJSONFeatureCollection(BaseModel): type:str='FeatureCollection'; features:list[GeoJSONFeature]
