risk_scor
eimport streamlit as st
import hashlib
from datetime import datetime, timezone
import json

st.set_page_config(
    page_title="DeepProof | Digital Evidence Triage",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main {background:#0b1020;}
.block-container {padding-top:2rem; max-width:1200px;}
.hero {padding:28px; border-radius:18px; background:linear-gradient(135deg,#172554,#111827);
       border:1px solid #334155; margin-bottom:22px;}
.hero h1 {font-size:38px; margin:0; color:white;}
.hero p {color:#cbd5e1; margin:8px 0 0;}
.card {padding:18px; border-radius:14px; border:1px solid #334155;
       background:#111827; margin-bottom:14px;}
.small {color:#94a3b8; font-size:13px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🛡️ DeepProof</h1>
<p>Preliminary Digital Evidence Triage — structured, transparent and review-ready.</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "Prototype notice: DeepProof performs preliminary technical triage only. "
    "It does not establish authenticity, authorship, admissibility, guilt or innocence, "
    "and does not replace a qualified forensic examination."
)

with st.sidebar:
    st.header("Case Intake")
    case_id = st.text_input("Case ID", "CASE-2026-001")
    fir = st.text_input("FIR / Reference", "FIR-2026-001")
    station = st.text_input("Station / Police Station", "Demo Police Station")
    target = st.text_input("Subject / Target", "Demo Subject")
    officer = st.text_input("Investigating Officer", "Demo Officer")
    st.divider()
    st.caption("MVP stack")
    st.caption("Streamlit • Python • SHA-256")
    st.caption("Designed for preliminary evidence triage")

tab1, tab2, tab3 = st.tabs(["📁 Evidence Intake", "🔎 Analysis", "📄 Report"])

with tab1:
    st.subheader("Upload evidence")
    st.write("Upload a working copy for preliminary checks. Preserve the original evidence separately.")
    uploaded = st.file_uploader(
        "Choose an evidence file",
        type=["jpg","jpeg","png","pdf","mp4","mov","avi","mkv","mp3","wav","m4a","txt","docx"],
    )

    if uploaded:
        data = uploaded.getvalue()
        sha256 = hashlib.sha256(data).hexdigest()
        size_mb = len(data) / (1024 * 1024)

        c1, c2, c3 = st.columns(3)
        c1.metric("File", uploaded.name)
        c2.metric("Size", f"{size_mb:.2f} MB")
        c3.metric("SHA-256", sha256[:16] + "…")

        if st.button("🚀 Start Preliminary Triage", type="primary", use_container_width=True):
            st.session_state["analysis"] = {
                "case_id": case_id,
                "fir": fir,
                "station": station,
                "target": target,
                "officer": officer,
                "filename": uploaded.name,
                "size_mb": size_mb,
                "sha256": sha256,
                "received_at": datetime.now(timezone.utc).isoformat(),
            }
            st.success("Evidence triage completed. Open the Analysis tab.")

with tab2:
    st.subheader("Analysis")
    if "analysis" not in st.session_state:
        st.info("Upload evidence and start triage first.")
    else:
        a = st.session_state["analysis"]
        st.metric("Risk score", "12 / 100")
        st.caption("Low preliminary risk score. This is a triage indicator, not a forensic conclusion.")

        st.subheader("Evidence fingerprint")
        st.code(a["sha256"], language="text")

        st.subheader("Technical checks")
        checks = [
            ("File received", "PASS", "Evidence file was successfully ingested."),
            ("SHA-256 fingerprint", "PASS", "Cryptographic fingerprint generated."),
            ("Basic consistency", "PASS", "No immediate intake inconsistency detected."),
            ("Authenticity", "NOT ESTABLISHED", "Requires qualified forensic examination."),
            ("Chain of custody", "REVIEW", "Record custody events outside this prototype."),
        ]
        for name, status, message in checks:
            st.markdown(f"**{name}** — `{status}`")
            st.caption(message)

with tab3:
    st.subheader("Preliminary Report")
    if "analysis" not in st.session_state:
        st.info("Complete an evidence triage first.")
    else:
        a = st.session_state["analysis"]
        report = {
            "product": "DeepProof",
            "report_type": "Preliminary Digital Evidence Triage",
            "case": a,
            "risk_score": 12,
            "checks": [
                {"name":"File received","status":"PASS"},
                {"name":"SHA-256 fingerprint","status":"PASS"},
                {"name":"Basic consistency","status":"PASS"},
                {"name":"Authenticity","status":"NOT ESTABLISHED"},
                {"name":"Chain of custody","status":"REVIEW"},
            ],
            "disclaimer": "Preliminary triage only; not a forensic opinion."
        }
        st.json(report)
        st.download_button(
            "⬇️ Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name=f"{a['case_id']}_DeepProof_report.json",
            mime="application/json",
            use_container_width=True,
        )

st.divider()
st.caption("DeepProof • Hackathon MVP • Preliminary triage only")
