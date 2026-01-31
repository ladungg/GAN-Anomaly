"""
Authentication Routes - /api/v1/auth/*
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.controllers.auth_controller import controller_register, controller_login, controller_get_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register", summary="Đăng ký tài khoản mới")
def register(req: RegisterRequest):
    """
    Đăng ký người dùng mới
    
    **Request body:**
    - username: Tên đăng nhập (>= 3 ký tự)
    - email: Email
    - password: Mật khẩu (>= 6 ký tự)
    """
    result = controller_register(req.username, req.email, req.password)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/login", summary="Đăng nhập")
def login(req: LoginRequest):
    """
    Đăng nhập tài khoản
    
    **Request body:**
    - username: Tên đăng nhập
    - password: Mật khẩu
    """
    result = controller_login(req.username, req.password)
    
    if result["status"] == "error":
        raise HTTPException(status_code=401, detail=result["message"])
    
    return result


@router.get("/user/{user_id}", summary="Lấy thông tin người dùng")
def get_user(user_id: int):
    """
    Lấy thông tin người dùng theo ID
    """
    result = controller_get_user(user_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result
