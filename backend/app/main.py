from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="AI Hub AI/ML Wrangler API",
    description="Statistical data imputation and analysis tool with AI-powered recommendations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Hub AI/ML Wrangler API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aihub-ai-ml-wrangler-api"}

@app.get("/api/v1/status")
async def api_status():
    return {
        "status": "running",
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": "pending",
            "redis": "pending",
            "celery": "pending"
        }
    }