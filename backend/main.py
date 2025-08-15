"""
File: main.py

Overview:
Main FastAPI application entry point for the AI Hub AI/ML Wrangler backend.
Sets up the FastAPI app with data processing pipeline endpoints.

Purpose:
Serves as the primary backend server for data processing, validation,
and analysis operations for the AI ML Wrangler tool.

Dependencies:
- FastAPI for web framework
- CORS middleware for frontend integration
- Data processing pipeline endpoints

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.data_preview import router as data_preview_router

app = FastAPI(
    title="AI Hub AI/ML Wrangler Backend",
    description="Data processing pipeline for statistical imputation and analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(data_preview_router, prefix="/api/data", tags=["data"])

@app.get("/")
async def root():
    return {"message": "AI Hub AI/ML Wrangler Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "data-processing-pipeline"}