"""
Data Collection Script for Hotel Booking Analysis
Collects hotel booking data from public sources for PowerBI analysis
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import time
import json
import os
from typing import List, Dict, Any


class HotelDataCollector:
    """Collect hotel booking data from public sources"""
    
    def __init__(self):
        """Initialize data collector"""
        self.data = []
    
    def generate_sample_hotel_data(self, n_records: int = 1000) -> pd.DataFrame:
        """
        Generate realistic sample hotel booking data
        This simulates data that would come from booking.com, Trivago, etc.
        
        Args:
            n_records: Number of records to generate
            
        Returns:
            DataFrame with hotel booking data
        """
        np.random.seed(42)
        
        # Hotel locations
        cities = ['New York', 'London', 'Paris', 'Tokyo', 'Dubai', 'Singapore', 
                  'Barcelona', 'Rome', 'Amsterdam', 'Berlin', 'Sydney', 'Toronto']
        
        # Hotel types
        hotel_types = ['Luxury', 'Business', 'Boutique', 'Resort', 'Budget', 'Airport']
        
        # Room types
        room_types = ['Single', 'Double', 'Twin', 'Suite', 'Deluxe', 'Standard']
        
        # Customer segments
        customer_segments = ['Business', 'Leisure', 'Family', 'Couple', 'Solo']
        
        # Booking channels
        booking_channels = ['Booking.com', 'Trivago', 'Direct', 'Expedia', 'Agoda', 'Hotels.com']
        
        # Generate dates
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        data = []
        for i in range(n_records):
            # Random booking date
            days_diff = (end_date - start_date).days
            booking_date = start_date + timedelta(days=int(np.random.randint(0, days_diff)))
            
            # Check-in date (after booking)
            days_advance = int(np.random.randint(1, 180))
            check_in = booking_date + timedelta(days=days_advance)
            
            # Length of stay
            length_of_stay = int(np.random.choice([1, 2, 3, 4, 5, 7, 10, 14], 
                                            p=[0.2, 0.25, 0.2, 0.15, 0.1, 0.05, 0.03, 0.02]))
            check_out = check_in + timedelta(days=length_of_stay)
            
            # Hotel details
            city = np.random.choice(cities)
            hotel_type = np.random.choice(hotel_types)
            room_type = np.random.choice(room_types)
            
            # Pricing (varies by city, type, season)
            base_rate = {
                'New York': 250, 'London': 200, 'Paris': 180, 'Tokyo': 150,
                'Dubai': 220, 'Singapore': 160, 'Barcelona': 120, 'Rome': 130,
                'Amsterdam': 140, 'Berlin': 100, 'Sydney': 180, 'Toronto': 150
            }
            
            room_rate = base_rate.get(city, 150)
            # Add variation based on hotel type
            if hotel_type == 'Luxury':
                room_rate *= 2.5
            elif hotel_type == 'Resort':
                room_rate *= 1.8
            elif hotel_type == 'Budget':
                room_rate *= 0.6
            
            # Seasonal variation
            month = check_in.month
            if month in [6, 7, 8, 12]:  # Peak season
                room_rate *= 1.3
            elif month in [1, 2, 11]:  # Low season
                room_rate *= 0.85
            
            # Add some randomness
            room_rate = np.random.normal(room_rate, room_rate * 0.15)
            room_rate = max(50, room_rate)  # Minimum rate
            
            # Calculate revenue
            total_revenue = room_rate * length_of_stay
            
            # Number of guests
            num_guests = np.random.choice([1, 2, 3, 4], p=[0.2, 0.4, 0.25, 0.15])
            
            # Customer segment
            customer_segment = np.random.choice(customer_segments)
            
            # Booking channel
            booking_channel = np.random.choice(booking_channels, 
                                            p=[0.3, 0.25, 0.15, 0.15, 0.1, 0.05])
            
            # Cancellation
            is_cancelled = np.random.choice([0, 1], p=[0.85, 0.15])
            
            # Customer rating (if not cancelled)
            if not is_cancelled:
                rating = np.random.normal(4.2, 0.8)
                rating = max(1, min(5, rating))
            else:
                rating = None
            
            # Country code
            country_codes = {
                'New York': 'US', 'London': 'GB', 'Paris': 'FR', 'Tokyo': 'JP',
                'Dubai': 'AE', 'Singapore': 'SG', 'Barcelona': 'ES', 'Rome': 'IT',
                'Amsterdam': 'NL', 'Berlin': 'DE', 'Sydney': 'AU', 'Toronto': 'CA'
            }
            
            record = {
                'booking_id': f'BK{10000 + i:06d}',
                'hotel_name': f'{hotel_type} Hotel {city}',
                'city': city,
                'country': country_codes.get(city, 'US'),
                'hotel_type': hotel_type,
                'room_type': room_type,
                'booking_date': booking_date.strftime('%Y-%m-%d'),
                'check_in_date': check_in.strftime('%Y-%m-%d'),
                'check_out_date': check_out.strftime('%Y-%m-%d'),
                'length_of_stay': length_of_stay,
                'num_guests': num_guests,
                'room_rate': round(room_rate, 2),
                'total_revenue': round(total_revenue, 2),
                'customer_segment': customer_segment,
                'booking_channel': booking_channel,
                'is_cancelled': is_cancelled,
                'rating': round(rating, 1) if rating else None,
                'adr': round(room_rate, 2),  # Average Daily Rate
                'revpar': round(total_revenue / length_of_stay, 2) if length_of_stay > 0 else 0
            }
            
            data.append(record)
        
        df = pd.DataFrame(data)
        return df
    
    def collect_from_kaggle_dataset(self, dataset_name: str = "jessemostipak/hotel-booking-demand") -> pd.DataFrame:
        """
        Instructions for downloading hotel booking data from Kaggle
        
        Args:
            dataset_name: Kaggle dataset name
            
        Returns:
            DataFrame with hotel booking data
        """
        print(f"To download data from Kaggle:")
        print(f"1. Install kaggle: pip install kaggle")
        print(f"2. Set up Kaggle API credentials")
        print(f"3. Download: kaggle datasets download -d {dataset_name}")
        print(f"4. Extract and load the CSV file")
        print("\nFor now, using generated sample data...")
        return self.generate_sample_hotel_data(5000)
    
    def save_to_csv(self, df: pd.DataFrame, filepath: str):
        """Save data to CSV file"""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Data saved to: {filepath}")
        print(f"Records: {len(df)}")
    
    def prepare_for_powerbi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data specifically for PowerBI
        
        Args:
            df: Input dataframe
            
        Returns:
            PowerBI-ready dataframe
        """
        # Convert date columns
        date_columns = ['booking_date', 'check_in_date', 'check_out_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        # Create time dimensions
        if 'check_in_date' in df.columns:
            df['year'] = df['check_in_date'].dt.year
            df['month'] = df['check_in_date'].dt.month
            df['month_name'] = df['check_in_date'].dt.strftime('%B')
            df['quarter'] = df['check_in_date'].dt.quarter
            df['weekday'] = df['check_in_date'].dt.day_name()
            df['is_weekend'] = df['check_in_date'].dt.weekday >= 5
            df['year_month'] = df['check_in_date'].dt.to_period('M').astype(str)
        
        # Create segments
        if 'total_revenue' in df.columns:
            df['revenue_segment'] = pd.cut(
                df['total_revenue'],
                bins=[0, 200, 500, 1000, float('inf')],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        
        if 'length_of_stay' in df.columns:
            df['stay_segment'] = pd.cut(
                df['length_of_stay'],
                bins=[0, 2, 5, 10, float('inf')],
                labels=['Short (1-2)', 'Medium (3-5)', 'Long (6-10)', 'Extended (10+)']
            )
        
        # Calculate KPIs
        df['occupancy_rate'] = 1.0  # Would need room availability data
        df['cancellation_rate'] = df['is_cancelled'].apply(lambda x: 1.0 if x else 0.0)
        
        return df


def main():
    """Main function to collect and prepare hotel data"""
    print("=" * 60)
    print("Hotel Data Collection for PowerBI")
    print("=" * 60)
    
    collector = HotelDataCollector()
    
    # Generate sample data (simulating booking.com/Trivago data)
    print("\n1. Generating hotel booking data...")
    df = collector.generate_sample_hotel_data(n_records=5000)
    
    print(f"Generated {len(df)} booking records")
    print(f"Date range: {df['check_in_date'].min()} to {df['check_in_date'].max()}")
    print(f"Cities: {df['city'].nunique()} unique cities")
    print(f"Total Revenue: ${df['total_revenue'].sum():,.2f}")
    
    # Prepare for PowerBI
    print("\n2. Preparing data for PowerBI...")
    df_powerbi = collector.prepare_for_powerbi(df)
    
    # Save raw data
    raw_path = 'data/raw/hotel_bookings_raw.csv'
    collector.save_to_csv(df, raw_path)
    
    # Save PowerBI-ready data
    powerbi_path = 'data/processed/hotel_bookings_powerbi.csv'
    collector.save_to_csv(df_powerbi, powerbi_path)
    
    # Display summary
    print("\n3. Data Summary")
    print("-" * 60)
    print(f"Total Bookings: {len(df_powerbi)}")
    print(f"Cancellation Rate: {df_powerbi['is_cancelled'].mean()*100:.1f}%")
    print(f"Average ADR: ${df_powerbi['adr'].mean():.2f}")
    print(f"Average Length of Stay: {df_powerbi['length_of_stay'].mean():.1f} days")
    print(f"Top Booking Channel: {df_powerbi['booking_channel'].mode()[0]}")
    print(f"Top City: {df_powerbi['city'].mode()[0]}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Open PowerBI Desktop")
    print("2. Import data from:", powerbi_path)
    print("3. Create visualizations and dashboards")
    print("=" * 60)
    
    return df_powerbi


if __name__ == "__main__":
    main()
