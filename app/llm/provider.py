import os
class LLMProvider:
    def __init__(self):
        self.api_key=os.getenv("OPENAI_API_KEY"); self.model=os.getenv("OPENAI_MODEL","gpt-4o-mini")
        self.client=None; self.last_usage={"prompt_tokens":0,"completion_tokens":0,"total_tokens":0}
        if self.api_key:
            try:
                from openai import OpenAI
                self.client=OpenAI(api_key=self.api_key)
            except Exception: pass
    def synthesize(self,supplier,dimensions,evidence,recommendations):
        top=sorted(dimensions.items(),key=lambda x:x[1]["score"],reverse=True)[:3]
        drivers=[d for _,v in top for d in v["drivers"][:2]]
        if not self.client:
            ev="\n".join(f"- {e['source']} / chunk {e['chunk_id']}: {e['snippet'][:450]}" for e in evidence)
            return (f"## Executive Assessment\n{supplier['supplier_name']} is **{supplier['overall_level']} risk** with an overall score of **{supplier['overall_score']}/100**.\n\n"
                    f"## Top Risk Contributors\n"+ "\n".join(f"{i}. **{n.title()}** — {v['score']:.1f}/100" for i,(n,v) in enumerate(top,1))+
                    "\n\n## Key Drivers\n"+"\n".join(f"- {d}" for d in drivers)+
                    "\n\n## Evidence\n"+ev+
                    "\n\n## Recommended Actions\n"+"\n".join(f"{i}. {x}" for i,x in enumerate(recommendations,1))+
                    "\n\n## Decision Guidance\nTreat this supplier as a high-priority mitigation case. Prioritize concentration and compliance controls while monitoring financial, delivery and quality recovery.")
        context="\n".join(f"[{e['source']} | chunk {e['chunk_id']}] {e['snippet'][:700]}" for e in evidence)
        prompt=f"""You are an enterprise procurement risk analyst. Use ONLY the facts and evidence below. Do not invent facts.
Return headings: EXECUTIVE ASSESSMENT, TOP RISK CONTRIBUTORS, KEY DRIVERS, EVIDENCE, RECOMMENDED ACTIONS, DECISION GUIDANCE.
Supplier: {supplier['supplier_name']}
Score: {supplier['overall_score']}/100
Level: {supplier['overall_level']}
Dimensions: {dimensions}
Evidence:
{context}
Actions: {recommendations}"""
        r=self.client.chat.completions.create(model=self.model,temperature=.1,max_tokens=650,
          messages=[{"role":"system","content":"You are a precise evidence-grounded enterprise supply-chain risk analyst."},{"role":"user","content":prompt}])
        if r.usage:
            self.last_usage={"prompt_tokens":r.usage.prompt_tokens or 0,"completion_tokens":r.usage.completion_tokens or 0,"total_tokens":r.usage.total_tokens or 0}
        return r.choices[0].message.content
