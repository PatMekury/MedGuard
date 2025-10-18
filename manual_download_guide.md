# 📥 MedGuard Manual Data Download Guide

Complete step-by-step instructions to manually download all required data.

---

## 📁 File Structure to Create First

Before downloading, create these folders in your project:

```bash
mkdir -p data/copernicus
mkdir -p data/emodnet
mkdir -p data/processed
```

---

## 🌊 PART 1: COPERNICUS MARINE DATA

### Prerequisites
1. Create account at: https://data.marine.copernicus.eu/register
2. Confirm your email
3. Login

---

### Dataset 1: Sea Surface Temperature (SST)

**Step 1:** Go to https://data.marine.copernicus.eu/

**Step 2:** In the search box, type: `Mediterranean Sea Physics Analysis`

**Step 3:** Click on: **"Mediterranean Sea Physics Analysis and Forecast"**
- Product ID: `MEDSEA_ANALYSISFORECAST_PHY_006_013`

**Step 4:** Click **"Download" or "Data Access"**

**Step 5:** Select **"Subset"** option

**Step 6:** Fill in the form:
- **Variables**: Select `Sea water potential temperature` (thetao)
- **Date Range**: 
  - Start: `2024-01-01`
  - End: `2024-10-18` (today)
- **Geographic Area**:
  - North: `46.0`
  - South: `30.0`
  - West: `-6.0`
  - East: `37.0`
- **Depth Range**:
  - Minimum: `0 m`
  - Maximum: `10 m`
- **Output Format**: `NetCDF`

**Step 7:** Click **"Submit"** or **"Download"**

**Step 8:** Wait for processing (5-30 minutes)

**Step 9:** Download the file

**Step 10:** Rename and save:
```bash
# Rename the downloaded file to:
med_sst.nc

# Move it to:
data/copernicus/med_sst.nc
```

**Alternative if above fails:**
- Try product: `Mediterranean Sea - High Resolution L4 Sea Surface Temperature`
- Product ID: `SST_MED_SST_L4_REP_OBSERVATIONS_010_021`

---

### Dataset 2: Ocean Currents

**Step 1:** Same product as SST: `MEDSEA_ANALYSISFORECAST_PHY_006_013`

**Step 2:** Select **"Subset"**

**Step 3:** Fill in:
- **Variables**: Select BOTH:
  - `Eastward sea water velocity` (uo)
  - `Northward sea water velocity` (vo)
- **Date Range**: 
  - Start: `2024-01-01`
  - End: `2024-10-18`
- **Geographic Area**: Same as SST
  - North: `46.0`, South: `30.0`
  - West: `-6.0`, East: `37.0`
- **Depth Range**:
  - Minimum: `0 m`
  - Maximum: `50 m`
- **Format**: `NetCDF`

**Step 4:** Download and save as:
```bash
data/copernicus/med_currents.nc
```

---

### Dataset 3: Chlorophyll-a

**Step 1:** Search for: `Mediterranean Chlorophyll`

**Step 2:** Select: **"Mediterranean Sea Colour Plankton"**
- Product ID: `OCEANCOLOUR_MED_BGC_L4_MY_009_144`

**Alternative (if unavailable):**
- Product: `Mediterranean Sea Biogeochemistry Analysis and Forecast`
- Product ID: `MEDSEA_ANALYSISFORECAST_BGC_006_014`

**Step 3:** Select **"Subset"**

**Step 4:** Fill in:
- **Variables**: `Mass concentration of chlorophyll a` (CHL or chl)
- **Date Range**:
  - Start: `2024-01-01`
  - End: `2024-10-18`
- **Geographic Area**: Same as above
  - North: `46.0`, South: `30.0`
  - West: `-6.0`, East: `37.0`
- **Format**: `NetCDF`

**Step 5:** Download and save as:
```bash
data/copernicus/med_chlorophyll.nc
```

---

### Dataset 4: Salinity (Optional but Recommended)

