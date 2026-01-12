"""
Classification models for AI analysis
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from typing import Dict, Any, Optional, Tuple
import joblib
import os


class MLClassifier:
    """Machine Learning Classifier with multiple algorithm support"""
    
    def __init__(self, algorithm: str = 'random_forest', **kwargs):
        """
        Initialize classifier
        
        Args:
            algorithm: Algorithm to use ('random_forest', 'gradient_boosting', 'logistic_regression', 'svm')
            **kwargs: Additional parameters for the algorithm
        """
        self.algorithm = algorithm
        self.model = self._create_model(algorithm, **kwargs)
        self.is_trained = False
        self.feature_importance_ = None
    
    def _create_model(self, algorithm: str, **kwargs):
        """Create model instance based on algorithm"""
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', None),
                random_state=kwargs.get('random_state', 42)
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                learning_rate=kwargs.get('learning_rate', 0.1),
                random_state=kwargs.get('random_state', 42)
            ),
            'logistic_regression': LogisticRegression(
                max_iter=kwargs.get('max_iter', 1000),
                random_state=kwargs.get('random_state', 42)
            ),
            'svm': SVC(
                kernel=kwargs.get('kernel', 'rbf'),
                probability=kwargs.get('probability', True),
                random_state=kwargs.get('random_state', 42)
            )
        }
        
        if algorithm not in models:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        return models[algorithm]
    
    def train(self, X: pd.DataFrame, y: pd.Series, 
              validation_split: float = 0.2, **kwargs) -> Dict[str, Any]:
        """
        Train the classifier
        
        Args:
            X: Feature dataframe
            y: Target series
            validation_split: Fraction of data to use for validation
            **kwargs: Additional training parameters
            
        Returns:
            Training results dictionary
        """
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        # Train model
        print(f"Training {self.algorithm} classifier...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Get feature importance if available
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance_ = pd.Series(
                self.model.feature_importances_,
                index=X.columns
            ).sort_values(ascending=False)
        
        # Evaluate on validation set
        y_pred = self.model.predict(X_val)
        
        results = {
            'algorithm': self.algorithm,
            'train_size': len(X_train),
            'val_size': len(X_val),
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred, average='weighted'),
            'recall': recall_score(y_val, y_pred, average='weighted'),
            'f1_score': f1_score(y_val, y_pred, average='weighted'),
            'classification_report': classification_report(y_val, y_pred)
        }
        
        print(f"\nTraining Results:")
        print(f"Accuracy: {results['accuracy']:.4f}")
        print(f"F1 Score: {results['f1_score']:.4f}")
        
        return results
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Feature dataframe
            
        Returns:
            Predictions array
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities
        
        Args:
            X: Feature dataframe
            
        Returns:
            Probability array
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        return self.model.predict_proba(X)
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Evaluate model on test data
        
        Args:
            X: Feature dataframe
            y: True labels
            
        Returns:
            Evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")
        
        y_pred = self.predict(X)
        
        return {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, average='weighted'),
            'recall': recall_score(y, y_pred, average='weighted'),
            'f1_score': f1_score(y, y_pred, average='weighted')
        }
    
    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> Dict[str, Any]:
        """
        Perform cross-validation
        
        Args:
            X: Feature dataframe
            y: Target series
            cv: Number of folds
            
        Returns:
            Cross-validation results
        """
        scores = cross_val_score(self.model, X, y, cv=cv, scoring='accuracy')
        
        return {
            'mean_accuracy': scores.mean(),
            'std_accuracy': scores.std(),
            'scores': scores.tolist()
        }
    
    def save_model(self, filepath: str):
        """
        Save trained model to file
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Model not trained.")
        
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        joblib.dump(self.model, filepath)
        print(f"Model saved to: {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load trained model from file
        
        Args:
            filepath: Path to the model file
        """
        self.model = joblib.load(filepath)
        self.is_trained = True
        print(f"Model loaded from: {filepath}")


if __name__ == "__main__":
    # Example usage
    print("ML Classifier Module")
    print("Use this module to train and evaluate classification models")
