"""
Script to create a PowerBI template structure
This helps set up the data model and measures for PowerBI
"""

import json
import os
from datetime import datetime


def create_dax_measures():
    """Create DAX measures for PowerBI"""
    
    measures = {
        "revenue_measures": {
            "Total Revenue": "SUM(Bookings[total_revenue])",
            "Average Daily Rate (ADR)": "AVERAGE(Bookings[room_rate])",
            "Average Revenue per Booking": "AVERAGE(Bookings[total_revenue])",
            "Revenue YTD": "TOTALYTD([Total Revenue], 'Date'[Date])",
            "Revenue vs Previous Year": """
                VAR CurrentYear = [Total Revenue]
                VAR PreviousYear = CALCULATE(
                    [Total Revenue],
                    SAMEPERIODLASTYEAR('Date'[Date])
                )
                RETURN CurrentYear - PreviousYear
            """,
            "Revenue Growth %": """
                DIVIDE(
                    [Revenue vs Previous Year],
                    CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date])),
                    0
                )
            """
        },
        "booking_measures": {
            "Total Bookings": "COUNTROWS(Bookings)",
            "Bookings YTD": "TOTALYTD([Total Bookings], 'Date'[Date])",
            "Average Length of Stay": "AVERAGE(Bookings[length_of_stay])",
            "Average Guests per Booking": "AVERAGE(Bookings[num_guests])"
        },
        "cancellation_measures": {
            "Cancelled Bookings": "CALCULATE([Total Bookings], Bookings[is_cancelled] = 1)",
            "Cancellation Rate": """
                DIVIDE(
                    [Cancelled Bookings],
                    [Total Bookings],
                    0
                )
            """,
            "Cancellation Revenue Loss": """
                CALCULATE(
                    [Total Revenue],
                    Bookings[is_cancelled] = 1
                )
            """
        },
        "kpi_measures": {
            "Occupancy Rate": """
                DIVIDE(
                    [Total Bookings],
                    [Total Rooms Available],
                    0
                )
            """,
            "RevPAR": """
                DIVIDE(
                    [Total Revenue],
                    [Total Rooms Available],
                    0
                )
            """,
            "Average Rating": "AVERAGE(Bookings[rating])"
        }
    }
    
    return measures


def create_powerbi_config():
    """Create PowerBI configuration file"""
    
    config = {
        "data_source": {
            "file_path": "data/processed/hotel_bookings_powerbi.csv",
            "file_type": "CSV",
            "refresh_schedule": "Daily"
        },
        "data_model": {
            "tables": [
                {
                    "name": "Bookings",
                    "type": "Fact",
                    "key_column": "booking_id"
                },
                {
                    "name": "Date",
                    "type": "Dimension",
                    "key_column": "Date",
                    "auto_generate": True
                }
            ],
            "relationships": [
                {
                    "from_table": "Bookings",
                    "from_column": "check_in_date",
                    "to_table": "Date",
                    "to_column": "Date"
                }
            ]
        },
        "dashboards": [
            {
                "name": "Executive Summary",
                "description": "High-level KPIs and trends",
                "visuals": [
                    "KPI Cards",
                    "Revenue Trend",
                    "Revenue by City",
                    "Booking Channel Performance"
                ]
            },
            {
                "name": "Revenue Analysis",
                "description": "Detailed revenue breakdown",
                "visuals": [
                    "Revenue by Hotel Type",
                    "ADR Trend",
                    "Revenue Heatmap",
                    "Top Hotels"
                ]
            },
            {
                "name": "Operational Metrics",
                "description": "Operational performance metrics",
                "visuals": [
                    "Length of Stay Distribution",
                    "Cancellation Analysis",
                    "Booking Channel Comparison",
                    "Customer Segment Analysis"
                ]
            }
        ],
        "filters": [
            "Date Range",
            "City",
            "Hotel Type",
            "Booking Channel",
            "Customer Segment"
        ]
    }
    
    return config


def save_dax_to_file(measures, filepath):
    """Save DAX measures to a text file"""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("DAX MEASURES FOR POWERBI\n")
        f.write("=" * 60 + "\n\n")
        f.write("Copy these measures into PowerBI Desktop:\n")
        f.write("1. Right-click on 'Bookings' table\n")
        f.write("2. Select 'New Measure'\n")
        f.write("3. Paste the DAX formula\n\n")
        
        for category, measure_dict in measures.items():
            f.write(f"\n{category.upper().replace('_', ' ')}\n")
            f.write("-" * 60 + "\n")
            for measure_name, formula in measure_dict.items():
                f.write(f"\n{measure_name}:\n")
                f.write(f"{formula.strip()}\n")
                f.write("\n")
    
    print(f"DAX measures saved to: {filepath}")


def save_config_to_file(config, filepath):
    """Save configuration to JSON file"""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to: {filepath}")


def main():
    """Create PowerBI template files"""
    print("=" * 60)
    print("Creating PowerBI Template Files")
    print("=" * 60)
    
    # Create DAX measures
    print("\n1. Creating DAX measures...")
    measures = create_dax_measures()
    save_dax_to_file(measures, 'docs/dax_measures.txt')
    
    # Create configuration
    print("\n2. Creating configuration file...")
    config = create_powerbi_config()
    save_config_to_file(config, 'docs/powerbi_config.json')
    
    # Create instructions
    print("\n3. Creating setup instructions...")
    instructions = """
# PowerBI Setup Instructions

## Quick Start

1. **Collect Data**
   ```bash
   python scripts/data_collection.py
   ```

2. **Process Data**
   ```bash
   python scripts/data_cleaning.py
   python scripts/data_transformation.py
   ```

3. **Open PowerBI Desktop**
   - Get Data → Text/CSV
   - Select: data/processed/hotel_bookings_powerbi.csv

4. **Create Measures**
   - Open docs/dax_measures.txt
   - Copy measures into PowerBI
   - Right-click Bookings table → New Measure

5. **Create Visualizations**
   - Follow guide in docs/powerbi_dashboard_guide.md

## Data Sources

- Generated sample data (default)
- Kaggle: hotel-booking-demand dataset
- Public APIs (if available)

## Next Steps

- Customize measures for your needs
- Add more data sources
- Create additional dashboards
- Set up scheduled refresh
"""
    
    with open('docs/powerbi_setup_instructions.txt', 'w') as f:
        f.write(instructions)
    
    print("Setup instructions saved to: docs/powerbi_setup_instructions.txt")
    
    print("\n" + "=" * 60)
    print("Template files created successfully!")
    print("=" * 60)
    print("\nFiles created:")
    print("  - docs/dax_measures.txt")
    print("  - docs/powerbi_config.json")
    print("  - docs/powerbi_setup_instructions.txt")
    print("\nNext: Run data_collection.py to generate data")


if __name__ == "__main__":
    main()
