#!/usr/bin/env python3
"""
CESM2 LENS2 Variable Scraper
Scrapes the CESM2 Large Ensemble output variables table and saves as CSV.

Source: https://www.cesm.ucar.edu/community-projects/lens2/output-variables
"""

import requests
import pandas as pd
import json
import re
import os
from bs4 import BeautifulSoup
from io import StringIO

def scrape_cesm_variables():
    """
    Scrape CESM2 LENS2 output variables from the official webpage
    """
    url = "https://www.cesm.ucar.edu/community-projects/lens2/output-variables"
    
    try:
        print(f"Fetching data from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table
        table = soup.find('table')
        if not table:
            print("No table found on the page")
            return None
            
        # Convert table to pandas DataFrame
        df = pd.read_html(StringIO(str(table)))[0]
        
        print(f"Successfully scraped {len(df)} variables")
        return df
        
    except Exception as e:
        print(f"Error scraping data: {e}")
        
        # Fallback: try to download CSV directly if available
        try:
            csv_url = "https://www.cesm.ucar.edu/community-projects/lens2/output-variables.csv"
            print(f"Trying CSV download from: {csv_url}")
            df = pd.read_csv(csv_url)
            print(f"Successfully downloaded CSV with {len(df)} variables")
            return df
        except:
            print("CSV download also failed")
            return None

def clean_variable_data(df):
    """
    Clean and standardize the scraped variable data
    """
    if df is None:
        return None
    
    print("Cleaning variable data...")
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('/', '_')
    
    # Map common column variations - handle the weird first column name
    column_mapping = {
        'standard_"moar"': 'standard_type',
        'variable_name': 'cesm_name',
        'long_name': 'description',
        'units': 'units'
    }
    
    # Fix the problematic first column name
    if len(df.columns) > 0 and 'standard' in df.columns[0].lower():
        df.columns = ['standard_type'] + list(df.columns[1:])
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    # Clean component names
    if 'component' in df.columns:
        df['component'] = df['component'].str.lower().str.strip()
    
    # Remove rows with missing essential data
    essential_cols = ['component', 'cesm_name']
    for col in essential_cols:
        if col in df.columns:
            df = df.dropna(subset=[col])
    
    # Clean variable names
    if 'cesm_name' in df.columns:
        df['cesm_name'] = df['cesm_name'].str.strip()
    
    # Filter out variables with "unknown" descriptions
    initial_count = len(df)
    
    # Check multiple columns for "unknown" values
    unknown_filters = []
    
    if 'description' in df.columns:
        unknown_filters.append(df['description'].str.contains('unknown', case=False, na=False))
    
    if 'standard_name' in df.columns:
        unknown_filters.append(df['standard_name'].str.contains('unknown', case=False, na=False))
        
    if 'long_name' in df.columns:
        unknown_filters.append(df['long_name'].str.contains('unknown', case=False, na=False))
    
    # Combine all unknown filters with OR logic
    if unknown_filters:
        combined_unknown_filter = unknown_filters[0]
        for filter_condition in unknown_filters[1:]:
            combined_unknown_filter = combined_unknown_filter | filter_condition
        
        # Keep only rows that do NOT have unknown descriptions
        df = df[~combined_unknown_filter]
        
        filtered_count = initial_count - len(df)
        print(f"Filtered out {filtered_count} variables with unknown descriptions")
    
    # Deduplicate exact duplicates
    before_dedup = len(df)
    df = df.drop_duplicates()
    after_dedup = len(df)
    duplicates_removed = before_dedup - after_dedup
    
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} exact duplicate variables")
    
    print(f"Cleaned data: {len(df)} variables remaining")
    return df

