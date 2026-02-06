from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.models import init_db
from app.routes import router
import os

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Marketing Automation Tool",
    description="Internal tool for automating marketing data processing and reporting",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Marketing Automation Tool API",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /upload-csv",
            "metrics": "GET /metrics",
            "summary": "GET /summary",
            "campaigns": "GET /campaigns",
            "daily_performance": "GET /daily-performance",
            "top_campaigns": "GET /top-campaigns",
            "upload_logs": "GET /upload-logs",
            "health": "GET /health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
