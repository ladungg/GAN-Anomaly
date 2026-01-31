import subprocess
import sys
from pathlib import Path

# Thư mục GAN model (song song với backend)
GAN_DIR = Path(__file__).resolve().parent.parent.parent.parent / "GANAnomaly"


def run_script(script_name: str):
    """
    Chạy train.py hoặc test.py và trả về process để stream log
    """
    script_path = GAN_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {script_path}")

    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        cwd=GAN_DIR,                 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    return process
