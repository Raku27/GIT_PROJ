"""
Data Transformation Script for Hotel Analysis
Transforms cleaned data into analysis-ready format for PowerBI
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class HotelDataTransformer:
    """Class for transforming hotel data for analysis"""
    
    def __init__(self, data_path):
        """
        Initialize the transformer
        
        Args:
            data_path (str): Path to the cleaned data file
        """
        self.data_path = data_path
        self.df = None
        
    def load_data(self):
        """Load cleaned data"""
        try:
            if self.data_path.endswith('.csv'):
                self.df = pd.read_csv(self.data_path)
            elif self.data_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(self.data_path)
            
            # Convert date columns if they exist
            date_cols = self.df.select_dtypes(include=['object']).columns
            for col in date_cols:
                if 'date' in col.lower():
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            
            print(f"Data loaded: {len(self.df)} rows")
            return self.df
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise
    
    def create_time_dimensions(self):
        """Create time-based dimensions for analysis"""
        date_col = None
        for col in self.df.columns:
            if 'date' in col.lower() and self.df[col].dtype == 'datetime64[ns]':
                date_col = col
                break
        
        if date_col:
            self.df['year'] = self.df[date_col].dt.year
            self.df['month'] = self.df[date_col].dt.month
            self.df['month_name'] = self.df[date_col].dt.strftime('%B')
            self.df['quarter'] = self.df[date_col].dt.quarter
            self.df['weekday'] = self.df[date_col].dt.day_name()
            self.df['is_weekend'] = self.df[date_col].dt.weekday >= 5
            self.df['year_month'] = self.df[date_col].dt.to_period('M')
            
            print("Time dimensions created")
        return self.df
    
    def create_segments(self):
        """Create customer and booking segments"""
        # Revenue segments (adjust thresholds based on your data)
        if 'total_revenue' in self.df.columns:
            self.df['revenue_segment'] = pd.cut(
                self.df['total_revenue'],
                bins=[0, 100, 500, 1000, float('inf')],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        
        # Length of stay segments
        if 'length_of_stay' in self.df.columns:
            self.df['stay_segment'] = pd.cut(
                self.df['length_of_stay'],
                bins=[0, 2, 5, 10, float('inf')],
                labels=['Short (1-2 days)', 'Medium (3-5 days)', 'Long (6-10 days)', 'Extended (10+ days)']
            )
        
        print("Segments created")
        return self.df
    
    def calculate_kpis(self):
        """Calculate key performance indicators"""
        # ADR (Average Daily Rate)
        if 'room_rate' in self.df.columns:
            self.df['adr'] = self.df['room_rate']
        
        # RevPAR (Revenue per Available Room) - would need room availability data
        # For now, calculate average revenue per booking
        if 'total_revenue' in self.df.columns:
            self.df['avg_revenue_per_booking'] = self.df['total_revenue']
        
        print("KPIs calculated")
        return self.df
    
    def create_summary_tables(self):
        """Create summary tables for PowerBI"""
        summaries = {}
        
        # Monthly summary
        if 'year_month' in self.df.columns and 'total_revenue' in self.df.columns:
            monthly_summary = self.df.groupby('year_month').agg({
                'total_revenue': ['sum', 'mean', 'count']
            }).reset_index()
            monthly_summary.columns = ['year_month', 'total_revenue', 'avg_revenue', 'booking_count']
            summaries['monthly_summary'] = monthly_summary
        
        # Segment summary
        if 'revenue_segment' in self.df.columns:
            segment_summary = self.df.groupby('revenue_segment').agg({
                'total_revenue': ['sum', 'mean', 'count']
            }).reset_index()
            summaries['segment_summary'] = segment_summary
        
        return summaries
    
    def transform_data(self):
        """Main transformation method"""
        print("Starting data transformation...")
        
        # Load data
        self.load_data()
        
        # Create time dimensions
        self.create_time_dimensions()
        
        # Create segments
        self.create_segments()
        
        # Calculate KPIs
        self.calculate_kpis()
        
        print("Data transformation completed!")
        return self.df
    
    def save_transformed_data(self, output_path):
        """Save transformed data"""
        try:
            if output_path.endswith('.csv'):
                self.df.to_csv(output_path, index=False)
            elif output_path.endswith('.xlsx'):
                self.df.to_excel(output_path, index=False)
            
            print(f"Transformed data saved to: {output_path}")
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            raise


def main():
    """Main function"""
    input_file = 'data/processed/hotel_bookings_cleaned.csv'
    output_file = 'data/processed/hotel_bookings_transformed.csv'
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Transform data
    transformer = HotelDataTransformer(input_file)
    transformed_df = transformer.transform_data()
    
    # Save transformed data
    transformer.save_transformed_data(output_file)
    
    # Create and save summary tables
    summaries = transformer.create_summary_tables()
    for name, summary_df in summaries.items():
        summary_path = f'data/processed/{name}.csv'
        summary_df.to_csv(summary_path, index=False)
        print(f"Summary table saved: {summary_path}")
    
    print("\n=== Transformation Summary ===")
    print(f"Total records: {len(transformed_df)}")
    print(f"New columns added: {len([col for col in transformed_df.columns if col not in ['year', 'month']])}")


if __name__ == "__main__":
    main()
