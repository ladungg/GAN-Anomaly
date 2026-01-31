import json
from pathlib import Path

CM_FILE = Path(
    "../GANAnomaly/output/FlowGANAnomaly/nsl/confusion_matrix.json"
)

def read_confusion_matrix():
    """
    Đọc confusion matrix từ file JSON
    """
    if not CM_FILE.exists():
        return None

    with open(CM_FILE, "r") as f:
        return json.load(f)
