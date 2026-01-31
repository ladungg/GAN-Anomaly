"""
NSL-KDD Data Preprocessor - One-hot encode categorical and scale numeric features
Matches the preprocessing in GANAnomaly/load_data/process_nslkdd.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple

class NSLKDDPreprocessor:
    """Preprocess NSL-KDD data to match training format (116 features)"""
    
    # Categorical columns to one-hot encode
    SYMBOLIC_COLUMNS = ["protocol_type", "service", "flag"]
    
    # Columns to drop
    DROP_COLUMNS = ["num", "number", "label"]
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.feature_names = None
        self.n_features = 0
        
    def fit(self, df: pd.DataFrame) -> int:
        """
        Fit preprocessor on training data and return number of features
        
        Args:
            df: Training DataFrame with all 44 columns
            
        Returns: Number of numeric features after preprocessing
        """
        # Copy to avoid modifying original
        df = df.copy()
        
        # Drop metadata columns
        for col in self.DROP_COLUMNS:
            if col in df.columns:
                df.drop(col, axis=1, inplace=True)
        
        # One-hot encode categorical columns
        for col in self.SYMBOLIC_COLUMNS:
            if col in df.columns:
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
        
        # Store feature names and count
        self.feature_names = df.columns.tolist()
        self.n_features = len(self.feature_names)
        
        print(f"[INFO] Preprocessor fitted with {self.n_features} features")
        print(f"[INFO] Features: {self.feature_names}")
        
        return self.n_features
    
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform data to match training format
        
        Args:
            df: DataFrame with 44 columns (NSL-KDD format)
            
        Returns: Numeric array (N, n_features) ready for inference
        """
        # Copy to avoid modifying original
        df = df.copy()
        
        # Drop metadata columns
        for col in self.DROP_COLUMNS:
            if col in df.columns:
                df.drop(col, axis=1, inplace=True)
        
        # One-hot encode categorical columns
        for col in self.SYMBOLIC_COLUMNS:
            if col in df.columns:
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
        
        # Add missing columns (fill with zeros if test data is missing some categories)
        if self.feature_names:
            for feat in self.feature_names:
                if feat not in df.columns:
                    df[feat] = 0
            
            # Reorder to match training data
            df = df[self.feature_names]
        
        # Scale numeric features
        data = df.values.astype(np.float32)
        data = self.scaler.fit_transform(data)
        
        return data
    
    @staticmethod
    def from_training_data(train_file_path: Path) -> 'NSLKDDPreprocessor':
        """
        Create preprocessor from actual training data
        
        Args:
            train_file_path: Path to NSL-KDD training CSV
            
        Returns: Fitted preprocessor
        """
        df_train = pd.read_csv(train_file_path)
        preprocessor = NSLKDDPreprocessor()
        preprocessor.fit(df_train)
        return preprocessor


def test_preprocessor():
    """Test the preprocessor"""
    # Load NSL-KDD test data
    kdd_test_path = Path("c:/Users/DungLA/Desktop/GAN/GANAnomaly/nsk-kdd/KDDTest+.csv")
    kdd_train_path = Path("c:/Users/DungLA/Desktop/GAN/GANAnomaly/nsk-kdd/KDDTrain+.csv")
    
    print("="*60)
    print("NSL-KDD PREPROCESSOR TEST")
    print("="*60)
    
    # Create preprocessor from training data
    print("\n1️⃣ Fitting preprocessor on training data...")
    preprocessor = NSLKDDPreprocessor.from_training_data(kdd_train_path)
    
    # Transform test data
    print("\n2️⃣ Transforming test data...")
    df_test = pd.read_csv(kdd_test_path)
    data_transformed = preprocessor.transform(df_test)
    
    print(f"\n✅ Test data shape: {data_transformed.shape}")
    print(f"   Samples: {data_transformed.shape[0]}")
    print(f"   Features: {data_transformed.shape[1]}")
    print(f"   Feature names: {preprocessor.feature_names[:5]}... (showing first 5)")
    
    # Save for reference
    output_path = Path(__file__).resolve().parent.parent.parent / "uploads" / "test_nslkdd_preprocessed.npy"
    np.save(output_path, data_transformed)
    print(f"\n✅ Saved preprocessed data to: {output_path}")

if __name__ == "__main__":
    test_preprocessor()
