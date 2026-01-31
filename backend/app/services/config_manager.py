"""
Config Manager - Handle reading and writing GAN config.json
"""
import json
from pathlib import Path
from typing import Dict, Any

# Path to GANAnomaly config.json
CONFIG_FILE = Path(__file__).resolve().parent.parent.parent.parent / "GANAnomaly" / "config.json"


def read_config() -> Dict[str, Any]:
    """
    Đọc toàn bộ config từ file config.json
    Returns: dict với cấu trúc {base: {...}, train: {...}}
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    return config


def write_config(config: Dict[str, Any]) -> bool:
    """
    Ghi config vào file config.json
    Args:
        config: dict với cấu trúc {base: {...}, train: {...}}
    Returns: True if success
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    
    return True


def update_config_section(section: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật một section cụ thể của config (base hoặc train)
    Args:
        section: 'base' hoặc 'train'
        updates: dict chứa các thay đổi
    Returns: toàn bộ config sau khi update
    """
    if section not in ["base", "train"]:
        raise ValueError(f"Invalid section: {section}. Must be 'base' or 'train'")

    config = read_config()
    
    # Cập nhật section
    if section in config:
        config[section].update(updates)
    else:
        config[section] = updates

    # Ghi lại file
    write_config(config)
    
    return config


def get_config_section(section: str) -> Dict[str, Any]:
    """
    Lấy một section cụ thể của config
    Args:
        section: 'base' hoặc 'train'
    Returns: dict chứa các thông số của section
    """
    if section not in ["base", "train"]:
        raise ValueError(f"Invalid section: {section}. Must be 'base' or 'train'")

    config = read_config()
    return config.get(section, {})


def validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate config có đúng cấu trúc không
    Returns: (is_valid, error_message)
    """
    # Check required sections
    if "base" not in config or "train" not in config:
        return False, "Config must have 'base' and 'train' sections"

    # Check required base fields
    required_base = ["dataset", "model", "batchsize", "niter"]
    for field in required_base:
        if field not in config["base"]:
            return False, f"Missing required base field: {field}"

    return True, ""
