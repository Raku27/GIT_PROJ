# PowerBI Web Setup Guide for Mac Users

Since PowerBI Desktop is Windows-only, Mac users can use **PowerBI Service (Web)** to create and view dashboards. This guide will walk you through the process.

## Prerequisites

1. **Microsoft Account** (free or Office 365 account)
2. **Web Browser** (Chrome, Safari, or Firefox recommended)
3. **PowerBI Service Access** - Sign up at https://powerbi.microsoft.com (free tier available)

## Step 1: Sign Up for PowerBI Service

1. Go to: https://powerbi.microsoft.com
2. Click **"Sign up free"** or **"Get started"**
3. Sign in with your Microsoft account
4. You'll get access to PowerBI Service (web version)

## Step 2: Prepare Your Data

### Option A: Use Generated Data (Recommended)

```bash
cd 01-data-hotel-analysis-powerbi
python scripts/data_collection.py
```

This creates: `data/processed/hotel_bookings_powerbi.csv`

### Option B: Use Your Own Data

Place your CSV file in the `data/processed/` directory.

## Step 3: Upload Data to PowerBI Service

### Method 1: Direct CSV Upload (Easiest)

1. **Log in to PowerBI Service**
   - Go to: https://app.powerbi.com
   - Sign in with your Microsoft account

2. **Create a New Dataset**
   - Click **"My workspace"** (or create a new workspace)
   - Click **"New"** → **"Dataset"**
   - Select **"Upload a file"** → **"Local file"**
   - Choose your CSV file: `data/processed/hotel_bookings_powerbi.csv`
   - Click **"Upload"**

3. **Wait for Processing**
   - PowerBI will process your data (usually takes 1-2 minutes)
   - You'll see a notification when it's ready

### Method 2: OneDrive/SharePoint (Recommended for Large Files)

1. **Upload to OneDrive**
   - Upload `hotel_bookings_powerbi.csv` to your OneDrive
   - Right-click the file → **"More"** → **"Open in PowerBI"**

2. **Or Use SharePoint**
   - Upload to SharePoint document library
   - Connect from PowerBI Service

### Method 3: Connect to Cloud Storage

1. In PowerBI Service, click **"New"** → **"Dataset"**
2. Choose your storage:
   - **OneDrive for Business**
   - **SharePoint**
   - **Google Drive** (via connector)
   - **Dropbox** (via connector)

## Step 4: Create Your First Report

1. **Open Your Dataset**
   - In PowerBI Service, find your dataset
   - Click **"Create report"** (or the dataset name)

2. **PowerBI Report Editor Opens**
   - You'll see your data fields on the right
   - Canvas in the center for visualizations
   - Visualizations panel on the right

## Step 5: Create Visualizations

### Create KPI Cards

1. Click on a **Card** visualization
2. Drag **Total Revenue** field to the card
3. Format: Click the paint roller icon
   - Set number format to Currency
   - Adjust size and color

### Create Revenue Trend Chart

1. Click on **Line chart**
2. Drag **check_in_date** to X-axis
3. Drag **total_revenue** to Y-axis
4. Format as needed

### Create Revenue by City

1. Click on **Bar chart**
2. Drag **city** to X-axis
3. Drag **total_revenue** to Y-axis
4. Sort by revenue (descending)

### Create Booking Channel Pie Chart

1. Click on **Pie chart**
2. Drag **booking_channel** to Legend
3. Drag **total_revenue** to Values

## Step 6: Add DAX Measures (Calculations)

Since you can't use PowerBI Desktop on Mac, you can:

### Option A: Use PowerBI Service DAX Editor

1. In your report, click on a table name (e.g., "hotel_bookings_powerbi")
2. Click **"New measure"** or **"New column"**
3. Enter DAX formula, for example:

```dax
Total Revenue = SUM(hotel_bookings_powerbi[total_revenue])
```

```dax
Average Daily Rate = AVERAGE(hotel_bookings_powerbi[room_rate])
```

```dax
Cancellation Rate = 
DIVIDE(
    COUNTROWS(FILTER(hotel_bookings_powerbi, hotel_bookings_powerbi[is_cancelled] = 1)),
    COUNTROWS(hotel_bookings_powerbi),
    0
)
```

### Option B: Pre-calculate in Python

You can add calculated columns in your Python script before uploading:

