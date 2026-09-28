import streamlit as st
import hashlib
import json
from datetime import datetime, timezone

st.set_page_config(
    page_title="DeepProof | Digital Evidence Triage",
    page_icon="🔎",
    layout="wide",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.main { background:#0b1020; }
.hero {
    padding:24px;
    border-radius:16px;
    background:linear-gradient(135deg,#172554,#111827);
    border:1px solid #334155;
    margin-bottom:18px;
}
.card {
    padding:18px;
    border-radius:14px;
    border:1px solid #334155;
    background:#111827;
    margin-bottom:14px;
}
.small { color:#94a3b8; font-size:0.9rem; }
.badge {
    display:inline-block;
    padding:5px 10px;
    border-radius:999px;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🔎 DeepProof</h1>
<p style="color:#cbd5e1">Digital Evidence Triage — structured, transparent and review-ready.</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "Prototype notice: DeepProof performs preliminary technical triage only. "
    "It does not establish authenticity, authorship, guilt or innocence."
)

# -----------------------------
# Sidebar / Case Intake
# -----------------------------
with st.sidebar:
    st.header("📁 Case Intake")
    case_id = st.text_input("Case ID", "CASE-2026-001")
    fir = st.text_input("FIR / Reference", "FIR-2026-001")
    station = st.text_input("Station / Police Station", "Demo Police Station")
    target = st.text_input("Subject / Target", "Demo Subject")
    officer = st.text_input("Investigating Officer", "Demo Officer")

tab1, tab2, tab3 = st.tabs(["📁 Evidence Intake", "🔍 Analysis", "📄 Report"])

# -----------------------------
# Analysis engine
# -----------------------------
def analyze_file(uploaded_file):
    data = uploaded_file.getvalue()
    filename = uploaded_file.name
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    size_bytes = len(data)
    size_mb = size_bytes / (1024 * 1024)
    sha256 = hashlib.sha256(data).hexdigest()

    # Text extraction for common text-based files
    text_content = ""
    if extension in {"txt", "csv", "json", "md", "py", "html", "xml"}:
        text_content = data.decode("utf-8", errors="ignore")

    if extension == "pdf":
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(data))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            text_content = "\n".join(pages)
        except Exception:
            text_content = ""

    text_lower = text_content.lower()
    name_lower = filename.lower()

    suspicious_terms = [
        "edited", "modified", "fake", "sample", "draft",
        "copy", "screenshot", "unknown", "temp", "final2"
    ]
    hits = [term for term in suspicious_terms
            if term in text_lower or term in name_lower]

    risk = 0
    factors = []
    evidence = []

    # Filename / content signal
    if hits:
        points = min(len(hits) * 12, 36)
        risk += points
        factors.append(
            f"Suspicious filename/content indicators detected: {', '.join(hits)}."
        )
        evidence.append("Filename/content indicators require review.")

    # Size signal
    if size_bytes == 0:
        risk += 30
        factors.append("File is empty.")
    elif size_mb < 0.01:
        risk += 12
        factors.append("Very small file size.")
    elif size_mb > 100:
        risk += 5
        factors.append("Large file requires additional technical review.")

    # File type signal
    if extension in {"jpg", "jpeg", "png", "webp"}:
        risk += 5
        factors.append("Image evidence requires metadata/visual verification.")
    elif extension == "pdf":
        risk += 7
        factors.append("PDF structure should be checked for document integrity.")
    elif extension in {"mp4", "mov", "avi", "mkv"}:
        risk += 6
        factors.append("Video evidence requires frame/metadata verification.")
    elif extension in {"mp3", "wav", "m4a"}:
        risk += 6
        factors.append("Audio evidence requires metadata/audio verification.")
    elif extension in {"doc", "docx"}:
        risk += 5
        factors.append("Document metadata and revision history should be reviewed.")
    else:
        risk += 3
        factors.append("File type has limited automatic verification.")

    # Deterministic hash variation: same-looking files do not all get the same score.
    hash_value = int(sha256[:8], 16)
    hash_adjustment = hash_value % 11
    risk += hash_adjustment

    # Content length gives text documents another differentiator.
    if text_content:
        if len(text_content) < 100:
            risk += 3
            factors.append("Very short extracted text; manual review is recommended.")
        elif len(text_content) > 10000:
            risk += 2
            factors.append("Large amount of extracted text; targeted review is recommended.")

    risk = max(0, min(risk, 100))
    confidence = max(0, 100 - risk)

    if risk >= 70:
        status = "HIGH ATTENTION"
        status_type = "error"
    elif risk >= 40:
        status = "REVIEW REQUIRED"
        status_type = "warning"
    else:
        status = "LOW INITIAL RISK"
        status_type = "success"

    if not factors:
        factors.append("No automatic integrity concern detected.")

    return {
        "case_id": case_id,
        "fir": fir,
        "station": station,
        "target": target,
        "officer": officer,
        "filename": filename,
        "extension": extension or "unknown",
        "size_mb": round(size_mb, 3),
        "sha256": sha256,
        "risk": risk,
        "confidence": confidence,
        "status": status,
        "status_type": status_type,
        "hits": hits,
        "factors": factors,
        "evidence": evidence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# -----------------------------
# Evidence Intake
# -----------------------------
with tab1:
    st.subheader("Upload Evidence")
    uploaded = st.file_uploader(
        "Choose an evidence file",
        type=[
            "pdf", "txt", "csv", "json", "md", "doc", "docx",
            "jpg", "jpeg", "png", "webp",
            "mp4", "mov", "avi", "mkv",
            "mp3", "wav", "m4a"
        ],
        help="Upload one file for preliminary technical triage.",
    )

    if uploaded is not None:
        result = analyze_file(uploaded)
        st.session_state["result"] = result
        st.success("Evidence uploaded and analyzed successfully.")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("File", result["filename"])
        with c2:
            st.metric("Size", f'{result["size_mb"]:.3f} MB')
        with c3:
            st.metric("Risk Score", f'{result["risk"]}/100')

        st.info(
            f'Initial status: **{result["status"]}**  •  '
            f'Confidence: **{result["confidence"]}%**'
        )

# -----------------------------
# Analysis
# -----------------------------
with tab2:
    st.subheader("Technical Analysis")

    result = st.session_state.get("result")

    if not result:
        st.info("Upload evidence first from the Evidence Intake tab.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Risk Score", f'{result["risk"]}/100')
        with c2:
            st.metric("Initial Confidence", f'{result["confidence"]}%')

        st.markdown("### Findings")
        for factor in result["factors"]:
            st.write("• " + factor)

        st.markdown("### Integrity Signals")
        if result["hits"]:
            st.error(
                "Potential filename/content signals found: "
                + ", ".join(result["hits"])
            )
        else:
            st.success("No predefined suspicious filename/content signals found.")

        st.markdown("### File Fingerprint")
        st.code(result["sha256"], language="text")

        st.markdown("### Technical Interpretation")
        if result["risk"] >= 70:
            st.error(
                "High-attention triage result. Preserve the original file and "
                "consider specialist forensic examination."
            )
        elif result["risk"] >= 40:
            st.warning(
                "Review-required triage result. Additional metadata, structure "
                "and source verification are recommended."
            )
        else:
            st.success(
                "Low initial risk. This result does not prove authenticity; "
                "normal forensic preservation and verification still apply."
            )

# -----------------------------
# Report
# -----------------------------
with tab3:
    st.subheader("📄 Review-Ready Report")

    result = st.session_state.get("result")

    if not result:
        st.info("Upload evidence first to generate a report.")
    else:
        st.markdown(f"### DeepProof Technical Triage Report")
        st.write(f"**Case ID:** {result['case_id']}")
        st.write(f"**FIR / Reference:** {result['fir']}")
        st.write(f"**Station:** {result['station']}")
        st.write(f"**Subject / Target:** {result['target']}")
        st.write(f"**Investigating Officer:** {result['officer']}")

        st.divider()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Risk", f"{result['risk']}/100")
        with c2:
            st.metric("Confidence", f"{result['confidence']}%")
        with c3:
            st.metric("Status", result["status"])

        st.markdown("### Evidence")
        st.write(f"**Filename:** {result['filename']}")
        st.write(f"**Extension:** {result['extension']}")
        st.write(f"**Size:** {result['size_mb']:.3f} MB")
        st.write(f"**SHA-256:** `{result['sha256']}`")

        st.markdown("### Findings")
        for factor in result["factors"]:
            st.write("• " + factor)

        st.markdown("### Conclusion")
        st.write(
            "DeepProof provides a preliminary technical triage based on observable "
            "file-level signals. The score is not a legal finding and should not "
            "be treated as proof that a file is genuine, altered, or fraudulent."
        )

        report = {
            "deepProof_report": {
                "generated_at": result["timestamp"],
                "case": {
                    "case_id": result["case_id"],
                    "fir": result["fir"],
                    "station": result["station"],
                    "target": result["target"],
                    "officer": result["officer"],
                },
                "evidence": result,
            }
        }

        st.download_button(
            "⬇️ Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name=f"deepProof_{result['case_id']}.json",
            mime="application/json",
        )
