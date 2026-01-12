"""
Feature engineering utilities for AI analysis
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from typing import List, Optional, Tuple


class FeatureEngineer:
    """Class for feature engineering operations"""
    
    def __init__(self):
        """Initialize feature engineer"""
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.onehot_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.feature_selector = None
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
        """
        Handle missing values in the dataset
        
        Args:
            df: Input dataframe
            strategy: Strategy for handling missing values ('mean', 'median', 'mode', 'drop')
            
        Returns:
            Dataframe with handled missing values
        """
        df = df.copy()
        
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if strategy == 'mean' and df[col].dtype in ['int64', 'float64']:
                    df[col].fillna(df[col].mean(), inplace=True)
                elif strategy == 'median' and df[col].dtype in ['int64', 'float64']:
                    df[col].fillna(df[col].median(), inplace=True)
                elif strategy == 'mode':
                    df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 0, inplace=True)
                elif strategy == 'drop':
                    df.dropna(subset=[col], inplace=True)
                else:
                    df[col].fillna(0, inplace=True)
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                          method: str = 'label') -> pd.DataFrame:
        """
        Encode categorical variables
        
        Args:
            df: Input dataframe
            columns: List of columns to encode (None = auto-detect)
            method: Encoding method ('label' or 'onehot')
            
        Returns:
            Dataframe with encoded categorical variables
        """
        df = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns.tolist()
        
        if method == 'label':
            for col in columns:
                if col in df.columns:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.label_encoders[col] = le
        
        elif method == 'onehot':
            df_encoded = pd.get_dummies(df, columns=columns, prefix=columns)
            return df_encoded
        
        return df
    
    def scale_features(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                      fit: bool = True) -> pd.DataFrame:
        """
        Scale numerical features
        
        Args:
            df: Input dataframe
            columns: List of columns to scale (None = all numeric)
            fit: Whether to fit the scaler (True for training, False for testing)
            
        Returns:
            Dataframe with scaled features
        """
        df = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if fit:
            df[columns] = self.scaler.fit_transform(df[columns])
        else:
            df[columns] = self.scaler.transform(df[columns])
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame, 
                                   feature_pairs: List[Tuple[str, str]]) -> pd.DataFrame:
        """
        Create interaction features
        
        Args:
            df: Input dataframe
            feature_pairs: List of (feature1, feature2) tuples to create interactions
            
        Returns:
            Dataframe with interaction features
        """
        df = df.copy()
        
        for feat1, feat2 in feature_pairs:
            if feat1 in df.columns and feat2 in df.columns:
                interaction_name = f"{feat1}_x_{feat2}"
                df[interaction_name] = df[feat1] * df[feat2]
        
        return df
    
    def create_polynomial_features(self, df: pd.DataFrame, columns: List[str],
                                   degree: int = 2) -> pd.DataFrame:
        """
        Create polynomial features
        
        Args:
            df: Input dataframe
            columns: Columns to create polynomial features for
            degree: Degree of polynomial
            
        Returns:
            Dataframe with polynomial features
        """
        df = df.copy()
        
        for col in columns:
            if col in df.columns:
                for d in range(2, degree + 1):
                    df[f"{col}_power_{d}"] = df[col] ** d
        
        return df
    
    def select_features(self, X: pd.DataFrame, y: pd.Series, k: int = 10) -> pd.DataFrame:
        """
        Select top k features using statistical tests
        
        Args:
            X: Feature dataframe
            y: Target series
            k: Number of features to select
            
        Returns:
            Dataframe with selected features
        """
        # Convert categorical to numeric if needed
        X_numeric = X.select_dtypes(include=[np.number])
        
        if len(X_numeric.columns) == 0:
            return X
        
        self.feature_selector = SelectKBest(score_func=f_classif, k=min(k, len(X_numeric.columns)))
        X_selected = self.feature_selector.fit_transform(X_numeric, y)
        
        selected_features = X_numeric.columns[self.feature_selector.get_support()].tolist()
        return X[selected_features]
    
    def transform(self, df: pd.DataFrame, target_column: Optional[str] = None,
                 fit: bool = True) -> pd.DataFrame:
        """
        Complete feature engineering pipeline
        
        Args:
            df: Input dataframe
            target_column: Target column name (if provided, will be excluded from transformations)
            fit: Whether to fit transformers (True for training)
            
        Returns:
            Transformed dataframe
        """
        df = df.copy()
        
        # Separate target if provided
        target = None
        if target_column and target_column in df.columns:
            target = df[target_column]
            df = df.drop(columns=[target_column])
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Encode categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            df = self.encode_categorical(df, categorical_cols, method='label')
        
        # Scale features
        df = self.scale_features(df, fit=fit)
        
        # Add target back if it was separated
        if target is not None:
            df[target_column] = target
        
        return df


if __name__ == "__main__":
    # Example usage
    print("Feature Engineering Module")
    print("Use this module to preprocess and engineer features for ML models")