**Step 1:** Same product as SST: `MEDSEA_ANALYSISFORECAST_PHY_006_013`

**Step 2:** Fill in:
- **Variables**: `Sea water salinity` (so)
- **Date Range**: `2024-01-01` to `2024-10-18`
- **Geographic Area**: Same as above
- **Depth**: 0-50 m
- **Format**: `NetCDF`

**Step 3:** Download and save as:
```bash
data/copernicus/med_salinity.nc
```

---

### Dataset 5: Sea Surface Height (Optional)

**Step 1:** Same product: `MEDSEA_ANALYSISFORECAST_PHY_006_013`

**Step 2:** Fill in:
- **Variables**: `Sea surface height` (zos)
- **Date Range**: `2024-01-01` to `2024-10-18`
- **Geographic Area**: Same as above
- **Format**: `NetCDF`

**Step 3:** Download and save as:
```bash
data/copernicus/med_ssh.nc
```

---

## 🗺️ PART 2: EMODNET DATA

### Dataset 6: Fishing Intensity

**Option A: Via WFS (Advanced)**

**Step 1:** Go to: https://www.emodnet-humanactivities.eu/

**Step 2:** Click **"View Data"** → **"Fishing Intensity"**

**Step 3:** Use the map interface:
- Zoom to Mediterranean Sea
- Select years: `2015-2021`
- Click **"Download"**

**Step 4:** Choose format: `GeoJSON` or `Shapefile`

**Step 5:** Save as:
```bash
data/emodnet/fishing_intensity.geojson
```

**Option B: Direct Download**

**Step 1:** Visit: https://www.emodnet-humanactivities.eu/search-results.php?dataname=Fishing+intensity

**Step 2:** Filter by:
- Region: Mediterranean Sea
- Years: 2015-2021
- Data type: All fishing activities

**Step 3:** Download data

**Step 4:** If it's a shapefile (.shp), convert to GeoJSON:
```python
import geopandas as gpd
gdf = gpd.read_file('downloaded_fishing_data.shp')
gdf.to_file('data/emodnet/fishing_intensity.geojson', driver='GeoJSON')
```

---

### Dataset 7: Marine Protected Areas (MPAs)

**Option A: From Protected Planet**

**Step 1:** Go to: https://www.protectedplanet.net/

**Step 2:** Click **"Explore"**

**Step 3:** In the search box, filter by:
- Region: Mediterranean
- Type: Marine

**Step 4:** Click **"Download"** button

**Step 5:** Select format: `Shapefile` or `GeoJSON`

**Step 6:** Save as:
```bash
data/emodnet/mpa_boundaries.geojson
```

**Option B: From EMODnet**

**Step 1:** Go to: https://www.emodnet-seabedhabitats.eu/

**Step 2:** Click **"Access Data"** → **"Data Products"**

**Step 3:** Look for: "Marine Protected Areas"

**Step 4:** Filter by Mediterranean region

**Step 5:** Download and save as:
```bash
data/emodnet/mpa_boundaries.geojson
```

---

### Dataset 8: Seabed Habitats (Optional)

**Step 1:** Go to: https://www.emodnet-seabedhabitats.eu/

**Step 2:** Click **"EUSeaMap"** (Broad-scale habitat map)

**Step 3:** Download Mediterranean section

**Step 4:** Save as:
```bash
data/emodnet/seabed_habitats.geojson
```

---

### Dataset 9: Bathymetry (Optional but Useful)

**Step 1:** Go to: https://portal.emodnet-bathymetry.eu/

**Step 2:** Click **"Download DTM"**

**Step 3:** Select area by drawing a box:
- Use coordinates: -6° to 37°E, 30° to 46°N

**Step 4:** Select:
- Resolution: `1/8 arc minute` (~250m) or `1/16` for higher detail
- Format: `NetCDF` (preferred) or `GeoTIFF`

**Step 5:** Click **"Request DTM"**

**Step 6:** Wait for email with download link (5-30 minutes)

