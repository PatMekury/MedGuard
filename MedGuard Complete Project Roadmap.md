# MedGuard: Real-Time Overfishing Risk Monitor for the Mediterranean
## Complete EDITO Model Lab Hackathon Project Guide

---

## 📋 PROJECT OVERVIEW

**Project Name:** MedGuard  
**Focus:** SDG Target 14.4 - End Overfishing & Restore Fish Stocks  
**Platform:** EDITO Model Lab (https://datalab.dive.edito.eu/)  
**Timeline:** Hackathon Duration  

### Project Objectives
1. Monitor overfishing risk zones in the Mediterranean Sea
2. Forecast juvenile catch events using predictive models
3. Simulate policy interventions (Marine Protected Area expansions)
4. Visualize biodiversity loss and high-risk fishing zones
5. Provide actionable insights for sustainable fisheries management

---

## 🎯 PHASE 1: PLATFORM SETUP (Day 1, Hours 1-3)

### Step 1.1: Access EDITO Platform
1. Navigate to https://datalab.dive.edito.eu/
2. Sign in with your credentials
3. Verify your account access

### Step 1.2: Configure Git Integration
Execute these commands in your terminal:

```bash
# Set Git username
git config --global user.name "patmekury"

# Set Git email
git config --global user.email "patrickobumselu@gmail.com"

# Verify configuration
git config --list
```

### Step 1.3: GitLab Access
1. Access https://gitlab.mercator-ocean.fr/
2. Your GitLab is for:
   - Version control of your application code
   - Publishing Docker images
   - Hosting Helm charts for deployment
3. Create a new repository named `medguard-app`

### Step 1.4: Understand EDITO Storage
Your MinIO (S3-compatible) storage credentials (expires in 24 hours):
- **Access Key ID:** Available as `$AWS_ACCESS_KEY_ID`
- **Secret Access Key:** Available as `$AWS_SECRET_ACCESS_KEY`
- **S3 Endpoint:** minio.dive.edito.eu
- **Region:** waw3-1

---

## 📊 PHASE 2: DATA ACQUISITION (Day 1, Hours 4-8)

### Step 2.1: Identify Required Datasets

#### A. Copernicus Marine Data
Access via Copernicus Marine Client

**Essential Datasets:**

1. **Sea Surface Temperature (SST)**
   - Product ID: `MEDSEA_ANALYSISFORECAST_PHY_006_013`
   - Variables: `thetao` (potential temperature)
   - Resolution: 1/24° (~4km)
   - Purpose: Habitat conditions for fish species

2. **Ocean Currents & Circulation**
   - Product ID: `MEDSEA_ANALYSISFORECAST_PHY_006_013`
   - Variables: `uo` (eastward velocity), `vo` (northward velocity)
   - Purpose: Larval dispersal patterns, migration routes

3. **Chlorophyll-a Concentration**
   - Product ID: `OCEANCOLOUR_MED_BGC_L4_MY_009_144`
   - Variables: `CHL` (chlorophyll concentration)
   - Purpose: Primary productivity, food availability

4. **Sea Surface Height**
   - Product ID: `MEDSEA_ANALYSISFORECAST_PHY_006_013`
   - Variables: `zos` (sea surface height)
   - Purpose: Oceanographic fronts, fishing hotspots

5. **Salinity**
   - Product ID: `MEDSEA_ANALYSISFORECAST_PHY_006_013`
   - Variables: `so` (salinity)
   - Purpose: Water mass characterization

#### B. EMODnet Data

1. **Fishing Intensity**
   - Portal: https://www.emodnet-humanactivities.eu/
   - Dataset: Commercial fishing effort and landings by gear type
   - Format: NetCDF/GeoTIFF
   - Purpose: Current fishing pressure zones

2. **Marine Protected Areas**
   - Portal: https://www.emodnet-seabedhabitats.eu/
   - Dataset: Existing MPA boundaries
   - Format: Shapefiles/GeoJSON
   - Purpose: Policy simulation baseline

3. **Bathymetry**
   - Product: EMODnet Digital Terrain Model (DTM)
   - Resolution: 1/8 arc minute
   - Purpose: Habitat mapping, depth zones

4. **Seabed Habitats**
   - Dataset: EUSeaMap broad-scale habitat types
   - Purpose: Biodiversity hotspot identification

5. **Fish Species Distribution**
   - Portal: EMODnet Biology
   - Dataset: Fish occurrence and abundance data
   - Purpose: Species vulnerability assessment

#### C. Additional Data Sources

1. **FAO Fisheries Statistics**
   - Mediterranean fish stock assessments
   - Catch data by species and country
   - Format: CSV/Excel

2. **GEBCO Bathymetry** (if needed)
   - Global Ocean & Terrain Models
   - Higher resolution bathymetry

---

### Step 2.2: Install Data Access Tools

Create a notebook in EDITO Datalab and run:

```python
# Install required packages
!pip install copernicus-marine-client
!pip install xarray netCDF4 h5netcdf
!pip install geopandas shapely
!pip install pandas numpy matplotlib seaborn
!pip install scikit-learn
!pip install folium plotly
```

---

### Step 2.3: Download Copernicus Data

**Create file: `01_download_copernicus_data.py`**

```python
import copernicusmarine as cm
import xarray as xr
from datetime import datetime, timedelta
import os

# Define spatial bounds for Mediterranean
MED_BOUNDS = {
    'lat_min': 30.0,
    'lat_max': 46.0,
    'lon_min': -6.0,
    'lon_max': 37.0
}

# Define time range (last 5 years for analysis)
end_date = datetime.now()
start_date = end_date - timedelta(days=5*365)

# Create output directory
os.makedirs('data/copernicus', exist_ok=True)

# 1. Download SST Data
print("Downloading Sea Surface Temperature...")
cm.subset(
    dataset_id="MEDSEA_ANALYSISFORECAST_PHY_006_013",
    variables=["thetao"],
    minimum_longitude=MED_BOUNDS['lon_min'],
    maximum_longitude=MED_BOUNDS['lon_max'],
    minimum_latitude=MED_BOUNDS['lat_min'],
    maximum_latitude=MED_BOUNDS['lat_max'],
    start_datetime=start_date.strftime('%Y-%m-%d'),
    end_datetime=end_date.strftime('%Y-%m-%d'),
    minimum_depth=0,
    maximum_depth=10,
    output_filename='data/copernicus/med_sst.nc'
)

# 2. Download Ocean Currents
print("Downloading Ocean Currents...")
cm.subset(
    dataset_id="MEDSEA_ANALYSISFORECAST_PHY_006_013",
    variables=["uo", "vo"],
    minimum_longitude=MED_BOUNDS['lon_min'],
    maximum_longitude=MED_BOUNDS['lon_max'],
    minimum_latitude=MED_BOUNDS['lat_min'],
    maximum_latitude=MED_BOUNDS['lat_max'],
    start_datetime=start_date.strftime('%Y-%m-%d'),
    end_datetime=end_date.strftime('%Y-%m-%d'),
    minimum_depth=0,
    maximum_depth=50,
    output_filename='data/copernicus/med_currents.nc'
)

# 3. Download Chlorophyll Data
print("Downloading Chlorophyll-a...")
cm.subset(
    dataset_id="OCEANCOLOUR_MED_BGC_L4_MY_009_144",
    variables=["CHL"],
    minimum_longitude=MED_BOUNDS['lon_min'],
    maximum_longitude=MED_BOUNDS['lon_max'],
    minimum_latitude=MED_BOUNDS['lat_min'],
    maximum_latitude=MED_BOUNDS['lat_max'],
    start_datetime=start_date.strftime('%Y-%m-%d'),
    end_datetime=end_date.strftime('%Y-%m-%d'),
    output_filename='data/copernicus/med_chlorophyll.nc'
)

print("Data download complete!")
```

---

### Step 2.4: Download EMODnet Data

**Create file: `02_download_emodnet_data.py`**

```python
import geopandas as gpd
import requests
import os

os.makedirs('data/emodnet', exist_ok=True)

# EMODnet WFS endpoints
EMODNET_WFS_BASE = "https://ows.emodnet-humanactivities.eu/wfs"

def download_emodnet_wfs(typename, output_file):
    """Download data from EMODnet WFS service"""
    params = {
        'service': 'WFS',
        'version': '2.0.0',
        'request': 'GetFeature',
        'typename': typename,
        'outputFormat': 'application/json',
        'bbox': '-6,30,37,46,EPSG:4326'
    }
    
    response = requests.get(EMODNET_WFS_BASE, params=params)
    
    if response.status_code == 200:
        with open(output_file, 'w') as f:
            f.write(response.text)
        print(f"Downloaded {typename} to {output_file}")
    else:
        print(f"Failed to download {typename}: {response.status_code}")

# Download fishing intensity data
download_emodnet_wfs(
    'emodnet:fishing_intensity',
    'data/emodnet/fishing_intensity.geojson'
)

# Download MPA boundaries
download_emodnet_wfs(
    'emodnet:mpa',
    'data/emodnet/mpa_boundaries.geojson'
)

# For bathymetry, use direct download
print("For bathymetry, visit:")
print("https://portal.emodnet-bathymetry.eu/")
print("Download DTM for Mediterranean region")
```

---

## 🔬 PHASE 3: DATA PROCESSING & ANALYSIS (Day 2)

### Step 3.1: Create Data Processing Pipeline

**Create file: `03_process_data.py`**

```python
import xarray as xr
import pandas as pd
import numpy as np
import geopandas as gpd
from scipy import stats
from sklearn.preprocessing import StandardScaler

class MedGuardDataProcessor:
    def __init__(self):
        self.data = {}
        self.processed_data = {}
        
    def load_copernicus_data(self):
        """Load all Copernicus datasets"""
        print("Loading Copernicus data...")
        self.data['sst'] = xr.open_dataset('data/copernicus/med_sst.nc')
        self.data['currents'] = xr.open_dataset('data/copernicus/med_currents.nc')
        self.data['chlorophyll'] = xr.open_dataset('data/copernicus/med_chlorophyll.nc')
        print("Copernicus data loaded successfully")
        
    def load_emodnet_data(self):
        """Load EMODnet datasets"""
        print("Loading EMODnet data...")
        self.data['fishing'] = gpd.read_file('data/emodnet/fishing_intensity.geojson')
        self.data['mpa'] = gpd.read_file('data/emodnet/mpa_boundaries.geojson')
        print("EMODnet data loaded successfully")
        
    def calculate_overfishing_risk(self):
        """Calculate overfishing risk index"""
        print("Calculating overfishing risk index...")
        
        # Extract recent SST anomalies
        sst_mean = self.data['sst']['thetao'].mean(dim='time')
        sst_std = self.data['sst']['thetao'].std(dim='time')
        sst_anomaly = (self.data['sst']['thetao'].isel(time=-1) - sst_mean) / sst_std
        
        # Calculate chlorophyll trends (productivity indicator)
        chl_trend = self.data['chlorophyll']['CHL'].polyfit(dim='time', deg=1)
        
        # Combine with fishing intensity
        # Risk = f(fishing_intensity, SST_anomaly, productivity_decline)
        
        self.processed_data['risk_index'] = {
            'sst_anomaly': sst_anomaly,
            'chl_trend': chl_trend
        }
        
    def identify_high_risk_zones(self, threshold=0.7):
        """Identify geographical zones with high overfishing risk"""
        # Implement spatial clustering of high-risk areas
        pass
        
    def forecast_juvenile_catch(self, forecast_days=30):
        """Forecast juvenile catch events based on oceanographic conditions"""
        # Use SST, currents, and chlorophyll to predict spawning zones
        pass
        
    def simulate_mpa_expansion(self, expansion_scenarios):
        """Simulate impact of MPA expansions"""
        # Model fish stock recovery under different protection scenarios
        pass
        
    def export_processed_data(self):
        """Export processed data to S3"""
        print("Exporting processed data...")
        # Save to EDITO S3 storage
        pass

# Run pipeline
processor = MedGuardDataProcessor()
processor.load_copernicus_data()
processor.load_emodnet_data()
processor.calculate_overfishing_risk()
processor.export_processed_data()
```

---

## 🤖 PHASE 4: PREDICTIVE MODEL DEVELOPMENT (Day 2-3)

### Step 4.1: Build Overfishing Risk Model

**Create file: `04_risk_model.py`**

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

class OverfishingRiskModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def prepare_features(self, data):
        """Prepare feature matrix for model training"""
        features = pd.DataFrame({
            'sst': data['sst_values'].flatten(),
            'sst_anomaly': data['sst_anomaly'].flatten(),
            'chlorophyll': data['chl_values'].flatten(),
            'current_speed': np.sqrt(data['u']**2 + data['v']**2).flatten(),
            'fishing_intensity': data['fishing_intensity'].flatten(),
            'distance_to_mpa': data['dist_to_mpa'].flatten(),
            'bathymetry': data['depth'].flatten()
        })
        return features
        
    def train(self, X_train, y_train):
        """Train the risk prediction model"""
        self.model.fit(X_train, y_train)
        
    def predict_risk(self, X):
        """Predict overfishing risk"""
        return self.model.predict_proba(X)[:, 1]
        
    def save_model(self, path='models/overfishing_risk_model.pkl'):
        """Save trained model"""
        joblib.dump(self.model, path)
```

---

## 🖥️ PHASE 5: APPLICATION DEVELOPMENT (Day 3-4)

### Step 5.1: Create Jupyter Notebook Service

**Create file: `05_medguard_dashboard.ipynb`**

```python
# MedGuard Interactive Dashboard
import panel as pn
import holoviews as hv
from holoviews import opts
import geoviews as gv
import cartopy.crs as ccrs

pn.extension()
hv.extension('bokeh')

class MedGuardDashboard:
    def __init__(self):
        self.title = "MedGuard: Mediterranean Overfishing Risk Monitor"
        
    def create_risk_map(self):
        """Create interactive risk visualization map"""
        # Load risk data
        # Create choropleth map with risk zones
        pass
        
    def create_forecast_plot(self):
        """Create juvenile catch forecast visualization"""
        pass
        
    def create_mpa_simulator(self):
        """Create MPA expansion simulation interface"""
        pass
        
    def build_dashboard(self):
        """Assemble complete dashboard"""
        template = pn.template.FastListTemplate(
            title=self.title,
            sidebar=[],
            main=[
                pn.Row(
                    pn.pane.Markdown("## Current Risk Assessment"),
                    self.create_risk_map()
                ),
                pn.Row(
                    pn.pane.Markdown("## Juvenile Catch Forecast"),
                    self.create_forecast_plot()
                ),
                pn.Row(
                    pn.pane.Markdown("## MPA Policy Simulator"),
                    self.create_mpa_simulator()
                )
            ]
        )
        return template

# Launch dashboard
dashboard = MedGuardDashboard()
dashboard.build_dashboard().servable()
```

---

## 🐳 PHASE 6: CONTAINERIZATION (Day 4)

### Step 6.1: Create Dockerfile

**Create file: `Dockerfile`**

```dockerfile
# Start from EDITO-compatible Jupyter base image
FROM quay.io/jupyter/scipy-notebook:python-3.12

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Switch to jovyan user
USER jovyan

# Copy environment file
COPY env.yaml /tmp/env.yaml

# Create conda environment
RUN mamba env update -n base -f /tmp/env.yaml && \
    mamba clean -afy

# Install additional packages
RUN pip install --no-cache-dir \
    copernicus-marine-client \
    panel \
    holoviews \
    geoviews \
    cartopy \
    scikit-learn \
    xarray \
    geopandas

# Copy application files
COPY --chown=jovyan:users notebooks/ /home/jovyan/work/
COPY --chown=jovyan:users scripts/ /home/jovyan/scripts/
COPY --chown=jovyan:users README.md /home/jovyan/

# Set working directory
WORKDIR /home/jovyan/work

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
```

### Step 6.2: Create Environment File

**Create file: `env.yaml`**

```yaml
name: medguard
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.12
  - numpy
  - pandas
  - xarray
  - netcdf4
  - geopandas
  - matplotlib
  - seaborn
  - scikit-learn
  - jupyterlab
  - panel
  - holoviews
  - geoviews
  - cartopy
  - pip:
      - copernicus-marine-client
```

### Step 6.3: Build and Push Docker Image

```bash
# Build the Docker image
docker build -t <YOUR_DOCKERHUB_USERNAME>/medguard:1.0 .

# Login to Docker Hub
docker login

# Push the image
docker push <YOUR_DOCKERHUB_USERNAME>/medguard:1.0
```

---

## ☸️ PHASE 7: EDITO DEPLOYMENT (Day 5)

### Step 7.1: Create Helm Chart

**File structure:**
```
medguard-helm/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    └── service.yaml
```

**Create file: `medguard-helm/Chart.yaml`**

```yaml
apiVersion: v2
name: medguard
description: MedGuard Overfishing Risk Monitor
type: application
version: 1.0.0
appVersion: "1.0"
```

**Create file: `medguard-helm/values.yaml`**

```yaml
image:
  repository: <YOUR_DOCKERHUB_USERNAME>/medguard
  tag: "1.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8888

resources:
  requests:
    memory: "4Gi"
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"

persistence:
  enabled: true
  size: 10Gi

s3:
  enabled: true
  endpoint: minio.dive.edito.eu
  region: waw3-1
```

### Step 7.2: Publish to EDITO GitLab

```bash
# Clone your GitLab repository
git clone https://gitlab.mercator-ocean.fr/<your-username>/medguard-app.git
cd medguard-app

# Add all files
git add .
git commit -m "Initial MedGuard application"
git push origin main
```

---

## 📊 PHASE 8: DATA VISUALIZATION & PUBLISHING (Day 5)

### Step 8.1: Create STAC Metadata

**Create file: `stac_metadata.json`**

```json
{
  "stac_version": "1.0.0",
  "type": "Collection",
  "id": "medguard-overfishing-risk",
  "title": "MedGuard Overfishing Risk Assessment",
  "description": "Real-time overfishing risk indices for the Mediterranean Sea",
  "license": "CC-BY-4.0",
  "extent": {
    "spatial": {
      "bbox": [[-6.0, 30.0, 37.0, 46.0]]
    },
    "temporal": {
      "interval": [["2024-01-01T00:00:00Z", null]]
    }
  },
  "providers": [
    {
      "name": "MedGuard Team",
      "roles": ["producer", "processor"]
    }
  ]
}
```

### Step 8.2: Publish Results to EDITO Catalog

**Create file: `06_publish_to_catalog.py`**

```python
import requests
import json

# EDITO Catalog API
CATALOG_API = "https://api.dive.edito.eu/data"

def publish_to_catalog(collection_id, data_path, metadata):
    """Publish processed data to EDITO catalog"""
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {YOUR_TOKEN}'
    }
    
    # Create collection
    collection_endpoint = f"{CATALOG_API}/collections/{collection_id}"
    response = requests.post(collection_endpoint, json=metadata, headers=headers)
    
    if response.status_code == 201:
        print(f"Collection {collection_id} created successfully")
    else:
        print(f"Error creating collection: {response.text}")
        
    # Upload data items
    # Implementation depends on data format

