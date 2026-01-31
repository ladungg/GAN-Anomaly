"""
CSV Processor - Handle CSV uploads and storage
"""
import csv
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, List
from app.models.database import get_db
import tempfile
import shutil

# Directory to store uploaded CSV files
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Directory to store inference result files
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Expected feature count for trained models
# NSL-KDD (preprocessed): 122 features (39 numeric + one-hot encoded categoricals)
# Or: 116 features (if already preprocessed or one-hot encoded differently)
EXPECTED_FEATURES = 116


def preprocess_nslkdd_data(df: pd.DataFrame, target_features: int = 116) -> np.ndarray:
    """
    Preprocess NSL-KDD data to match training format (116 features)
    One-hot encode categorical columns: protocol_type, service, flag
    Scale numeric features using MinMaxScaler
    Pad to 116 features if needed
    
    Args:
        df: DataFrame with NSL-KDD format (44 columns)
        target_features: Target feature count (default 116 for model input)
        
    Returns: Preprocessed numpy array (N, 116)
    """
    from sklearn.preprocessing import MinMaxScaler
    
    df = df.copy()
    
    # Drop metadata columns
    drop_cols = ["num", "number"]
    for col in drop_cols:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)
    
    # One-hot encode categorical columns
    symbolic_columns = ["protocol_type", "service", "flag"]
    for col in symbolic_columns:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col)
            df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
    
    # Drop label column
    if "label" in df.columns:
        df.drop("label", axis=1, inplace=True)
    
    # Scale numeric features
    scaler = MinMaxScaler()
    data = scaler.fit_transform(df.values.astype(float))
    
    # Pad or truncate to target features
    num_rows, current_features = data.shape
    if current_features < target_features:
        # Pad with zeros
        padding = np.zeros((num_rows, target_features - current_features))
        data = np.hstack([data, padding])
        print(f"[INFO] Padded {current_features} → {target_features} features")
    elif current_features > target_features:
        # Truncate to target
        data = data[:, :target_features]
        print(f"[INFO] Truncated {current_features} → {target_features} features")
    
    return data


def reshape_data_to_features(data: np.ndarray, target_features: int = EXPECTED_FEATURES) -> np.ndarray:
    """
    Reshape or pad CSV data to match expected feature count
    
    Args:
        data: Input data (num_rows, num_features)
        target_features: Target feature count (default 116 for NSL-KDD)
    
    Returns:
        Reshaped data (num_rows, target_features)
    """
    num_rows, current_features = data.shape
    
    if current_features == target_features:
        return data
    elif current_features < target_features:
        # Pad with zeros
        padding = np.zeros((num_rows, target_features - current_features))
        reshaped = np.hstack([data, padding])
        print(f"⚠️  Input has {current_features} features, padded to {target_features}")
        return reshaped
    else:
        # Truncate
        reshaped = data[:, :target_features]
        print(f"⚠️  Input has {current_features} features, truncated to {target_features}")
        return reshaped



def save_uploaded_file(file_content: bytes, filename: str) -> Tuple[Path, bool]:
    """
    Save uploaded file to disk
    Args:
        file_content: File content as bytes
        filename: Original filename
    Returns: (file_path, success)
    """
    try:
        # Create safe filename
        safe_filename = Path(filename).name
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path, True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return None, False


