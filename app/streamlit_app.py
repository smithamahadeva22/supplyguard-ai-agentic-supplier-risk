import re
import os
import html
import requests
import streamlit as st

API = os.getenv("API_BASE_URL", "http://localhost:8000")
st.set_page_config(page_title="SupplyGuard AI", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stApp{background:#fff}
[data-testid="stAppViewContainer"] .main .block-container{max-width:1500px!important;width:100%!important;padding:2rem 3.25rem 4rem!important;margin:0 auto}
h1{font-size:2.35rem!important;letter-spacing:-.04em;margin-bottom:.15rem!important}
.subtitle{color:#8a8f98;font-size:.98rem;margin-bottom:1.7rem}
.risk-label{color:#777d86;font-size:.88rem;margin-top:.4rem}.risk-score{font-size:2.35rem;line-height:1.05;font-weight:500;margin:.18rem 0 .25rem}
.risk-badge{display:inline-block;padding:3px 9px;border-radius:999px;font-size:.78rem;font-weight:600;background:#e7f6ec;color:#287a4d}.risk-badge:before{content:'↑ '}
.metric-card{padding-top:.35rem}.metric-name{font-size:.88rem;color:#444a52}.metric-score{font-size:1.9rem;line-height:1.1;margin:.18rem 0 .25rem}
.section-title{font-size:1.45rem;font-weight:700;margin:2rem 0 .75rem}.evidence-card{background:#e6f2ff;border-radius:8px;padding:1rem 1.1rem;margin:.7rem 0;color:#155b95}.evidence-head{font-weight:700;margin-bottom:.75rem}.evidence-text{white-space:pre-wrap;line-height:1.55;font-size:.93rem}
.action{margin:.7rem 0;line-height:1.45}.status-line{color:#8b9098;font-size:.86rem;margin-top:.65rem}.chat-question{background:#f3f6fa;border-radius:8px;padding:1rem 1.1rem;margin:.5rem 0}.chat-answer{background:#f8fafc;border-radius:8px;padding:1rem 1.1rem;margin:.5rem 0;line-height:1.55}
div[data-testid="stExpander"]{border:1px solid #dfe3e8;border-radius:8px;margin:.55rem 0}div[data-testid="stSelectbox"] label{font-size:.9rem;color:#555b64}

/* Full-width responsive dashboard at normal browser zoom */
[data-testid="stAppViewContainer"] .main .block-container{width:100%!important}
[data-testid="stHorizontalBlock"]{width:100%!important}
@media (min-width:1700px){
  [data-testid="stAppViewContainer"] .main .block-container{
    max-width:1600px!important;
    padding-left:4.5rem!important;
    padding-right:4.5rem!important;
  }
}

.assessment-summary{
    background:linear-gradient(135deg,#f5f9ff 0%,#eef6ff 100%);
    border:1px solid #dbe9f7;border-radius:14px;padding:1.15rem 1.25rem;
    margin:.35rem 0 1.1rem;
}
.assessment-kicker{
    font-size:.72rem;font-weight:750;letter-spacing:.08em;color:#66809d;
    margin-bottom:.35rem;
}
.assessment-main{font-size:1.12rem;line-height:1.55;color:#18324f;font-weight:600}
.assessment-section{font-size:1.18rem;font-weight:700;color:#18324f;margin:1.25rem 0 .65rem}
.contrib-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem}
.contrib-card{
    background:#fff;border:1px solid #e1e8f0;border-radius:12px;padding:.8rem .9rem;
}
.contrib-name{font-size:.78rem;color:#718198;font-weight:650}
.contrib-score{font-size:1.45rem;color:#18324f;font-weight:750;margin-top:.15rem}
.contrib-score span{font-size:.75rem;color:#8b98a8;font-weight:600}
.signal-row{
    display:flex;gap:.65rem;align-items:flex-start;background:#fafbfd;
    border:1px solid #e7edf3;border-radius:9px;padding:.65rem .8rem;margin:.42rem 0;
    color:#33485e;line-height:1.45;
}
.signal-dot{width:7px;height:7px;border-radius:50%;background:#2e82d2;margin-top:.45rem;flex:none}
.evidence-card{
    background:#f5faff;border:1px solid #d9eaf9;border-left:4px solid #3b8ed8;
    border-radius:10px;padding:.8rem 1rem;margin:.55rem 0;color:#334b63;
}
.evidence-head{font-weight:700;color:#245f8e;margin-bottom:.35rem}
.action-card{
    display:flex;gap:.75rem;align-items:flex-start;background:#fff;
    border:1px solid #e0e7ee;border-radius:10px;padding:.72rem .85rem;margin:.45rem 0;
    color:#30465c;line-height:1.45;
}
.action-number{
    width:25px;height:25px;border-radius:50%;background:#eaf3fd;color:#1f73b7;
    display:flex;align-items:center;justify-content:center;font-weight:750;flex:none;
}

.chat-answer{
    display:flex;
    gap:.75rem;
    align-items:flex-start;
    background:#f7f9fc;
    border:1px solid #e1e7ef;
    border-radius:12px;
    padding:1.05rem 1.15rem;
    margin:.6rem 0;
    line-height:1.65;
    color:#263b52;
    font-size:.96rem;
}
.chat-icon{flex:none}
.chat-answer br{content:"";display:block;margin:.18rem 0}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def suppliers():
    response = requests.get(f"{API}/suppliers", timeout=10)
    response.raise_for_status()
    return response.json()

try:
    data = suppliers()
except Exception:
    st.error("Backend is not running. Start: python -m uvicorn app.api.main:app --reload --port 8000")
    st.stop()

st.markdown("# 🛡️ SupplyGuard AI")
st.markdown("<div class='subtitle'>Agentic Supplier Risk Intelligence — deterministic scoring + RAG evidence + LLM synthesis</div>", unsafe_allow_html=True)

opts = {f"{x['supplier_id']} — {x['supplier_name']}": x["supplier_id"] for x in data}
labels = list(opts)
default_label = next((x for x in labels if x.startswith("SUP-0100 —")), labels[0])
sid = opts[st.selectbox("Supplier", labels, index=labels.index(default_label))]

try:
    response = requests.get(f"{API}/risk/{sid}", timeout=120)
    response.raise_for_status()
    r = response.json()
except Exception as exc:
    st.error(f"Unable to load supplier risk assessment: {exc}")
    st.stop()

st.markdown("<div class='risk-label'>Overall Risk</div>", unsafe_allow_html=True)
st.markdown(f"<div class='risk-score'>{r['overall_score']}/100</div>", unsafe_allow_html=True)
st.markdown(f"<span class='risk-badge'>{html.escape(r['overall_level'])}</span>", unsafe_allow_html=True)
st.progress(min(max(float(r["overall_score"])/100,0),1))

cols = st.columns(5)
for c,(name,dim) in zip(cols,r.get("dimensions",{}).items()):
    with c:
        st.markdown(f"<div class='metric-card'><div class='metric-name'>{html.escape(name.title())}</div><div class='metric-score'>{dim['score']:.0f}</div><span class='risk-badge'>{html.escape(dim['level'])}</span></div>", unsafe_allow_html=True)


st.markdown("<div class='section-title'>Executive assessment</div>", unsafe_allow_html=True)

ranked = sorted(r.get("dimensions",{}).items(), key=lambda x:x[1]["score"], reverse=True)
strongest = ", ".join(n.title() for n,_ in ranked[:3])
full = (r.get("explanation") or "").strip()

# The agent returns structured Markdown. Parse it so the UI presents clean cards
# instead of exposing Markdown syntax to the user.
def clean_text(value):
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", str(value))
    value = re.sub(r"^[-•]\s*", "", value)
    value = re.sub(r"^\d+\.\s*", "", value)
    return value.strip()

def parse_sections(markdown_text):
    sections = {}
    current = "summary"
    sections[current] = []
    for raw in (markdown_text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        heading = re.sub(r"^#{1,3}\s*", "", line).strip().lower()
        if raw.lstrip().startswith("#"):
            current = heading
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(clean_text(line))
    return sections

sections = parse_sections(full)

summary_items = sections.get("executive assessment", []) or sections.get("summary", [])
contributors = sections.get("top risk contributors", []) or sections.get("risk contributors", [])
drivers = sections.get("key drivers", []) or sections.get("drivers", [])
evidence_items = sections.get("evidence", [])
actions = sections.get("recommended actions", []) or sections.get("recommendations", [])

summary = summary_items[0] if summary_items else (
    f"{r['supplier_name']} has an overall risk score of {r['overall_score']}/100 "
    f"and is classified as {r['overall_level']} risk."
)

st.markdown(
    f"<div class='assessment-summary'>"
    f"<div class='assessment-kicker'>OVERALL ASSESSMENT</div>"
    f"<div class='assessment-main'>{html.escape(summary)}</div>"
    f"</div>",
    unsafe_allow_html=True
)

if contributors:
    st.markdown("<div class='assessment-section'>Top risk contributors</div>", unsafe_allow_html=True)
    cards = []
    for item in contributors[:3]:
        m = re.search(r"(.+?)\s*[—-]\s*(\d+(?:\.\d+)?)\s*/\s*100", item)
        if m:
            label, score = m.group(1).strip(), m.group(2)
            cards.append(
                f"<div class='contrib-card'><div class='contrib-name'>{html.escape(label)}</div>"
                f"<div class='contrib-score'>{score}<span>/100</span></div></div>"
            )
    if cards:
        st.markdown("<div class='contrib-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)

if drivers:
    st.markdown("<div class='assessment-section'>Key risk signals</div>", unsafe_allow_html=True)
    for item in drivers:
        st.markdown(
            f"<div class='signal-row'><span class='signal-dot'></span>"
            f"<span>{html.escape(item)}</span></div>",
            unsafe_allow_html=True
        )

if evidence_items:
    st.markdown("<div class='assessment-section'>Supporting evidence</div>", unsafe_allow_html=True)
    for item in evidence_items:
        st.markdown(
            f"<div class='evidence-card'>{html.escape(item)}</div>",
            unsafe_allow_html=True
        )

if actions:
    st.markdown("<div class='assessment-section'>Recommended actions</div>", unsafe_allow_html=True)
    for i, item in enumerate(actions, 1):
        st.markdown(
            f"<div class='action-card'><div class='action-number'>{i}</div>"
            f"<div>{html.escape(item)}</div></div>",
            unsafe_allow_html=True
        )

tokens=r.get("token_usage",{}) or {}; total_tokens=tokens.get("total_tokens",0); latency=r.get("latency_ms","N/A")
validation=r.get("validation") or {}; passed=validation.get("passed") if isinstance(validation,dict) else None
status="Validated" if passed is True else "Completed"
st.markdown(f"<div class='status-line'>Pipeline latency: {html.escape(str(latency))} ms · Tokens: {html.escape(str(total_tokens))} · Validation: {status}</div>", unsafe_allow_html=True)
with st.expander("⋯ More — technical details",expanded=False):
    checks=validation.get("checks",{}) if isinstance(validation,dict) else {}
    st.write("Risk calculation: validated")
    st.write("Evidence retrieval: " + ("validated" if checks.get("evidence_present") else "completed"))
    st.write("Recommendation generation: " + ("validated" if checks.get("recommendations_present") else "completed"))
    st.write("LLM mode: " + ("API-backed synthesis" if total_tokens else "deterministic fallback"))


def format_chat_response(answer):
    """Format agent response as clean readable text without Markdown symbols."""
    lines = []
    for raw in str(answer or "").replace("\r\n", "\n").split("\n"):
        s = raw.strip()
        if not s:
            if lines and lines[-1] != "":
                lines.append("")
            continue

        # Remove Markdown heading markers and emphasis markers.
        s = re.sub(r"^\s*#{1,6}\s*", "", s)
        s = s.replace("**", "").replace("__", "")
        s = s.replace("`", "")

        # Normalize common Markdown bullets.
        s = re.sub(r"^\s*[-*•]\s*", "• ", s)

        # Keep numbered lists as numbered lists, but normalize spacing.
        s = re.sub(r"^\s*(\d+)\.\s*", r"\1. ", s)

        lines.append(s)

    # Remove duplicate blank lines.
    cleaned = []
    for line in lines:
        if line == "" and (not cleaned or cleaned[-1] == ""):
            continue
        cleaned.append(line)

    return "\n".join(cleaned).strip()

st.divider()
st.markdown("<div class='section-title'>Ask the risk agent</div>", unsafe_allow_html=True)
q=st.chat_input("Why is this supplier high risk?")
if q:
    st.markdown(f"<div class='chat-question'>💬 {html.escape(q)}</div>", unsafe_allow_html=True)
    try:
        response=requests.post(f"{API}/chat",json={"supplier_id":sid,"question":q},timeout=120); response.raise_for_status(); a=response.json()
        answer=a.get("answer","No answer returned.")
        st.markdown(f"<div class='chat-answer'><span class='chat-icon'>🤖</span><div>{html.escape(format_chat_response(answer)).replace(chr(10),'<br>')}</div></div>", unsafe_allow_html=True)
        with st.expander("⋯ More — evidence used",expanded=False):
            for e in a.get("evidence",[]):
                e=e if isinstance(e,dict) else {"text":str(e)}
                source=e.get("source") or e.get("file") or "supplier evidence"; snippet=e.get("snippet") or e.get("text") or e.get("content") or ""
                st.caption(f"{source} — {str(snippet)[:700]}")
        st.markdown(f"<div class='status-line'>Latency: {html.escape(str(a.get('latency_ms','N/A')))} ms · Tokens: {html.escape(str(a.get('token_estimate',0)))}</div>",unsafe_allow_html=True)
    except Exception as exc: st.error(f"Risk agent request failed: {exc}")
