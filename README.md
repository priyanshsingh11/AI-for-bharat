# 🏛️ AI-Based Tender Evaluation System

A **production-ready, end-to-end AI pipeline** for automated government tender bid evaluation. The system extracts structured data from uploaded documents using OCR and a Groq LLM, evaluates bidder eligibility using a deterministic rule engine, provides page-level evidence citations, and supports human-in-the-loop review with a full audit trail.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📤 **Document Upload** | Upload tender and bidder PDFs/images via REST API or Streamlit UI |
| 🔍 **OCR Text Extraction** | Page-wise text extraction using PyMuPDF (PDFs) and EasyOCR (images) |
| 🧠 **LLM-based Data Extraction** | Structured JSON extraction via Groq (`llama-3.3-70b-versatile`) |
| ⚖️ **Deterministic Rule Engine** | Smart criterion-to-bidder-key matching with operator comparison |
| 📄 **Evidence Extraction** | Page-level evidence snippets with value variant normalization (e.g. `₹3 Cr`) |
| 🗣️ **Explainability Layer** | Professional, human-readable explanations for every criterion decision |
| 🧑‍⚖️ **Human-in-the-Loop Review** | API + UI to override AI decisions with full audit timestamping |
| 📊 **Confidence Scoring** | Heuristic confidence per criterion based on evidence availability |
| 🖥️ **Streamlit Dashboard** | Interactive frontend with color-coded results and one-click review |

---

## 🗂️ Project Structure

```text
AI-for-bharat/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── core/
│   │   └── pipeline.py            # Extraction + Evaluation orchestration
│   ├── routes/
│   │   ├── upload.py              # POST /upload
│   │   ├── process.py             # POST /process
│   │   ├── extract.py             # POST /extract
│   │   ├── evaluate.py            # POST /evaluate
│   │   └── human_review.py        # POST /review
│   ├── services/
│   │   ├── ocr_service.py         # PyMuPDF + EasyOCR text extraction
│   │   ├── llm_service.py         # Groq API client + output sanitization
│   │   ├── extraction_service.py  # Tender criteria & bidder data extraction
│   │   ├── rule_engine.py         # Deterministic eligibility evaluation
│   │   └── explain_service.py     # Evidence + explanation generation
│   ├── utils/
│   │   └── formatters.py          # INR number formatting utilities
│   └── models/
│       └── __init__.py
├── data/
│   ├── uploads/                   # Raw uploaded files (PDFs/images)
│   ├── processed/                 # Page-wise OCR JSON output
│   ├── extracted/                 # Structured LLM extraction JSON
│   └── results/                   # Final evaluation results JSON
├── frontend/
│   └── app.py                     # Streamlit interactive dashboard
├── venv/                          # Isolated Python virtual environment
├── .env                           # Environment variables (API keys)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- A [Groq API Key](https://console.groq.com/) (free tier available)

### 1. Clone the Repository
```powershell
git clone https://github.com/your-username/AI-for-bharat.git
cd "AI for bharat"
```

### 2. Create & Activate the Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

> ⚠️ **Note**: `easyocr` and `torch` are large packages (~2GB). The first run will also download OCR model weights automatically.

### 4. Set Up Environment Variables
Create a `.env` file in the project root (or export in your shell):
```env
GROQ_API_KEY=your_groq_api_key_here
```

**For PowerShell:**
```powershell
$env:GROQ_API_KEY="your_groq_api_key_here"
```

---

## ▶️ Running the Application

You need **two terminal windows** — one for the backend, one for the frontend.

### Terminal 1 — Start the FastAPI Backend
```powershell
uvicorn app.main:app --reload
```
The API will be live at: `http://127.0.0.1:8000`

### Terminal 2 — Start the Streamlit Frontend
```powershell
streamlit run frontend/app.py
```
The dashboard will be live at: `http://localhost:8501`

---

## 🔄 Pipeline Flow

```
[Document Upload]
      │
      ▼
[OCR Processing]  ──── PyMuPDF (PDF) / EasyOCR (Image)
      │                Page-wise JSON → data/processed/
      ▼
[LLM Extraction]  ──── Groq llama-3.3-70b-versatile
      │                Tender criteria / Bidder data → data/extracted/
      ▼
[Rule Engine]     ──── Smart key matching + operator evaluation
      │                Pass / Fail / Needs Review per criterion
      ▼
[Explainability]  ──── Rule-based professional explanations
      │                Page-level evidence + confidence score
      ▼
[Results]         ──── Final JSON → data/results/
      │
      ▼
[Human Review]    ──── Override AI decision via UI or API
                       Timestamped audit trail preserved
```

