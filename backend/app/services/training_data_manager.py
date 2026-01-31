"""
Training Data Manager - Handle training data uploads
"""
import csv
import numpy as np
from pathlib import Path
from typing import Tuple

# Directory to store training data
TRAINING_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "training_data"
TRAINING_DATA_DIR.mkdir(exist_ok=True)


def save_training_file(file_content: bytes, filename: str) -> Tuple[Path, bool]:
    """
    Save training data file to disk
    Args:
        file_content: File content as bytes
        filename: Original filename
    Returns: (file_path, success)
    """
    try:
        safe_filename = Path(filename).name
        file_path = TRAINING_DATA_DIR / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path, True
    except Exception as e:
        print(f"❌ Error saving training file: {e}")
        return None, False


def read_training_file(file_path: Path) -> Tuple[np.ndarray, int, int, bool]:
    """
    Read training CSV file and convert to numpy array
    Args:
        file_path: Path to CSV file
    Returns: (data_array, num_rows, num_features, success)
    """
    try:
        data = np.genfromtxt(file_path, delimiter=',', dtype=float, skip_header=0)
        
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        
        num_rows, num_features = data.shape
        
        if np.isnan(data).any():
            print(f"⚠️ Warning: Training data contains NaN values, replacing with 0")
            data = np.nan_to_num(data, nan=0.0)
        
        return data, num_rows, num_features, True
    except Exception as e:
        print(f"❌ Error reading training file: {e}")
        return None, 0, 0, False


def validate_training_data(data: np.ndarray) -> Tuple[bool, str]:
    """
    Validate training data format
    Args:
        data: Numpy array of training data
    Returns: (is_valid, message)
    """
    if len(data) < 10:
        return False, "Training data phải có ít nhất 10 mẫu"
    
    if np.any(np.isnan(data)) or np.any(np.isinf(data)):
        return False, "Training data chứa giá trị không hợp lệ (NaN, Inf)"
    
    return True, "OK"
