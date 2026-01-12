# PowerBI Dashboard Guide - Hotel Booking Analysis

This guide will help you create a comprehensive PowerBI dashboard using hotel booking data from Booking.com, Trivago, and other sources.

## Step 1: Data Collection

### Option A: Use Generated Sample Data (Quick Start)

```bash
cd 01-data-hotel-analysis-powerbi
python scripts/data_collection.py
```

This will generate realistic hotel booking data and save it to `data/processed/hotel_bookings_powerbi.csv`

### Option B: Use Real Public Datasets

#### Kaggle Dataset (Recommended)
1. Go to: https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand
2. Download the dataset
3. Place the CSV file in `data/raw/` directory
4. Run the data processing scripts

#### Other Public Sources
- **Hotel Booking Demand Dataset**: Available on Kaggle
- **Airbnb Open Data**: Available on Kaggle
- **TripAdvisor Reviews**: Available on Kaggle

## Step 2: Data Processing

Run the data processing pipeline:

```bash
# Clean the data
python scripts/data_cleaning.py

# Transform for PowerBI
python scripts/data_transformation.py

# Validate data quality
python scripts/data_validation.py
```

## Step 3: Import Data into PowerBI

1. **Open PowerBI Desktop**
2. **Get Data** → **Text/CSV**
3. Navigate to: `data/processed/hotel_bookings_powerbi.csv`
4. Click **Load** or **Transform Data** (if you need to modify)

## Step 4: Create Data Model

### Key Tables
- **Bookings**: Main fact table with booking details
- **Date Table**: Time dimension (auto-created from dates)
- **Hotels**: Dimension table (if you have hotel master data)
- **Customers**: Dimension table (if you have customer data)

### Relationships
- Bookings[check_in_date] → Date[Date]
- Bookings[hotel_id] → Hotels[hotel_id] (if applicable)

## Step 5: Create Key Measures (DAX)

### Revenue Measures

```dax
Total Revenue = SUM(Bookings[total_revenue])

Average Daily Rate (ADR) = AVERAGE(Bookings[room_rate])

Revenue per Available Room (RevPAR) = 
    DIVIDE([Total Revenue], [Total Rooms Available], 0)
    // Note: Requires room availability data

Average Revenue per Booking = 
    AVERAGE(Bookings[total_revenue])
```

### Occupancy Measures

```dax
Total Bookings = COUNTROWS(Bookings)

Occupancy Rate = 
    DIVIDE(
        COUNTROWS(Bookings),
        [Total Rooms Available],
        0
    )

Cancellation Rate = 
    DIVIDE(
        COUNTROWS(FILTER(Bookings, Bookings[is_cancelled] = 1)),
        [Total Bookings],
        0
    )
```

### Time-Based Measures

```dax
Revenue YTD = 
    TOTALYTD([Total Revenue], 'Date'[Date])

Revenue vs Previous Year = 
    VAR CurrentYear = [Total Revenue]
    VAR PreviousYear = CALCULATE(
        [Total Revenue],
        SAMEPERIODLASTYEAR('Date'[Date])
    )
    RETURN CurrentYear - PreviousYear

Revenue Growth % = 
    DIVIDE(
        [Revenue vs Previous Year],
        CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date])),
        0
    )
```

## Step 6: Create Visualizations

### Dashboard 1: Executive Summary

**Visualizations:**
1. **KPI Cards** (Top Row)
   - Total Revenue
   - Total Bookings
   - Average ADR
   - Occupancy Rate
   - Cancellation Rate

2. **Revenue Trend** (Line Chart)
   - X-axis: Month/Year
   - Y-axis: Total Revenue
   - Show trend over time

3. **Revenue by City** (Bar Chart)
   - X-axis: City
   - Y-axis: Total Revenue
   - Sort by revenue descending

4. **Booking Channel Performance** (Pie Chart)
   - Values: Booking Channel
   - Size: Total Revenue or Booking Count

### Dashboard 2: Revenue Analysis

