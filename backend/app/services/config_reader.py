from pathlib import Path

OPT_FILE = Path("../GANAnomaly/output/FlowGANAnomaly/nsl/train/opt.txt")

def read_training_config():
    """
    Đọc cấu hình training từ file opt.txt
    """
    if not OPT_FILE.exists():
        return {}

    config = {}
    with open(OPT_FILE, "r") as f:
        for line in f:
            if ":" in line:
                k, v = line.split(":", 1)
                config[k.strip()] = v.strip()

    return config
