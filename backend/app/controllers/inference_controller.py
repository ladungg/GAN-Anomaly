"""
Inference Controller - Orchestrate CSV upload and predictions

Response Structure for /predict endpoint:
{
    "status": "success",
    "upload_id": <id>,
    "total": <total_rows>,
    "normal_count": <count>,
    "attack_count": <count>,
    "anomaly_percentage": <percentage>,
    "predictions": [0, 1, 0, 1, ...],  # 0=normal (no color), 1=attack (RED)
    "anomaly_scores": [0.2, 0.8, 0.1, 0.9, ...]  # Confidence scores
}

Frontend uses:
- predictions[i] = 1 → Color row RED (attack detected)
- predictions[i] = 0 → No color (normal)
"""
from typing import Dict, Any
import numpy as np
from app.services.inference_engine import InferenceEngine
from app.services.csv_processor import (
    save_uploaded_file,
    read_csv_file,
    reshape_data_to_features,
    store_csv_upload,
    store_predictions,
    store_inference_summary,
    get_upload_info,
    get_predictions_by_upload,
    get_inference_summary,
    list_all_uploads,
)
from app.services.config_reader import read_training_config
from app.services.logging_service import (
    create_inference_log,
    get_all_inference_logs,
    get_logs_by_upload,
    get_inference_statistics,
)

# Global inference engine
_inference_engine = None


def get_inference_engine() -> InferenceEngine:
    """
    Get or create inference engine singleton
    """
    global _inference_engine
    
    if _inference_engine is None:
        _inference_engine = InferenceEngine(device="cpu")
    
    return _inference_engine


def initialize_inference_engine(config: Dict[str, Any] = None) -> bool:
    """
    Initialize inference engine with pre-trained models
    Args:
        config: Training config (optional)
    Returns: True if successful
    """
    engine = get_inference_engine()
    
    if not engine.is_loaded:
        return engine.load_models(config)
    
    return True


def upload_csv_file(filename: str, file_content: bytes) -> Dict[str, Any]:
    """
    Handle CSV file upload
    Args:
        filename: Original filename
        file_content: File content as bytes
    Returns: Dict with upload info
    """
    try:
        # Save file to disk
        file_path, success = save_uploaded_file(file_content, filename)
        if not success:
            return {
                "status": "error",
                "message": "Failed to save file",
                "upload_id": None
            }
        
        # Read CSV data
        data, num_rows, num_features, success = read_csv_file(file_path)
        if not success:
            return {
                "status": "error",
                "message": "Failed to read CSV file",
                "upload_id": None
            }
        
        # Store in database
        upload_id = store_csv_upload(filename, file_path, num_rows, num_features)
        if upload_id == -1:
            return {
                "status": "error",
                "message": "Failed to store upload info in database",
                "upload_id": None
            }
        
        return {
            "status": "success",
            "message": f"File uploaded successfully",
            "upload_id": upload_id,
            "filename": filename,
            "num_rows": num_rows,
            "num_features": num_features
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Upload error: {str(e)}",
            "upload_id": None
        }


