from typing import Any,Dict,List,Literal
from pydantic import BaseModel,Field
RiskLevel=Literal["LOW","MEDIUM","HIGH","CRITICAL"]
class RiskDimension(BaseModel):
    score:float; level:RiskLevel; drivers:List[str]=Field(default_factory=list)
class SupplierRiskResponse(BaseModel):
    supplier_id:str; supplier_name:str; overall_score:float; overall_level:RiskLevel
    dimensions:Dict[str,RiskDimension]; evidence:List[Dict[str,Any]]; recommendations:List[str]
    explanation:str; validation:Dict[str,Any]; latency_ms:float; token_estimate:int; token_usage:Dict[str,int]
class ChatRequest(BaseModel):
    supplier_id:str; question:str
class ChatResponse(BaseModel):
    answer:str; supplier_id:str; evidence:List[Dict[str,Any]]; validation:Dict[str,Any]
    latency_ms:float; token_estimate:int; token_usage:Dict[str,int]
