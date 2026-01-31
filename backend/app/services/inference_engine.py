"""
Inference Engine - Load GAN models and run predictions
"""
import sys
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Any
import time

# Add GANAnomaly to path
GAN_PATH = Path(__file__).resolve().parent.parent.parent.parent / "GANAnomaly"
if str(GAN_PATH) not in sys.path:
    sys.path.insert(0, str(GAN_PATH))

# Import actual GANAnomaly models
try:
    from lib.networks import NetG, NetD
    MODELS_IMPORTED = True
except ImportError as e:
    print(f"[WARN] Could not import GANAnomaly models: {e}")
    MODELS_IMPORTED = False

# Path to trained models
MODEL_DIR = Path(__file__).resolve().parent.parent.parent.parent / "GANAnomaly" / "output" / "FlowGANAnomaly" / "nsl" / "train" / "weights"
NETG_PATH = MODEL_DIR / "netG.pth"
NETD_PATH = MODEL_DIR / "netD.pth"


class InferenceEngine:
    """Inference engine for GAN-based anomaly detection"""
    
    def __init__(self, device: str = "cpu", feature_number: int = 116):
        self.device = torch.device(device)
        # Model trained on 116 features (NSL-KDD after preprocessing)
        # Input data will be padded/truncated to match this
        self.feature_number = feature_number
        self.netG = None
        self.netD = None
        self.is_loaded = False
        
    def load_models(self, config: Dict[str, Any] = None) -> bool:
        """
        Load pre-trained Generator and Discriminator models
        Uses actual GANAnomaly architecture from lib.networks
        """
        try:
            # Check if model files exist
            if not NETG_PATH.exists():
                raise FileNotFoundError(f"netG.pth not found: {NETG_PATH}")
            if not NETD_PATH.exists():
                raise FileNotFoundError(f"netD.pth not found: {NETD_PATH}")
            
            if not MODELS_IMPORTED:
                raise ImportError("Could not import GANAnomaly lib.networks")
            
            # Default config
            if config is None:
                config = {
                    "isize": 32,
                    "nz": 100,
                    "nc": 1,
                    "ngf": 64,
                    "extralayers": 0
                }
            
            # Create config wrapper for NetG/NetD
            class OptConfig:
                pass
            
            opt = OptConfig()
            opt.isize = config.get("isize", 32)
            opt.nz = config.get("nz", 100)
            opt.nc = config.get("nc", 1)
            opt.ngf = config.get("ngf", 64)
            opt.ngpu = 0  # CPU mode
            opt.extralayers = config.get("extralayers", 0)
            
            # Create models with correct feature count
            self.netG = NetG(opt, self.feature_number).to(self.device)
            self.netD = NetD(opt, self.feature_number).to(self.device)
            
            print(f"[OK] Initialized NetG and NetD with {self.feature_number} features")
            
            # Load checkpoints
            print(f"[INFO] Loading netG from: {NETG_PATH}")
            print(f"[INFO] Loading netD from: {NETD_PATH}")
            
            netG_ckpt = torch.load(NETG_PATH, map_location=self.device)
            netG_state = netG_ckpt.get("state_dict", netG_ckpt)
            self.netG.load_state_dict(netG_state)
            print(f"[OK] netG.pth loaded successfully")
            
            netD_ckpt = torch.load(NETD_PATH, map_location=self.device)
            netD_state = netD_ckpt.get("state_dict", netD_ckpt)
            self.netD.load_state_dict(netD_state)
            print(f"[OK] netD.pth loaded successfully")
            
            # Set eval mode
            self.netG.eval()
            self.netD.eval()
            
            self.is_loaded = True
            print(f"[OK] Models loaded and ready for inference")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load models: {e}")
            self.is_loaded = False
            return False
    
    def preprocess_data(self, data: np.ndarray) -> torch.Tensor:
        """
        Preprocess input data for model
        Args:
            data: Input numpy array (N, num_features) - will be padded to 116 if needed
        Returns: Torch tensor ready for model (batch_size, 116)
        
        Note: NSL-KDD uses 116 features as input, not image format.
              Discriminator has Linear(116, 32) as first layer.
        """
        # Ensure 2D array
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        
        # Pad or truncate to 116 features
        num_rows, current_features = data.shape
        if current_features < 116:
            # Pad with zeros
            padding = np.zeros((num_rows, 116 - current_features))
            data = np.hstack([data, padding])
            print(f"[INFO] Padded {current_features} → 116 features")
        elif current_features > 116:
            # Truncate
            data = data[:, :116]
            print(f"[INFO] Truncated {current_features} → 116 features")
        
        # ⚠️ CRITICAL FIX: Data is already normalized from CSV preprocessing (MinMaxScaler [0,1])
        # Do NOT re-normalize to avoid double-scaling which corrupts the feature distribution!
        # The training pipeline already scaled the data properly, so we use it as-is.
        data = data.astype(np.float32)
        
        # Convert to torch tensor (batch_size, 116)
        tensor = torch.from_numpy(data).float().to(self.device)
        return tensor
    
    def compute_anomaly_score(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute anomaly scores for input data using GAN
        
        Method:
        1. Pass data through Discriminator
        2. Lower discriminator output = more anomalous (model doesn't recognize it)
        3. Higher discriminator output = more normal (model recognizes it)
        
        Args:
            data: Input data (N, 32, 32) or similar
        Returns: (anomaly_scores, binary_predictions)
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first")
        
        with torch.no_grad():
            # Preprocess data
            tensor = self.preprocess_data(data)
            
            # Forward through Discriminator
            # NetD returns (classifier, features) tuple
            d_output, _ = self.netD(tensor)
            
            # Convert to numpy and flatten
            d_output_np = d_output.cpu().numpy().flatten()
            
            # Debug: print D output statistics
            print(f"[DEBUG] D output min={d_output_np.min():.4f}, max={d_output_np.max():.4f}, mean={d_output_np.mean():.4f}")
            print(f"[DEBUG] D output samples (first 5): {d_output_np[:5]}")
            print(f"[DEBUG] Anomaly score = 1 - D_output")
            
            # Anomaly score = 1 - D_output
            # High D output (>0.5) = normal, so anomaly_score is low
            # Low D output (<0.5) = anomaly, so anomaly_score is high
            anomaly_scores = 1.0 - d_output_np
            
            print(f"[DEBUG] Anomaly scores (first 5): {anomaly_scores[:5]}")
            
            # Return anomaly scores only - let predict_batch handle thresholding
            # NOTE: Higher D output = more normal, lower D output = more anomaly
            # So anomaly_score = D_output directly (don't invert)
            return d_output_np, None
    
    def predict_batch(self, data: np.ndarray, threshold: float = 0.2) -> Dict[str, Any]:
        """
        Predict on a batch of data
        
        Args:
            data: Input data (N, 32, 32)
            threshold: Anomaly threshold (0-1)
            Default: 0.985 (optimal for NSL-KDD model based on testing)
            
        Returns: Dict with predictions and statistics
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded")
        
        start_time = time.time()
        
        # Compute anomaly scores
        anomaly_scores, predictions = self.compute_anomaly_score(data)
        
        # Threshold-based classification
        # anomaly_scores = D_output (higher = more normal, lower = more anomaly)
        # So: is_anomaly = (anomaly_scores < threshold)
        is_anomaly = (anomaly_scores < threshold).astype(int)
        
        # Statistics
        num_samples = len(anomaly_scores)
        num_anomalies = int(is_anomaly.sum())
        num_normal = num_samples - num_anomalies
        anomaly_percentage = (num_anomalies / num_samples * 100) if num_samples > 0 else 0
        
        inference_time = (time.time() - start_time) * 1000  # ms
        
        return {
            "anomaly_scores": anomaly_scores.tolist(),
            "is_anomaly": is_anomaly.tolist(),
            "predictions": is_anomaly.tolist(),  # Use is_anomaly as predictions
            "statistics": {
                "total_samples": num_samples,
                "normal_count": num_normal,
                "anomaly_count": num_anomalies,
                "anomaly_percentage": anomaly_percentage,
                "threshold": threshold,
                "inference_time_ms": inference_time
            }
        }
