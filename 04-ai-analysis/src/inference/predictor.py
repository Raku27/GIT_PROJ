"""
Prediction/inference module for AI analysis
"""

import pandas as pd
import numpy as np
import joblib
from typing import Dict, Any, List, Optional
import os


class Predictor:
    """Class for making predictions with trained models"""
    
    def __init__(self, model_path: str):
        """
        Initialize predictor
        
        Args:
            model_path: Path to the saved model file
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        self.model = joblib.load(self.model_path)
        print(f"Model loaded from: {self.model_path}")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Feature dataframe
            
        Returns:
            Predictions array
        """
        if self.model is None:
            raise ValueError("Model not loaded.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities
        
        Args:
            X: Feature dataframe
            
        Returns:
            Probability array
        """
        if self.model is None:
            raise ValueError("Model not loaded.")
        
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            raise ValueError("Model does not support probability predictions.")
    
    def predict_with_confidence(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Get predictions with confidence scores
        
        Args:
            X: Feature dataframe
            
        Returns:
            DataFrame with predictions and confidence scores
        """
        predictions = self.predict(X)
        probabilities = self.predict_proba(X)
        
        # Get maximum probability as confidence
        confidence = np.max(probabilities, axis=1)
        
        result = pd.DataFrame({
            'prediction': predictions,
            'confidence': confidence,
            'probabilities': probabilities.tolist()
        })
        
        return result
    
    def batch_predict(self, data_list: List[Dict[str, Any]], 
                     feature_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Make batch predictions
        
        Args:
            data_list: List of dictionaries with feature values
            feature_columns: List of feature column names
            
        Returns:
            List of prediction results
        """
        # Convert to DataFrame
        df = pd.DataFrame(data_list)
        
        # Ensure all feature columns are present
        missing_cols = set(feature_columns) - set(df.columns)
        if missing_cols:
            for col in missing_cols:
                df[col] = 0  # Fill missing with 0
        
        # Select only feature columns
        X = df[feature_columns]
        
        # Make predictions
        predictions = self.predict(X)
        probabilities = self.predict_proba(X)
        
        # Format results
        results = []
        for i, pred in enumerate(predictions):
            results.append({
                'prediction': pred,
                'confidence': float(np.max(probabilities[i])),
                'probabilities': probabilities[i].tolist()
            })
        
        return results


if __name__ == "__main__":
    # Example usage
    print("Predictor Module")
    print("Use this module to make predictions with trained models")
