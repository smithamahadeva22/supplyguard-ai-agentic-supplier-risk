from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; DOCS=ROOT/"data"/"documents"
class EvidenceRetriever:
    def __init__(self):
        self.chunks=[]
        for p in DOCS.glob("*.txt"):
            for i,s in enumerate([x.strip() for x in p.read_text(encoding="utf-8").split("\n\n") if x.strip()]):
                self.chunks.append({"supplier_id":p.stem,"source":p.name,"chunk_id":i,"text":s})
        self.backend="keyword"; self.model=None; self.index=None
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            self.model=SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            emb=self.model.encode([c["text"] for c in self.chunks],normalize_embeddings=True)
            self.index=faiss.IndexFlatIP(emb.shape[1]); self.index.add(np.asarray(emb,dtype="float32")); self.backend="faiss"
        except Exception: pass
    def search(self,query,supplier_id,k=4):
        scoped=[c for c in self.chunks if c["supplier_id"]==supplier_id]
        if not scoped:return []
        if self.backend=="faiss":
            q=self.model.encode([query],normalize_embeddings=True)
            scores,ids=self.index.search(np.asarray(q,dtype="float32"),min(len(self.chunks),k*8))
            out=[]
            for score,idx in zip(scores[0],ids[0]):
                if idx>=0 and self.chunks[int(idx)]["supplier_id"]==supplier_id:
                    c=self.chunks[int(idx)]; out.append({"source":c["source"],"chunk_id":c["chunk_id"],"score":round(float(score),4),"snippet":c["text"][:1000]})
                    if len(out)>=k:break
            if out:return out
        terms=set(query.lower().split())
        ranked=sorted(((sum(t in c["text"].lower() for t in terms),c) for c in scoped),key=lambda x:x[0],reverse=True)
        return [{"source":c["source"],"chunk_id":c["chunk_id"],"score":s,"snippet":c["text"][:1000]} for s,c in ranked[:k]]
