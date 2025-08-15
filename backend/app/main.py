"""
File: main.py

Overview:
FastAPI application entry point with CORS and API routing

Purpose:
Main application setup and configuration for the AI/ML Wrangler backend

Dependencies:
- fastapi for web framework
- fastapi.middleware.cors for CORS support
- upload API routes

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.upload import router as upload_router

# Create FastAPI application
app = FastAPI(
    title="AI Hub AI/ML Wrangler API",
    description="Backend API for AI-powered data imputation and analysis tool",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Hub AI/ML Wrangler API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)