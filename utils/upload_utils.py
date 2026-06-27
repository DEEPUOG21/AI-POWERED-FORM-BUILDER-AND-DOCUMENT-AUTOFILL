import streamlit as st

ALLOWED_TYPES = ["pdf", "png", "jpg", "jpeg"]
ALLOWED_MIME = ["application/pdf", "image/png", "image/jpeg"]
MAX_SIZE_MB = 10


def handle_file_upload():
    uploaded = st.file_uploader(
        "Choose a file",
        type=ALLOWED_TYPES,
        label_visibility="collapsed",
        key="doc_uploader",
    )

    if uploaded is None:
        st.markdown("""
        <div class="upload-zone">
            <div style="font-size:2rem;margin-bottom:0.5rem">📂</div>
            <div style="color:#9ca3af;font-size:0.9rem">
                Drag & drop or click above to upload<br>
                <span style="font-size:0.8rem;color:#4b5563">PDF · PNG · JPG · JPEG — max 10 MB</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Size check
    file_bytes = uploaded.read()
    size_mb = len(file_bytes) / (1024 * 1024)

    if size_mb > MAX_SIZE_MB:
        st.markdown(f"""
        <div class="alert-error">
            ❌ File too large ({size_mb:.1f} MB). Maximum allowed size is {MAX_SIZE_MB} MB.
            Please compress your file and try again.
        </div>
        """, unsafe_allow_html=True)
        return

    # Extension check
    ext = uploaded.name.split(".")[-1].lower()
    if ext not in ALLOWED_TYPES:
        st.markdown(f"""
        <div class="alert-error">
            ❌ Unsupported file type: <b>.{ext}</b><br>
            Only PDF, PNG, JPG, and JPEG files are accepted.
        </div>
        """, unsafe_allow_html=True)
        return

    # Store in session
    st.session_state.uploaded_file_data = file_bytes
    st.session_state.uploaded_file_type = "pdf" if ext == "pdf" else "image"
    st.session_state.uploaded_file_name = uploaded.name
    # Reset extraction when new file uploaded
    st.session_state.extraction_done = False
    st.session_state.extracted_values = {}

    st.markdown(f"""
    <div class="alert-success">
        ✅ <b>{uploaded.name}</b> uploaded successfully ({size_mb:.2f} MB).<br>
        Click <b>Extract with AI →</b> to proceed.
    </div>
    """, unsafe_allow_html=True)

    # Preview for images
    if st.session_state.uploaded_file_type == "image":
        st.image(file_bytes, caption=uploaded.name, use_container_width=True)
    else:
        st.markdown(f"""
        <div style="background:#0f1117;border:1px solid #1e2130;border-radius:10px;
                    padding:1rem;display:flex;align-items:center;gap:12px;margin-top:0.5rem">
            <span style="font-size:1.5rem">📄</span>
            <div>
                <div style="color:#e8eaf0;font-weight:600">{uploaded.name}</div>
                <div style="color:#6b7280;font-size:0.8rem">PDF · {size_mb:.2f} MB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
