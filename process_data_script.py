#!/usr/bin/env python3
"""
MedGuard Data Processing Pipeline
Processes raw data from Copernicus and EMODnet into analysis-ready formats
"""

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from pathlib import Path
from datetime import datetime
from scipy import stats, ndimage
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class MedGuardProcessor:
    """Main data processing class for MedGuard project"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.copernicus_dir = self.data_dir / 'copernicus'
        self.emodnet_dir = self.data_dir / 'emodnet'
        self.processed_dir = self.data_dir / 'processed'
        self.processed_dir.mkdir(exist_ok=True)
        
        self.raw_data = {}
        self.processed_data = {}
        
    def load_copernicus_data(self):
        """Load all Copernicus Marine datasets"""
        print("\n" + "="*60)
        print("LOADING COPERNICUS MARINE DATA")
        print("="*60)
        
        datasets = {
            'sst': 'med_sst.nc',
            'currents': 'med_currents.nc',
            'chlorophyll': 'med_chlorophyll.nc',
            'salinity': 'med_salinity.nc',
            'ssh': 'med_ssh.nc'
        }
        
        for key, filename in datasets.items():
            filepath = self.copernicus_dir / filename
            if filepath.exists():
                try:
                    self.raw_data[key] = xr.open_dataset(filepath)
                    print(f"✓ Loaded {key}: {filepath.name}")
                except Exception as e:
                    print(f"✗ Error loading {key}: {e}")
            else:
                print(f"⚠ Missing {key}: {filepath.name}")
                
    def load_emodnet_data(self):
        """Load EMODnet datasets"""
        print("\n" + "="*60)
        print("LOADING EMODNET DATA")
        print("="*60)
        
        datasets = {
            'fishing': 'fishing_intensity.geojson',
            'mpa': 'mpa_boundaries.geojson',
            'habitats': 'seabed_habitats.geojson'
        }
        
        for key, filename in datasets.items():
            filepath = self.emodnet_dir / filename
            if filepath.exists():
                try:
                    self.raw_data[key] = gpd.read_file(filepath)
                    print(f"✓ Loaded {key}: {filepath.name}")
                except Exception as e:
                    print(f"✗ Error loading {key}: {e}")
            else:
                print(f"⚠ Missing {key}: {filepath.name}")
                
    def calculate_sst_anomaly(self):
        """Calculate sea surface temperature anomalies"""
        print("\n" + "="*60)
        print("CALCULATING SST ANOMALIES")
        print("="*60)
        
        if 'sst' not in self.raw_data:
            print("✗ SST data not available")
            return
            
        try:
            sst = self.raw_data['sst']['thetao']
            
            # Calculate climatology (long-term mean)
            sst_climatology = sst.groupby('time.month').mean('time')
            
            # Calculate anomaly
            sst_anomaly = sst.groupby('time.month') - sst_climatology
            
            # Calculate standardized anomaly
            sst_std = sst.groupby('time.month').std('time')
            sst_standardized = (sst.groupby('time.month') - sst_climatology) / sst_std
            
            self.processed_data['sst_anomaly'] = sst_anomaly
            self.processed_data['sst_standardized'] = sst_standardized
            self.processed_data['sst_climatology'] = sst_climatology
            
            print(f"✓ SST anomalies calculated")
            print(f"  Mean anomaly: {float(sst_anomaly.mean()):.3f}°C")
            print(f"  Max anomaly: {float(sst_anomaly.max()):.3f}°C")
            
        except Exception as e:
            print(f"✗ Error calculating SST anomaly: {e}")
            
    def calculate_current_speed(self):
        """Calculate current speed and direction"""
        print("\n" + "="*60)
        print("CALCULATING CURRENT SPEED")
        print("="*60)
        
        if 'currents' not in self.raw_data:
            print("✗ Current data not available")
            return
            
        try:
            u = self.raw_data['currents']['uo']
            v = self.raw_data['currents']['vo']
            
            # Calculate speed
            speed = np.sqrt(u**2 + v**2)
            
            # Calculate direction (oceanographic convention)
            direction = np.arctan2(v, u) * 180 / np.pi
            direction = (direction + 360) % 360
            
            self.processed_data['current_speed'] = speed
            self.processed_data['current_direction'] = direction
            
            print(f"✓ Current speed calculated")
            print(f"  Mean speed: {float(speed.mean()):.4f} m/s")
            print(f"  Max speed: {float(speed.max()):.4f} m/s")
            
        except Exception as e:
            print(f"✗ Error calculating current speed: {e}")
            
    def calculate_productivity_index(self):
        """Calculate ocean productivity index from chlorophyll"""
        print("\n" + "="*60)
        print("CALCULATING PRODUCTIVITY INDEX")
        print("="*60)
        
        if 'chlorophyll' not in self.raw_data:
            print("✗ Chlorophyll data not available")
            return
            
        try:
            chl = self.raw_data['chlorophyll']['CHL']
            
            # Calculate temporal trend
            time_numeric = (chl['time'] - chl['time'][0]) / np.timedelta64(1, 'D')
            
            # Fit linear trend for each pixel
            def calc_trend(data):
                if np.all(np.isnan(data)):
                    return np.nan
                mask = ~np.isnan(data)
                if mask.sum() < 10:  # Need at least 10 points
                    return np.nan
                slope, _, _, _, _ = stats.linregress(
                    time_numeric[mask], 
                    data[mask]
                )
                return slope
                
            # Apply trend calculation
            chl_trend = xr.apply_ufunc(
                calc_trend,
                chl,
                input_core_dims=[['time']],
                vectorize=True,
                dask='parallelized'
            )
            
            # Calculate productivity categories
            chl_mean = chl.mean('time')
            productivity = xr.where(chl_mean < 0.1, 'oligotrophic',
                          xr.where(chl_mean < 1.0, 'mesotrophic', 'eutrophic'))
            
            self.processed_data['chl_trend'] = chl_trend
            self.processed_data['chl_mean'] = chl_mean
            self.processed_data['productivity_class'] = productivity
            
            print(f"✓ Productivity index calculated")
            print(f"  Mean chlorophyll: {float(chl_mean.mean()):.4f} mg/m³")
            
        except Exception as e:
            print(f"✗ Error calculating productivity: {e}")
            
    def calculate_frontal_zones(self):
        """Identify oceanographic fronts (high gradients)"""
        print("\n" + "="*60)
        print("IDENTIFYING OCEANOGRAPHIC FRONTS")
        print("="*60)
        
        if 'sst' not in self.raw_data:
            print("✗ SST data not available for front detection")
            return
            
        try:
            # Use recent SST
            sst = self.raw_data['sst']['thetao'].isel(time=-1)
            
            # Calculate gradients
            grad_x = sst.differentiate('lon')
            grad_y = sst.differentiate('lat')
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Identify fronts (high gradient zones)
            front_threshold = gradient_magnitude.quantile(0.9)
            frontal_zones = gradient_magnitude > front_threshold
            
            self.processed_data['sst_gradient'] = gradient_magnitude
            self.processed_data['frontal_zones'] = frontal_zones
            
            print(f"✓ Frontal zones identified")
            print(f"  Frontal area: {float(frontal_zones.sum() / frontal_zones.size * 100):.2f}%")
            
        except Exception as e:
            print(f"✗ Error calculating fronts: {e}")
            
    def calculate_fishing_pressure(self):
        """Process fishing intensity data"""
        print("\n" + "="*60)
        print("PROCESSING FISHING PRESSURE DATA")
        print("="*60)
        
        if 'fishing' not in self.raw_data:
            print("✗ Fishing data not available")
            return
            
        try:
            fishing = self.raw_data['fishing']
            
            # Aggregate fishing effort by spatial grid
            # This depends on the structure of your fishing data
            
            # Create summary statistics
            if 'effort' in fishing.columns or 'intensity' in fishing.columns:
                effort_col = 'effort' if 'effort' in fishing.columns else 'intensity'
                
                fishing_summary = {
                    'total_effort': fishing[effort_col].sum(),
                    'mean_effort': fishing[effort_col].mean(),
                    'high_intensity_zones': len(fishing[fishing[effort_col] > fishing[effort_col].quantile(0.75)])
                }
                
                self.processed_data['fishing_summary'] = fishing_summary
                print(f"✓ Fishing pressure processed")
                print(f"  Total effort: {fishing_summary['total_effort']:.0f}")
                print(f"  High-intensity zones: {fishing_summary['high_intensity_zones']}")
            else:
                print("⚠ Fishing intensity column not found")
                
        except Exception as e:
            print(f"✗ Error processing fishing data: {e}")
            
    def calculate_mpa_coverage(self):
        """Calculate MPA coverage statistics"""
        print("\n" + "="*60)
        print("ANALYZING MARINE PROTECTED AREAS")
        print("="*60)
        
        if 'mpa' not in self.raw_data:
            print("✗ MPA data not available")
            return
            
        try:
            mpa = self.raw_data['mpa']
            
            # Calculate total MPA area
            mpa_area = mpa.to_crs(epsg=3857).area.sum() / 1e6  # Convert to km²
            
            # Mediterranean total area (approximate)
            med_total_area = 2.5e6  # km²
            
            mpa_coverage_pct = (mpa_area / med_total_area) * 100
            
            mpa_stats = {
                'total_mpa_area_km2': mpa_area,
                'coverage_percentage': mpa_coverage_pct,
                'number_of_mpas': len(mpa)
            }
            
            self.processed_data['mpa_stats'] = mpa_stats
            
            print(f"✓ MPA analysis complete")
            print(f"  Number of MPAs: {mpa_stats['number_of_mpas']}")
            print(f"  Total area: {mpa_area:.0f} km²")
            print(f"  Coverage: {mpa_coverage_pct:.2f}% of Mediterranean")
            
        except Exception as e:
            print(f"✗ Error analyzing MPAs: {e}")
            
    def calculate_overfishing_risk_index(self):
        """Calculate comprehensive overfishing risk index"""
        print("\n" + "="*60)
        print("CALCULATING OVERFISHING RISK INDEX")
        print("="*60)
        
        try:
            # Initialize risk components
            risk_components = {}
            
            # Component 1: SST Anomaly Risk
            if 'sst_standardized' in self.processed_data:
                # High positive or negative anomalies increase risk
                sst_risk = np.abs(self.processed_data['sst_standardized'].isel(time=-1))
                risk_components['sst'] = sst_risk
                print("  ✓ SST anomaly risk component")
            
            # Component 2: Productivity Decline Risk
            if 'chl_trend' in self.processed_data:
                # Negative trends (declining productivity) increase risk
                chl_risk = xr.where(
                    self.processed_data['chl_trend'] < 0,
                    -self.processed_data['chl_trend'],
                    0
                )
                risk_components['productivity'] = chl_risk
                print("  ✓ Productivity decline risk component")
            
            # Component 3: Frontal Zone Risk
            if 'frontal_zones' in self.processed_data:
                # Fronts are fishing hotspots - higher risk
                frontal_risk = self.processed_data['frontal_zones'].astype(float)
                risk_components['frontal'] = frontal_risk
                print("  ✓ Frontal zone risk component")
            
            # Combine risk components (weighted average)
            if risk_components:
                weights = {
                    'sst': 0.3,
                    'productivity': 0.4,
                    'frontal': 0.3
                }
                
                # Normalize each component to 0-1 range
                normalized_risks = {}
                for key, risk in risk_components.items():
                    risk_min = float(risk.min())
                    risk_max = float(risk.max())
                    if risk_max > risk_min:
                        normalized_risks[key] = (risk - risk_min) / (risk_max - risk_min)
                    else:
                        normalized_risks[key] = risk * 0
                
                # Calculate weighted sum
                risk_index = sum(
                    normalized_risks[key] * weights.get(key, 1.0)
                    for key in normalized_risks.keys()
                ) / sum(weights.get(key, 1.0) for key in normalized_risks.keys())
                
                # Classify risk levels
                risk_class = xr.where(risk_index < 0.3, 'low',
                             xr.where(risk_index < 0.6, 'medium', 'high'))
                
                self.processed_data['overfishing_risk_index'] = risk_index
                self.processed_data['overfishing_risk_class'] = risk_class
                
                print(f"\n✓ Overfishing risk index calculated")
                print(f"  Low risk area: {float((risk_index < 0.3).sum() / risk_index.size * 100):.1f}%")
                print(f"  Medium risk area: {float(((risk_index >= 0.3) & (risk_index < 0.6)).sum() / risk_index.size * 100):.1f}%")
                print(f"  High risk area: {float((risk_index >= 0.6).sum() / risk_index.size * 100):.1f}%")
            else:
                print("✗ Insufficient data for risk index calculation")
                
        except Exception as e:
            print(f"✗ Error calculating risk index: {e}")
            import traceback
            traceback.print_exc()
            
    def identify_juvenile_habitat_zones(self):
        """Identify potential juvenile fish habitats"""
        print("\n" + "="*60)
        print("IDENTIFYING JUVENILE HABITAT ZONES")
        print("="*60)
        
        try:
            # Juvenile fish prefer:
            # - Moderate temperatures (species-dependent, using 15-22°C as example)
            # - Productive waters (higher chlorophyll)
            # - Protected areas (low current speed)
            # - Shallow coastal zones
            
            habitat_score = None
            
            if 'sst' in self.raw_data:
                sst = self.raw_data['sst']['thetao'].isel(time=-1)
                # Optimal temperature range (15-22°C for many Mediterranean species)
                temp_score = 1 - np.abs((sst - 18.5) / 18.5)
                temp_score = xr.where((sst >= 15) & (sst <= 22), temp_score, 0)
                habitat_score = temp_score
                print("  ✓ Temperature suitability calculated")
            
            if 'chlorophyll' in self.raw_data and habitat_score is not None:
                chl = self.raw_data['chlorophyll']['CHL'].isel(time=-1)
                # Higher productivity better for juveniles
                chl_score = chl / chl.quantile(0.95)
                chl_score = xr.where(chl_score > 1, 1, chl_score)
                
                # Regrid to match SST if needed
                if chl_score.shape != habitat_score.shape:
                    chl_score = chl_score.interp_like(habitat_score)
                
                habitat_score = (habitat_score + chl_score) / 2
                print("  ✓ Productivity suitability calculated")
            
            if 'current_speed' in self.processed_data and habitat_score is not None:
                current = self.processed_data['current_speed'].isel(time=-1)
                # Lower current speeds preferred
                current_score = 1 - (current / current.quantile(0.95))
                current_score = xr.where(current_score < 0, 0, current_score)
                
                if current_score.shape != habitat_score.shape:
                    current_score = current_score.interp_like(habitat_score)
                
                habitat_score = (habitat_score * 2 + current_score) / 3
                print("  ✓ Current suitability calculated")
            
            if habitat_score is not None:
                # Classify habitat quality
                habitat_class = xr.where(habitat_score < 0.3, 'poor',
                                xr.where(habitat_score < 0.6, 'moderate', 'good'))
                
                self.processed_data['juvenile_habitat_score'] = habitat_score
                self.processed_data['juvenile_habitat_class'] = habitat_class
                
                print(f"\n✓ Juvenile habitat zones identified")
                print(f"  Good habitat: {float((habitat_score >= 0.6).sum() / habitat_score.size * 100):.1f}%")
            else:
                print("✗ Insufficient data for habitat assessment")
                
        except Exception as e:
            print(f"✗ Error identifying juvenile habitats: {e}")
            
    def export_processed_data(self):
        """Export all processed data to NetCDF and CSV"""
        print("\n" + "="*60)
        print("EXPORTING PROCESSED DATA")
        print("="*60)
        
        try:
            # Export xarray datasets to NetCDF
            for key, data in self.processed_data.items():
                if isinstance(data, (xr.DataArray, xr.Dataset)):
                    output_file = self.processed_dir / f'{key}.nc'
                    data.to_netcdf(output_file)
                    print(f"  ✓ Exported {key} to {output_file.name}")
            
            # Export summary statistics to CSV
            summary_data = {}
            for key in ['fishing_summary', 'mpa_stats']:
                if key in self.processed_data:
                    summary_data[key] = self.processed_data[key]
            
            if summary_data:
                summary_df = pd.DataFrame([summary_data])
                output_file = self.processed_dir / 'summary_statistics.csv'
                summary_df.to_csv(output_file, index=False)
                print(f"  ✓ Exported summary statistics to {output_file.name}")
            
            # Create metadata file
            metadata = {
                'processing_date': datetime.now().isoformat(),
                'datasets_processed': list(self.processed_data.keys()),
                'output_directory': str(self.processed_dir.absolute())
            }
            
            import json
            metadata_file = self.processed_dir / 'processing_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"  ✓ Exported metadata to {metadata_file.name}")
            
            print(f"\n✓ All processed data exported to {self.processed_dir}")
            
        except Exception as e:
            print(f"✗ Error exporting data: {e}")
            
    def generate_processing_report(self):
        """Generate a summary report of processing"""
        print("\n" + "="*60)
        print("PROCESSING SUMMARY REPORT")
        print("="*60)
        
        report_lines = [
            "\nMedGuard Data Processing Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n" + "="*60,
            "\nDatasets Loaded:",
        ]
        
        for key in self.raw_data.keys():
            report_lines.append(f"  ✓ {key}")
            
        report_lines.extend([
            "\nProcessed Outputs:",
        ])
        
        for key in self.processed_data.keys():
            report_lines.append(f"  ✓ {key}")
            
        if 'overfishing_risk_index' in self.processed_data:
            risk = self.processed_data['overfishing_risk_index']
            report_lines.extend([
                "\nOverfishing Risk Assessment:",
                f"  Mean risk index: {float(risk.mean()):.3f}",
                f"  Maximum risk: {float(risk.max()):.3f}",
                f"  High-risk areas: {float((risk > 0.6).sum() / risk.size * 100):.1f}%"
            ])
            
        if 'mpa_stats' in self.processed_data:
            mpa = self.processed_data['mpa_stats']
            report_lines.extend([
                "\nMarine Protected Areas:",
                f"  Total MPAs: {mpa['number_of_mpas']}",
                f"  Coverage: {mpa['coverage_percentage']:.2f}%"
            ])
            
        report_text = "\n".join(report_lines)
        
        # Save report
        report_file = self.processed_dir / 'processing_report.txt'
        with open(report_file, 'w') as f:
            f.write(report_text)
            
        print(report_text)
        print(f"\n✓ Report saved to {report_file}")
        
    def run_full_pipeline(self):
        """Execute complete processing pipeline"""
        print("\n" + "="*70)
        print(" "*15 + "MEDGUARD DATA PROCESSING PIPELINE")
        print("="*70)
        print(f"Processing start: {datetime.now()}")
        
        # Load data
        self.load_copernicus_data()
        self.load_emodnet_data()
        
        # Process oceanographic variables
        self.calculate_sst_anomaly()
        self.calculate_current_speed()
        self.calculate_productivity_index()
        self.calculate_frontal_zones()
        
        # Process human activities
        self.calculate_fishing_pressure()
        self.calculate_mpa_coverage()
        
        # Calculate risk indices
        self.calculate_overfishing_risk_index()
        self.identify_juvenile_habitat_zones()
        
        # Export results
        self.export_processed_data()
        self.generate_processing_report()
        
        print("\n" + "="*70)
        print(" "*20 + "PROCESSING COMPLETE!")
        print("="*70)
        print(f"Processing end: {datetime.now()}")
        print(f"\nResults saved to: {self.processed_dir.absolute()}")
        print("\nNext steps:")
        print("1. Train models: python 04_train_models.py")
        print("2. Build dashboard: python 05_create_dashboard.py")
        print("3. Deploy application: python 06_deploy_to_edito.py")


def main():
    """Main execution function"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         MEDGUARD DATA PROCESSING SYSTEM                   ║
    ║     Real-Time Overfishing Risk Monitor - Mediterranean    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    processor = MedGuardProcessor(data_dir='data')
    
    try:
        processor.run_full_pipeline()
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())