---

## 📡 API Endpoints

### 1. `GET /`
Health check.
```json
{ "message": "Backend is running" }
```

---

### 2. `POST /upload`
Upload tender and bidder documents.

**Form Data:**
| Field | Type | Description |
|-------|------|-------------|
| `tender_file` | File | Single tender document (PDF/PNG/JPG) |
| `bidder_files` | File[] | One or more bidder documents |

**Response:**
```json
{
    "message": "Files uploaded successfully",
    "tender_file_path": "data/uploads/tender.pdf",
    "bidder_file_paths": ["data/uploads/bidder1.pdf"]
}
```

---

### 3. `POST /process`
Run OCR on all uploaded files. Outputs page-wise JSON to `data/processed/`.

**Response:**
```json
{
    "message": "Processing completed.",
    "processed_files": ["tender.pdf"],
    "output_paths": ["data/processed/tender.json"]
}
```

---

### 4. `POST /extract`
Run LLM-based structured extraction on processed text files. Outputs to `data/extracted/`.

**Response:**
```json
{
    "message": "Extraction pipeline completed.",
    "summary": { "processed_files": ["bidder1.json"], "errors": [] }
}
```

---

### 5. `POST /evaluate`
Run rule engine + explainability pipeline. Outputs final evaluation JSON to `data/results/`.

**Example output in `data/results/bidder1.json`:**
```json
{
    "ai_status": "Eligible",
    "human_status": null,
    "final_status": "Eligible",
    "reviewed": false,
    "review_timestamp": null,
    "summary": "3/3 criteria passed",
    "passed": 3,
    "failed": 0,
    "needs_review": 0,
    "total": 3,
    "evaluations": [
        {
            "criterion": "annual turnover",
            "required": 20000000,
            "required_display": "₹2 Cr",
            "found": 80000000,
            "found_display": "₹8 Cr",
            "result": "pass",
            "reason": "Annual turnover requirement satisfied (Required: ₹2 Cr, Found: ₹8 Cr).",
            "evidence": "...annual turnover of rs 8 crore for the last three financial years...",
            "page": 1,
            "source": "Page 1 - Extracted from document",
            "confidence": 0.95
        }
    ]
}
```

---

### 6. `POST /review`
Submit a human-in-the-loop decision override.

**Payload:**
```json
{
    "bidder": "bidder1",
    "human_status": "Eligible"
}
```
*(Valid statuses: `"Eligible"`, `"Not Eligible"`, `"Needs Review"`)*

**Response:**
```json
{
    "message": "Review submitted successfully.",
    "bidder": "bidder1.json",
    "final_status": "Eligible",
    "timestamp": "2026-05-01T11:42:05.123Z"
}
```

### Interactive API Docs
FastAPI auto-generates interactive API documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🖥️ Streamlit Dashboard

The frontend provides a full workflow in three sections:

| Section | What you can do |
|---------|----------------|
| **1. Upload Documents** | Select and upload tender + bidder files |
| **2. Run Evaluation** | Trigger OCR → Extraction → Evaluation in one click |
| **3. Results Dashboard** | View color-coded criteria table, evidence highlights, confidence, and submit human review |

**Color coding:**
- 🟢 **Green** — Criterion passed
- 🔴 **Red** — Criterion failed
- 🟡 **Yellow** — Needs manual review

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI |
| LLM Provider | Groq (`llama-3.3-70b-versatile`) |
| PDF Text Extraction | PyMuPDF (fitz) |
| Image OCR | EasyOCR |
| Frontend | Streamlit |
| HTTP Client | Requests |
| Data Validation | Pydantic |
| Environment Config | python-dotenv |

---

## 🔒 Design Principles

- **Deterministic Decisions**: The rule engine (not the LLM) makes all pass/fail decisions. LLM is used only for extraction.
- **Full Auditability**: Evidence snippets with exact page references are stored for every criterion decision.
- **Human Override**: Human reviewers can always override the AI with a timestamped record, without destroying the original AI analysis.
- **Graceful Degradation**: All pipeline steps have error handling. A single file failure does not crash the pipeline.
- **Extensibility**: Swap out the mock/Groq LLM in `llm_service.py` with any other provider without changing extraction logic.

---

## 📁 Git Structure Notes

The following directories are tracked via `.gitkeep` to preserve structure but their contents are gitignored:
- `data/uploads/` — Raw user-uploaded files
- `data/processed/` — OCR outputs
- `data/extracted/` — LLM extraction outputs
- `data/results/` — Final evaluation outputs

---

## 📄 License

This project was built for the **AI for Bharat** initiative. All rights reserved.
