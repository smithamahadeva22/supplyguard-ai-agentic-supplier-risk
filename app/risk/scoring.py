WEIGHTS={"financial":.30,"operational":.25,"quality":.20,"compliance":.15,"geographic":.10}
def level(s): return "LOW" if s<30 else "MEDIUM" if s<60 else "HIGH" if s<80 else "CRITICAL"
def clamp(x): return max(0,min(100,float(x)))
def calculate_overall(r):
    d={
      "financial":{"score":clamp(.45*(100-r.financial_score)+.25*r.debt_ratio*100+.15*max(0,-r.revenue_growth_pct)*3+.15*(100-r.cash_flow_score)),"level":"","drivers":[]},
      "operational":{"score":clamp(.55*(100-r.on_time_delivery_pct)+.45*r.average_delay_days*5),"level":"","drivers":[]},
      "quality":{"score":clamp(.60*(100-r.quality_score)+.40*r.defect_rate_pct*10),"level":"","drivers":[]},
      "compliance":{"score":clamp(.55*(100-r.compliance_score)+.35*(100-r.audit_score)+(10 if r.certification_status!="Valid" else 0)),"level":"","drivers":[]},
      "geographic":{"score":clamp(.60*r.geopolitical_risk+.40*r.single_source_dependency),"level":"","drivers":[]}}
    for x in d:d[x]["level"]=level(d[x]["score"])
    d["financial"]["drivers"]=[x for x in [
      f"Debt ratio is elevated at {r.debt_ratio:.0%}." if r.debt_ratio>.60 else "",
      f"Revenue growth is negative at {r.revenue_growth_pct:.1f}%." if r.revenue_growth_pct<0 else "",
      f"Cash-flow score is weak at {r.cash_flow_score:.0f}/100." if r.cash_flow_score<55 else ""] if x]
    d["operational"]["drivers"]=[x for x in [
      f"On-time delivery is {r.on_time_delivery_pct:.1f}%." if r.on_time_delivery_pct<85 else "",
      f"Average delivery delay is {r.average_delay_days:.1f} days." if r.average_delay_days>6 else ""] if x]
    d["quality"]["drivers"]=[x for x in [
      f"Defect rate is {r.defect_rate_pct:.2f}%." if r.defect_rate_pct>4 else "",
      f"Quality score is {r.quality_score:.0f}/100." if r.quality_score<70 else ""] if x]
    d["compliance"]["drivers"]=[x for x in [
      f"Compliance score is {r.compliance_score:.0f}/100." if r.compliance_score<60 else "",
      f"Audit score is {r.audit_score:.0f}/100." if r.audit_score<60 else "",
      f"Certification status is {r.certification_status}." if r.certification_status!="Valid" else ""] if x]
    d["geographic"]["drivers"]=[x for x in [
      f"Geopolitical risk is {r.geopolitical_risk:.0f}/100." if r.geopolitical_risk>60 else "",
      f"Single-source dependency is {r.single_source_dependency:.0f}%." if r.single_source_dependency>70 else ""] if x]
    score=round(sum(WEIGHTS[k]*d[k]["score"] for k in WEIGHTS),1)
    return score,level(score),d
