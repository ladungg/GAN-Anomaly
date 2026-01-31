"""
GAN Anomaly Detection Backend - Entry Point
"""
import uvicorn
from app.config import create_app
from app.routes import register_routes
from app.models.init_db import init_db

# Initialize database
init_db()

# Tạo FastAPI app instance
app = create_app()

# Register all routes
register_routes(app)

if __name__ == "__main__":
    # Chạy server với reload mode cho development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )