"""
Metrics API Endpoints - Lấy metrics, scores, config
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.controllers.metrics_controller import (
    get_training_metrics,
    get_training_config,
    get_anomaly_scores,
    get_confusion_matrix_data,
)

router = APIRouter(
    tags=["metrics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/api/metrics", summary="Lấy training metrics")
def get_metrics():
    """
    Lấy các metrics từ training (ROC AUC, Runtime, etc.)
    """
    metrics = get_training_metrics()
    if metrics is None:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return JSONResponse(metrics)


@router.get("/api/config", summary="Lấy training config")
def get_config():
    """
    Lấy cấu hình training được sử dụng
    """
    config = get_training_config()
    return JSONResponse(config)


@router.get("/api/anomaly-scores", summary="Lấy anomaly scores")
def get_scores():
    """
    Lấy anomaly scores từ model output
    """
    scores = get_anomaly_scores()
    if scores is None:
        raise HTTPException(status_code=404, detail="Anomaly scores not found")
    return JSONResponse({"scores": scores})


@router.get("/api/confusion-matrix", summary="Lấy confusion matrix")
def get_confusion_matrix():
    """
    Lấy confusion matrix từ model evaluation
    """
    cm = get_confusion_matrix_data()
    if cm is None:
        raise HTTPException(status_code=404, detail="Confusion matrix not found")
    return JSONResponse(cm)
