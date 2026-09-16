import time
from pathlib import Path
import pandas as pd
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import *
from app.agents.graph import build_graph
ROOT=Path(__file__).resolve().parents[2]; suppliers=pd.read_csv(ROOT/"data/suppliers.csv"); graph=build_graph(suppliers)
app=FastAPI(title="SupplyGuard AI API",version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
@app.get("/health")
def health():return {"status":"ok","suppliers":len(suppliers)}
@app.get("/suppliers")
def list_suppliers():return suppliers[["supplier_id","supplier_name","country","category"]].to_dict(orient="records")
def execute(sid,q):
    t=time.perf_counter()
    try:s=graph.invoke({"supplier_id":sid,"question":q})
    except ValueError as e:raise HTTPException(404,str(e))
    return s,(time.perf_counter()-t)*1000
@app.get("/risk/{supplier_id}",response_model=SupplierRiskResponse)
def risk(supplier_id):
    s,ms=execute(supplier_id,"overall supplier risk assessment"); u=s.get("token_usage",{})
    dims={k:RiskDimension(score=round(v["score"],1),level=v["level"],drivers=v["drivers"]) for k,v in s["dimensions"].items()}
    return SupplierRiskResponse(supplier_id=supplier_id,supplier_name=s["supplier"]["supplier_name"],overall_score=s["score"],overall_level=s["level"],dimensions=dims,evidence=s["evidence"],recommendations=s["recommendations"],explanation=s["explanation"],validation=s["validation"],latency_ms=round(ms,1),token_estimate=u.get("total_tokens",max(1,len(s["explanation"])//4)),token_usage=u)
@app.post("/chat",response_model=ChatResponse)
def chat(req:ChatRequest):
    s,ms=execute(req.supplier_id,req.question); u=s.get("token_usage",{})
    return ChatResponse(answer=s["explanation"],supplier_id=req.supplier_id,evidence=s["evidence"],validation=s["validation"],latency_ms=round(ms,1),token_estimate=u.get("total_tokens",max(1,len(s["explanation"])//4)),token_usage=u)