# Publish MedGuard results
with open('stac_metadata.json') as f:
    metadata = json.load(f)
    
publish_to_catalog('medguard-overfishing-risk', 'output/', metadata)
```

---

## 🎨 PHASE 9: WEB INTERFACE DEVELOPMENT (Day 6)

### Step 9.1: Create Interactive Web Application

**Create file: `app.py`**

```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd

st.set_page_config(page_title="MedGuard", layout="wide", page_icon="🐟")

st.title("🐟 MedGuard: Mediterranean Overfishing Risk Monitor")
st.markdown("**Monitoring SDG 14.4 - Sustainable Fisheries Management**")

# Sidebar controls
st.sidebar.header("Controls")
date_range = st.sidebar.date_input("Select Date Range", [])
risk_threshold = st.sidebar.slider("Risk Threshold", 0.0, 1.0, 0.7)
show_mpa = st.sidebar.checkbox("Show Marine Protected Areas", True)

# Main dashboard layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Current Risk Assessment")
    # Load and display risk map
    # fig = create_risk_map()
    # st.plotly_chart(fig, use_container_width=True)
    
with col2:
    st.subheader("📈 Risk Trends Over Time")
    # Load and display trend chart
    # fig = create_trend_chart()
    # st.plotly_chart(fig, use_container_width=True)