def read_csv_file(file_path: Path) -> Tuple[np.ndarray, int, int, bool]:
    """
    Read CSV file and convert to numpy array
    Automatically detect: preprocessed (124 features) vs raw NSL-KDD (44 columns)
    
    Args:
        file_path: Path to CSV file
    Returns: (data_array, num_rows, num_features, success)
    """
    try:
        # Read CSV with pandas to handle headers properly
        df = pd.read_csv(file_path)
        
        # Check if this is NSL-KDD raw format (has protocol_type, service, flag, label columns)
        is_nslkdd_raw = ('protocol_type' in df.columns and 
                         'service' in df.columns and 
                         'flag' in df.columns and
                         df.shape[1] >= 40)
        
        if is_nslkdd_raw:
            print(f"[INFO] Detected NSL-KDD raw format ({df.shape[1]} columns)")
            # Preprocess NSL-KDD data (one-hot encode + scale)
            data = preprocess_nslkdd_data(df)
            num_rows, num_features = data.shape
            print(f"[INFO] NSL-KDD preprocessed: {num_rows} rows × {num_features} features")
            return data, num_rows, num_features, True
        
        # Check if this is already preprocessed NSL-KDD (124 numeric + bool columns)
        # Include both numeric and bool columns (bool columns are one-hot encoded categoricals)
        numeric_cols = df.select_dtypes(include=[np.number, 'bool']).columns.tolist()
        
        if len(numeric_cols) >= 120:  # 124 preprocessed features (44 numeric + 78-80 bool)
            print(f"[INFO] Detected preprocessed format ({len(numeric_cols)} numeric/bool columns)")
            # Remove label if present
            non_feature_cols = ['label', 'number', 'Label', 'Number']
            feature_cols = [col for col in numeric_cols if col not in non_feature_cols]
            # Convert bool to float (True=1.0, False=0.0)
            data = df[feature_cols].astype(float).values
            num_rows, num_features = data.shape
            print(f"[INFO] Using {num_features} preprocessed features")
            return data, num_rows, num_features, True
        
        # Otherwise, handle as generic numeric CSV
        # Remove label column if present
        # Include both numeric and bool columns
        numeric_cols = df.select_dtypes(include=[np.number, 'bool']).columns.tolist()
        non_feature_cols = ['label', 'number', 'Label', 'Number']
        feature_cols = [col for col in numeric_cols if col not in non_feature_cols]
        
        # Select appropriate columns
        if len(feature_cols) == 116:
            data = df[feature_cols].values.astype(float)
            print(f"[INFO] Using {len(feature_cols)} features (removed label column)")
        elif len(numeric_cols) == 116:
            data = df[numeric_cols].values.astype(float)
            print(f"[INFO] Using {len(numeric_cols)} numeric features")
        elif len(numeric_cols) >= 116:
            data = df[numeric_cols[:116]].values.astype(float)
            print(f"[INFO] CSV has {len(numeric_cols)} numeric columns, keeping first 116 features")
        else:
            data = df[numeric_cols].values.astype(float)
            print(f"[INFO] CSV has {len(numeric_cols)} numeric columns (less than 116)")
        
        # Handle 1D array (single row)
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        
        num_rows, num_features = data.shape
        
        # Check for NaN values
        if np.isnan(data).any():
            print(f"⚠️  Warning: CSV contains NaN values, they will be replaced with 0")
            data = np.nan_to_num(data, nan=0.0)
        
        return data, num_rows, num_features, True
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        import traceback
        traceback.print_exc()
        return None, 0, 0, False



