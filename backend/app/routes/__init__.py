"""
Routes package - API endpoint definitions
"""
from fastapi import FastAPI


def register_routes(app: FastAPI):
    """
    Register all API routes to the FastAPI app
    """
    from app.routes.v1 import training, metrics, inference, auth

    # Register all routers
    app.include_router(auth.router)
    app.include_router(training.router)
    app.include_router(inference.router)
    app.include_router(metrics.router)
