# Matali Pricing System - User Guide

## Overview
Matali Pricing System is a comprehensive solution for capacity management and dynamic pricing for logistics services.

## Quick Start

### Starting the Application
```powershell
cd "c:\Users\ahmed\vs code\PRICE\matali_pricing_system"
& "C:\Users\ahmed\AppData\Local\Microsoft\WindowsApps\python.exe" -m streamlit run app.py
```

The system will open automatically at: `http://localhost:8502`

## ⚠️ Important: System Starts Empty!

**This is intentional!** When you first open the system:
- ✅ Dashboard will be **empty** - this is normal
- ✅ You will see **warning messages** guiding you
- ✅ The system has **NO default data** to avoid confusion
- ✅ You must input your own data following the sequence below

## Data Entry Sequence

### Step 1: Setup Capacity Data
**Page:** ⚙️ Capacity Setup

**Option A: Manual Entry**
1. Go to "➕ Add New Service" tab
2. Fill in service details
3. Click "Add Service"

**Option B: Excel Import**
1. Download template from "📥 Excel Templates"
2. Fill in your data
3. Upload the file back

### Step 2: Define Pricing Tiers
**Page:** 💵 Pricing Tiers OR 🤖 Dynamic Pricing

**Option A: Smart Dynamic Pricing (Recommended)**
1. Go to "🤖 Dynamic Pricing"
2. Adjust parameters:
   - Target profit margin
   - Expected utilization rate
   - Waste cost recovery
3. Review calculated prices
4. Click "Save as Pricing Tiers"

**Option B: Manual Entry**
1. Go to "💵 Pricing Tiers"
2. Add tiers manually

### Step 3: Create Quotes
**Page:** 📋 New Quote

1. Enter client information
2. Select services and quantities
3. System calculates prices automatically
4. Save quote

### Step 4: View Analytics
**Page:** 📊 Advanced Dashboard

Now you'll see meaningful data and insights!

## Features

### 🎯 Capacity Management
- Track daily and static capacities
- Monitor utilization rates
- Calculate waste costs

### 💰 Dynamic Pricing
- Automatic price calculation
- Volume-based tier generation
- Profit margin optimization

### 📊 Advanced Analytics
- KPI dashboard
- Profitability analysis
- Service performance tracking
- Alerts and recommendations

### 📥 Excel Integration
- Download empty templates
- Upload bulk data
- Export reports

## File Structure

```
matali_pricing_system/
├── app.py                      # Main application
├── advanced_dashboard.py       # Analytics dashboard
├── requirements.txt            # Dependencies
├── data/                       # Data folder (created automatically)
│   ├── capacity_config.xlsx
│   ├── pricing_tiers.xlsx
│   └── quotes_history.xlsx
├── دليل_الاستخدام.md          # Arabic user guide
└── README.md                   # This file
```

## Troubleshooting

### "Dashboard shows no data"
✅ **Expected behavior!** Follow the data entry sequence above.

### "Cannot add pricing tiers"
❌ Add capacity data first in "⚙️ Capacity Setup"

### "Cannot calculate dynamic pricing"
❌ Add capacity and cost data first

## Technologies Used

- **Streamlit** 1.50.0 - Web framework
- **Pandas** 2.3.3 - Data manipulation
- **Plotly** 6.4.0 - Interactive charts
- **OpenPyXL** 3.1.5 - Excel handling
- **NumPy** 2.3.4 - Numerical computations

## License

© 2025 Matali Pro - All Rights Reserved

---

**For support:** support@matali.pro
