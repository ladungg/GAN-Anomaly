"""
Logging Service - Handle inference logs
"""
from typing import Optional, List, Dict, Any
from app.models.database import get_db
from datetime import datetime


def create_inference_log(
    upload_id: int,
    csv_filename: str,
    total_samples: int,
    normal_count: int,
    anomaly_count: int,
    anomaly_percentage: float,
    threshold: float,
    inference_time_ms: float,
    model_status: str = "success",
    error_message: Optional[str] = None,
    user_notes: Optional[str] = None
) -> int:
    """
    Create inference log entry in database
    
    Args:
        upload_id: ID of CSV upload
        csv_filename: Original CSV filename
        total_samples: Total samples processed
        normal_count: Count of normal samples
        anomaly_count: Count of anomalous samples
        anomaly_percentage: Percentage of anomalies
        threshold: Anomaly threshold used
        inference_time_ms: Time taken for inference
        model_status: Status of inference (success/error)
        error_message: Error message if any
        user_notes: Optional user notes
        
    Returns: log_id if successful, -1 if error
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO inference_logs 
            (upload_id, csv_filename, total_samples, normal_count, anomaly_count, 
             anomaly_percentage, threshold, inference_time_ms, model_status, 
             error_message, user_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            upload_id, csv_filename, total_samples, normal_count, anomaly_count,
            anomaly_percentage, threshold, inference_time_ms, model_status,
            error_message, user_notes
        ))
        
        log_id = cursor.lastrowid
        
        print(f"✅ Log created with ID: {log_id}")
        return log_id
    
    except Exception as e:
        print(f"❌ Error creating inference log: {e}")
        import traceback
        traceback.print_exc()
        return -1
    finally:
        if conn:
            conn.close()


def get_inference_log(log_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific inference log by ID
    
    Args:
        log_id: ID of the log
        
    Returns: Dict with log details or None
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM inference_logs WHERE log_id = ?", (log_id,))
        result = cursor.fetchone()
        
        if result:
            return {
                "log_id": result[0],
                "upload_id": result[1],
                "csv_filename": result[2],
                "total_samples": result[3],
                "normal_count": result[4],
                "anomaly_count": result[5],
                "anomaly_percentage": result[6],
                "threshold": result[7],
                "inference_time_ms": result[8],
                "model_status": result[9],
                "error_message": result[10],
                "user_notes": result[11],
                "created_at": result[12]
            }
        return None
    except Exception as e:
        print(f"❌ Error getting inference log: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_inference_logs(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all inference logs with pagination
    
    Args:
        limit: Max number of logs to return
        offset: Offset for pagination
        
    Returns: List of log dicts
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM inference_logs 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        results = cursor.fetchall()
        
        logs = []
        for row in results:
            logs.append({
                "log_id": row[0],
                "upload_id": row[1],
                "csv_filename": row[2],
                "total_samples": row[3],
                "normal_count": row[4],
                "anomaly_count": row[5],
                "anomaly_percentage": row[6],
                "threshold": row[7],
                "inference_time_ms": row[8],
                "model_status": row[9],
                "error_message": row[10],
                "user_notes": row[11],
                "created_at": row[12]
            })
        
        return logs
    
    except Exception as e:
        print(f"❌ Error getting inference logs: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_logs_by_upload(upload_id: int) -> List[Dict[str, Any]]:
    """
    Get all logs for a specific upload
    
    Args:
        upload_id: ID of CSV upload
        
    Returns: List of log dicts
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM inference_logs 
            WHERE upload_id = ? 
            ORDER BY created_at DESC
        """, (upload_id,))
        
        results = cursor.fetchall()
        
        logs = []
        for row in results:
            logs.append({
                "log_id": row[0],
                "upload_id": row[1],
                "csv_filename": row[2],
                "total_samples": row[3],
                "normal_count": row[4],
                "anomaly_count": row[5],
                "anomaly_percentage": row[6],
                "threshold": row[7],
                "inference_time_ms": row[8],
                "model_status": row[9],
                "error_message": row[10],
                "user_notes": row[11],
                "created_at": row[12]
            })
        
        return logs
    
    except Exception as e:
        print(f"❌ Error getting logs by upload: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_logs_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Get logs within a date range (YYYY-MM-DD format)
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns: List of log dicts
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM inference_logs 
            WHERE DATE(created_at) >= ? AND DATE(created_at) <= ?
            ORDER BY created_at DESC
        """, (start_date, end_date))
        
        results = cursor.fetchall()
        
        logs = []
        for row in results:
            logs.append({
                "log_id": row[0],
                "upload_id": row[1],
                "csv_filename": row[2],
                "total_samples": row[3],
                "normal_count": row[4],
                "anomaly_count": row[5],
                "anomaly_percentage": row[6],
                "threshold": row[7],
                "inference_time_ms": row[8],
                "model_status": row[9],
                "error_message": row[10],
                "user_notes": row[11],
                "created_at": row[12]
            })
        
        return logs
    
    except Exception as e:
        print(f"❌ Error getting logs by date range: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_inference_statistics() -> Dict[str, Any]:
    """
    Get overall inference statistics
    
    Returns: Dict with statistics
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Total logs
        cursor.execute("SELECT COUNT(*) FROM inference_logs")
        total_logs = cursor.fetchone()[0]
        
        # Total samples processed
        cursor.execute("SELECT SUM(total_samples) FROM inference_logs WHERE model_status = 'success'")
        total_samples = cursor.fetchone()[0] or 0
        
        # Total anomalies
        cursor.execute("SELECT SUM(anomaly_count) FROM inference_logs WHERE model_status = 'success'")
        total_anomalies = cursor.fetchone()[0] or 0
        
        # Average anomaly percentage
        cursor.execute("SELECT AVG(anomaly_percentage) FROM inference_logs WHERE model_status = 'success'")
        avg_anomaly_percentage = cursor.fetchone()[0] or 0
        
        # Failed inferences
        cursor.execute("SELECT COUNT(*) FROM inference_logs WHERE model_status = 'error'")
        failed_inferences = cursor.fetchone()[0]
        
        # Average inference time
        cursor.execute("SELECT AVG(inference_time_ms) FROM inference_logs WHERE model_status = 'success'")
        avg_inference_time = cursor.fetchone()[0] or 0
        
        return {
            "total_logs": total_logs,
            "successful_inferences": total_logs - failed_inferences,
            "failed_inferences": failed_inferences,
            "total_samples_processed": int(total_samples),
            "total_anomalies_detected": int(total_anomalies),
            "average_anomaly_percentage": round(avg_anomaly_percentage, 2),
            "average_inference_time_ms": round(avg_inference_time, 2)
        }
    
    except Exception as e:
        print(f"❌ Error getting inference statistics: {e}")
        return {}
    finally:
        if conn:
            conn.close()


def update_log_notes(log_id: int, user_notes: str) -> bool:
    """
    Update user notes for a log
    
    Args:
        log_id: ID of the log
        user_notes: Notes to add
        
    Returns: True if successful
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE inference_logs 
            SET user_notes = ? 
            WHERE log_id = ?
        """, (user_notes, log_id))
        
        return True
    
    except Exception as e:
        print(f"❌ Error updating log notes: {e}")
        return False
    finally:
        if conn:
            conn.close()


def delete_old_logs(days: int = 30) -> int:
    """
    Delete logs older than specified days
    
    Args:
        days: Keep logs from last N days
        
    Returns: Number of logs deleted
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM inference_logs 
            WHERE DATE(created_at) < DATE('now', ? || ' days')
        """, (f'-{days}',))
        
        deleted_count = cursor.rowcount
        
        print(f"✅ Deleted {deleted_count} old logs")
        return deleted_count
    
    except Exception as e:
        print(f"❌ Error deleting old logs: {e}")
        return 0
    finally:
        if conn:
            conn.close()
