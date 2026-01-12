# Quick Start Guide for Mac Users

## 🚀 Get Started in 5 Minutes

### Step 1: Generate Data (2 minutes)

```bash
cd 01-data-hotel-analysis-powerbi
python scripts/data_collection.py
```

✅ This creates: `data/processed/hotel_bookings_powerbi.csv` with 5,000 booking records

### Step 2: Sign Up for PowerBI Service (1 minute)

1. Go to: https://powerbi.microsoft.com
2. Click **"Sign up free"**
3. Sign in with your Microsoft account (or create one)

### Step 3: Upload Data (1 minute)

1. Go to: https://app.powerbi.com
2. Click **"My workspace"**
3. Click **"New"** → **"Dataset"**
4. Click **"Upload a file"** → **"Local file"**
5. Select: `data/processed/hotel_bookings_powerbi.csv`
6. Wait for processing (1-2 minutes)

### Step 4: Create Your First Visualization (1 minute)

1. Click on your dataset name
2. Click **"Create report"**
3. Drag **total_revenue** to canvas → Creates a card
4. Drag **city** and **total_revenue** → Creates a bar chart
5. Click **"Save"** and name your report

### Step 5: View Your Dashboard

1. Click **"Pin visual"** to pin to dashboard
2. View your dashboard with all visualizations

## 📊 What You'll See

- **5,000 hotel bookings** from 12 major cities
- **Revenue data**: $3.8M+ total revenue
- **Booking channels**: Booking.com, Trivago, Expedia, etc.
- **Time period**: 2023-2025
- **Metrics**: ADR, cancellation rates, length of stay

## 🎯 Next Steps

1. **Add More Visualizations**: See `docs/powerbi_web_setup_mac.md`
2. **Create DAX Measures**: See `docs/dax_measures.txt`
3. **Share Dashboard**: Click "Share" button in PowerBI Service

## 💡 Pro Tips

- **Use Chrome browser** for best experience
- **Upload to OneDrive** for automatic refresh (Pro account)
- **Pre-calculate metrics** in Python before uploading
- **Create multiple pages** for different analysis views

## 📚 Full Documentation

- **Mac Setup Guide**: `docs/powerbi_web_setup_mac.md`
- **Dashboard Guide**: `docs/powerbi_dashboard_guide.md`
- **DAX Measures**: `docs/dax_measures.txt`

## ❓ Need Help?

- PowerBI Service: https://app.powerbi.com
- PowerBI Docs: https://docs.microsoft.com/power-bi/
- Community: https://community.powerbi.com/

---

**Ready?** Run `python scripts/data_collection.py` and start creating! 🎉
