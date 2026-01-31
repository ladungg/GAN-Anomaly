"""
Training API Endpoints - Stream training log realtime
"""
import json
import os
import subprocess
import sys
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.controllers.training_controller import (
    start_training,
    start_testing,
    upload_training_data,
    run_training_with_config,
)

router = APIRouter(
    prefix="/api/training",
    tags=["training"],
    responses={404: {"description": "Not found"}},
)


class TrainingConfigRequest(BaseModel):
    niter: int = 5
    lr: float = 0.0002
    beta1: float = 0.5
    w_adv: float = 1
    w_con: float = 50
    w_enc: float = 1


@router.post("/upload-data", summary="Upload training data")
async def upload_data(file: UploadFile = File(...)):
    """
    Upload training data CSV file
    """
    content = await file.read()
    result = upload_training_data(file.filename or "training.csv", content)
    
    if result["status"] == "error":
        return {"status": "error", "message": result["message"]}
    
    return result


@router.post("/train", summary="Huấn luyện mô hình với config tùy chỉnh")
async def train_with_config(config: TrainingConfigRequest):
    """
    Bắt đầu huấn luyện mô hình GAN - chạy train.py từ GANAnomaly folder
    Stream logs real-time trở lại frontend
    
    **Request body:**
    - niter: Số epoch (mặc định: 5)
    - lr: Learning rate (mặc định: 0.0002)
    - beta1: Beta1 (mặc định: 0.5)
    - w_adv: Adversarial loss weight (mặc định: 1)
    - w_con: Content loss weight (mặc định: 50)
    - w_enc: Encoder loss weight (mặc định: 1)
    """
    async def generate_logs():
        try:
            # Đường dẫn tới GANAnomaly folder
            current_file = os.path.abspath(__file__)
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            gan_root = os.path.dirname(backend_dir)
            gan_anomaly_dir = os.path.join(gan_root, "GANAnomaly")
            train_script = os.path.join(gan_anomaly_dir, "train.py")
            
            yield f"[INFO] Starting training from {gan_anomaly_dir}\n"
            yield f"[INFO] Script: {train_script}\n"
            
            if not os.path.exists(train_script):
                yield f"[ERROR] train.py not found at {train_script}\n"
                return
            
            # Chạy train.py
            process = subprocess.Popen(
                [sys.executable, train_script],
                cwd=gan_anomaly_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream logs
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                yield line + "\n"
            
            process.wait()
            if process.returncode == 0:
                yield "[OK] Training completed successfully\n"
            else:
                yield f"[ERROR] Training failed with code {process.returncode}\n"
                
        except Exception as e:
            yield f"[ERROR] Exception: {str(e)}\n"
    
    return StreamingResponse(generate_logs(), media_type="text/plain")


@router.get("/train", summary="Huấn luyện mô hình GAN")
def train():
    """
    Bắt đầu huấn luyện mô hình GAN (mặc định config)
    """
    result = start_training()
    return {"status": "started", "message": "Training started"}


@router.get("/test", summary="Chạy kiểm thử mô hình")
def test():
    """
    Bắt đầu kiểm thử mô hình
    """
    result = start_testing()
    return {"status": "started", "message": "Testing started"}


@router.get("/get-config", summary="Get current training configuration")
def get_config():
    """
    Lấy cấu hình huấn luyện hiện tại từ GANAnomaly/config.json
    """
    try:
        # Đường dẫn: từ app/routes/v1 lên 4 cấp tới GAN root, rồi vào GANAnomaly
        current_file = os.path.abspath(__file__)  # /backend/app/routes/v1/training.py
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))  # /backend
        gan_root = os.path.dirname(backend_dir)  # /GAN
        config_path = os.path.join(gan_root, "GANAnomaly", "config.json")
        
        # Đọc config hiện tại
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
                train_config = full_config.get("train", {})
                
                return {
                    "status": "success",
                    "config": {
                        "niter": train_config.get("niter", 5),
                        "lr": train_config.get("lr", 0.0002),
                        "beta1": train_config.get("beta1", 0.5),
                        "w_adv": train_config.get("w_adv", 1),
                        "w_con": train_config.get("w_con", 50),
                        "w_enc": train_config.get("w_enc", 1),
                    }
                }
        else:
            # Trả về default nếu file không tìm thấy
            return {
                "status": "success",
                "config": {
                    "niter": 5,
                    "lr": 0.0002,
                    "beta1": 0.5,
                    "w_adv": 1,
                    "w_con": 50,
                    "w_enc": 1,
                }
            }
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to get config: {str(e)}"
        }


@router.post("/save-config", summary="Save training configuration")
async def save_config(config: TrainingConfigRequest):
    """
    Lưu cấu hình huấn luyện vào ../GANAnomaly/config.json
    """
    try:
        # Đường dẫn: từ app/routes/v1 lên 4 cấp tới GAN root, rồi vào GANAnomaly
        current_file = os.path.abspath(__file__)  # /backend/app/routes/v1/training.py
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))  # /backend
        gan_root = os.path.dirname(backend_dir)  # /GAN
        config_path = os.path.join(gan_root, "GANAnomaly", "config.json")
        
        print(f"[DEBUG] Config path: {config_path}")
        
        # Đọc config hiện tại
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
        else:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        # Cập nhật train config - convert to correct types
        full_config["train"]["niter"] = int(config.niter)
        full_config["train"]["lr"] = float(config.lr)
        full_config["train"]["beta1"] = float(config.beta1)
        full_config["train"]["w_adv"] = float(config.w_adv)
        full_config["train"]["w_con"] = int(config.w_con)
        full_config["train"]["w_enc"] = float(config.w_enc)
        
        # Lưu lại file
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2)
        
        print(f"[OK] Config saved: {config.model_dump()}")
        
        return {
            "status": "success",
            "message": "Config saved successfully",
            "config": config.model_dump()
        }
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to save config: {str(e)}"
        }
