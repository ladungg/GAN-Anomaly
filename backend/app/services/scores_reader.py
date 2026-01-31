import numpy as np
from pathlib import Path

SCORES_FILE = Path(
    "../GANAnomaly/output/FlowGANAnomaly/nsl/anomaly_scores.npy"
)

def read_anomaly_scores():
    """
    Đọc anomaly scores từ file numpy
    """
    if not SCORES_FILE.exists():
        return None

    scores = np.load(SCORES_FILE)
    return scores.tolist()
