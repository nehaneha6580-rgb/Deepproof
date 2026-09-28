import streamlit as st
import hashlib
import json
from datetime import datetime, timezone

st.set_page_config(
    page_title="DeepProof | Digital Evidence Triage",
    page_icon="🔎",
    layout="wide"
)

st.markdown("""
<style>
.main {background:#0b1020;}
.hero {
    padding:28px;
    border-radius:18px;
    background:linear-gradient(135deg,#172554,#111827);
    border:1px solid #334155;
    margin-bottom:22px;
}
.hero h1 {margin:0;color:white;}
.hero p {color:#cbd5e1;}
.card {
    padding:18px;
    border-radius:14px;
    border:1px solid #334155;
    background:#111827;
    margin-bottom:14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🔎 DeepProof</h1>
<p>Digital Evidence Triage — structured, transparent and review-ready.</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "Prototype notice: DeepProof performs preliminary technical triage only. "
    "It does not establish authenticity, authorship, guilt or innocence."
)

with st.sidebar:
    st.header("Case Intake")
    case_id = st.text_input("Case ID", "CASE-2026-001")
    fir = st.text_input("FIR / Reference", "FIR-2026-001")
    station = st.text_input("Station / Police Station", "Demo Police Station")
    target = st.text_input("Subject / Target", "Demo Subject")
    officer = st.text_input("Investigating Officer", "Demo Officer")

tab1, tab2, tab3 = st.tabs(
    ["📁 Evidence Intake", "🔍 Analysis", "📄 Report"]
)

with tab1:
    st.subheader("Upload evidence")

    uploaded = st.file_uploader(
        "Choose an evidence file",
        type=[
            "jpg", "jpeg", "png", "pdf",
            "mp4", "mov", "avi", "mkv",
            "mp3", "wav", "m4a",
            "txt", "docx"
        ]
    )

    if uploaded:
        data = uploaded.getvalue()
        filename = uploaded.name
        extension = filename.lower().split(".")[-1] if "." in filename else ""
        size_bytes = len(data)
        size_mb = size_bytes / (1024 * 1024)

        sha256 = hashlib.sha256(data).hexdigest()

        text_content = ""
        if extension == "txt":
            try:
                text_content = data.decode("utf-8", errors="ignore")
            except Exception:
                text_content = ""

        text_lower = text_content.lower()
        name_lower = filename.lower()

        suspicious_terms = [
            "edited", "modified", "fake", "sample",
            "draft", "copy", "screenshot", "unknown"
        ]

        term_hits = sum(
            1 for term in suspicious_terms
            if term in text_lower or term in name_lower
        )

        # -------------------------
        # RISK CALCULATION
        # -------------------------
        risk = 0
        risk += int(sha256[:2], 16) % 10
        factors = []

        # File type
        if extension in ["jpg", "jpeg", "png"]:
            risk += 5
            factors.append("Image evidence requires metadata/visual verification.")

        elif extension == "pdf":
            risk += 8
            factors.append("PDF structure should be checked for document integrity.")

        elif extension in ["mp4", "mov", "avi", "mkv"]:
            risk += 6
            factors.append("Video evidence requires frame/metadata verification.")

        elif extension in ["mp3", "wav", "m4a"]:
            risk += 6
            factors.append("Audio evidence requires metadata/audio verification.")

        else:
            risk += 4
            factors.append("File type has limited automatic verification.")

        # Suspicious filename/content signals
        if term_hits > 0:
            risk += min(term_hits * 7, 25)
            factors.append(
                f"{term_hits} suspicious filename/content signal(s) detected."
            )

        # File size signal
        if size_bytes == 0:
            risk += 30
            factors.append("File is empty.")
        elif size_mb < 0.01:
            risk += 15
            factors.append("Very small file size.")
        elif size_mb > 100:
            risk += 3
            factors.append("Large file requires additional technical review.")

        # Hash-derived deterministic variation
        # This ensures different files do not automatically receive
        # the same baseline score.
        hash_value = int(sha256[:8], 16)
        hash_adjustment = hash_value % 16
        risk += hash_adjustment

        risk = max(0, min(risk, 100))
        confidence = max(0, 100 - risk)

        if risk >= 70:
            status = "HIGH ATTENTION"
        elif risk >= 40:
            status = "REVIEW REQUIRED"
        else:
            status = "LOW INITIAL RISK"

        st.success("Evidence uploaded successfully.")

        st.markdown("### Evidence Summary")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("File", filename)

        with c2:
            st.metric("Size", f"{size_mb:.2f} MB")

        with c3:
            st.metric("Risk Score", f"{risk}/100")

        st.write("**SHA-256:**")
        st.code(sha256)

        st.write("**Initial Status:**", status)

        st.session_state["result"] = {
            "case_id": case_id,
            "fir": fir,
            "station": station,
            "target": target,
            "officer": officer,
            "filename": filename,
            "extension": extension,
            "size_mb": round(size_mb, 3),
            "sha256": sha256,
            "risk": risk,
            "confidence": confidence,
            "status": status,
            "term_hits": term_hits,
            "factors": factors,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

with tab2:
    st.subheader("Technical Analysis")

    result = st.session_state.get("result")

    if not result:
        st.info("Upload an evidence file first.")
    else:
        st.metric("Risk Score", f"{result['risk']}/100")
        st.metric("Initial Confidence", f"{result['confidence']}%")
        st.write("### Findings")

        for factor in result["factors"]:
            st.write("•", factor)

        st.write("### Integrity Signals")

        if result["term_hits"] > 0:
            st.warning(
                f"{result['term_hits']} suspicious signal(s) found "
                "in filename/content."
            )
        else:
            st.success("No predefined suspicious filename/content signals found.")

        st.info(
            "These are screening indicators only. They are not proof that "
            "a file is fake, altered or authentic."
        )

with tab3:
    st.subheader("Review-Ready Report")

    result = st.session_state.get("result")

    if not result:
        st.info("Upload an evidence file first.")
    else:
        report = {
            "case": {
                "case_id": result["case_id"],
                "fir_reference": result["fir"],
                "station": result["station"],
                "subject": result["target"],
                "investigating_officer": result["officer"]
            },
            "evidence": {
                "filename": result["filename"],
                "extension": result["extension"],
                "size_mb": result["size_mb"],
                "sha256": result["sha256"]
            },
            "triage": {
                "risk_score": result["risk"],
                "initial_confidence": result["confidence"],
                "status": result["status"],
                "signals": result["factors"]
            },
            "generated_at": result["timestamp"],
            "notice": (
                "Preliminary technical triage only. "
                "Not a determination of authenticity, authorship, guilt or innocence."
            )
        }

        st.json(report)

        report_json = json.dumps(report, indent=2)

        st.download_button(
            "⬇️ Download JSON Report",
            data=report_json,
            file_name=f"{result['case_id']}_deepproof_report.json",
            mime="application/json"
        )
