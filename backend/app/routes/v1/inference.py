"""
Inference API Endpoints - Upload CSV and run anomaly detection
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from app.controllers.inference_controller import (
    upload_csv_file,
    run_inference,
    get_inference_result,
    get_all_uploads,
    get_inference_logs,
    get_logs_for_upload,
    get_inference_stats,
)

router = APIRouter(
    prefix="/api/inference",
    tags=["inference"],
    responses={404: {"description": "Not found"}},
)


# ===============================
# Pydantic Models for validation
# ===============================
class InferenceRequest(BaseModel):
    """Schema for inference request"""
    upload_id: int
    threshold: float = 0.5


# ===============================
# POST Endpoints (Upload & Predict)
# ===============================
@router.post("/upload", summary="Upload CSV file")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file for anomaly detection
    
    The CSV should contain network traffic or other numerical features.
    Each row is treated as one sample.
    
    Returns:
    - upload_id: ID for this upload (use for prediction)
    - num_rows: Number of samples in CSV
    - num_features: Number of features per sample
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Read file content
        content = await file.read()
        
        # Process upload
        result = upload_csv_file(file.filename, content)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@router.post("/predict", summary="Run inference on file")
async def predict(file: UploadFile = File(...)):
    """
    Run inference on uploaded CSV file
    Returns counts: total, normal_count, attack_count
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files allowed")
        
        content = await file.read()
        result = run_inference(file.filename, content)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# ===============================
# GET Endpoints (Retrieve Results)
# ===============================
@router.get("/result/{upload_id}", summary="Get inference result")
def get_result(upload_id: int):
    """
    Get complete inference result for an upload
    
    Returns:
    - upload_info: File and upload details
    - predictions: Per-sample predictions and anomaly scores
    - summary: Overall statistics
    """
    try:
        if upload_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid upload_id")
        
        result = get_inference_result(upload_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/download/{filename}", summary="Download annotated CSV file")
def download_file(filename: str):
    """
    Download CSV file with prediction annotations from results folder
    
    CSV will have a 'prediction_status' column with values:
    - 'NORMAL': No attack detected (no color in frontend)
    - 'ATTACK': Attack detected (RED in frontend)
    """
    from pathlib import Path
    from fastapi.responses import FileResponse
    
    try:
        # Get file from results directory
        file_path = Path("results") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found in results")
        
        # Prevent directory traversal attacks
        if ".." in str(file_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="text/csv"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/uploads", summary="List all uploads")
def list_uploads():
    """
    Get list of all CSV uploads and their inference results
    
    Returns:
    - List of uploads with summaries
    - total_uploads: Total number of uploads
    """
    try:
        result = get_all_uploads()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ===============================
# GET Endpoints (Logs & Statistics)
# ===============================
@router.get("/logs", summary="Get all inference logs")
def get_all_logs(limit: int = Query(100), offset: int = Query(0)):
    """
    Get all inference logs with pagination
    
    Parameters:
    - limit: Max number of logs to return (default 100)
    - offset: Offset for pagination (default 0)
    
    Returns:
    - logs: List of all inference logs
    - statistics: Overall statistics
    """
    try:
        result = get_inference_logs(limit=limit, offset=offset)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/logs/upload/{upload_id}", summary="Get logs for specific upload")
def get_upload_logs(upload_id: int):
    """
    Get all logs for a specific upload
    
    Returns:
    - logs: All inference logs for this upload
    - total_logs: Number of logs
    """
    try:
        if upload_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid upload_id")
        
        result = get_logs_for_upload(upload_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/statistics", summary="Get inference statistics")
def get_stats():
    """
    Get overall inference statistics
    
    Returns:
    - total_logs: Total number of inference runs
    - successful_inferences: Number of successful runs
    - failed_inferences: Number of failed runs
    - total_samples_processed: Total samples analyzed
    - total_anomalies_detected: Total anomalies found
    - average_anomaly_percentage: Average anomaly rate
    - average_inference_time_ms: Average inference time
    """
    try:
        result = get_inference_stats()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return JSONResponse(result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ===============================
# Health Check
# ===============================
@router.get("/health", summary="Check inference service health")
def health_check():
    """
    Check if inference service is ready
    
    Returns:
    - status: 'ready' if models are loaded, 'not_ready' if not
    """
    try:
        from app.controllers.inference_controller import initialize_inference_engine
        
        if initialize_inference_engine():
            return JSONResponse({
                "status": "ready",
                "message": "Inference service is ready"
            })
        else:
            return JSONResponse({
                "status": "not_ready",
                "message": "Failed to load models",
                "hint": "Make sure netG.pth and netD.pth exist in GANAnomaly/output/FlowGANAnomaly/nsl/train/weights/"
            }, status_code=503)
    
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)
