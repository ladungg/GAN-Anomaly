"""
Metrics Controller - Xử lý logic lấy metrics và kết quả
"""
from app.services import (
    parse_training_metrics,
    read_training_config,
    read_anomaly_scores,
    read_confusion_matrix,
)

def get_training_metrics():
    """
    Lấy training metrics từ log file
    """
    return parse_training_metrics()

def get_training_config():
    """
    Lấy cấu hình training
    """
    return read_training_config()

def get_anomaly_scores():
    """
    Lấy anomaly scores từ model output
    """
    return read_anomaly_scores()

def get_confusion_matrix_data():
    """
    Lấy confusion matrix từ model output
    """
    return read_confusion_matrix()
