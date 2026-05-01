from fastapi import FastAPI
from app.routes import upload, process, extract, evaluate, human_review

app = FastAPI(title="Tender Evaluation System Backend")

# Include the routers
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(extract.router)
app.include_router(evaluate.router)
app.include_router(human_review.router)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}