**Step 7:** Download and save as:
```bash
data/emodnet/bathymetry.nc
```

**Alternative - GEBCO:**
- Visit: https://download.gebco.net/
- Download global grid
- Extract Mediterranean subset later

---

## 📊 PART 3: FAO FISHERIES DATA (Optional)

### Dataset 10: Fish Catch Statistics

**Step 1:** Go to: https://www.fao.org/fishery/statistics-query/en/capture/capture_quantity

**Step 2:** Configure query:
- **Area**: Select `Mediterranean and Black Sea` (Area 37)
- **Years**: `2014-2023` (last 10 years)
- **Species**: Select `All commercial species` or major ones like:
  - European anchovy
  - Sardine
  - Red mullet
  - European hake
  - Swordfish
- **Countries**: Select Mediterranean countries or `All`

**Step 3:** Click **"Submit Query"**

**Step 4:** Click **"Download"** → Select `CSV` format

**Step 5:** Save as:
```bash
data/emodnet/fao_fisheries_stats.csv
```

---

## 🔍 VERIFICATION: Check Your Downloads

After downloading, run this script to verify:

```python
# Save as: verify_downloads.py
from pathlib import Path
import xarray as xr
import geopandas as gpd
import pandas as pd

def verify_data():
    print("="*60)
    print("VERIFYING DOWNLOADED DATA")
    print("="*60)
    
    # Check Copernicus NetCDF files
    copernicus_files = {
        'SST': 'data/copernicus/med_sst.nc',
        'Currents': 'data/copernicus/med_currents.nc',
        'Chlorophyll': 'data/copernicus/med_chlorophyll.nc',
        'Salinity': 'data/copernicus/med_salinity.nc',
    }
    
    print("\n### COPERNICUS DATA ###\n")
    for name, filepath in copernicus_files.items():
        path = Path(filepath)
        if path.exists():
            try:
                ds = xr.open_dataset(path)
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"✓ {name:15s} - {size_mb:8.2f} MB")
                print(f"  Variables: {list(ds.data_vars.keys())}")
                print(f"  Dimensions: {dict(ds.dims)}")
                print()
            except Exception as e:
                print(f"✗ {name:15s} - Error: {e}")
        else:
            print(f"✗ {name:15s} - FILE NOT FOUND")
    
    # Check EMODnet files
    emodnet_files = {
        'Fishing': 'data/emodnet/fishing_intensity.geojson',
        'MPAs': 'data/emodnet/mpa_boundaries.geojson',
    }
    
    print("\n### EMODNET DATA ###\n")
    for name, filepath in emodnet_files.items():
        path = Path(filepath)
        if path.exists():
            try:
                gdf = gpd.read_file(path)
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"✓ {name:15s} - {size_mb:8.2f} MB")
                print(f"  Features: {len(gdf)}")
                print(f"  Columns: {list(gdf.columns)}")
                print()
            except Exception as e:
                print(f"✗ {name:15s} - Error: {e}")
        else:
            print(f"✗ {name:15s} - FILE NOT FOUND")
    
    print("="*60)
    print("Verification complete!")

if __name__ == "__main__":
    verify_data()
```

Run it:
```bash
python verify_downloads.py
```

---

## 📝 DATA SPECIFICATIONS SUMMARY

### Spatial Coverage (All Datasets)
- **North**: 46.0°N
- **South**: 30.0°N  
- **West**: -6.0°E (Gibraltar)
- **East**: 37.0°E (Levantine Basin)

### Temporal Coverage
- **Start**: 2024-01-01 (or 2023-01-01 for more data)
- **End**: 2024-10-18 (today, or latest available)
- **Recommended**: At least 1 year of data

### File Formats
- **Oceanographic data**: NetCDF (.nc)
- **Geographic data**: GeoJSON (.geojson) or Shapefile (.shp)
- **Tabular data**: CSV (.csv)

