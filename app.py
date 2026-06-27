import streamlit as st
import json
import base64
import io
from datetime import date
from utils.form_utils import (
    init_session_state,
    add_field,
    remove_field,
    move_field_up,
    move_field_down,
    render_form_builder,
    render_live_preview,
    render_review_form,
)
from utils.upload_utils import handle_file_upload
from utils.ai_utils import extract_fields_from_document

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FormAI — Smart Form Builder",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* Reset & base */
* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0f1117;
    color: #e8eaf0;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

/* App header */
.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #1e2130;
}
.app-logo {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}
.app-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f2f6;
    margin: 0;
}
.app-subtitle { font-size: 0.8rem; color: #6b7280; margin: 0; font-weight: 400; }

/* Step tabs */
.step-bar {
    display: flex;
    gap: 0;
    margin-bottom: 2rem;
    background: #1a1d2e;
    border-radius: 12px;
    padding: 6px;
    border: 1px solid #1e2130;
}
.step-item {
    flex: 1;
    text-align: center;
    padding: 10px 8px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #6b7280;
    cursor: default;
    transition: all 0.2s;
}
.step-item.active {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff;
    font-weight: 600;
}
.step-item.done {
    color: #a78bfa;
}

/* Section cards */
.section-card {
    background: #1a1d2e;
    border: 1px solid #1e2130;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #c4b5fd;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Field row */
.field-row {
    background: #0f1117;
    border: 1px solid #1e2130;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.field-row:hover { border-color: #6366f1; }

/* Pill badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-required { background: #3b1f5e; color: #c084fc; }
.badge-optional { background: #1a2240; color: #60a5fa; }
.badge-high { background: #14532d; color: #4ade80; }
.badge-medium { background: #713f12; color: #fbbf24; }
.badge-low { background: #450a0a; color: #f87171; }
.badge-missing { background: #1a1a1a; color: #6b7280; }

/* Buttons override */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    border: 1px solid #2a2d3e !important;
}
.stButton > button:hover {
    border-color: #6366f1 !important;
    color: #a78bfa !important;
}

/* Primary action button */
.primary-btn > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

/* Upload zone */
.upload-zone {
    border: 2px dashed #2a2d3e;
    border-radius: 12px;
    padding: 2.5rem 2rem;
    text-align: center;
    background: #0f1117;
    transition: border-color 0.2s;
}
.upload-zone:hover { border-color: #6366f1; }

/* Alert boxes */
.alert-info {
    background: #1a2240;
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #a5b4fc;
    margin: 0.5rem 0;
}
.alert-warning {
    background: #2d1f00;
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #fcd34d;
    margin: 0.5rem 0;
}
.alert-success {
    background: #052e16;
    border-left: 3px solid #22c55e;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #86efac;
    margin: 0.5rem 0;
}
.alert-error {
    background: #2d0a0a;
    border-left: 3px solid #ef4444;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #fca5a5;
    margin: 0.5rem 0;
}

/* Preview form fields */
.preview-field {
    margin-bottom: 1.1rem;
}
.preview-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #9ca3af;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.preview-input {
    background: #0f1117;
    border: 1px solid #2a2d3e;
    border-radius: 8px;
    padding: 10px 12px;
    width: 100%;
    color: #e8eaf0;
    font-size: 0.9rem;
}

/* Confidence bar */
.conf-bar-wrap { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
.conf-bar {
    height: 4px;
    border-radius: 2px;
    flex: 1;
}

/* Divider */
.divider { border: none; border-top: 1px solid #1e2130; margin: 1.5rem 0; }

/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #4b5563;
}
.empty-state-icon { font-size: 2.5rem; margin-bottom: 1rem; }
.empty-state-text { font-size: 0.95rem; }

/* Scrollable schema viewer */
.schema-json {
    background: #0a0c12;
    border: 1px solid #1e2130;
    border-radius: 10px;
    padding: 1rem;
    font-family: monospace;
    font-size: 0.78rem;
    color: #a78bfa;
    overflow-x: auto;
    max-height: 200px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-logo">📋</div>
    <div>
        <div class="app-title">FormAI</div>
        <div class="app-subtitle">Build forms · Upload documents · AI autofill</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
init_session_state()

# ── Step indicator ────────────────────────────────────────────────────────────
step = st.session_state.get("current_step", 1)
steps = ["1 · Build Form", "2 · Upload Document", "3 · AI Extraction", "4 · Review & Save"]
step_html = '<div class="step-bar">'
for i, s in enumerate(steps, 1):
    css = "active" if i == step else ("done" if i < step else "")
    step_html += f'<div class="step-item {css}">{s}</div>'
step_html += "</div>"
st.markdown(step_html, unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
def go_to(n):
    st.session_state.current_step = n

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — FORM BUILDER
# ═══════════════════════════════════════════════════════════════════════════════
if step == 1:
    left, right = st.columns([3, 2], gap="large")

    with left:
        render_form_builder()

    with right:
        render_live_preview()

    # Schema export / import
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col_exp, col_imp, col_next = st.columns([2, 2, 3])

    with col_exp:
        if st.session_state.fields:
            schema_bytes = json.dumps(st.session_state.fields, indent=2).encode()
            st.download_button(
                "⬇ Export Schema",
                data=schema_bytes,
                file_name="form_schema.json",
                mime="application/json",
                use_container_width=True,
            )

    with col_imp:
        imp = st.file_uploader("Import Schema", type=["json"], key="schema_import", label_visibility="collapsed")
        if imp:
            try:
                loaded = json.loads(imp.read())
                if isinstance(loaded, list):
                    st.session_state.fields = loaded
                    st.success("Schema loaded!")
                    st.rerun()
                else:
                    st.error("Invalid schema format.")
            except Exception:
                st.error("Could not parse JSON file.")

    with col_next:
        if st.session_state.fields:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Continue to Upload →", use_container_width=True):
                go_to(2)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-info">Add at least one field to continue.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — DOCUMENT UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    c1, c2 = st.columns([3, 2], gap="large")

    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📂 Upload Your Document</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="alert-info">
            Supported formats: <strong>PDF</strong>, <strong>PNG</strong>, <strong>JPG</strong>, <strong>JPEG</strong><br>
            The AI will read this document and fill your form automatically.
        </div>
        """, unsafe_allow_html=True)

        handle_file_upload()
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Your Form Fields</div>', unsafe_allow_html=True)
        for f in st.session_state.fields:
            req_badge = '<span class="badge badge-required">Required</span>' if f["required"] else '<span class="badge badge-optional">Optional</span>'
            st.markdown(f'<div class="field-row"><b style="color:#e8eaf0">{f["label"]}</b> &nbsp; <span style="color:#6b7280;font-size:0.8rem">{f["type"]}</span> &nbsp; {req_badge}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    nav1, nav2, nav3 = st.columns([1, 1, 4])
    with nav1:
        if st.button("← Back", use_container_width=True):
            go_to(1); st.rerun()
    with nav2:
        if st.session_state.get("uploaded_file_data"):
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("Extract with AI →", use_container_width=True):
                go_to(3); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — AI EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🤖 AI Extraction</div>', unsafe_allow_html=True)

    if not st.session_state.get("extraction_done"):
        with st.spinner("Reading document and extracting field values…"):
            result = extract_fields_from_document(
                st.session_state.fields,
                st.session_state.uploaded_file_data,
                st.session_state.uploaded_file_type,
            )
            st.session_state.extracted_values = result
            st.session_state.extraction_done = True
            # Pre-fill editable values
            st.session_state.edited_values = {
                f["id"]: result.get(f["id"], {}).get("value", "") for f in st.session_state.fields
            }

    result = st.session_state.extracted_values
    total = len(st.session_state.fields)
    filled = sum(1 for f in st.session_state.fields if result.get(f["id"], {}).get("value", ""))
    missing = total - filled

    cols = st.columns(3)
    cols[0].metric("Total Fields", total)
    cols[1].metric("Extracted", filled, delta=None)
    cols[2].metric("Need Review", missing)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    for f in st.session_state.fields:
        fid = f["id"]
        r = result.get(fid, {})
        val = r.get("value", "")
        conf = r.get("confidence", "missing")  # high / medium / low / missing

        conf_colors = {"high": "#4ade80", "medium": "#fbbf24", "low": "#f87171", "missing": "#6b7280"}
        conf_label = conf.capitalize() if conf != "missing" else "Not found"

        badge = f'<span class="badge badge-{conf}">{conf_label}</span>'
        req = '<span class="badge badge-required">Required</span>' if f["required"] else ""
        flag = "⚠️ " if f["required"] and not val else ""

        st.markdown(f"""
        <div class="field-row">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="color:#e8eaf0;font-weight:600">{flag}{f['label']}</span>
                <span>{req}&nbsp;{badge}</span>
            </div>
            <div style="margin-top:6px;color:{'#e8eaf0' if val else '#4b5563'};font-size:0.9rem">
                {val if val else '<i>No value found — field will be blank</i>'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns([1, 1, 4])
    with nav1:
        if st.button("← Back", use_container_width=True):
            st.session_state.extraction_done = False
            go_to(2); st.rerun()
    with nav2:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("Review & Edit →", use_container_width=True):
            go_to(4); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — REVIEW & SAVE
# ═══════════════════════════════════════════════════════════════════════════════
elif step == 4:
    render_review_form()
