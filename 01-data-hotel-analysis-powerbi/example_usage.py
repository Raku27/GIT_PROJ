"""
Example usage script for Data Hotel Analysis
Demonstrates how to use the data processing scripts
"""

import os
import sys
from scripts.data_cleaning import HotelDataCleaner
from scripts.data_transformation import HotelDataTransformer
from scripts.data_validation import HotelDataValidator

def main():
    """Example workflow for hotel data analysis"""
    
    print("=" * 60)
    print("Hotel Data Analysis - Example Usage")
    print("=" * 60)
    
    # Step 1: Data Cleaning
    print("\n1. Data Cleaning")
    print("-" * 60)
    input_file = 'data/raw/hotel_bookings.csv'
    cleaned_file = 'data/processed/hotel_bookings_cleaned.csv'
    
    # Create directories if they don't exist
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Note: In real usage, you would have actual data
    # For now, this demonstrates the workflow
    print(f"Input file: {input_file}")
    print(f"Output file: {cleaned_file}")
    print("\nTo use:")
    print("  cleaner = HotelDataCleaner(input_file)")
    print("  cleaned_df = cleaner.clean_data(date_columns=['check_in_date', 'check_out_date'])")
    print("  cleaner.save_cleaned_data(cleaned_file)")
    
    # Step 2: Data Transformation
    print("\n2. Data Transformation")
    print("-" * 60)
    transformed_file = 'data/processed/hotel_bookings_transformed.csv'
    print(f"Input: {cleaned_file}")
    print(f"Output: {transformed_file}")
    print("\nTo use:")
    print("  transformer = HotelDataTransformer(cleaned_file)")
    print("  transformed_df = transformer.transform_data()")
    print("  transformer.save_transformed_data(transformed_file)")
    
    # Step 3: Data Validation
    print("\n3. Data Validation")
    print("-" * 60)
    print(f"Validating: {transformed_file}")
    print("\nTo use:")
    print("  validator = HotelDataValidator(transformed_file)")
    print("  results = validator.generate_validation_report()")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Load transformed data into PowerBI")
    print("   - Mac Users: Use PowerBI Service (web) - see QUICK_START_MAC.md")
    print("   - Windows Users: Use PowerBI Desktop")
    print("2. Create interactive dashboards")
    print("3. Analyze KPIs: Occupancy Rate, ADR, RevPAR")
    print("=" * 60)

if __name__ == "__main__":
    main()
