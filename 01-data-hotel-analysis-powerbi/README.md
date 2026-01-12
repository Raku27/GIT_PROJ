# Data Hotel Analysis with PowerBI

[![PowerBI](https://img.shields.io/badge/PowerBI-F2C811?style=flat&logo=Power-BI&logoColor=black)](https://powerbi.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

## 📋 Overview

A comprehensive data analysis project focusing on hotel industry data using PowerBI for visualization and business intelligence. This project demonstrates expertise in data extraction, transformation, cleaning, and creating interactive dashboards that provide actionable insights for hotel management and operations.

## ✨ Features

- **Data Extraction & Transformation**: Automated data pipeline for hotel datasets
- **Interactive Dashboards**: Multiple PowerBI dashboards with drill-down capabilities
- **Key Performance Indicators (KPIs)**: Revenue, occupancy rates, customer satisfaction metrics
- **Time Series Analysis**: Trend analysis for bookings, revenue, and seasonal patterns
- **Geographic Visualization**: Location-based insights and heat maps
- **Customer Segmentation**: Analysis of customer demographics and preferences
- **Revenue Analytics**: Revenue per available room (RevPAR), average daily rate (ADR) analysis

## 🎯 Business Objectives

- Identify booking trends and peak seasons
- Analyze revenue patterns and optimization opportunities
- Understand customer behavior and preferences
- Monitor operational performance metrics
- Support data-driven decision making for hotel management

## 🛠️ Technologies Used

- **PowerBI**: Dashboard creation and data visualization
- **Python**: Data preprocessing and analysis (Pandas, NumPy)
- **SQL**: Data extraction and querying
- **Excel/CSV**: Data sources and exports
- **DAX**: Data Analysis Expressions for PowerBI calculations

## 📁 Project Structure

```
01-data-hotel-analysis-powerbi/
├── data/                    # Raw and processed datasets
│   ├── raw/                 # Original data files
│   └── processed/           # Cleaned and transformed data
├── powerbi/                 # PowerBI dashboard files (.pbix)
├── scripts/                 # Python data processing scripts
│   ├── data_cleaning.py
│   ├── data_transformation.py
│   └── data_validation.py
├── docs/                    # Documentation
│   ├── data_dictionary.md
│   └── dashboard_guide.md
├── reports/                  # Generated reports and exports
└── README.md                # This file
```

## 🚀 Getting Started

### Prerequisites

- **For Mac Users**: PowerBI Service (web) - Sign up at https://powerbi.microsoft.com (free)
- **For Windows Users**: PowerBI Desktop (free download from Microsoft)
- Python 3.8+ with required packages
- Access to hotel dataset (or use generated sample data)

### Installation

```bash
# Clone the repository
git clone https://github.com/Raku27/GIT_PROJ.git
cd GIT_PROJ/01-data-hotel-analysis-powerbi

# Install Python dependencies
pip install -r requirements.txt
```

### Quick Start - Create PowerBI Dashboard

1. **Collect Hotel Booking Data** (from Booking.com, Trivago, or public sources):
   ```bash
   python scripts/data_collection.py
   ```
   This generates realistic hotel booking data simulating Booking.com/Trivago data and saves it to `data/processed/hotel_bookings_powerbi.csv`

2. **Process and Clean Data**:
   ```bash
   python scripts/data_cleaning.py
   python scripts/data_transformation.py
   ```

3. **Create PowerBI Template** (optional):
   ```bash
   python scripts/create_powerbi_template.py
   ```
   This creates DAX measures and configuration files

4. **Open PowerBI** (Mac or Windows):

   **For Mac Users (PowerBI Web/Service)**:
   - Go to: https://app.powerbi.com
   - Sign in with Microsoft account
   - Click **"New"** → **"Dataset"** → **"Upload a file"**
   - Select: `data/processed/hotel_bookings_powerbi.csv`
   - See detailed guide: `docs/powerbi_web_setup_mac.md`

   **For Windows Users (PowerBI Desktop)**:
   - Open PowerBI Desktop
   - Get Data → Text/CSV
   - Select: `data/processed/hotel_bookings_powerbi.csv`
   - Load the data

5. **Create Dashboards**:
   - **Mac**: Follow `docs/powerbi_web_setup_mac.md` for web-based dashboard creation
   - **Windows**: Follow `docs/powerbi_dashboard_guide.md` for Desktop
   - Use DAX measures from `docs/dax_measures.txt`
   - Create visualizations for revenue, bookings, occupancy, and more

### Data Sources

**Option 1: Generated Sample Data (Quick Start)**
- Run `python scripts/data_collection.py` to generate realistic hotel booking data
- Simulates data from Booking.com, Trivago, and other booking platforms
- Includes 5,000+ booking records with realistic patterns

**Option 2: Public Datasets**
- **Kaggle**: Hotel Booking Demand dataset (https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand)
- Download and place CSV in `data/raw/` directory
- Process using the provided scripts

**Option 3: Real Data Collection**
- Use the data collection script as a template
- Modify to connect to your data sources
- Supports CSV, Excel, and database connections

## 📊 Dashboard Features

### Main Dashboard
- Executive summary with key metrics
- Revenue trends and forecasts
- Occupancy rate analysis
- Customer satisfaction scores

### Revenue Analysis Dashboard
- Revenue by room type
- Revenue by location/region
- Revenue by customer segment
- Revenue forecasting

### Operational Dashboard
- Booking trends
- Cancellation analysis
- Staff performance metrics
- Resource utilization

## 📈 Key Metrics & KPIs

- **Occupancy Rate**: Percentage of rooms occupied
- **ADR (Average Daily Rate)**: Average revenue per occupied room
- **RevPAR (Revenue per Available Room)**: Total revenue / Total rooms
- **Customer Satisfaction Score**: Average rating from reviews
- **Booking Conversion Rate**: Successful bookings / Total inquiries

## 📝 Data Sources

- Hotel booking system data
- Customer reviews and ratings
- Financial transaction records
- Operational metrics

## 🔍 Insights & Findings

*(Add your key findings and insights here after analysis)*

## 📸 Screenshots

*(Add screenshots of your PowerBI dashboards here)*

## 🧪 Testing

```bash
# Run data validation tests
python scripts/data_validation.py

# Verify data quality
python -m pytest tests/
```

## 📚 Documentation

- [Data Dictionary](docs/data_dictionary.md) - Description of all data fields
- [Dashboard Guide](docs/dashboard_guide.md) - How to use the PowerBI dashboards
- [Analysis Methodology](docs/methodology.md) - Approach and techniques used

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guidelines](../../CONTRIBUTING.md) first.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 👤 Author

**Rahul Kumaar Subramani**
- GitHub: [@Raku27](https://github.com/Raku27)
- Email: rahulkumaar27@gmail.com

---

⭐ If you found this project helpful, please give it a star!
