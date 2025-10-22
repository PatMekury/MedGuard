#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os
from pathlib import Path

def print_section(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

# Define Mediterranean countries by ISO3 code
MEDITERRANEAN_COUNTRIES_ISO3 = [
    'ALB', 'DZA', 'BIH', 'HRV', 'CYP', 'EGY', 'FRA', 'GRC', 'ISR', 'ITA',
    'LBN', 'LBY', 'MLT', 'MCO', 'MNE', 'MAR', 'SVN', 'ESP', 'SYR', 'TUN',
    'TUR', 'PSE'
]

def load_reference_data(data_folder):
    print_section("LOADING REFERENCE DATA")
    ref_data = {}
    try:
        ref_data['countries'] = pd.read_csv(os.path.join(data_folder, 'CL_FI_COUNTRY_GROUPS.csv'))
        ref_data['species'] = pd.read_csv(os.path.join(data_folder, 'CL_FI_SPECIES_GROUPS.csv'))
        ref_data['areas'] = pd.read_csv(os.path.join(data_folder, 'CL_FI_WATERAREA_GROUPS.csv'))
        ref_data['symbols'] = pd.read_csv(os.path.join(data_folder, 'CL_FI_SYMBOL_SDMX.csv'))
        return ref_data
    except Exception as e:
        print(f"Error loading reference data: {e}")
        return None

def identify_mediterranean_code(areas_df):
    print_section("IDENTIFYING MEDITERRANEAN AREA CODE")
    med_codes = areas_df[
        areas_df['Name_En'].str.contains('Mediterranean', case=False, na=False)
    ]
    if len(med_codes) > 0:
        return med_codes['Code'].astype(str).tolist()
    else:
        return ['37']

def get_column_name_mapping(columns):
    column_map = {}
    patterns = {
        'COUNTRY': ['COUNTRY', 'COUNTRY.UN_CODE', 'COUNTRY_UN_CODE'],
        'SPECIES': ['SPECIES', 'SPECIES.ALPHA_3_CODE', 'SPECIES_ALPHA_3_CODE'],
        'AREA': ['AREA', 'AREA.CODE', 'AREA_CODE', 'AREACODE'],
        'MEASURE': ['MEASURE'],
        'PERIOD': ['PERIOD', 'YEAR'],
        'VALUE': ['VALUE'],
        'STATUS': ['STATUS']
    }
    for expected, variations in patterns.items():
        for var in variations:
            if var in columns:
                column_map[expected] = var
                break
    return column_map

def explore_capture_data(file_path, nrows=10):
    print_section("EXPLORING CAPTURE DATA STRUCTURE")
    try:
        sample = pd.read_csv(file_path, nrows=nrows)
        column_map = get_column_name_mapping(sample.columns)
        return sample.columns.tolist(), column_map
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None

def extract_mediterranean_data(capture_file, output_file, ref_data, med_codes, column_map, start_year=2014, end_year=2023):
    print_section("EXTRACTING MEDITERRANEAN DATA")
    try:
        area_col = column_map['AREA']
        period_col = column_map.get('PERIOD', 'PERIOD')
        chunk_size = 100000
        chunks = []
        for chunk in pd.read_csv(capture_file, chunksize=chunk_size):
            chunk[area_col] = chunk[area_col].astype(str).str.strip()
            med_chunk = chunk[chunk[area_col].isin(med_codes)]
            if len(med_chunk) > 0:
                chunks.append(med_chunk)
        if len(chunks) == 0:
            print("No Mediterranean data found")
            return None
        df_med = pd.concat(chunks, ignore_index=True)
        df_filtered = df_med[
            (df_med[period_col] >= start_year) &
            (df_med[period_col] <= end_year)
        ]
        rename_dict = {v: k for k, v in column_map.items()}
        df_filtered = df_filtered.rename(columns=rename_dict)

        # Merge country reference
        df_filtered['COUNTRY'] = pd.to_numeric(df_filtered['COUNTRY'], errors='coerce')
        df_filtered = df_filtered.merge(
            ref_data['countries'][['UN_Code', 'Name_En', 'ISO3_Code']],
            left_on='COUNTRY',
            right_on='UN_Code',
            how='left'
        )
        df_filtered.rename(columns={'Name_En': 'Country_Name'}, inplace=True)

        # Filter for Mediterranean countries only
        df_filtered = df_filtered[df_filtered['ISO3_Code'].isin(MEDITERRANEAN_COUNTRIES_ISO3)]
        print(f"✓ Filtered to {len(df_filtered):,} records for Mediterranean countries only")

        # Merge species reference
        df_filtered['SPECIES'] = df_filtered['SPECIES'].astype(str).str.strip().str.upper()
        ref_data['species']['3A_Code'] = ref_data['species']['3A_Code'].astype(str).str.strip().str.upper()
        df_filtered = df_filtered.merge(
            ref_data['species'][['3A_Code', 'Name_En', 'Scientific_Name', 'ISSCAAP_Group_En']],
            left_on='SPECIES',
            right_on='3A_Code',
            how='left'
        )
        df_filtered.rename(columns={'Name_En': 'Species_Name'}, inplace=True)

        # Merge area reference
        df_filtered['AREA'] = pd.to_numeric(df_filtered['AREA'], errors='coerce')
        ref_data['areas']['Code'] = pd.to_numeric(ref_data['areas']['Code'], errors='coerce')
        df_filtered = df_filtered.merge(
            ref_data['areas'][['Code', 'Name_En']],
            left_on='AREA',
            right_on='Code',
            how='left'
        )
        df_filtered.rename(columns={'Name_En': 'Area_Name'}, inplace=True)

        # Merge status symbols
        if 'STATUS' in df_filtered.columns:
            df_filtered = df_filtered.merge(
                ref_data['symbols'][['Symbol', 'Description_En']],
                left_on='STATUS',
                right_on='Symbol',
                how='left'
            )
            df_filtered.rename(columns={'Description_En': 'Status_Description'}, inplace=True)

        # Final output columns
        output_columns = [
            'PERIOD', 'Country_Name', 'ISO3_Code', 'Species_Name', 'Scientific_Name',
            'ISSCAAP_Group_En', 'Area_Name', 'MEASURE', 'VALUE', 'STATUS',
            'Status_Description', 'COUNTRY', 'SPECIES', 'AREA'
        ]
        available_columns = [col for col in output_columns if col in df_filtered.columns]
        df_output = df_filtered[available_columns].copy()
        df_output = df_output.sort_values(['PERIOD', 'Country_Name', 'Species_Name'])
        df_output.to_csv(output_file, index=False)
        print(f"✓ Saved {len(df_output):,} records to {output_file}")
        return df_output
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def main():
    print_section("FAO MEDITERRANEAN FISH CATCH EXTRACTION")
    data_folder = "data/Fish Catch Statistics"
    capture_file = os.path.join(data_folder, "Capture_Quantity.csv")
    output_file = "fao_mediterranean_only.csv"
    if not os.path.exists(data_folder) or not os.path.exists(capture_file):
        print("Missing data files")
        return
    ref_data = load_reference_data(data_folder)
    if ref_data is None:
        return
    med_codes = identify_mediterranean_code(ref_data['areas'])
    columns, column_map = explore_capture_data(capture_file, nrows=5)
    if column_map is None:
        return
    result = extract_mediterranean_data(
        capture_file=capture_file,
        output_file=output_file,
        ref_data=ref_data,
        med_codes=med_codes,
        column_map=column_map,
        start_year=2014,
        end_year=2023
    )
    if result is not None:
        print_section("EXTRACTION COMPLETE")
        print(f"Output file: {output_file}")
        print(f"Total records: {len(result):,}")
        print("Region: Mediterranean Sea (Country-filtered)")
    else:
        print_section("EXTRACTION FAILED")

if __name__ == "__main__":
    main()