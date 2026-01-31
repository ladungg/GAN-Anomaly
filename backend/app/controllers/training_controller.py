"""
Training Controller - Xử lý logic liên quan đến training
"""
from typing import Dict, Any
from pathlib import Path
import json
from app.services import run_script
from app.services.training_data_manager import (
    save_training_file,
    read_training_file,
    validate_training_data,
)


def start_training():
    """
    Khởi động quá trình training
    """
    process = run_script("train.py")
    return process


def start_testing():
    """
    Khởi động quá trình testing
    """
    process = run_script("test.py")
    return process


def upload_training_data(filename: str, file_content: bytes) -> Dict[str, Any]:
    """
    Handle training data file upload
    Args:
        filename: Original filename
        file_content: File content as bytes
    Returns: Dict with upload info
    """
    try:
        # Save file to disk
        file_path, success = save_training_file(file_content, filename)
        if not success:
            return {
                "status": "error",
                "message": "Failed to save file",
            }
        
        # Read and validate data
        data, num_rows, num_features, success = read_training_file(file_path)
        if not success:
            return {
                "status": "error",
                "message": "Failed to read CSV file",
            }
        
        # Validate
        is_valid, msg = validate_training_data(data)
        if not is_valid:
            return {
                "status": "error",
                "message": msg,
            }
        
        return {
            "status": "success",
            "message": "Training data uploaded successfully",
            "filename": filename,
            "num_rows": int(num_rows),
            "num_features": int(num_features),
            "file_path": str(file_path),
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Upload error: {str(e)}",
        }


def run_training_with_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run GAN training with custom config
    Args:
        config: Training config (niter, lr, beta1, w_adv, w_con, w_enc)
    Returns: Dict with status
    """
    try:
        # Save config to temporary file
        gan_path = Path(__file__).resolve().parent.parent.parent.parent / "GANAnomaly"
        config_file = gan_path / "config_training.json"
        
        # Load base config
        base_config_file = gan_path / "config.json"
        with open(base_config_file, 'r') as f:
            base_config = json.load(f)
        
        # Update train config with user settings
        base_config["train"]["niter"] = config.get("niter", 5)
        base_config["train"]["lr"] = config.get("lr", 0.0002)
        base_config["train"]["beta1"] = config.get("beta1", 0.5)
        base_config["train"]["w_adv"] = config.get("w_adv", 1)
        base_config["train"]["w_con"] = config.get("w_con", 50)
        base_config["train"]["w_enc"] = config.get("w_enc", 1)
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(base_config, f, indent=2)
        
        return {
            "status": "success",
            "message": "Training started with custom config",
            "config_file": str(config_file),
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Training error: {str(e)}",
        }
