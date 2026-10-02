# ⚖️ LegalEase AI — Legal Document Generator

A production-ready, full-stack AI application that generates professional legal documents using **Google Gemini**, **FastAPI**, and **Streamlit**.

---

## 📁 Project Structure

```
LegalEaseAI/
│
├── backend/
│   ├── __init__.py
│   ├── main.py               ← FastAPI app entry-point
│   ├── routes.py             ← API route: POST /generate
│   ├── models.py             ← Pydantic request/response models
│   └── ai_core/
│       ├── __init__.py
│       └── gemini_generator.py  ← Gemini AI document generator
│
├── frontend/
│   └── app.py               ← Streamlit UI
│
├── utils/
│   ├── __init__.py
│   ├── formatter.py         ← format_txt / format_docx / format_pdf
│   └── sanitizer.py         ← sanitize_text / sanitize_filename
│
├── .env                     ← API keys & config (DO NOT commit)
├── requirements.txt
└── README.md
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Document Types** | NDA, Employment Contract, Lease Agreement, Custom |
| **AI Engine** | Google Gemini 1.5 Pro |
| **Structured Prompts** | Title, Preamble, Definitions, Numbered Clauses, Signature Block |
| **Editable Preview** | Edit document in-browser before downloading |
| **Export: TXT** | UTF-8 plain text |
| **Export: DOCX** | Professionally formatted Word document |
| **Export: PDF** | Formatted PDF with header & footer |
| **Error Handling** | Input validation, API failures, connection errors |
| **Health Check** | `GET /health` + sidebar button in UI |

---

## 🚀 Setup & Installation

### 1. Clone / Open the project

```bash
cd LegalEaseAI
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Open `.env` and replace the placeholder with your real Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-1.5-pro
BACKEND_URL=http://127.0.0.1:8000
```

> Get a free Gemini API key at [https://aistudio.google.com](https://aistudio.google.com)

---

## ▶️ Running the Application

### Terminal 1 — Start the Backend (FastAPI)

```bash
# From the LegalEaseAI root directory
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

API will be available at:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health

### Terminal 2 — Start the Frontend (Streamlit)

```bash
# From the LegalEaseAI root directory
streamlit run frontend/app.py
```

Frontend will open at: **http://localhost:8501**

---

## 🔌 API Reference

### `POST /generate`

Generate a legal document.

**Request Body (JSON):**
```json
{
  "document_type": "NDA",
  "parties": "Acme Corp, John Doe",
  "terms": "Confidentiality period: 2 years; Jurisdiction: New York",
  "date": "2026-01-01",
  "additional_context": null
}
```

**Success Response (200):**
```json
{
  "success": true,
  "document_type": "NDA",
  "generated_text": "NON-DISCLOSURE AGREEMENT\n\n...",
  "message": "Document generated successfully."
}
```

**Error Response (400 / 500):**
```json
{
  "detail": "GEMINI_API_KEY is not set. Please add it to your .env file."
}
```

---

## 🛠️ Utility Functions

| Function | Module | Description |
|---|---|---|
| `sanitize_text(text)` | `utils/sanitizer.py` | Cleans Unicode, control chars, smart quotes |
| `sanitize_filename(name)` | `utils/sanitizer.py` | Makes a string filesystem-safe |
| `format_txt(text)` | `utils/formatter.py` | Returns UTF-8 bytes of the document |
| `format_docx(text, title)` | `utils/formatter.py` | Returns DOCX bytes (python-docx) |
| `format_pdf(text, title)` | `utils/formatter.py` | Returns PDF bytes (fpdf2) |

---

## ⚠️ Disclaimer

> LegalEase AI generates document drafts for **reference and educational purposes only**.  
> Always consult a qualified attorney before using any AI-generated legal document in a real legal matter.

---

## 📄 License

MIT © LegalEase AI
