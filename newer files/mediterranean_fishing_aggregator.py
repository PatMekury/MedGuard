import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Mediterranean Sea bounding box
MED_BOUNDS = {
    'lat_min': 30.0,
    'lat_max': 46.0,
    'lon_min': -6.0,
    'lon_max': 37.0
}

def is_in_mediterranean(lat, lon):
    """Check if coordinates are within Mediterranean Sea bounds"""
    return (MED_BOUNDS['lat_min'] <= lat <= MED_BOUNDS['lat_max'] and 
            MED_BOUNDS['lon_min'] <= lon <= MED_BOUNDS['lon_max'])

def create_cell_polygon(ll_lat, ll_lon, cell_size=0.1):
    """Create a polygon for a grid cell given lower-left corner"""
    return [
        [ll_lon, ll_lat],  # Lower-left
        [ll_lon + cell_size, ll_lat],  # Lower-right
        [ll_lon + cell_size, ll_lat + cell_size],  # Upper-right
        [ll_lon, ll_lat + cell_size],  # Upper-left
        [ll_lon, ll_lat]  # Close polygon
    ]

def process_file_in_chunks(file_path, chunk_size=50000):
    """
    Process a CSV file in chunks to avoid memory issues
    Returns only Mediterranean Sea data
    """
    print(f"  Reading {file_path.name}...")
    
    med_chunks = []
    total_rows = 0
    med_rows = 0
    
    # Read file in chunks
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        total_rows += len(chunk)
        
        # Filter for Mediterranean in this chunk
        med_chunk = chunk[
            chunk.apply(
                lambda row: is_in_mediterranean(row['cell_ll_lat'], row['cell_ll_lon']), 
                axis=1
            )
        ]
        
        med_rows += len(med_chunk)
        
        if len(med_chunk) > 0:
            med_chunks.append(med_chunk)
        
        # Progress indicator
        print(f"    Processed {total_rows:,} rows, found {med_rows:,} Mediterranean rows so far...")
    
    # Combine chunks from this file
    if med_chunks:
        return pd.concat(med_chunks, ignore_index=True)
    else:
        return pd.DataFrame()

def process_monthly_files():
    """Process all 12 monthly CSV files one at a time"""
    
    # Define file paths
    data_folder = Path("data/fleet-monthly-csvs-10-v3-2023")
    
    if not data_folder.exists():
        print(f"ERROR: Folder not found: {data_folder}")
        print("Please check your file structure!")
        return None
    
    # List of all monthly files
    monthly_files = [
        f"fleet-monthly-csvs-10-v3-2023-{month:02d}-01.csv" 
        for month in range(1, 13)
    ]
    
    # Process files one by one (memory efficient!)
    print("=" * 60)
    print("Step 1: Processing CSV files ONE AT A TIME")
    print("=" * 60)
    
    all_med_data = []
    
    for file_name in monthly_files:
        file_path = data_folder / file_name
        
        if file_path.exists():
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024*1024)
            print(f"\nMonth: {file_name}")
            print(f"  File size: {file_size_mb:.1f} MB")
            
            # Process this file in chunks
            med_data = process_file_in_chunks(file_path)
            
            if len(med_data) > 0:
                all_med_data.append(med_data)
                print(f"  ✓ Kept {len(med_data):,} Mediterranean rows")
            else:
                print(f"  ⚠ No Mediterranean data in this file")
                
        else:
            print(f"\n⚠ WARNING: {file_name} not found!")
    
    if not all_med_data:
        print("\nERROR: No Mediterranean data found in any files!")
        return None
    
    # Combine all Mediterranean data
    print("\n" + "=" * 60)
    print("Step 2: Combining all Mediterranean data")
    print("=" * 60)
    combined_df = pd.concat(all_med_data, ignore_index=True)
    print(f"✓ Total Mediterranean rows: {len(combined_df):,}")
    
    # Create GeoJSON structure
    print("\n" + "=" * 60)
    print("Step 3: Creating GeoJSON file")
    print("=" * 60)
    
    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "title": "Mediterranean Fishing Intensity 2023",
            "description": "Fishing activity in the Mediterranean Sea from January to December 2023",
            "source": "Global Fishing Watch AIS data",
            "time_period": "2023-01-01 to 2023-12-01",
            "spatial_extent": MED_BOUNDS,
            "created": datetime.now().isoformat(),
            "total_features": len(combined_df)
        },
        "features": []
    }
    
    # Convert to GeoJSON features
    print("Converting to GeoJSON features...")
    print("(This might take a few minutes...)")
    
    for idx, row in combined_df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [create_cell_polygon(
                    row['cell_ll_lat'], 
                    row['cell_ll_lon']
                )]
            },
            "properties": {
                "date": row['date'],
                "month": int(row['month']),
                "cell_ll_lat": float(row['cell_ll_lat']),
                "cell_ll_lon": float(row['cell_ll_lon']),
                "flag": row['flag'],
                "geartype": row['geartype'],
                "hours": float(row['hours']),
                "fishing_hours": float(row['fishing_hours']),
                "mmsi_present": int(row['mmsi_present']),
                "fishing_intensity": float(row['fishing_hours'] / row['hours']) if row['hours'] > 0 else 0
            }
        }
        geojson['features'].append(feature)
        
        # Progress indicator every 10000 rows
        if (idx + 1) % 10000 == 0:
            print(f"  Processed {idx + 1:,} / {len(combined_df):,} features ({(idx+1)/len(combined_df)*100:.1f}%)")
    
    # Save to GeoJSON file
    print("\n" + "=" * 60)
    print("Step 4: Saving to file")
    print("=" * 60)
    
    output_file = "fishing_intensity.geojson"
    print(f"Writing to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(geojson, f)
    
    file_size_mb = Path(output_file).stat().st_size / (1024*1024)
    
    print(f"\n✓ SUCCESS! Created {output_file}")
    print(f"  Total features: {len(geojson['features']):,}")
    print(f"  File size: {file_size_mb:.2f} MB")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total fishing hours: {combined_df['fishing_hours'].sum():,.0f}")
    print(f"Total vessel hours: {combined_df['hours'].sum():,.0f}")
    print(f"Unique flags: {combined_df['flag'].nunique()}")
    print(f"Unique gear types: {combined_df['geartype'].nunique()}")
    print(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
    
    # Top 5 flags
    print("\nTop 5 countries by fishing hours:")
    top_flags = combined_df.groupby('flag')['fishing_hours'].sum().sort_values(ascending=False).head()
    for flag, hours in top_flags.items():
        print(f"  {flag}: {hours:,.0f} hours")
    
    # Top 5 gear types
    print("\nTop 5 gear types by fishing hours:")
    top_gears = combined_df.groupby('geartype')['fishing_hours'].sum().sort_values(ascending=False).head()
    for gear, hours in top_gears.items():
        print(f"  {gear}: {hours:,.0f} hours")
    
    return geojson

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MEDITERRANEAN FISHING INTENSITY DATA PROCESSOR")
    print("Memory-Efficient Version")
    print("=" * 60)
    print()
    
    try:
        geojson_data = process_monthly_files()
        
        if geojson_data:
            print("\n" + "=" * 60)
            print("✓ ✓ ✓ PROCESSING COMPLETE! ✓ ✓ ✓")
            print("=" * 60)
            print("\nYour file 'fishing_intensity2023.geojson' is ready to use!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check:")
        print("1. Your CSV files are in: data/fleet-monthly-csvs-10-v3-2023/")
        print("2. You have enough disk space")
        print("3. The CSV files have these columns: date, month, cell_ll_lat, cell_ll_lon, flag, geartype, hours, fishing_hours, mmsi_present")