"""
Data Cleaning Script for Hotel Analysis
Cleans and preprocesses hotel booking data for PowerBI analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class HotelDataCleaner:
    """Class for cleaning hotel booking data"""
    
    def __init__(self, data_path):
        """
        Initialize the data cleaner
        
        Args:
            data_path (str): Path to the raw data file
        """
        self.data_path = data_path
        self.df = None
        
    def load_data(self):
        """Load data from CSV or Excel file"""
        try:
            if self.data_path.endswith('.csv'):
                self.df = pd.read_csv(self.data_path)
            elif self.data_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(self.data_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or Excel files.")
            
            print(f"Data loaded successfully: {len(self.df)} rows, {len(self.df.columns)} columns")
            return self.df
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise
    
    def remove_duplicates(self):
        """Remove duplicate records"""
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = initial_count - len(self.df)
        print(f"Removed {removed} duplicate records")
        return self.df
    
    def handle_missing_values(self):
        """Handle missing values in the dataset"""
        # Fill missing values based on column type
        for col in self.df.columns:
            if self.df[col].dtype in ['int64', 'float64']:
                # Fill numeric columns with median
                self.df[col].fillna(self.df[col].median(), inplace=True)
            elif self.df[col].dtype == 'object':
                # Fill categorical columns with mode
                mode_value = self.df[col].mode()[0] if not self.df[col].mode().empty else 'Unknown'
                self.df[col].fillna(mode_value, inplace=True)
        
        print("Missing values handled")
        return self.df
    
    def convert_date_columns(self, date_columns):
        """
        Convert date columns to datetime format
        
        Args:
            date_columns (list): List of column names that contain dates
        """
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                print(f"Converted {col} to datetime")
        return self.df
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics like length of stay, revenue, etc."""
        # Example calculations (adjust based on your data structure)
        if 'check_in_date' in self.df.columns and 'check_out_date' in self.df.columns:
            self.df['length_of_stay'] = (
                (self.df['check_out_date'] - self.df['check_in_date']).dt.days
            )
        
        if 'room_rate' in self.df.columns and 'length_of_stay' in self.df.columns:
            self.df['total_revenue'] = self.df['room_rate'] * self.df['length_of_stay']
        
        print("Derived metrics calculated")
        return self.df
    
    def clean_data(self, date_columns=None):
        """
        Main method to clean the entire dataset
        
        Args:
            date_columns (list): List of date column names
        """
        print("Starting data cleaning process...")
        
        # Load data
        self.load_data()
        
        # Remove duplicates
        self.remove_duplicates()
        
        # Handle missing values
        self.handle_missing_values()
        
        # Convert dates
        if date_columns:
            self.convert_date_columns(date_columns)
        
        # Calculate derived metrics
        self.calculate_derived_metrics()
        
        print("Data cleaning completed!")
        return self.df
    
    def save_cleaned_data(self, output_path):
        """
        Save cleaned data to file
        
        Args:
            output_path (str): Path to save the cleaned data
        """
        try:
            if output_path.endswith('.csv'):
                self.df.to_csv(output_path, index=False)
            elif output_path.endswith('.xlsx'):
                self.df.to_excel(output_path, index=False)
            else:
                raise ValueError("Unsupported output format")
            
            print(f"Cleaned data saved to: {output_path}")
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            raise


def main():
    """Main function to run data cleaning"""
    # Configuration
    input_file = 'data/raw/hotel_bookings.csv'  # Update with your file path
    output_file = 'data/processed/hotel_bookings_cleaned.csv'
    date_columns = ['check_in_date', 'check_out_date', 'booking_date']  # Update based on your data
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Initialize cleaner
    cleaner = HotelDataCleaner(input_file)
    
    # Clean data
    cleaned_df = cleaner.clean_data(date_columns=date_columns)
    
    # Save cleaned data
    cleaner.save_cleaned_data(output_file)
    
    # Display summary
    print("\n=== Data Summary ===")
    print(f"Total records: {len(cleaned_df)}")
    print(f"Total columns: {len(cleaned_df.columns)}")
    print("\nColumn names:")
    print(cleaned_df.columns.tolist())
    print("\nFirst few rows:")
    print(cleaned_df.head())


if __name__ == "__main__":
    main()