```python
# In data_collection.py or data_transformation.py
df['total_revenue_calc'] = df['room_rate'] * df['length_of_stay']
df['cancellation_rate'] = df['is_cancelled'].mean()
```

## Step 7: Create Multiple Pages/Dashboards

1. **Add New Page**
   - Click **"+"** at the bottom to add a new page
   - Name it (e.g., "Revenue Analysis", "Operational Metrics")

2. **Create Different Visualizations** on each page

3. **Pin Visualizations to Dashboard**
   - Click the pin icon on any visualization
   - Choose which dashboard to pin to
   - Create a new dashboard if needed

## Step 8: Share Your Dashboard

1. **Publish Report**
   - Click **"Publish"** or **"Share"** button
   - Choose workspace or create shareable link

2. **Share Options**
   - **Share with specific people** (email addresses)
   - **Publish to web** (public link - be careful with sensitive data)
   - **Embed in website** (if you have a website)

## Step 9: Set Up Data Refresh (Optional)

For automatic data updates:

1. **Go to Dataset Settings**
   - Click on your dataset
   - Click **"..."** → **"Settings"**

2. **Configure Refresh**
   - Set up **Scheduled refresh** (requires PowerBI Pro or Premium)
   - Or manually refresh by clicking **"Refresh now"**

3. **For Free Tier**
   - Manual refresh only
   - Re-upload updated CSV files when needed

## Tips for Mac Users

### Browser Recommendations
- **Chrome**: Best compatibility
- **Safari**: Works well, but some features may be limited
- **Firefox**: Good alternative

### Keyboard Shortcuts
- **Ctrl + Click** (Mac) = Right-click equivalent
- **Cmd + C/V**: Copy/Paste
- **Cmd + Z**: Undo

### Limitations on Web vs Desktop
- **No Power Query Editor**: Limited data transformation
- **Limited DAX Editor**: Basic measures only
- **No Direct Database Connections**: Use CSV/Excel files or cloud storage
- **Visualization Options**: Slightly fewer options than Desktop

### Workarounds

1. **Data Transformation**: Do all transformations in Python before uploading
2. **Complex DAX**: Pre-calculate in Python or use calculated columns
3. **Large Files**: Use OneDrive/SharePoint for files >100MB

## Quick Reference: Creating Common Visualizations

### KPI Card
- Visualization: **Card**
- Field: Any numeric field (e.g., total_revenue)

### Line Chart (Trend)
- Visualization: **Line chart**
- X-axis: Date field
- Y-axis: Numeric field

### Bar Chart
- Visualization: **Clustered bar chart**
- X-axis: Category field
- Y-axis: Numeric field

### Pie Chart
- Visualization: **Pie chart**
- Legend: Category field
- Values: Numeric field

### Map
- Visualization: **Map**
- Location: City/Country field
- Size: Numeric field (e.g., revenue)

### Table
- Visualization: **Table**
- Values: Multiple fields

## Troubleshooting

### "File too large" Error
- **Solution**: Use OneDrive/SharePoint instead of direct upload
- Or reduce data size in Python before uploading

### "Can't create measure" Error
- **Solution**: Make sure you're clicking on the table name, not a field
- Free tier has limited DAX capabilities

### Visualizations Not Showing
- **Solution**: Check data types (dates, numbers)
- Verify field names match
- Refresh the page

### Slow Performance
- **Solution**: Reduce data size
- Use aggregations instead of raw data
- Filter data before uploading

## Next Steps

1. **Explore Sample Reports**: PowerBI Service has sample reports you can explore
2. **Learn DAX**: Even on web, you can create basic measures
3. **Join PowerBI Community**: Get help and see examples
4. **Watch Tutorials**: Many YouTube tutorials for PowerBI Service

## Resources

- **PowerBI Service**: https://app.powerbi.com
- **PowerBI Documentation**: https://docs.microsoft.com/power-bi/
- **PowerBI Community**: https://community.powerbi.com/
- **DAX Reference**: https://docs.microsoft.com/dax/

## Alternative: Use PowerBI Desktop via Virtual Machine

If you need full PowerBI Desktop features:

1. **Use Parallels Desktop** or **VMware Fusion**
2. **Install Windows VM**
3. **Install PowerBI Desktop** in the VM
4. **Publish to PowerBI Service** from VM
5. **View on Mac** via PowerBI Service

This is more complex but gives you full Desktop features.

---

**Your data is ready!** Follow these steps to create beautiful dashboards on your Mac using PowerBI Service.
