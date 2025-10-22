#!/usr/bin/env python3
"""
Extract Mediterranean Marine Protected Areas from WDPA Geodatabase
Author: MedGuard Project
Date: October 2025

This script reads a File Geodatabase containing protected areas data,
filters for marine protected areas in the Mediterranean Sea region,
and exports the results to a GeoJSON file.
"""

import geopandas as gpd
import fiona
import os
from shapely.geometry import box
from geopandas import GeoDataFrame

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def extract_mediterranean_mpa(
    gdb_path="data/WDPA_Geotatabase_file.gdb",
    output_file="mpa_boundaries.geojson",
    med_bounds=None
):
    """
    Extract Marine Protected Areas from the Mediterranean Sea
    
    Parameters:
    -----------
    gdb_path : str
        Path to the File Geodatabase folder
    output_file : str
        Name of the output GeoJSON file
    med_bounds : dict
        Dictionary with min_lon, max_lon, min_lat, max_lat keys
        If None, uses default Mediterranean boundaries
    """
    
    try:
        # Set default Mediterranean boundaries if not provided
        if med_bounds is None:
            med_bounds = {
                'min_lon': -6,    # Western boundary (Strait of Gibraltar)
                'max_lon': 37,    # Eastern boundary (Levantine Sea)
                'min_lat': 30,    # Southern boundary (North Africa)
                'max_lat': 46     # Northern boundary (Northern Italy/Balkans)
            }
        
        print_section("MEDITERRANEAN MPA EXTRACTION STARTED")
        
        # Step 1: Check if geodatabase exists
        print("\n[1/8] Checking geodatabase path...")
        if not os.path.exists(gdb_path):
            raise FileNotFoundError(f"Geodatabase not found at: {gdb_path}")
        print(f"✓ Found geodatabase at: {gdb_path}")
        
        # Step 2: List available layers
        print("\n[2/8] Reading geodatabase layers...")
        layers = fiona.listlayers(gdb_path)
        print(f"✓ Available layers: {layers}")
        
        if len(layers) == 0:
            raise ValueError("No layers found in geodatabase")
        
        # Step 3: Load the protected areas data
        print(f"\n[3/8] Loading protected areas data from layer '{layers[0]}'...")
        print("⏳ This may take 2-5 minutes (loading 217 MB)...")
        gdf = gpd.read_file(gdb_path, layer=layers[0])
        print(f"✓ Loaded {len(gdf):,} protected areas")
        print(f"✓ Coordinate system: {gdf.crs}")
        
        # Step 4: Examine data structure
        print("\n[4/8] Examining data structure...")
        print(f"✓ Columns available: {len(gdf.columns)}")
        print(f"  Main columns: {', '.join(gdf.columns[:10].tolist())}")
        
        # Check for MARINE column
        if 'MARINE' in gdf.columns:
            marine_counts = gdf['MARINE'].value_counts()
            print(f"\n  Marine classification:")
            for key, val in marine_counts.items():
                print(f"    {key}: {val:,} areas")
        
        # Step 5: Filter for Marine Protected Areas
        print("\n[5/8] Filtering for Marine Protected Areas...")
        if 'MARINE' in gdf.columns:
            # Filter for marine areas (1 = marine only, 2 = both marine & terrestrial)
            gdf_marine = gdf[gdf['MARINE'].astype(str).isin(['1', '2'])].copy()
            print(f"✓ Found {len(gdf_marine):,} marine protected areas")
        else:
            print("⚠ Warning: 'MARINE' column not found. Using all areas.")
            gdf_marine = gdf.copy()
        
        # Step 6: Convert to WGS84 if needed
        print("\n[6/8] Converting coordinate system...")
        if gdf_marine.crs != "EPSG:4326":
            print(f"  Converting from {gdf_marine.crs} to EPSG:4326...")
            gdf_marine = gdf_marine.to_crs("EPSG:4326")
            print("✓ Converted to WGS84 (EPSG:4326)")
        else:
            print("✓ Already in WGS84 (EPSG:4326)")
        
        # Step 7: Filter for Mediterranean region
        print("\n[7/8] Filtering for Mediterranean Sea region...")
        print(f"  Boundaries: Lon [{med_bounds['min_lon']}, {med_bounds['max_lon']}], "
              f"Lat [{med_bounds['min_lat']}, {med_bounds['max_lat']}]")
        
        # Create bounding box
        med_bbox = box(med_bounds['min_lon'], med_bounds['min_lat'], 
                      med_bounds['max_lon'], med_bounds['max_lat'])
        
        # Filter areas that intersect with Mediterranean
        gdf_med = gdf_marine[gdf_marine.intersects(med_bbox)].copy()
        print(f"✓ Found {len(gdf_med):,} MPAs in the Mediterranean")
        
        # Display summary statistics
        if len(gdf_med) > 0:
            print("\n  Summary:")
            if 'ISO3' in gdf_med.columns:
                top_countries = gdf_med['ISO3'].value_counts().head(5)
                print("  Top 5 countries:")
                for country, count in top_countries.items():
                    print(f"    {country}: {count} MPAs")
            
            if 'NAME' in gdf_med.columns:
                print(f"\n  Sample MPA names:")
                for i, name in enumerate(gdf_med['NAME'].head(5), 1):
                    print(f"    {i}. {name}")
        else:
            print("⚠ WARNING: No MPAs found in the Mediterranean region!")
            print("  Check if the boundaries need adjustment.")
            return None
        
        # Step 8: Save to GeoJSON
        print("\n[8/8] Saving to GeoJSON...")
        gdf_med.to_file(output_file, driver='GeoJSON')
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Saved {len(gdf_med):,} MPAs to '{output_file}'")
        print(f"✓ File size: {file_size_mb:.2f} MB")
        
        print_section("EXTRACTION COMPLETE!")
        print(f"\n✓ Output file: {output_file}")
        print(f"✓ Total MPAs extracted: {len(gdf_med):,}")
        print(f"✓ Geographic coverage: Mediterranean Sea")
        print("\nYou can now use this file in your analysis!\n")
        
        return gdf_med
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("Please check that the geodatabase path is correct.")
        return None
    
    except Exception as e:
        print(f"\n❌ ERROR: An unexpected error occurred:")
        print(f"   {type(e).__name__}: {e}")
        print("\nPlease check:")
        print("  1. All required libraries are installed (geopandas, fiona, shapely)")
        print("  2. The geodatabase files are not corrupted")
        print("  3. You have enough disk space for the output file")
        return None


def main():
    """Main function to run the script"""
    # You can customize these parameters:
    GDB_PATH = "data/WDPA_Geotatabase_file.gdb"
    OUTPUT_FILE = "mpa_boundaries.geojson"
    
    # Mediterranean Sea boundaries (can be adjusted if needed)
    MED_BOUNDARIES = {
        'min_lon': -6,    # Western boundary
        'max_lon': 37,    # Eastern boundary
        'min_lat': 30,    # Southern boundary
        'max_lat': 46     # Northern boundary
    }
    
    # Run the extraction
    result = extract_mediterranean_mpa(
        gdb_path=GDB_PATH,
        output_file=OUTPUT_FILE,
        med_bounds=MED_BOUNDARIES
    )
    
    return result


if __name__ == "__main__":
    # This runs when the script is executed
    main()