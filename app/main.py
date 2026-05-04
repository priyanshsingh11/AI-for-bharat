from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, process, extract, evaluate, human_review, results

app = FastAPI(title="TrustGraph AI Backend")

# Allow requests from the Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(extract.router)
app.include_router(evaluate.router)
app.include_router(human_review.router)
app.include_router(results.router)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}
