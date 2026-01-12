"""
Data loading utilities for AI analysis
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, Any
import os


class DataLoader:
    """Class for loading and preparing data for ML models"""
    
    def __init__(self, data_path: str):
        """
        Initialize data loader
        
        Args:
            data_path: Path to the data file
        """
        self.data_path = data_path
        self.df: Optional[pd.DataFrame] = None
    
    def load_csv(self, **kwargs) -> pd.DataFrame:
        """Load data from CSV file"""
        self.df = pd.read_csv(self.data_path, **kwargs)
        print(f"Loaded {len(self.df)} rows and {len(self.df.columns)} columns")
        return self.df
    
    def load_excel(self, sheet_name: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """Load data from Excel file"""
        self.df = pd.read_excel(self.data_path, sheet_name=sheet_name, **kwargs)
        print(f"Loaded {len(self.df)} rows and {len(self.df.columns)} columns")
        return self.df
    
    def get_basic_info(self) -> Dict[str, Any]:
        """Get basic information about the dataset"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_csv() or load_excel() first.")
        
        return {
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'numeric_columns': self.df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': self.df.select_dtypes(include=['object']).columns.tolist()
        }
    
    def split_features_target(self, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Split data into features and target
        
        Args:
            target_column: Name of the target column
            
        Returns:
            Tuple of (features, target)
        """
        if self.df is None:
            raise ValueError("Data not loaded.")
        
        if target_column not in self.df.columns:
            raise ValueError(f"Target column '{target_column}' not found in data.")
        
        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]
        
        return X, y
    
    def get_data(self) -> pd.DataFrame:
        """Get the loaded dataframe"""
        if self.df is None:
            raise ValueError("Data not loaded.")
        return self.df


def load_data(file_path: str, file_type: str = 'csv', **kwargs) -> pd.DataFrame:
    """
    Convenience function to load data
    
    Args:
        file_path: Path to data file
        file_type: Type of file ('csv' or 'excel')
        **kwargs: Additional arguments for pandas read functions
        
    Returns:
        Loaded dataframe
    """
    loader = DataLoader(file_path)
    
    if file_type.lower() == 'csv':
        return loader.load_csv(**kwargs)
    elif file_type.lower() in ['excel', 'xlsx', 'xls']:
        return loader.load_excel(**kwargs)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


if __name__ == "__main__":
    # Example usage
    data_path = "data/raw/dataset.csv"
    
    if os.path.exists(data_path):
        loader = DataLoader(data_path)
        df = loader.load_csv()
        info = loader.get_basic_info()
        print("\nDataset Info:")
        for key, value in info.items():
            print(f"{key}: {value}")
    else:
        print(f"Data file not found: {data_path}")