def generate_cesm_components():
    """
    Generate comprehensive CESM component definitions
    """
    components = {
        "atm": {
            "full_name": "Community Atmosphere Model",
            "abbreviation": "CAM",
            "description": "Atmospheric component of CESM - handles atmospheric dynamics, physics, and chemistry",
            "domain": "atmosphere"
        },
        "ocn": {
            "full_name": "Parallel Ocean Program", 
            "abbreviation": "POP",
            "description": "Ocean component of CESM - simulates ocean circulation, temperature, and biogeochemistry",
            "domain": "ocean"
        },
        "lnd": {
            "full_name": "Community Land Model",
            "abbreviation": "CLM", 
            "description": "Land component of CESM - models land surface processes, vegetation, and biogeochemistry",
            "domain": "land"
        },
        "ice": {
            "full_name": "Community Ice CodE",
            "abbreviation": "CICE",
            "description": "Sea ice component of CESM - simulates sea ice dynamics and thermodynamics", 
            "domain": "seaice"
        },
        "rof": {
            "full_name": "Model for Scale Adaptive River Transport",
            "abbreviation": "MOSART",
            "description": "River routing component of CESM - handles river discharge and routing",
            "domain": "land"
        },
        "glc": {
            "full_name": "Community Ice Sheet Model",
            "abbreviation": "CISM",
            "description": "Glacier/ice sheet component of CESM - models ice sheet dynamics",
            "domain": "ice"
        },
        "wav": {
            "full_name": "WaveWatch III",
            "abbreviation": "WW3",
            "description": "Wave component of CESM - simulates ocean surface waves",
            "domain": "ocean"
        }
    }
    
    return components

def save_to_csv(df, components, output_filename='cesm_variables/cesm_variables_output.csv'):
    """
    Save the cleaned data to a CSV file
    """
    if df is None:
        print("No data to save")
        return
    
    print(f"Saving data to {output_filename}...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Add component information if available
    component_mapping = {}
    for comp_key, comp_info in components.items():
        component_mapping[comp_key] = {
            'component_full_name': comp_info['full_name'],
            'component_abbreviation': comp_info['abbreviation'],
            'component_description': comp_info['description'],
            'component_domain': comp_info['domain']
        }
    
    # Merge component information with the main dataframe
    df_output = df.copy()
    
    # Add component details if component column exists
    if 'component' in df_output.columns:
        for comp_key, comp_details in component_mapping.items():
            mask = df_output['component'] == comp_key
            for detail_key, detail_value in comp_details.items():
                df_output.loc[mask, detail_key] = detail_value
    
    # Save to CSV
    df_output.to_csv(output_filename, index=False)
    
    print(f"Successfully saved {len(df_output)} variables to {output_filename}")
    print(f"Columns saved: {list(df_output.columns)}")
    
    # Print summary statistics
    if 'component' in df_output.columns:
        print("\nVariables per component:")
        component_counts = df_output['component'].value_counts()
        for comp, count in component_counts.items():
            comp_name = component_mapping.get(comp, {}).get('component_abbreviation', comp.upper())
            print(f"  {comp_name}: {count} variables")

def main():
    """
    Main execution function
    """
    print("CESM2 LENS2 Variable Scraper")
    print("=" * 40)
    
    # Step 1: Scrape the data
    df = scrape_cesm_variables()
    if df is None:
        print("Failed to scrape data. Exiting.")
        return
    
    # Step 2: Clean the data
    df_clean = clean_variable_data(df)
    if df_clean is None:
        print("Failed to clean data. Exiting.")
        return
    
    # Step 3: Generate components
    components = generate_cesm_components()
    
    # Step 4: Save to CSV
    save_to_csv(df_clean, components, 'cesm_variables/cesm_variables_output.csv')
    
    # Also save raw data for inspection
    os.makedirs('cesm_variables', exist_ok=True)
    df_clean.to_csv('cesm_variables/cesm_variables_raw.csv', index=False)
    print(f"Raw data also saved to cesm_variables_raw.csv ({len(df_clean)} rows)")
    
    print("\nScraping completed successfully!")

if __name__ == "__main__":
    main() 
