"""
File: router.py

Overview:
Main API router that includes all endpoint modules

Purpose:
Centralize API routing and provide organized endpoint structure

Dependencies:
- FastAPI: Router functionality
- endpoints: Individual endpoint modules

Last Modified: 2025-08-15
Author: Claude
"""

from fastapi import APIRouter

from api.endpoints import health

api_router = APIRouter()

# Include endpoint modules
api_router.include_router(health.router, prefix="/health", tags=["health"])