from pathlib import Path
import random,pandas as pd
from datetime import date,timedelta
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/"data"; DOCS=DATA/"documents"
def generate():
    random.seed(42); DATA.mkdir(exist_ok=True); DOCS.mkdir(exist_ok=True)
    countries=["India","Vietnam","China","Germany","Mexico","Poland","USA","Brazil"]
    cats=["Electronics","Metals","Plastics","Aerospace","Packaging","Chemicals"]
    rows=[]
    for i in range(1,101):
        rows.append({"supplier_id":f"SUP-{i:04d}","supplier_name":f"{random.choice(['Apex','Prime','Global','Nova','Vertex','Summit','Orion','Delta'])} {random.choice(['Components','Industries','Manufacturing','Systems','Materials'])} {i}",
        "country":random.choice(countries),"category":random.choice(cats),"annual_spend_usd":random.randint(100000,8000000),
        "supplier_tenure_years":round(random.uniform(1,18),1),"financial_score":round(random.uniform(15,95),1),
        "debt_ratio":round(random.uniform(.15,.85),2),"revenue_growth_pct":round(random.uniform(-18,20),1),
        "cash_flow_score":round(random.uniform(15,95),1),"on_time_delivery_pct":round(random.uniform(65,99),1),
        "average_delay_days":round(random.uniform(.5,15),1),"defect_rate_pct":round(random.uniform(.2,8.5),2),
        "quality_score":round(random.uniform(20,98),1),"compliance_score":round(random.uniform(20,98),1),
        "audit_score":round(random.uniform(20,98),1),"certification_status":random.choice(["Valid","Valid","Valid","Expiring","Missing"]),
        "geopolitical_risk":round(random.uniform(10,90),1),"single_source_dependency":round(random.uniform(5,95),1),
        "previous_incidents":random.randint(0,6)})
    next(x for x in rows if x["supplier_id"]=="SUP-0100").update({
        "supplier_name":"Apex Components 100","country":"Vietnam","category":"Electronics","annual_spend_usd":5800000,
        "financial_score":35,"debt_ratio":.78,"revenue_growth_pct":-12.5,"cash_flow_score":30,
        "on_time_delivery_pct":70,"average_delay_days":12.0,"defect_rate_pct":7.0,"quality_score":45,
        "compliance_score":30,"audit_score":35,"certification_status":"Expiring","geopolitical_risk":78,
        "single_source_dependency":90,"previous_incidents":4})
    df=pd.DataFrame(rows); df.to_csv(DATA/"suppliers.csv",index=False)
    ev=[]; base=date(2026,1,1)
    for i in range(1,101):
        sid=f"SUP-{i:04d}"
        for _ in range(random.randint(1,4)):
            typ=random.choice(["Delivery","Quality","Financial","Compliance","Geopolitical"])
            sev=random.choice(["LOW","MEDIUM","HIGH"])
            ev.append({"supplier_id":sid,"event_date":(base+timedelta(days=random.randint(0,250))).isoformat(),
                       "event_type":typ,"severity":sev,"description":f"{sev.title()} {typ.lower()} event recorded during supplier monitoring."})
    ev += [
      {"supplier_id":"SUP-0100","event_date":"2026-07-12","event_type":"Compliance","severity":"HIGH","description":"Compliance audit identified unresolved corrective actions."},
      {"supplier_id":"SUP-0100","event_date":"2026-08-03","event_type":"Delivery","severity":"HIGH","description":"On-time delivery declined to 70% and average delay increased to 12.0 days."},
      {"supplier_id":"SUP-0100","event_date":"2026-08-27","event_type":"Financial","severity":"HIGH","description":"Cash-flow score deteriorated and debt ratio reached 78%."},
      {"supplier_id":"SUP-0100","event_date":"2026-09-05","event_type":"Geopolitical","severity":"HIGH","description":"Port disruption affects the supplier's primary export route."},
      {"supplier_id":"SUP-0100","event_date":"2026-09-07","event_type":"Quality","severity":"HIGH","description":"Quality review recorded elevated defect rate and corrective-action requirement."}]
    edf=pd.DataFrame(ev); edf.to_csv(DATA/"supplier_events.csv",index=False)
    for _,r in df.iterrows():
        e=edf[edf.supplier_id==r.supplier_id].sort_values("event_date").tail(5)
        lines="\n".join(f"- {x.event_date}: {x.event_type} ({x.severity}) — {x.description}" for _,x in e.iterrows())
        txt=f"""Supplier Risk Review — {r.supplier_name}
Supplier ID: {r.supplier_id}
Country: {r.country}
Category: {r.category}
Annual Spend: ${r.annual_spend_usd:,.0f}

Financial indicators:
Financial score {r.financial_score}/100, debt ratio {r.debt_ratio:.0%}, revenue growth {r.revenue_growth_pct:.1f}%, cash-flow score {r.cash_flow_score}/100.

Operational indicators:
On-time delivery {r.on_time_delivery_pct:.1f}%, average delay {r.average_delay_days:.1f} days.

Quality indicators:
Defect rate {r.defect_rate_pct:.2f}%, quality score {r.quality_score}/100.

Compliance indicators:
Compliance score {r.compliance_score}/100, audit score {r.audit_score}/100, certification status {r.certification_status}.

Concentration and geographic exposure:
Geopolitical risk {r.geopolitical_risk}/100, single-source dependency {r.single_source_dependency:.1f}%.

Recent events:
{lines}"""
        (DOCS/f"{r.supplier_id}.txt").write_text(txt,encoding="utf-8")
if __name__=="__main__":generate()