### Expected File Sizes
- **SST**: 500 MB - 2 GB (depends on resolution and time period)
- **Currents**: 1 GB - 3 GB
- **Chlorophyll**: 300 MB - 1 GB
- **Salinity**: 500 MB - 2 GB
- **Fishing**: 5-50 MB
- **MPAs**: 1-10 MB

---

## 💡 TIPS FOR REDUCING FILE SIZE

### Option 1: Reduce Temporal Resolution
Instead of daily data, select:
- **Weekly**: Every 7 days
- **Monthly**: Monthly averages

In Copernicus interface:
- Look for "Temporal Resolution" option
- Select "Weekly" or "Monthly mean"

### Option 2: Reduce Spatial Resolution
- Select "Low Resolution" option if available
- Or choose `0.25°` instead of `0.04°`

### Option 3: Shorter Time Period
- Download only 3-6 months instead of 1 year
- Example: `2024-04-01` to `2024-10-18`

### Option 4: Subset After Download

If files are too large, subset them:

```python
import xarray as xr

# Open large file
ds = xr.open_dataset('large_file.nc')

# Subset to smaller area or time
ds_small = ds.sel(
    time=slice('2024-07-01', '2024-10-18'),  # Last 3 months
    lat=slice(35, 45),  # Smaller region
    lon=slice(0, 30)
)

# Save smaller file
ds_small.to_netcdf('smaller_file.nc')
```

---

## 🆘 TROUBLESHOOTING

### Problem: "Dataset not found"
**Solution**: Dataset IDs change. Use the search function instead:
1. Go to Copernicus Marine homepage
2. Use search: "Mediterranean temperature"
3. Browse available products

### Problem: Download too slow
**Solution**: 
1. Use smaller date range (3 months instead of 1 year)
2. Select lower resolution
3. Download during off-peak hours (evening/night in Europe)

### Problem: File format not supported
**Solution**: Convert using Python:
```python
# Shapefile to GeoJSON
import geopandas as gpd
gdf = gpd.read_file('file.shp')
gdf.to_file('file.geojson', driver='GeoJSON')

# GeoTIFF to NetCDF
import rioxarray as rxr
data = rxr.open_rasterio('file.tif')
data.to_netcdf('file.nc')
```

### Problem: "Access denied" or "Login failed"
**Solution**:
1. Verify your email is confirmed
2. Check you're logged in
3. Some datasets require additional access request
4. Wait 24 hours after registration

### Problem: Processing takes forever
**Solution**:
1. The system queues requests
2. Check your email for download link
3. Usually takes 10-60 minutes
4. Can be up to 24 hours for large requests

---

## ✅ FINAL CHECKLIST

After manual download, you should have:

```
data/
├── copernicus/
│   ├── med_sst.nc              ✓
│   ├── med_currents.nc         ✓
│   ├── med_chlorophyll.nc      ✓
│   ├── med_salinity.nc         ✓ (optional)
│   └── med_ssh.nc              ✓ (optional)
├── emodnet/
│   ├── fishing_intensity.geojson   ✓
│   ├── mpa_boundaries.geojson      ✓
│   ├── seabed_habitats.geojson     ✓ (optional)
│   ├── bathymetry.nc               ✓ (optional)
│   └── fao_fisheries_stats.csv     ✓ (optional)
└── processed/
    └── (empty for now)
```

---

## 🚀 NEXT STEPS

Once you have the data downloaded:

1. **Verify data**:
```bash
python verify_downloads.py
```

2. **Process data**:
```bash
python process_data.py
```

3. **Train models**:
```bash
python train_models.py
```

4. **Launch dashboard**:
```bash
streamlit run dashboard_app.py
```

---

## 📞 NEED HELP?

**Copernicus Marine Support:**
- Email: servicedesk.cmems@mercator-ocean.eu
- Documentation: https://help.marine.copernicus.eu/

**EMODnet Support:**
- Contact form: https://www.emodnet.eu/en/contact
- Technical support: secretariat@emodnet.eu

**Good luck with your hackathon! 🐟🌊**