from typing import TypedDict,Dict,List,Any
import pandas as pd
from langgraph.graph import StateGraph,END
from app.risk.scoring import calculate_overall
from app.rag.retriever import EvidenceRetriever
from app.llm.provider import LLMProvider
class State(TypedDict,total=False):
    supplier_id:str; question:str; intent:str; supplier:Dict[str,Any]; score:float; level:str
    dimensions:Dict[str,Dict]; evidence:List[Dict]; recommendations:List[str]; validation:Dict[str,Any]
    explanation:str; token_usage:Dict[str,int]
def build_graph(suppliers):
    retriever=EvidenceRetriever(); llm=LLMProvider()
    def load(s):
        x=suppliers[suppliers.supplier_id==s["supplier_id"]]
        if x.empty:raise ValueError(f"Supplier {s['supplier_id']} not found")
        return {"supplier":x.iloc[0].to_dict()}
    def intent(s):
        q=(s.get("question") or "").lower()
        return {"intent":"mitigation" if any(x in q for x in ["action","mitigat","recommend","improve"]) else "evidence" if any(x in q for x in ["why","evidence","event","driver","reason"]) else "risk_assessment"}
    def score(s):
        a,b,c=calculate_overall(pd.Series(s["supplier"])); return {"score":a,"level":b,"dimensions":c}
    def evidence(s):
        return {"evidence":retriever.search(s.get("question") or "overall supplier risk financial delivery quality compliance geographic",s["supplier_id"],4)}
    def recommend(s):
        d=s["dimensions"]; r=[]
        if d["geographic"]["score"]>=60:r.append("Qualify a secondary supplier and reduce single-source dependency.")
        if d["compliance"]["score"]>=60:r.append("Request compliance remediation evidence and confirm certification renewal.")
        if d["financial"]["score"]>=60:r.append("Initiate a supplier financial review and request a 90-day recovery plan.")
        if d["operational"]["score"]>=60:r.append("Increase safety-stock coverage and review delivery SLA commitments.")
        if d["quality"]["score"]>=60:r.append("Launch a focused quality corrective-action review.")
        return {"recommendations":r or ["Continue standard supplier monitoring."]}
    def validate(s):
        expected="LOW" if s["score"]<30 else "MEDIUM" if s["score"]<60 else "HIGH" if s["score"]<80 else "CRITICAL"
        checks={"score_in_range":0<=s["score"]<=100,"level_consistent":expected==s["level"],"evidence_present":bool(s.get("evidence")),"recommendations_present":bool(s.get("recommendations"))}
        return {"validation":{"checks":checks,"passed":all(checks.values())}}
    def synth(s):
        supplier=dict(s["supplier"]); supplier.update({"overall_score":s["score"],"overall_level":s["level"]})
        return {"explanation":llm.synthesize(supplier,s["dimensions"],s["evidence"],s["recommendations"]),"token_usage":dict(llm.last_usage)}
    g=StateGraph(State)
    for n,f in [("load",load),("intent",intent),("score",score),("evidence",evidence),("recommend",recommend),("validate",validate),("synthesize",synth)]:g.add_node(n,f)
    g.set_entry_point("load"); g.add_edge("load","intent"); g.add_edge("intent","score"); g.add_edge("intent","evidence")
    g.add_edge("score","recommend"); g.add_edge("evidence","recommend"); g.add_edge("recommend","validate"); g.add_edge("validate","synthesize"); g.add_edge("synthesize",END)
    return g.compile()
