# AI-Based Tender Evaluation System Backend

A clean, modular, and production-ready backend built with FastAPI. This backend is designed to handle file uploads for tender and bidder documents, laying the foundation for an AI-driven tender evaluation system.

## Project Structure

```text
├── app/
│   ├── core/              # Core settings and configurations
│   ├── models/            # Data models and schemas
│   ├── routes/            # API routing files (e.g., upload.py)
│   ├── services/          # Business logic and external services (e.g., file saving)
│   ├── utils/             # Helper functions and utilities
│   ├── main.py            # FastAPI application entry point
│   └── __init__.py
├── data/
│   ├── extracted/         # Directory for structured JSON extracted data
│   ├── processed/         # Directory for processed AI outputs (e.g. OCR text)
│   ├── results/           # Directory for final rule engine evaluations & LLM explanations
│   └── uploads/           # Directory for raw uploaded files
├── venv/                  # Isolated Python virtual environment
├── .gitignore             # Standard Python gitignore rules
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Setup & Installation

### 1. Activate the Virtual Environment
To keep your global environment clean, activate the isolated virtual environment where the project dependencies are already installed.

**For PowerShell (Windows):**
```powershell
.\venv\Scripts\activate
```

### 2. Install Dependencies (If needed)
If you need to re-install or update packages in the future, run:
```powershell
pip install -r requirements.txt
```

### 3. Set Environment Variables
The extraction pipeline uses Groq's LLM API. You must set your API key before running the server.

**For PowerShell (Windows):**
```powershell
$env:GROQ_API_KEY="your_groq_api_key_here"
```

## Running the Server

Start the development server using `uvicorn`:

```powershell
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

## API Endpoints

### 1. Root Endpoint
- **URL**: `/`
- **Method**: `GET`
- **Description**: Health check endpoint to verify the backend is running.
- **Response**: `{"message": "Backend is running"}`

### 2. File Upload API
- **URL**: `/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Description**: Accepts one tender file and multiple bidder files. Validates for allowed formats (PDF, PNG, JPG, JPEG) and saves them locally.
- **Form Data Parameters**:
  - `tender_file`: A single file upload.
  - `bidder_files`: Multiple file uploads.
- **Success Response**:
  ```json
  {
      "message": "Files uploaded successfully",
      "tender_file_path": "data/uploads/tender.pdf",
      "bidder_file_paths": [
          "data/uploads/bidder1.pdf",
          "data/uploads/bidder2.png"
      ]
  }
  ```

### 3. Document Processing API
- **URL**: `/process`
- **Method**: `POST`
- **Description**: Reads all files in the `data/uploads/` directory, extracts their text using PyMuPDF (for PDFs) and EasyOCR (for images), and saves the extracted text to `data/processed/` as `.txt` files.
- **Success Response**:
  ```json
  {
      "message": "Processing completed.",
      "processed_files": [
          "tender.pdf",
          "bidder1.png"
      ],
      "output_paths": [
          "data/processed/tender.txt",
          "data/processed/bidder1.txt"
      ]
  }
  ```

### 4. Extraction API
- **URL**: `/extract`
- **Method**: `POST`
- **Description**: Triggers the LLM extraction pipeline. It reads the `.txt` files in `data/processed/`, identifies whether each is a tender or a bidder document based on its filename, and extracts the structured JSON. The outputs are saved as `.json` files in `data/extracted/`.
- **Success Response**:
  ```json
  {
      "message": "Extraction pipeline completed.",
      "summary": {
          "processed_files": [
              "tender.json",
              "bidder1.json"
          ],
          "errors": []
      }
  }
  ```

### 5. Evaluate API
- **URL**: `/evaluate`
- **Method**: `POST`
- **Description**: Triggers the Explainability Layer and Rule Engine pipeline. It cross-references bidder data against tender criteria extracted in the previous step, generates rule-based deterministic decisions, and creates natural language explanations via the Groq LLM. Outputs are saved as `.json` in `data/results/`.
- **Success Response**:
  ```json
  {
      "message": "Evaluation pipeline completed.",
      "summary": {
          "processed_files": [
              "bidder1.json"
          ],
          "errors": []
      }
  }
  ```

### 6. Human Review API
- **URL**: `/review`
- **Method**: `POST`
- **Description**: Submits a human-in-the-loop validation for an evaluated bidder. Allows a reviewer to override or confirm the AI's decision while safely locking in the audit trail without destroying the raw evidence data.
- **Payload**:
  ```json
  {
      "bidder": "bidder1",
      "human_status": "Eligible" 
  }
  ```
  *(Valid statuses: "Eligible", "Not Eligible", "Needs Review")*
- **Success Response**:
  ```json
  {
      "message": "Review submitted successfully.",
      "bidder": "bidder1.json",
      "final_status": "Eligible",
      "timestamp": "2026-05-01T11:42:05.123Z"
  }
  ```

### Interactive API Docs
FastAPI automatically generates interactive API documentation. You can view it by navigating to:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