def run_inference(filename: str, file_content: bytes, threshold: float = 0.985) -> Dict[str, Any]:
    """
    Run inference on CSV file directly (from dashboard upload)
    Args:
        filename: CSV filename
        file_content: CSV file bytes
        threshold: Anomaly threshold (0-1)
    Returns: Dict with counts - total, normal_count, attack_count
    """
    try:
        # Save file temporarily
        file_path, success = save_uploaded_file(file_content, filename)
        if not success:
            return {
                "status": "error",
                "message": "Failed to save file"
            }
        
        # Read CSV data - skip the label column
        data, num_rows, num_features, success = read_csv_file(file_path)
        if not success:
            return {
                "status": "error",
                "message": "Failed to read CSV file"
            }
        
        # Store in database FIRST (get upload_id)
        upload_id = store_csv_upload(filename, file_path, num_rows, num_features)
        if upload_id == -1:
            return {
                "status": "error",
                "message": "Failed to store upload info in database"
            }
        
        # Initialize engine if needed
        if not initialize_inference_engine():
            return {
                "status": "error",
                "message": "Failed to load inference models. Check if netG.pth and netD.pth exist."
            }
        
        # Run inference
        engine = get_inference_engine()
        
        # Data should be (N, features) - typically 116 for NSL-KDD
        # Remove label column if present (last column)
        if data.shape[1] > 116:
            data = data[:, :116]  # Keep only first 116 features
        
        print(f"[INFO] Running inference on {data.shape[0]} samples with {data.shape[1]} features")
        
        # Run inference using discriminator
        result = engine.predict_batch(data, threshold=threshold)
        
        # Get stats
        stats = result["statistics"]
        
        # Store row-by-row predictions
        store_predictions(
            upload_id=upload_id,
            anomaly_scores=result["anomaly_scores"],
            is_anomaly=result["is_anomaly"],
            predictions=result["predictions"],
            confidence=result["anomaly_scores"]
        )
        
        # Save annotated CSV with prediction_status column (NORMAL/ATTACK)
        from app.services.csv_processor import save_annotated_csv
        annotated_path = save_annotated_csv(file_path, result["is_anomaly"])
        
        # Create inference log with the upload_id we just got
        log_id = create_inference_log(
            upload_id=upload_id,
            csv_filename=filename,
            total_samples=stats["total_samples"],
            normal_count=stats["normal_count"],
            anomaly_count=stats["anomaly_count"],
            anomaly_percentage=stats["anomaly_percentage"],
            threshold=threshold,
            inference_time_ms=stats["inference_time_ms"],
            model_status="success",
            error_message=None
        )
        
        print(f"[OK] Inference result: {stats['normal_count']} normal, {stats['anomaly_count']} anomalies")
        print(f"[OK] Log ID: {log_id}, Upload ID: {upload_id}")
        
        return {
            "status": "success",
            "message": "Inference completed successfully",
            "upload_id": upload_id,
            "total": stats["total_samples"],
            "normal_count": stats["normal_count"],
            "attack_count": stats["anomaly_count"],
            "anomaly_percentage": stats["anomaly_percentage"],
            "log_id": log_id,
            "predictions": result["is_anomaly"],  # Row-by-row anomaly flags (0=normal, 1=attack)
            "anomaly_scores": result["anomaly_scores"],  # Confidence scores for each row
            "download_filename": annotated_path.name if annotated_path else None  # File to download
        }
    
    except Exception as e:
        print(f"[ERROR] Inference error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Inference error: {str(e)}"
        }