# Juvenile catch forecast
st.subheader("🐠 Juvenile Catch Forecast (Next 30 Days)")
# Display forecast visualization

# MPA Policy Simulator
st.subheader("🏛️ MPA Expansion Simulator")
expansion_percentage = st.slider("MPA Expansion (%)", 0, 100, 25)
# Run simulation and display results
```

---

## 🚀 PHASE 10: TESTING & DEPLOYMENT (Day 7)

### Step 10.1: Test Locally

```bash
# Run Docker container locally
docker run -p 8888:8888 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_S3_ENDPOINT=$AWS_S3_ENDPOINT \
  <YOUR_DOCKERHUB_USERNAME>/medguard:1.0
```

### Step 10.2: Deploy to EDITO

1. Go to https://datalab.dive.edito.eu/
2. Navigate to "My Services"
3. Click "New Service"
4. Configure:
   - Name: MedGuard
   - Docker Image: `<YOUR_DOCKERHUB_USERNAME>/medguard:1.0`
   - Resources: 4GB RAM, 2 CPU
   - Enable S3 access
5. Click "Launch"

### Step 10.3: Create Tutorial Entry

Create a tutorial page on EDITO platform explaining:
- Project objectives
- How to use the dashboard
- Data sources
- Interpretation of results

---

## 📝 DELIVERABLES CHECKLIST

- [ ] Data downloaded from Copernicus Marine
- [ ] Data downloaded from EMODnet
- [ ] Data processing pipeline implemented
- [ ] Overfishing risk model trained
- [ ] Juvenile catch forecasting model developed
- [ ] MPA simulation tool created
- [ ] Interactive dashboard built
- [ ] Docker image created and pushed
- [ ] Application deployed on EDITO
- [ ] Results published to EDITO catalog
- [ ] Documentation and tutorial created
- [ ] Presentation prepared for jury

---

## 🎯 KEY SUCCESS METRICS FOR HACKATHON

1. **Data Integration**: Successfully combined Copernicus + EMODnet data
2. **Model Accuracy**: Risk prediction model performance
3. **Visualization Quality**: Clear, actionable dashboards
4. **EDITO Integration**: Proper use of platform features
5. **SDG 14.4 Alignment**: Clear connection to sustainable fisheries
6. **Innovation**: Novel approach to overfishing monitoring
7. **Scalability**: Can be extended to other regions

---

## 🆘 TROUBLESHOOTING

### Data Download Issues
- Check Copernicus Marine credentials
- Verify spatial bounds are correct
- Ensure sufficient disk space

### Docker Build Failures
- Check Dockerfile syntax
- Verify base image availability
- Check internet connection

### EDITO Deployment Issues
- Verify GitLab repository access
- Check Helm chart syntax
- Verify S3 credentials

---

## 📚 USEFUL RESOURCES

- **EDITO Documentation**: https://docs.lab.dive.edito.eu/
- **Copernicus Marine**: https://data.marine.copernicus.eu/
- **EMODnet Portal**: https://www.emodnet.eu/
- **SDG 14 Information**: https://sdgs.un.org/goals/goal14
- **GitLab Support**: Contact EDITO infrastructure team

---

## 👥 NEXT STEPS AFTER HACKATHON

1. Refine models with more historical data
2. Add real-time alerting system
3. Integrate with fishing fleet tracking systems
4. Expand to other Mediterranean species
5. Collaborate with fisheries management authorities
6. Publish research findings

---

**Good luck with your hackathon! 🚀🐟**