"""
Config Controller - Business logic cho config management
"""
from typing import Dict, Any
from app.services.config_manager import (
    read_config,
    get_config_section,
    update_config_section,
    validate_config,
)


def get_full_config() -> Dict[str, Any]:
    """
    Lấy toàn bộ config
    """
    return read_config()


def get_base_config() -> Dict[str, Any]:
    """
    Lấy phần config base (dataset, model settings, etc.)
    """
    return get_config_section("base")


def get_train_config() -> Dict[str, Any]:
    """
    Lấy phần config train (learning rate, iterations, etc.)
    """
    return get_config_section("train")


def update_base_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật base config
    Args:
        updates: dict chứa các thông số cần thay đổi
    Returns: toàn bộ config sau khi update
    """
    config = update_config_section("base", updates)
    
    # Validate lại config
    is_valid, error_msg = validate_config(config)
    if not is_valid:
        raise ValueError(f"Config validation failed: {error_msg}")
    
    return config


def update_train_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật train config
    Args:
        updates: dict chứa các thông số training cần thay đổi
    Returns: toàn bộ config sau khi update
    """
    config = update_config_section("train", updates)
    
    # Validate lại config
    is_valid, error_msg = validate_config(config)
    if not is_valid:
        raise ValueError(f"Config validation failed: {error_msg}")
    
    return config


def update_full_config(new_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật toàn bộ config
    Args:
        new_config: dict mới với cấu trúc {base: {...}, train: {...}}
    Returns: config đã được update
    """
    # Validate config trước khi update
    is_valid, error_msg = validate_config(new_config)
    if not is_valid:
        raise ValueError(f"Config validation failed: {error_msg}")
    
    # Ghi vào file
    from app.services.config_manager import write_config
    write_config(new_config)
    
    return new_config
