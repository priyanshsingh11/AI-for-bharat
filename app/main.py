from fastapi import FastAPI
from app.routes import upload, process, extract

app = FastAPI(title="Tender Evaluation System Backend")

# Include the routers
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(extract.router)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}