**Visualizations:**
1. **Revenue by Hotel Type** (Stacked Column Chart)
   - X-axis: Hotel Type
   - Y-axis: Total Revenue
   - Stack by: Month

2. **ADR Trend** (Line Chart)
   - X-axis: Date
   - Y-axis: Average ADR
   - Show trend and forecast

3. **Revenue Heatmap** (Matrix)
   - Rows: City
   - Columns: Month
   - Values: Total Revenue
   - Color scale: Revenue amount

4. **Top 10 Hotels by Revenue** (Table)
   - Columns: Hotel Name, City, Total Revenue, Booking Count

### Dashboard 3: Operational Metrics

**Visualizations:**
1. **Length of Stay Distribution** (Histogram)
   - X-axis: Length of Stay (buckets)
   - Y-axis: Booking Count

2. **Cancellation Analysis** (Donut Chart)
   - Values: Cancelled vs Not Cancelled
   - Show percentage

3. **Booking Channel Comparison** (Clustered Bar Chart)
   - X-axis: Booking Channel
   - Y-axis: Revenue, Bookings, ADR

4. **Customer Segment Analysis** (Treemap)
   - Size: Total Revenue
   - Color: Customer Segment

### Dashboard 4: Geographic Analysis

**Visualizations:**
1. **Revenue by Country/City** (Map Visual)
   - Location: City or Country
   - Size: Total Revenue
   - Color: Average ADR

2. **City Performance Table** (Table)
   - Columns: City, Bookings, Revenue, ADR, Cancellation Rate

3. **Regional Comparison** (Bar Chart)
   - Compare regions or countries

## Step 7: Add Filters and Slicers

Add slicers for:
- **Date Range**: For time-based filtering
- **City**: Filter by location
- **Hotel Type**: Filter by hotel category
- **Booking Channel**: Filter by source
- **Customer Segment**: Filter by segment

## Step 8: Formatting and Design

### Color Scheme
- Primary: Professional blue (#1F4E79)
- Secondary: Green for positive metrics
- Red for negative metrics (cancellations)
- Use consistent colors across visuals

### Layout
- Use grid layout for alignment
- Group related visuals
- Add titles and subtitles
- Include data refresh timestamp

## Step 9: Publish and Share

1. **Publish to PowerBI Service**
   - File → Publish → Select workspace
   - Set up scheduled data refresh

2. **Share Dashboard**
   - Create shareable link
   - Set permissions
   - Embed in websites if needed

## Sample Dashboard Structure

```
┌─────────────────────────────────────────────────┐
│         HOTEL BOOKING ANALYSIS DASHBOARD        │
├─────────────────────────────────────────────────┤
│  [Revenue] [Bookings] [ADR] [Occupancy] [Cancel]│
├─────────────────────────────────────────────────┤
│  Revenue Trend          │  Revenue by City      │
│  [Line Chart]           │  [Bar Chart]          │
├─────────────────────────────────────────────────┤
│  Booking Channels       │  Top Hotels           │
│  [Pie Chart]            │  [Table]               │
├─────────────────────────────────────────────────┤
│  Geographic Revenue Map                         │
│  [Map Visual]                                   │
└─────────────────────────────────────────────────┘
```

## Tips for Best Results

1. **Performance**: Use DirectQuery for large datasets, Import for smaller ones
2. **Refresh**: Set up automatic data refresh schedules
3. **Security**: Implement Row-Level Security if needed
4. **Mobile**: Optimize layout for mobile viewing
5. **Drill-through**: Add drill-through pages for detailed analysis

## Troubleshooting

### Data Not Loading
- Check file path
- Verify CSV format
- Check for special characters

### Measures Not Calculating
- Verify relationships
- Check for null values
- Review DAX syntax

### Visuals Not Displaying
- Check data types
- Verify field mappings
- Review filter settings

## Next Steps

1. Add more data sources (reviews, competitor data)
2. Create predictive analytics
3. Set up alerts for key metrics
4. Integrate with other tools (Excel, SharePoint)

For questions or issues, refer to the main README.md or create an issue on GitHub.
