from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, process, extract, evaluate, human_review, results

app = FastAPI(title="TrustGraph AI Backend")

# Allow all origins for hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers with an /api prefix
app.include_router(upload.router, prefix="/api")
app.include_router(process.router, prefix="/api")
app.include_router(extract.router, prefix="/api")
app.include_router(evaluate.router, prefix="/api")
app.include_router(human_review.router, prefix="/api")
app.include_router(results.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Backend is running"}
