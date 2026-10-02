"""
LegalEase — Streamlit Frontend
================================
Run with:
    streamlit run frontend/app.py
"""
import sys
import os

# Ensure project root is importable (for utils)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import requests
import streamlit as st
from datetime import date
from dotenv import load_dotenv

from utils.formatter import format_txt, format_docx, format_pdf
from utils.sanitizer import sanitize_text, sanitize_filename

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(_ROOT, ".env"))

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="LegalEase AI — Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        /* ---- Global font & background ---- */
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ---- Header banner ---- */
        .legal-header {
            background: linear-gradient(135deg, #1a1a5e 0%, #2d2d8e 60%, #4a4ab8 100%);
            color: white;
            padding: 2rem 2.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(26,26,94,0.3);
        }
        .legal-header h1 {
            font-family: 'Merriweather', serif;
            font-size: 2.2rem;
            margin: 0;
            letter-spacing: 0.5px;
        }
        .legal-header p {
            margin: 0.4rem 0 0;
            font-size: 1rem;
            opacity: 0.85;
        }

        /* ---- Section cards ---- */
        .card {
            background: #ffffff;
            border: 1px solid #e0e4ef;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        /* ---- Generate button ---- */
        div.stButton > button {
            background: linear-gradient(135deg, #1a1a5e, #4a4ab8);
            color: white;
            font-size: 1.05rem;
            font-weight: 600;
            padding: 0.65rem 2.5rem;
            border: none;
            border-radius: 8px;
            width: 100%;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        div.stButton > button:hover {
            opacity: 0.88;
        }

        /* ---- Download button ---- */
        div.stDownloadButton > button {
            border-radius: 6px;
            font-weight: 500;
        }

        /* ---- Document preview textarea ---- */
        textarea {
            font-family: 'Courier New', monospace !important;
            font-size: 0.85rem !important;
            border-radius: 6px !important;
        }

        /* ---- Status badges ---- */
        .badge-success {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            display: inline-block;
        }
        .badge-error {
            background: #fce4ec;
            color: #c62828;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            display: inline-block;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="legal-header">
        <h1>⚖️ LegalEase AI</h1>
        <p>Professional legal document generation powered by Google Gemini</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — About
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/law.png",
        width=72,
    )
    st.markdown("## About LegalEase AI")
    st.markdown(
        """
        LegalEase generates professional, structured legal documents
        using **Google Gemini** and a FastAPI backend.

        **Supported Documents**
        - Non-Disclosure Agreement (NDA)
        - Employment Contract
        - Lease Agreement
        - Custom document type

        **Export Formats**
        - Plain Text (.txt)
        - Word Document (.docx)
        - PDF (.pdf)
        """
    )
    st.divider()
    st.markdown(
        f"**Backend:** `{BACKEND_URL}`",
    )

    # Health check
    if st.button("Check Backend Status"):
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if r.status_code == 200:
                st.success("Backend is online ✅")
            else:
                st.error(f"Backend returned {r.status_code}")
        except Exception as e:
            st.error(f"Cannot reach backend: {e}")

# ---------------------------------------------------------------------------
# Input Form
# ---------------------------------------------------------------------------

st.markdown("### 📋 Document Details")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    document_type = st.selectbox(
        "Document Type *",
        options=[
            "NDA (Non-Disclosure Agreement)",
            "Employment Contract",
            "Lease Agreement",
            "Custom",
        ],
        help="Select the type of legal document you want to generate.",
    )

    # If custom, allow free-text entry
    if document_type == "Custom":
        document_type = st.text_input(
            "Custom Document Type *",
            placeholder="e.g. Service Level Agreement, Partnership Deed...",
        )

    parties = st.text_input(
        "Parties Involved *",
        placeholder="e.g. Acme Corp, John Doe",
        help="Enter the names of all parties, separated by commas.",
    )

    effective_date = st.date_input(
        "Effective Date *",
        value=date.today(),
        help="The date from which this agreement becomes effective.",
    )

with col2:
    terms = st.text_area(
        "Terms & Clauses *",
        placeholder=(
            "Enter each term separated by a semicolon (;)\n\n"
            "Example:\n"
            "Confidentiality period: 2 years; "
            "Governing law: New York; "
            "Non-compete radius: 50 miles; "
            "Notice period: 30 days"
        ),
        height=180,
        help="List all clauses and terms separated by semicolons.",
    )

    additional_context = st.text_area(
        "Additional Instructions (optional)",
        placeholder="Any special clauses, jurisdictions, or notes for the AI...",
        height=80,
    )

# ---------------------------------------------------------------------------
# Generate Button
# ---------------------------------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)
generate_clicked = st.button("⚡ Generate Legal Document", use_container_width=True)

# ---------------------------------------------------------------------------
# Validation + Generation
# ---------------------------------------------------------------------------

if generate_clicked:
    errors = []
    if not document_type or not document_type.strip():
        errors.append("Document Type is required.")
    if not parties or not parties.strip():
        errors.append("Parties Involved is required.")
    if not terms or not terms.strip():
        errors.append("Terms & Clauses are required.")

    if errors:
        for err in errors:
            st.error(f"❌ {err}")
    else:
        with st.spinner("⚙️ Generating your legal document via Gemini AI..."):
            payload = {
                "document_type": document_type.strip(),
                "parties": parties.strip(),
                "terms": terms.strip(),
                "date": str(effective_date),
                "additional_context": additional_context.strip() or None,
            }

            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,  # Gemini can take a while for long docs
                )

                if response.status_code == 200:
                    data = response.json()
                    generated_text = data.get("generated_text", "")
                    st.session_state["generated_text"] = generated_text
                    st.session_state["doc_type"] = document_type.strip()
                    st.markdown(
                        '<span class="badge-success">✓ Document Generated Successfully</span>',
                        unsafe_allow_html=True,
                    )

                elif response.status_code == 400:
                    detail = response.json().get("detail", "Bad request.")
                    st.error(f"❌ Validation Error: {detail}")

                elif response.status_code == 500:
                    detail = response.json().get("detail", "Server error.")
                    st.error(f"❌ Server Error: {detail}")
                    st.info("💡 Tip: Check that your GEMINI_API_KEY is set correctly in `.env`.")

                else:
                    st.error(f"❌ Unexpected response ({response.status_code}): {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to the backend. "
                    "Make sure it is running:\n\n"
                    "```\nuvicorn backend.main:app --reload\n```"
                )
            except requests.exceptions.Timeout:
                st.error(
                    "❌ The request timed out. The document may be too long. "
                    "Try shortening the terms or waiting and retrying."
                )
            except Exception as exc:
                st.error(f"❌ Unexpected error: {exc}")

# ---------------------------------------------------------------------------
# Document Preview + Export
# ---------------------------------------------------------------------------

if "generated_text" in st.session_state and st.session_state["generated_text"]:
    generated_text = st.session_state["generated_text"]
    doc_type_label = st.session_state.get("doc_type", "legal_document")

    st.divider()
    st.markdown("### 📄 Document Preview")
    st.markdown(
        "_You can edit the document below before downloading._",
        unsafe_allow_html=False,
    )

    # Editable text area
    edited_text = st.text_area(
        label="Generated Document (editable)",
        value=generated_text,
        height=520,
        key="doc_editor",
        label_visibility="collapsed",
    )

    # Sync edits back to session state
    st.session_state["generated_text"] = edited_text

    st.markdown("### 💾 Export Document")

    # Build file name base
    safe_name = sanitize_filename(doc_type_label)
    date_suffix = str(date.today()).replace("-", "")
    file_base = f"LegalEase_{safe_name}_{date_suffix}"

    export_col1, export_col2, export_col3 = st.columns(3)

    # ---- TXT ----
    with export_col1:
        try:
            txt_bytes = format_txt(edited_text)
            st.download_button(
                label="📄 Download TXT",
                data=txt_bytes,
                file_name=f"{file_base}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"TXT export error: {e}")

    # ---- DOCX ----
    with export_col2:
        try:
            docx_bytes = format_docx(edited_text, title=doc_type_label)
            st.download_button(
                label="📝 Download DOCX",
                data=docx_bytes,
                file_name=f"{file_base}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"DOCX export error: {e}")

    # ---- PDF ----
    with export_col3:
        try:
            pdf_bytes = format_pdf(edited_text, title=doc_type_label)
            st.download_button(
                label="📋 Download PDF",
                data=pdf_bytes,
                file_name=f"{file_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF export error: {e}")

    st.markdown(
        """
        <br>
        <div style='text-align:center; color:#888; font-size:0.8rem;'>
            ⚠️ <em>LegalEase AI generates document drafts for reference only.
            Always consult a qualified attorney before using any legal document.</em>
        </div>
        """,
        unsafe_allow_html=True,
    )
