uimport streamlit as st
import hashlib
import json
import re
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
<p>Preliminary Digital Evidence Triage — structured, transparent and review-ready.</p>
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

        sha256 = hashlib.sha256(data).hexdigest()
        size_bytes = len(data)
        size_mb = size_bytes / (1024 * 1024)

        filename = uploaded.name
        extension = filename.lower().split(".")[-1] if "." in filename else ""

        # -------- CONTENT SIGNALS --------
        text_content = ""

        if extension == "txt":
            try:
                text_content = data.decode("utf-8", errors="ignore")
            except Exception:
                text_content = ""

        text_lower = text_content.lower()

        suspicious_terms = [
            "edited", "modified", "fake", "sample",
            "draft", "copy", "screenshot", "unknown"
        ]

        term_hits = sum(
            1 for term in suspicious_terms
            if term in text_lower or term in filename.lower()
        )

        # -------- RISK CALCULATION --------
        risk = 5

        # File type factor
        if extension in ["jpg", "jpeg", "png"]:
            risk
