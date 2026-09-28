import streamlit as st
import hashlib
import re
from datetime import datetime, timezone

st.set_page_config(
    page_title="DeepProof | Digital Evidence Triage",
    page_icon="🔎",
    layout="wide",
)

# -----------------------------
# Helpers
# -----------------------------
SUSPICIOUS_TERMS = [
    "forged", "fake", "tampered", "altered", "fraud", "scam",
    "malware", "virus", "phishing", "stolen", "counterfeit",
    "edited", "manipulated", "unauthorized"
]

def analyze_evidence(uploaded_file):
    data = uploaded_file.getvalue()
    filename = uploaded_file.name
    size_bytes = len(data)
    size_mb = size_bytes / (1024 * 1024)
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else "unknown"

    sha256 = hashlib.sha256(data).hexdigest()
    text = ""
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        text = ""

    lower_text = text.lower()
    lower_name = filename.lower()

    suspicious_hits = []
    for term in SUSPICIOUS_TERMS:
        if term in lower_name or term in lower_text:
            suspicious_hits.append(term)

    signals = []
    score = 0

    # Filename/content signals
    if suspicious_hits:
        score += min(30, len(suspicious_hits) * 7)
        signals.append(
            f"Suspicious indicator term(s): {', '.join(suspicious_hits[:6])}"
        )

    # File-size signals
    if size_bytes == 0:
        score += 35
        signals.append("File is empty.")
    elif size_bytes < 1024:
        score += 12
        signals.append("Very small file; limited evidence may be available.")
    elif size_mb > 100:
        score += 5
        signals.append("Large file; additional technical review may be useful.")

    # Type-specific checks
    if extension in {"jpg", "jpeg", "png"}:
        score += 2
        signals.append("Image evidence: visual and metadata verification recommended.")
    elif extension == "pdf":
        score += 3
        signals.append("PDF evidence: structure, metadata and page-level review recommended.")
    elif extension in {"mp4", "mov", "avi", "mkv"}:
        score += 3
        signals.append("Video evidence: frame, codec and metadata verification recommended.")
    elif extension in {"mp3", "wav", "m4a"}:
        score += 3
        signals.append("Audio evidence: metadata and waveform verification recommended.")
    elif extension in {"txt", "doc", "docx"}:
        signals.append("Text/document evidence: content and metadata review available.")
    else:
        score += 4
        signals.append("File type has limited automatic verification.")

    # Deterministic content-derived variation.
    # This makes different files produce different baseline scores.
    hash_component = int(sha256[:8], 16) % 16
    score += hash_component

    # Basic structural signals for text-like files
    if text:
        lines = [x for x in text.splitlines() if x.strip()]
        if len(lines) >= 3:
            signals.append(f"Readable text detected ({len(lines)} non-empty lines).")
        if re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text):
            signals.append("Date-like fields detected.")
        if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I):
            signals.append("Email-like fields detected.")
        if re.search(r"\b(?:signature|signed|signatory)\b", lower_text):
            signals.append("Signature-related wording detected.")

    score = max(0, min(100, score))

    if score >= 70:
        status = "HIGH ATTENTION"
        status_text = "High-risk indicators detected. Human forensic review is recommended."
    elif score >= 40:
        status = "REVIEW REQUIRED"
        status_text = "Some indicators require human review before relying on the evidence."
    else:
        status = "LOW INITIAL RISK"
        status_text = "No strong automated red flags were detected. This is not proof of authenticity."

    confidence = max(0, 100 - score)

    return {
        "filename": filename,
        "extension": extension,
        "size_bytes": size_bytes,
        "size_mb": round(size_mb, 3),
        "sha256": sha256,
        "score": score,
        "confidence": confidence,
        "status": status,
        "status_text": status_text,
        "signals": signals,
        "suspicious_hits": suspicious_hits,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <style>
    .hero {
        padding: 24px;
        border-radius: 16px;
        background: linear-gradient(135deg,#172554,#111827);
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .hero h1 { margin: 0; color: white; }
    .hero p { color: #cbd5e1; margin-bottom: 0; }
    .box {
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #334155;
        background: #111827;
        margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🔎 DeepProof</h1>
        <p>Digital Evidence Triage — structured, transparent and review-ready.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "Prototype notice: DeepProof performs preliminary technical triage only. "
    "It does not establish authenticity, authorship, guilt or innocence."
)

# -----------------------------
# Case intake
# -----------------------------
with st.sidebar:
    st.header("📁 Case Intake")
    case_id = st.text_input("Case ID", "CASE-2026-001")
    fir = st.text_input("FIR / Reference", "FIR-2026-001")
    station = st.text_input("Station / Police Station", "Demo Police Station")
    target = st.text_input("Subject / Target", "Demo Subject")
    officer = st.text_input("Investigating Officer", "Demo Officer")

tab1, tab2, tab3 = st.tabs(["📁 Evidence Intake", "🔍 Analysis", "📄 Report"])

with tab1:
    st.subheader("Upload evidence")
    uploaded = st.file_uploader(
        "Choose an evidence file",
        type=[
            "jpg", "jpeg", "png", "pdf",
            "mp4", "mov", "avi", "mkv",
            "mp3", "wav", "m4a",
            "txt", "doc", "docx"
        ],
    )

    if uploaded:
        result = analyze_evidence(uploaded)
        st.session_state["result"] = result
        st.success("Evidence uploaded and analyzed successfully.")

        c1, c2, c3 = st.columns(3)
        c1.metric("File", result["filename"])
        c2.metric("Size", f'{result["size_mb"]:.3f} MB')
        c3.metric("Risk Score", f'{result["score"]}/100')

        st.markdown("### SHA-256")
        st.code(result["sha256"])

with tab2:
    result = st.session_state.get("result")

    if not result:
        st.info("Upload an evidence file first.")
    else:
        st.subheader("Technical Analysis")

        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Score", f'{result["score"]}/100')
        c2.metric("Initial Confidence", f'{result["confidence"]}%')
        c3.metric("Status", result["status"])

        st.markdown("### Findings")
        st.info(result["status_text"])

        st.markdown("### Integrity Signals")
        if result["signals"]:
            for signal in result["signals"]:
                st.write(f"• {signal}")
        else:
            st.success("No automated integrity signals were detected.")

        st.markdown("### Hash")
        st.code(result["sha256"])

with tab3:
    result = st.session_state.get("result")

    if not result:
        st.info("Upload and analyze evidence before generating the report.")
    else:
        st.subheader("📄 Evidence Triage Report")

        st.markdown("### Case Details")
        case_data = {
            "Case ID": case_id,
            "FIR / Reference": fir,
            "Station": station,
            "Subject / Target": target,
            "Investigating Officer": officer,
        }
        for key, value in case_data.items():
            st.write(f"**{key}:** {value}")

        st.markdown("### Evidence Details")
        st.write(f"**Filename:** {result['filename']}")
        st.write(f"**Type:** {result['extension'].upper()}")
        st.write(f"**Size:** {result['size_mb']:.3f} MB")
        st.write(f"**SHA-256:** `{result['sha256']}`")
        st.write(f"**Risk Score:** **{result['score']}/100**")
        st.write(f"**Initial Confidence:** **{result['confidence']}%**")
        st.write(f"**Status:** **{result['status']}**")

        st.markdown("### Automated Findings")
        for signal in result["signals"]:
            st.write(f"• {signal}")

        st.markdown("### Review Guidance")
        if result["score"] >= 70:
            st.error("Do not rely on automated output alone. Escalate for detailed forensic examination.")
        elif result["score"] >= 40:
            st.warning("Human review is recommended before drawing conclusions.")
        else:
            st.success("No strong automated red flags were detected, but authenticity is not established.")

        st.caption(
            "DeepProof is a preliminary triage prototype. Final evidentiary conclusions "
            "require qualified human/forensic examination."
        )

# -----------------------------
# Footer
# -----------------------------
st.caption("DeepProof • Preliminary Digital Evidence Triage • Prototype")
