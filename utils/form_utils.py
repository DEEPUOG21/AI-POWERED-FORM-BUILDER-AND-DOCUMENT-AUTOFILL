import streamlit as st
import uuid
import json
from datetime import date, datetime

FIELD_TYPES = [
    "Single-line text",
    "Multi-line text",
    "Number",
    "Date",
    "Dropdown",
    "Checkbox",
]


def init_session_state():
    defaults = {
        "fields": [],
        "current_step": 1,
        "uploaded_file_data": None,
        "uploaded_file_type": None,
        "uploaded_file_name": None,
        "extracted_values": {},
        "edited_values": {},
        "extraction_done": False,
        "saved_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def add_field():
    st.session_state.fields.append({
        "id": str(uuid.uuid4())[:8],
        "label": f"Field {len(st.session_state.fields) + 1}",
        "type": "Single-line text",
        "required": False,
        "options": "",  # for dropdowns
    })


def remove_field(fid):
    st.session_state.fields = [f for f in st.session_state.fields if f["id"] != fid]


def move_field_up(idx):
    if idx > 0:
        st.session_state.fields[idx], st.session_state.fields[idx - 1] = (
            st.session_state.fields[idx - 1],
            st.session_state.fields[idx],
        )


def move_field_down(idx):
    fields = st.session_state.fields
    if idx < len(fields) - 1:
        fields[idx], fields[idx + 1] = fields[idx + 1], fields[idx]


def render_form_builder():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛠 Form Builder</div>', unsafe_allow_html=True)

    if not st.session_state.fields:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📝</div>
            <div class="empty-state-text">No fields yet.<br>Click <b>Add Field</b> below to start building your form.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, field in enumerate(st.session_state.fields):
            fid = field["id"]
            with st.container():
                st.markdown(f'<div class="field-row">', unsafe_allow_html=True)

                c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 1, 0.5, 0.5, 0.5])

                with c1:
                    new_label = st.text_input(
                        "Label",
                        value=field["label"],
                        key=f"label_{fid}",
                        label_visibility="collapsed",
                        placeholder="Field label…",
                    )
                    st.session_state.fields[idx]["label"] = new_label

                with c2:
                    new_type = st.selectbox(
                        "Type",
                        FIELD_TYPES,
                        index=FIELD_TYPES.index(field["type"]),
                        key=f"type_{fid}",
                        label_visibility="collapsed",
                    )
                    st.session_state.fields[idx]["type"] = new_type

                with c3:
                    req = st.checkbox(
                        "Required",
                        value=field["required"],
                        key=f"req_{fid}",
                    )
                    st.session_state.fields[idx]["required"] = req

                with c4:
                    if st.button("↑", key=f"up_{fid}", help="Move up"):
                        move_field_up(idx)
                        st.rerun()

                with c5:
                    if st.button("↓", key=f"dn_{fid}", help="Move down"):
                        move_field_down(idx)
                        st.rerun()

                with c6:
                    if st.button("✕", key=f"rm_{fid}", help="Remove field"):
                        remove_field(fid)
                        st.rerun()

                # Dropdown options sub-row
                if new_type == "Dropdown":
                    opts = st.text_input(
                        "Options (comma-separated)",
                        value=field.get("options", ""),
                        key=f"opts_{fid}",
                        placeholder="e.g. Engineering, Marketing, Sales",
                    )
                    st.session_state.fields[idx]["options"] = opts

                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col_add, col_clear = st.columns([2, 1])
    with col_add:
        if st.button("➕ Add Field", use_container_width=True):
            add_field()
            st.rerun()
    with col_clear:
        if st.session_state.fields:
            if st.button("🗑 Clear All", use_container_width=True):
                st.session_state.fields = []
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_live_preview():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👁 Live Preview</div>', unsafe_allow_html=True)

    if not st.session_state.fields:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">👈</div>
            <div class="empty-state-text">Your form preview will appear here as you add fields.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for field in st.session_state.fields:
            label = field["label"] or "Untitled Field"
            req_star = " *" if field["required"] else ""
            ftype = field["type"]

            st.markdown(f'<div class="preview-field">', unsafe_allow_html=True)

            if ftype == "Single-line text":
                st.text_input(f"{label}{req_star}", key=f"prev_{field['id']}", disabled=True, label_visibility="visible")
            elif ftype == "Multi-line text":
                st.text_area(f"{label}{req_star}", key=f"prev_{field['id']}", disabled=True, height=80, label_visibility="visible")
            elif ftype == "Number":
                st.number_input(f"{label}{req_star}", key=f"prev_{field['id']}", disabled=True, label_visibility="visible")
            elif ftype == "Date":
                st.date_input(f"{label}{req_star}", key=f"prev_{field['id']}", disabled=True, label_visibility="visible")
            elif ftype == "Dropdown":
                opts = [o.strip() for o in field.get("options", "").split(",") if o.strip()]
                opts = opts if opts else ["Option 1", "Option 2"]
                st.selectbox(f"{label}{req_star}", opts, key=f"prev_{field['id']}", disabled=True, label_visibility="visible")
            elif ftype == "Checkbox":
                st.checkbox(f"{label}{req_star}", key=f"prev_{field['id']}", disabled=True)

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Schema viewer (collapsible)
    if st.session_state.fields:
        with st.expander("📄 View Form Schema (JSON)"):
            schema = [{"label": f["label"], "type": f["type"], "required": f["required"]} for f in st.session_state.fields]
            st.code(json.dumps(schema, indent=2), language="json")