def store_csv_upload(filename: str, file_path: Path, num_rows: int, num_features: int) -> int:
    """
    Store CSV upload information in database
    Args:
        filename: Original filename
        file_path: Path where file was saved
        num_rows: Number of rows in CSV
        num_features: Number of features (columns)
    Returns: upload_id
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        print(f"[DEBUG] Inserting CSV upload: filename={filename}, rows={num_rows}, features={num_features}")
        print(f"[DEBUG] File path: {file_path}")
        
        cursor.execute("""
            INSERT INTO csv_uploads (filename, file_path, num_rows, num_features, upload_status)
            VALUES (?, ?, ?, ?, ?)
        """, (filename, str(file_path), num_rows, num_features, 'completed'))
        
        upload_id = cursor.lastrowid
        
        # Verify insertion (autocommit already done)
        cursor.execute("SELECT COUNT(*) FROM csv_uploads WHERE upload_id = ?", (upload_id,))
        count = cursor.fetchone()[0]
        
        if count == 1:
            print(f"✅ CSV upload stored successfully! upload_id={upload_id}")
            return upload_id
        else:
            print(f"❌ Verification failed! Expected 1 row, got {count}")
            return -1
    
    except Exception as e:
        print(f"❌ Error storing upload info: {e}")
        import traceback
        traceback.print_exc()
        return -1
    finally:
        if conn:
            conn.close()


def store_predictions(upload_id: int, anomaly_scores: List[float], 
                     is_anomaly: List[int], predictions: List[float], 
                     confidence: List[float] = None) -> bool:
    """
    Store prediction results in database
    Args:
        upload_id: ID of CSV upload
        anomaly_scores: List of anomaly scores
        is_anomaly: List of binary predictions (0 or 1)
        predictions: List of model predictions
        confidence: List of confidence scores
    Returns: True if success
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # If confidence not provided, use anomaly_scores
        if confidence is None:
            confidence = anomaly_scores
        
        # Insert each prediction
        for idx, (score, anomaly, pred, conf) in enumerate(
            zip(anomaly_scores, is_anomaly, predictions, confidence)):
            
            cursor.execute("""
                INSERT INTO predictions 
                (upload_id, row_index, anomaly_score, is_anomaly, prediction, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (upload_id, idx, float(score), int(anomaly), float(pred), float(conf)))
        
        # Autocommit is enabled, no need for explicit commit
        print(f"✅ Stored {len(anomaly_scores)} predictions for upload_id={upload_id}")
        return True
    except Exception as e:
        print(f"❌ Error storing predictions: {e}")
        return False
    finally:
        if conn:
            conn.close()


def store_inference_summary(upload_id: int, total_samples: int, 
                           normal_count: int, anomaly_count: int, 
                           anomaly_percentage: float, inference_time_ms: float) -> bool:
    """
    Store inference summary in database
    Args:
        upload_id: ID of CSV upload
        total_samples: Total number of samples
        normal_count: Count of normal samples
        anomaly_count: Count of anomaly samples
        anomaly_percentage: Percentage of anomalies
        inference_time_ms: Inference time in milliseconds
    Returns: True if success
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO inference_summary 
            (upload_id, total_samples, normal_count, anomaly_count, anomaly_percentage, inference_time_ms, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (upload_id, total_samples, normal_count, anomaly_count, 
              anomaly_percentage, inference_time_ms, 'completed'))
        
        print(f"✅ Stored inference summary for upload_id={upload_id}")
        return True
    except Exception as e:
        print(f"❌ Error storing inference summary: {e}")
        return False
    finally:
        if conn:
            conn.close()


def get_upload_info(upload_id: int) -> dict:
    """
    Get upload information from database
    Args:
        upload_id: ID of upload
    Returns: Dict with upload info
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM csv_uploads WHERE upload_id = ?", (upload_id,))
        result = cursor.fetchone()
        
        if result:
            return {
                "upload_id": result[0],
                "filename": result[1],
                "file_path": result[2],
                "num_rows": result[3],
                "num_features": result[4],
                "status": result[5],
                "created_at": result[6]
            }
        return None
    except Exception as e:
        print(f"❌ Error getting upload info: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_predictions_by_upload(upload_id: int) -> list:
    """
    Get all predictions for an upload
    Args:
        upload_id: ID of upload
    Returns: List of prediction records
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM predictions WHERE upload_id = ? ORDER BY row_index
        """, (upload_id,))
        
        results = cursor.fetchall()
        
        predictions = []
        for row in results:
            predictions.append({
                "prediction_id": row[0],
                "upload_id": row[1],
                "row_index": row[2],
                "anomaly_score": row[3],
                "is_anomaly": row[4],
                "prediction": row[5],
                "confidence": row[6],
                "created_at": row[7]
            })
        
        return predictions
    except Exception as e:
        print(f"❌ Error getting predictions: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_inference_summary(upload_id: int) -> dict:
    """
    Get inference summary for an upload
    Args:
        upload_id: ID of upload
    Returns: Dict with summary info
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM inference_summary WHERE upload_id = ?
        """, (upload_id,))
        
        result = cursor.fetchone()
        
        if result:
            return {
                "summary_id": result[0],
                "upload_id": result[1],
                "total_samples": result[2],
                "normal_count": result[3],
                "anomaly_count": result[4],
                "anomaly_percentage": result[5],
                "inference_time_ms": result[6],
                "status": result[7],
                "created_at": result[8]
            }
        return None
    except Exception as e:
        print(f"❌ Error getting inference summary: {e}")
        return None
    finally:
        if conn:
            conn.close()


def list_all_uploads() -> list:
    """
    Get list of all uploads
    Returns: List of upload records
    """
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT upload_id, filename, num_rows, num_features, created_at 
            FROM csv_uploads 
            ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        
        uploads = []
        for row in results:
            uploads.append({
                "upload_id": row[0],
                "filename": row[1],
                "num_rows": row[2],
                "num_features": row[3],
                "created_at": row[4]
            })
        
        return uploads
    except Exception as e:
        print(f"❌ Error listing uploads: {e}")
        return []
    finally:
        if conn:
            conn.close()

def save_annotated_csv(original_file_path: Path, is_anomaly_list: List[int], 
                       output_filename: str = None) -> Path:
    """
    Save CSV file with prediction annotations (NORMAL/ATTACK) in results folder
    
    Args:
        original_file_path: Path to original CSV file
        is_anomaly_list: List of 0/1 predictions (1 = attack)
        output_filename: Custom output filename (if None, adds _results suffix)
    
    Returns: Path to annotated CSV file
    """
    try:
        # Read original CSV
        df = pd.read_csv(original_file_path)
        
        # Add prediction_status column at the beginning
        predictions = ['ATTACK' if x == 1 else 'NORMAL' for x in is_anomaly_list]
        df.insert(0, 'prediction_status', predictions)
        
        # Generate output filename
        if output_filename is None:
            stem = original_file_path.stem
            suffix = original_file_path.suffix
            output_filename = f"{stem}_results{suffix}"
        
        # Save annotated CSV to results folder
        output_path = RESULTS_DIR / output_filename
        df.to_csv(output_path, index=False)
        
        print(f"✅ Annotated CSV saved: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"❌ Error saving annotated CSV: {e}")
        return None