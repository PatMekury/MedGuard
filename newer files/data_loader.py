#!/usr/bin/env python3
"""
MedGuard 2.0 - Advanced Data Loader
Loads your manually downloaded data with proper error handling and validation
"""

import xarray as xr
import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

class MedGuardDataLoader:
    """Load and validate all MedGuard datasets"""
    
    def __init__(self, base_dir='Data'):
        self.base_dir = Path(base_dir)
        self.data = {}
        self.metadata = {
            'load_time': datetime.now().isoformat(),
            'datasets_loaded': [],
            'data_quality_checks': {}
        }
        
    def load_sst_data(self):
        """Load Sea Surface Temperature data (2023-2024)"""
        print("\n" + "="*60)
        print("LOADING SEA SURFACE TEMPERATURE DATA")
        print("="*60)
        
        # Try multiple possible directory structures
        possible_locations = [
            self.base_dir / 'Sea Temperature',
            self.base_dir,
            Path('.')
        ]
        
        files_to_find = {
            '2023': 'med_sst2023.nc',
            '2024': 'med_sst2024.nc'
        }
        
        datasets = []
        for year, filename in files_to_find.items():
            found = False
            for location in possible_locations:
                filepath = location / filename
                if filepath.exists():
                    try:
                        ds = xr.open_dataset(filepath, chunks={'time': 10})
                        datasets.append(ds)
                        print(f"✓ Loaded SST {year}: {filepath}")
                        print(f"  Shape: {dict(ds.dims)}")
                        print(f"  Variables: {list(ds.data_vars)}")
                        
                        # Check coordinate names
                        coord_names = list(ds.coords.keys())
                        print(f"  Coordinates: {coord_names}")
                        found = True
                        break
                    except Exception as e:
                        print(f"✗ Error loading {filepath.name}: {e}")
                        continue
            
            if not found:
                print(f"⚠ Missing {filename} in any known location")
        
        if datasets:
            # Combine both years
            self.data['sst'] = xr.concat(datasets, dim='time')
            self.metadata['datasets_loaded'].append('sst')
            
            # Standardize coordinate names (latitude/lat, longitude/lon)
            if 'latitude' in self.data['sst'].dims:
                self.data['sst'] = self.data['sst'].rename({'latitude': 'lat', 'longitude': 'lon'})
            
            # Quality checks
            sst_var = list(self.data['sst'].data_vars)[0]
            lat_coord = 'lat'
            lon_coord = 'lon'
            
            self.metadata['data_quality_checks']['sst'] = {
                'time_range': [
                    str(self.data['sst'].time.min().values),
                    str(self.data['sst'].time.max().values)
                ],
                'spatial_coverage': {
                    'lat_range': [float(self.data['sst'][lat_coord].min()), 
                                 float(self.data['sst'][lat_coord].max())],
                    'lon_range': [float(self.data['sst'][lon_coord].min()), 
                                 float(self.data['sst'][lon_coord].max())]
                },
                'missing_data_pct': float((self.data['sst'][sst_var].isnull().sum() / 
                                          self.data['sst'][sst_var].size * 100).values)
            }
            print(f"\n  Quality Check:")
            print(f"    Time span: {self.metadata['data_quality_checks']['sst']['time_range']}")
            print(f"    Spatial extent: lat [{self.metadata['data_quality_checks']['sst']['spatial_coverage']['lat_range'][0]:.2f}, {self.metadata['data_quality_checks']['sst']['spatial_coverage']['lat_range'][1]:.2f}], lon [{self.metadata['data_quality_checks']['sst']['spatial_coverage']['lon_range'][0]:.2f}, {self.metadata['data_quality_checks']['sst']['spatial_coverage']['lon_range'][1]:.2f}]")
            print(f"    Missing data: {self.metadata['data_quality_checks']['sst']['missing_data_pct']:.2f}%")
    
    def load_current_data(self):
        """Load ocean current data (u, v components)"""
        print("\n" + "="*60)
        print("LOADING OCEAN CURRENT DATA")
        print("="*60)
        
        # Try multiple possible locations
        possible_locations = [
            self.base_dir / 'Sea Current',
            self.base_dir,
            Path('.')
        ]
        
        files_to_find = {
            '2023': 'med_currents2023.nc',
            '2024': 'med_currents2024.nc'
        }
        
        datasets = []
        for year, filename in files_to_find.items():
            for location in possible_locations:
                filepath = location / filename
                if filepath.exists():
                    try:
                        ds = xr.open_dataset(filepath, chunks={'time': 10, 'depth': 5})
                        # Standardize coordinate names
                        if 'latitude' in ds.dims:
                            ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})
                        datasets.append(ds)
                        print(f"✓ Loaded Currents {year}: {filepath}")
                        print(f"  Shape: {dict(ds.dims)}")
                        break
                    except Exception as e:
                        continue
        
        if datasets:
            self.data['currents'] = xr.concat(datasets, dim='time')
            self.metadata['datasets_loaded'].append('currents')
            print(f"  ✓ Combined {len(datasets)} years of current data")
    
    def load_salinity_data(self):
        """Load salinity data"""
        print("\n" + "="*60)
        print("LOADING SALINITY DATA")
        print("="*60)
        
        possible_locations = [
            self.base_dir / 'Sea Current',
            self.base_dir,
            Path('.')
        ]
        
        files_to_find = {
            '2023': 'med_salinity2023.nc',
            '2024': 'med_salinity2024.nc'
        }
        
        datasets = []
        for year, filename in files_to_find.items():
            for location in possible_locations:
                filepath = location / filename
                if filepath.exists():
                    try:
                        ds = xr.open_dataset(filepath, chunks={'time': 10})
                        if 'latitude' in ds.dims:
                            ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})
                        datasets.append(ds)
                        print(f"✓ Loaded Salinity {year}: {filepath}")
                        break
                    except Exception as e:
                        continue
        
        if datasets:
            self.data['salinity'] = xr.concat(datasets, dim='time')
            self.metadata['datasets_loaded'].append('salinity')
    
    def load_chlorophyll_data(self):
        """Load chlorophyll-a concentration data"""
        print("\n" + "="*60)
        print("LOADING CHLOROPHYLL-A DATA")
        print("="*60)
        
        possible_locations = [
            self.base_dir / 'Sea Current',
            self.base_dir,
            Path('.')
        ]
        
        files_to_find = {
            '2023': 'med_chlorophyll2023.nc',
            '2024': 'med_chlorophyll2024.nc'
        }
        
        datasets = []
        for year, filename in files_to_find.items():
            for location in possible_locations:
                filepath = location / filename
                if filepath.exists():
                    try:
                        ds = xr.open_dataset(filepath, chunks={'time': 10})
                        if 'latitude' in ds.dims:
                            ds = ds.rename({'latitude': 'lat', 'longitude': 'lon'})
                        datasets.append(ds)
                        print(f"✓ Loaded Chlorophyll {year}: {filepath}")
                        break
                    except Exception as e:
                        continue
        
        if datasets:
            self.data['chlorophyll'] = xr.concat(datasets, dim='time')
            self.metadata['datasets_loaded'].append('chlorophyll')
    
    def load_fishing_intensity(self):
        """Load AIS fishing intensity data"""
        print("\n" + "="*60)
        print("LOADING FISHING INTENSITY DATA")
        print("="*60)
        
        possible_locations = [
            self.base_dir / 'Fishing Intensity',
            self.base_dir,
            Path('.')
        ]
        
        files_to_find = {
            '2023': 'fishing_intensity2023.geojson',
            '2024': 'fishing_intensity2024.geojson'
        }
        
        gdfs = []
        for year, filename in files_to_find.items():
            for location in possible_locations:
                filepath = location / filename
                if filepath.exists():
                    try:
                        gdf = gpd.read_file(filepath)
                        gdf['year'] = year
                        gdfs.append(gdf)
                        print(f"✓ Loaded Fishing {year}: {filepath}")
                        print(f"  Records: {len(gdf)}")
                        if len(gdf) > 0:
                            print(f"  Columns: {list(gdf.columns[:5])}...")  # Show first 5 columns
                        break
                    except Exception as e:
                        continue
        
        if gdfs:
            self.data['fishing'] = pd.concat(gdfs, ignore_index=True)
            self.metadata['datasets_loaded'].append('fishing')
            print(f"  ✓ Total fishing records: {len(self.data['fishing'])}")
    
    def load_mpa_data(self):
        """Load Marine Protected Areas boundaries"""
        print("\n" + "="*60)
        print("LOADING MARINE PROTECTED AREAS DATA")
        print("="*60)
        
        possible_locations = [
            self.base_dir,
            Path('.')
        ]
        
        for location in possible_locations:
            mpa_file = location / 'mpa_boundaries.geojson'
            if mpa_file.exists():
                try:
                    self.data['mpa'] = gpd.read_file(mpa_file)
                    self.metadata['datasets_loaded'].append('mpa')
                    print(f"✓ Loaded MPA data: {mpa_file}")
                    print(f"  Number of MPAs: {len(self.data['mpa'])}")
                    if len(self.data['mpa']) > 0:
                        print(f"  Columns: {list(self.data['mpa'].columns[:5])}...")
                    
                    # Calculate total MPA area
                    try:
                        mpa_area_km2 = self.data['mpa'].to_crs(epsg=3857).area.sum() / 1e6
                        print(f"  Total MPA area: {mpa_area_km2:.0f} km²")
                    except:
                        print(f"  (Could not calculate area)")
                    return
                except Exception as e:
                    print(f"✗ Error loading {mpa_file.name}: {e}")
                    continue
        
        print(f"⚠ MPA data not found in any location")
    
    def load_fao_statistics(self):
        """Load FAO fisheries catch statistics"""
        print("\n" + "="*60)
        print("LOADING FAO FISHERIES STATISTICS")
        print("="*60)
        
        possible_locations = [
            self.base_dir,
            Path('.')
        ]
        
        for location in possible_locations:
            fao_file = location / 'fao_fisheries_stats.csv'
            if fao_file.exists():
                try:
                    self.data['fao_stats'] = pd.read_csv(fao_file)
                    self.metadata['datasets_loaded'].append('fao_stats')
                    print(f"✓ Loaded FAO statistics: {fao_file}")
                    print(f"  Records: {len(self.data['fao_stats'])}")
                    print(f"  Columns: {list(self.data['fao_stats'].columns[:5])}...")
                    
                    # Try to identify year column
                    year_cols = [col for col in self.data['fao_stats'].columns if 'year' in col.lower() or 'period' in col.lower()]
                    if year_cols:
                        year_col = year_cols[0]
                        print(f"  Year range: {self.data['fao_stats'][year_col].min()} - {self.data['fao_stats'][year_col].max()}")
                    return
                except Exception as e:
                    print(f"✗ Error loading {fao_file.name}: {e}")
                    continue
        
        print(f"⚠ FAO statistics not found in any location")
    
    def validate_data_consistency(self):
        """Validate temporal and spatial consistency across datasets"""
        print("\n" + "="*60)
        print("VALIDATING DATA CONSISTENCY")
        print("="*60)
        
        validation_report = {}
        
        # Check temporal consistency
        temporal_datasets = ['sst', 'currents', 'salinity', 'chlorophyll']
        available_temporal = [ds for ds in temporal_datasets if ds in self.data]
        
        if len(available_temporal) > 1:
            time_ranges = {}
            for ds_name in available_temporal:
                ds = self.data[ds_name]
                time_ranges[ds_name] = {
                    'start': str(ds.time.min().values),
                    'end': str(ds.time.max().values),
                    'n_timesteps': len(ds.time)
                }
            
            validation_report['temporal_consistency'] = time_ranges
            print("  ✓ Temporal coverage:")
            for ds_name, times in time_ranges.items():
                print(f"    {ds_name}: {times['start']} to {times['end']} ({times['n_timesteps']} steps)")
        
        # Check spatial consistency
        if 'sst' in self.data and 'currents' in self.data:
            sst_grid = (self.data['sst'].lat.size, self.data['sst'].lon.size)
            curr_grid = (self.data['currents'].lat.size, self.data['currents'].lon.size)
            
            if sst_grid == curr_grid:
                print(f"  ✓ Spatial grids aligned: {sst_grid}")
                validation_report['spatial_alignment'] = True
            else:
                print(f"  ⚠ Grid mismatch: SST {sst_grid} vs Currents {curr_grid}")
                validation_report['spatial_alignment'] = False
        
        self.metadata['validation'] = validation_report
    
    def export_metadata(self, output_dir='processed'):
        """Export loading metadata"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        metadata_file = output_dir / 'data_load_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"\n✓ Metadata exported to {metadata_file}")
    
    def load_all(self):
        """Load all datasets"""
        print("\n" + "="*70)
        print(" "*20 + "MEDGUARD DATA LOADING")
        print("="*70)
        print(f"Start time: {datetime.now()}")
        
        self.load_sst_data()
        self.load_current_data()
        self.load_salinity_data()
        self.load_chlorophyll_data()
        self.load_fishing_intensity()
        self.load_mpa_data()
        self.load_fao_statistics()
        
        self.validate_data_consistency()
        self.export_metadata()
        
        print("\n" + "="*70)
        print(" "*25 + "LOADING COMPLETE")
        print("="*70)
        print(f"End time: {datetime.now()}")
        print(f"\nDatasets loaded: {', '.join(self.metadata['datasets_loaded'])}")
        
        return self.data


def main():
    """Main execution"""
    loader = MedGuardDataLoader(base_dir='Data')
    data = loader.load_all()
    return data


if __name__ == "__main__":
    data = main()