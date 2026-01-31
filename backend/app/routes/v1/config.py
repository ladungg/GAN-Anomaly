"""
Config API Endpoints - Manage GAN model configuration
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any

from app.controllers.config_controller import (
    get_full_config,
    get_base_config,
    get_train_config,
    update_base_config,
    update_train_config,
    update_full_config,
)

router = APIRouter(
    prefix="/api/v1/config",
    tags=["config"],
    responses={404: {"description": "Not found"}},
)


# ===============================
# Pydantic Models for validation
# ===============================
class BaseConfigUpdate(BaseModel):
    """Schema for updating base config"""
    dataset: str = None
    batchsize: int = None
    isize: int = None
    nc: int = None
    nz: int = None
    ngf: int = None
    ndf: int = None
    device: str = None
    gpu_ids: str = None
    proportion: float = None
    metric: str = None
    model: str = None

    class Config:
        extra = "allow"  # Allow additional fields


class TrainConfigUpdate(BaseModel):
    """Schema for updating train config"""
    niter: int = None
    lr: float = None
    beta1: float = None
    w_adv: float = None
    w_con: float = None
    w_enc: float = None
    print_freq: int = None
    load_weights: bool = None

    class Config:
        extra = "allow"  # Allow additional fields


class FullConfigUpdate(BaseModel):
    """Schema for updating full config"""
    base: Dict[str, Any]
    train: Dict[str, Any]


# ===============================
# GET Endpoints
# ===============================
@router.get("/", summary="Lấy toàn bộ config")
def get_config():
    """
    Lấy toàn bộ GAN model config (base + train)
    """
    try:
        config = get_full_config()
        return JSONResponse(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/base", summary="Lấy base config")
def get_base():
    """
    Lấy phần base config (dataset, model, batch size, etc.)
    """
    try:
        config = get_base_config()
        return JSONResponse(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/train", summary="Lấy train config")
def get_train():
    """
    Lấy phần train config (learning rate, iterations, losses weights, etc.)
    """
    try:
        config = get_train_config()
        return JSONResponse(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===============================
# PUT Endpoints (Update)
# ===============================
@router.put("/base", summary="Cập nhật base config")
def update_base(config_update: BaseConfigUpdate):
    """
    Cập nhật phần base config
    
    Ví dụ body:
    ```json
    {
        "batchsize": 32,
        "lr": 0.0001,
        "device": "gpu"
    }
    ```
    """
    try:
        # Remove None values
        updates = {k: v for k, v in config_update.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        config = update_base_config(updates)
        return JSONResponse({
            "message": "Base config updated successfully",
            "config": config
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/train", summary="Cập nhật train config")
def update_train(config_update: TrainConfigUpdate):
    """
    Cập nhật phần train config
    
    Ví dụ body:
    ```json
    {
        "niter": 10,
        "lr": 0.0002,
        "w_adv": 1,
        "w_con": 50,
        "w_enc": 1
    }
    ```
    """
    try:
        # Remove None values
        updates = {k: v for k, v in config_update.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        config = update_train_config(updates)
        return JSONResponse({
            "message": "Train config updated successfully",
            "config": config
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/", summary="Cập nhật toàn bộ config")
def update_full(config_update: FullConfigUpdate):
    """
    Cập nhật toàn bộ config (base + train)
    
    Ví dụ body:
    ```json
    {
        "base": {
            "dataset": "nsl",
            "batchsize": 64,
            "model": "FlowGANAnomaly"
        },
        "train": {
            "niter": 5,
            "lr": 0.0002
        }
    }
    ```
    """
    try:
        config = update_full_config(config_update.dict())
        return JSONResponse({
            "message": "Config updated successfully",
            "config": config
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
