import pandas as pd
from app.risk.scoring import calculate_overall,level
def test_levels():
    assert level(10)=="LOW";assert level(45)=="MEDIUM";assert level(70)=="HIGH";assert level(90)=="CRITICAL"
def test_demo_supplier():
    r=pd.Series({"financial_score":35,"debt_ratio":.78,"revenue_growth_pct":-12.5,"cash_flow_score":30,"on_time_delivery_pct":70,"average_delay_days":12,"defect_rate_pct":7,"quality_score":45,"compliance_score":30,"audit_score":35,"certification_status":"Expiring","geopolitical_risk":78,"single_source_dependency":90})
    s,l,d=calculate_overall(r);assert s>=60;assert l=="HIGH";assert d["compliance"]["drivers"]
