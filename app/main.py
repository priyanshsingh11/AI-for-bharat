from fastapi import FastAPI
from app.routes import upload

app = FastAPI(title="Tender Evaluation System Backend")

# Include the upload router
app.include_router(upload.router)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}
