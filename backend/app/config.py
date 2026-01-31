"""
Application configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app():
    """
    Factory function để tạo FastAPI application
    """
    app = FastAPI(
        title="GAN Anomaly Detection API",
        description="Backend API cho GAN Anomaly Detection Dashboard",
        version="1.0.0",
    )

    # ===============================
    # CORS Configuration
    # ===============================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
