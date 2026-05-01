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
│   ├── processed/         # Directory for processed AI outputs
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

### Interactive API Docs
FastAPI automatically generates interactive API documentation. You can view it by navigating to:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