def run_inference_by_id(upload_id: int, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Run inference on uploaded CSV data (original version using upload_id)
    Args:
        upload_id: ID of uploaded CSV
        threshold: Anomaly threshold (0-1)
    Returns: Dict with predictions and summary
    """
    try:
        # Get upload info
        upload_info = get_upload_info(upload_id)
        if not upload_info:
            # Log error
            create_inference_log(
                upload_id, "unknown", 0, 0, 0, 0, threshold, 0,
                model_status="error",
                error_message=f"Upload ID {upload_id} not found"
            )
            return {
                "status": "error",
                "message": f"Upload ID {upload_id} not found",
                "upload_id": upload_id
            }
        
        # Read CSV data again
        from pathlib import Path
        file_path = Path(upload_info["file_path"])
        data, num_rows, num_features, success = read_csv_file(file_path)
        if not success:
            # Log error
            create_inference_log(
                upload_id, upload_info["filename"], 0, 0, 0, 0, threshold, 0,
                model_status="error",
                error_message="Failed to read CSV file"
            )
            return {
                "status": "error",
                "message": "Failed to read CSV file",
                "upload_id": upload_id
            }
        
        # Initialize engine if needed
        if not initialize_inference_engine():
            # Log error
            create_inference_log(
                upload_id, upload_info["filename"], num_rows, 0, 0, 0, threshold, 0,
                model_status="error",
                error_message="Failed to load inference models"
            )
            return {
                "status": "error",
                "message": "Failed to load inference models",
                "upload_id": upload_id
            }
        
        # Run inference
        engine = get_inference_engine()
        
        # Reshape data to match expected features (116 for NSL-KDD)
        reshaped_data = reshape_data_to_features(data, target_features=116)
        
        # Run inference using discriminator
        result = engine.predict_batch(reshaped_data, threshold=threshold)
        
        # Store predictions
        store_predictions(
            upload_id,
            result["anomaly_scores"],
            result["is_anomaly"],
            result["predictions"]
        )
        
        # Store summary
        stats = result["statistics"]
        store_inference_summary(
            upload_id,
            stats["total_samples"],
            stats["normal_count"],
            stats["anomaly_count"],
            stats["anomaly_percentage"],
            stats["inference_time_ms"]
        )
        
        # CREATE INFERENCE LOG
        log_id = create_inference_log(
            upload_id=upload_id,
            csv_filename=upload_info["filename"],
            total_samples=stats["total_samples"],
            normal_count=stats["normal_count"],
            anomaly_count=stats["anomaly_count"],
            anomaly_percentage=stats["anomaly_percentage"],
            threshold=threshold,
            inference_time_ms=stats["inference_time_ms"],
            model_status="success",
            error_message=None
        )
        
        return {
            "status": "success",
            "message": "Inference completed successfully",
            "upload_id": upload_id,
            "log_id": log_id,
            "filename": upload_info["filename"],
            "row_predictions": result["is_anomaly"],  # 0=normal (no color), 1=attack (red)
            "anomaly_scores": result["anomaly_scores"],  # Confidence scores
            "predictions": result,  # Full prediction details
            "summary": {
                "total_samples": stats["total_samples"],
                "normal_count": stats["normal_count"],
                "anomaly_count": stats["anomaly_count"],
                "anomaly_percentage": f"{stats['anomaly_percentage']:.2f}%",
                "inference_time_ms": f"{stats['inference_time_ms']:.2f}",
                "threshold": threshold
            }
        }
    
    except Exception as e:
        # Log error
        create_inference_log(
            upload_id, "unknown", 0, 0, 0, 0, threshold, 0,
            model_status="error",
            error_message=str(e)
        )
        return {
            "status": "error",
            "message": f"Inference error: {str(e)}",
            "upload_id": upload_id
        }


def get_inference_result(upload_id: int) -> Dict[str, Any]:
    """
    Get complete inference result for an upload
    Args:
        upload_id: ID of upload
    Returns: Dict with upload info, predictions, and summary
    """
    try:
        upload_info = get_upload_info(upload_id)
        if not upload_info:
            return {
                "status": "error",
                "message": f"Upload ID {upload_id} not found"
            }
        
        predictions = get_predictions_by_upload(upload_id)
        summary = get_inference_summary(upload_id)
        
        return {
            "status": "success",
            "upload_id": upload_id,
            "upload_info": upload_info,
            "predictions": predictions,
            "summary": summary
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving result: {str(e)}"
        }


def get_all_uploads() -> Dict[str, Any]:
    """
    Get list of all uploads with their summaries
    Returns: Dict with list of uploads
    """
    try:
        uploads = list_all_uploads()
        
        # Add summary for each upload
        for upload in uploads:
            summary = get_inference_summary(upload["upload_id"])
            if summary:
                upload["summary"] = summary
        
        return {
            "status": "success",
            "uploads": uploads,
            "total_uploads": len(uploads)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing uploads: {str(e)}"
        }


def get_inference_logs(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """
    Get all inference logs with pagination
    Args:
        limit: Max number of logs to return
        offset: Offset for pagination
    Returns: Dict with logs and metadata
    """
    try:
        logs = get_all_inference_logs(limit=limit, offset=offset)
        stats = get_inference_statistics()
        
        return {
            "status": "success",
            "logs": logs,
            "total_logs": stats.get("total_logs", 0),
            "statistics": stats
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting logs: {str(e)}"
        }


def get_logs_for_upload(upload_id: int) -> Dict[str, Any]:
    """
    Get all logs for a specific upload
    Args:
        upload_id: ID of upload
    Returns: Dict with logs for that upload
    """
    try:
        logs = get_logs_by_upload(upload_id)
        
        return {
            "status": "success",
            "upload_id": upload_id,
            "logs": logs,
            "total_logs": len(logs)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting logs for upload: {str(e)}"
        }


def get_inference_stats() -> Dict[str, Any]:
    """
    Get overall inference statistics
    Returns: Dict with statistics
    """
    try:
        stats = get_inference_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting statistics: {str(e)}"
        }