def render_review_form():
    result = st.session_state.extracted_values
    edited = st.session_state.edited_values

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✏️ Review & Edit Extracted Values</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="alert-info">
        Review the AI-extracted values below. Edit any field manually if needed. 
        <b>Required fields highlighted in orange</b> must be filled before saving.
    </div>
    """, unsafe_allow_html=True)

    validation_errors = []

    for field in st.session_state.fields:
        fid = field["id"]
        ftype = field["type"]
        current_val = edited.get(fid, "")
        conf = result.get(fid, {}).get("confidence", "missing")
        conf_badge = f'<span class="badge badge-{conf}">{conf.capitalize() if conf != "missing" else "Not found"}</span>'
        req_badge = '<span class="badge badge-required">Required</span>' if field["required"] else ""

        # Highlight missing required fields
        border_color = "#f59e0b" if field["required"] and not current_val else "#1e2130"

        st.markdown(f"""
        <div style="background:#0f1117;border:1px solid {border_color};border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.75rem">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                <span style="color:#e8eaf0;font-weight:600">{field['label']}</span>
                <span>{req_badge}&nbsp;{conf_badge}</span>
            </div>
        """, unsafe_allow_html=True)

        key = f"edit_{fid}"
        if ftype == "Single-line text":
            val = st.text_input("", value=current_val, key=key, label_visibility="collapsed")
        elif ftype == "Multi-line text":
            val = st.text_area("", value=current_val, key=key, height=90, label_visibility="collapsed")
        elif ftype == "Number":
            try:
                num_val = float(current_val) if current_val else 0.0
            except ValueError:
                num_val = 0.0
            val = st.number_input("", value=num_val, key=key, label_visibility="collapsed")
            val = str(val) if val else ""
        elif ftype == "Date":
            try:
                date_val = date.fromisoformat(current_val) if current_val else date.today()
            except ValueError:
                date_val = date.today()
            val = st.date_input("", value=date_val, key=key, label_visibility="collapsed")
            val = val.isoformat() if val else ""
        elif ftype == "Dropdown":
            opts = [o.strip() for o in field.get("options", "").split(",") if o.strip()]
            if not opts:
                opts = ["Option 1"]
            idx = opts.index(current_val) if current_val in opts else 0
            val = st.selectbox("", opts, index=idx, key=key, label_visibility="collapsed")
        elif ftype == "Checkbox":
            checked = current_val in (True, "True", "true", "yes", "Yes", "1")
            val = st.checkbox("Checked", value=checked, key=key)
            val = str(val)
        else:
            val = current_val

        st.session_state.edited_values[fid] = val

        if field["required"] and not val:
            validation_errors.append(field["label"])

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Validation summary
    if validation_errors:
        st.markdown(f"""
        <div class="alert-warning">
            ⚠️ The following required fields are empty: <b>{', '.join(validation_errors)}</b>
        </div>
        """, unsafe_allow_html=True)

    # Navigation + save
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    nav1, nav2, nav3, nav4 = st.columns([1, 1, 1, 3])

    with nav1:
        if st.button("← Back", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()

    with nav2:
        # Export filled form as JSON
        if st.session_state.edited_values:
            output = {
                f["label"]: st.session_state.edited_values.get(f["id"], "")
                for f in st.session_state.fields
            }
            st.download_button(
                "⬇ Export JSON",
                data=json.dumps(output, indent=2).encode(),
                file_name="filled_form.json",
                mime="application/json",
                use_container_width=True,
            )

    with nav3:
        can_save = len(validation_errors) == 0
        if can_save:
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("💾 Save Form", use_container_width=True):
                st.session_state.saved_result = {
                    f["label"]: st.session_state.edited_values.get(f["id"], "")
                    for f in st.session_state.fields
                }
                st.balloons()
                st.success("✅ Form saved successfully!")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.button("💾 Save Form", disabled=True, use_container_width=True, help="Fill all required fields first")

    # Show saved result
    if st.session_state.saved_result:
        st.markdown('<div class="section-card" style="margin-top:1.5rem">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">✅ Saved Form Data</div>', unsafe_allow_html=True)
        for label, val in st.session_state.saved_result.items():
            st.markdown(f"""
            <div style="display:flex;gap:1rem;padding:0.5rem 0;border-bottom:1px solid #1e2130">
                <span style="color:#9ca3af;font-size:0.85rem;min-width:180px">{label}</span>
                <span style="color:#e8eaf0;font-size:0.85rem">{val if val else '—'}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
