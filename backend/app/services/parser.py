import re
from pathlib import Path

LOG_FILE = Path("../GANAnomaly/output/FlowGANAnomaly/nsl/loss_log.txt")

ROC_PATTERN = re.compile(
    r"Avg Run Time \(ms/batch\): ([0-9.]+) roc: ([0-9.]+) max roc: ([0-9.]+)"
)

def parse_training_metrics():
    """
    Parse các metrics từ training log file
    """
    if not LOG_FILE.exists():
        return None

    runtimes = []
    rocs = []
    max_rocs = []

    with open(LOG_FILE, "r") as f:
        for line in f:
            match = ROC_PATTERN.search(line)
            if match:
                runtime, roc, max_roc = match.groups()
                runtimes.append(float(runtime))
                rocs.append(float(roc))
                max_rocs.append(float(max_roc))

    if not rocs:
        return None

    return {
        "roc_auc": max(rocs),
        "avg_runtime_ms": sum(runtimes) / len(runtimes),
        "max_roc": max(max_rocs),
        "roc_history": rocs
    }
