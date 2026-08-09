#!/usr/bin/env python3
"""
Fix the existing CESM variables CSV by properly quoting fields.
"""

import csv
import os
import shutil

def fix_cesm_csv():
    input_file = "/mnt/c/Users/ahmed/Documents/Work/LEAP/ClimateKGAgenticAI/NasaCMRData/cesm_variables/cesm_variables_raw.csv"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return

    print(f"Fixing CSV: {input_file}")

    # Read the original file line by line
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Parse header
    header_line = lines[0].strip()
    expected_columns = ['standard_type', 'component', 'temporal_frequency', 'cesm_name', 'time_averaging', 'description', 'units', 'dimensions']

    fixed_rows = [expected_columns]  # Start with clean header

    # Process each data line
    for i, line in enumerate(lines[1:], 1):
        line = line.strip()
        if not line:
            continue

        # Split by comma - this is tricky due to embedded commas
        parts = line.split(',')

        if len(parts) < 8:
            print(f"Warning: Line {i+1} has too few fields: {line}")
            continue

        # Extract fields carefully
        standard_type = parts[0].strip()
        component = parts[1].strip()
        temporal_frequency = parts[2].strip()
        cesm_name = parts[3].strip()
        time_averaging = parts[4].strip()

        # Everything from part 5 to second-to-last is description
        # Last part is dimensions, second-to-last is units
        remaining = parts[5:]

        if len(remaining) >= 2:
            dimensions = remaining[-1].strip()
            units = remaining[-2].strip()
            description_parts = remaining[:-2]
            description = ' '.join(description_parts).strip()
        else:
            # Fallback
            dimensions = remaining[-1].strip() if remaining else ""
            units = ""
            description = ' '.join(remaining[:-1]).strip() if len(remaining) > 1 else ""

        # Clean fields
        def clean_field(text):
            if not text:
                return ""
            # Remove quotes and clean whitespace
            text = text.replace('"', "'").replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            return ' '.join(text.split()).strip()

        cleaned_row = [
            clean_field(standard_type),
            clean_field(component),
            clean_field(temporal_frequency),
            clean_field(cesm_name),
            clean_field(time_averaging),
            clean_field(description),
            clean_field(units),
            clean_field(dimensions)
        ]

        fixed_rows.append(cleaned_row)

    # Create backup
    backup_file = input_file + ".backup"
    shutil.copy2(input_file, backup_file)
    print(f"Created backup: {backup_file}")

    # Write fixed CSV with proper quoting
    with open(input_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(fixed_rows)

    print(f"✓ Fixed CSV with {len(fixed_rows)-1} variables")
    print(f"✓ All fields are now properly quoted")

    # Show first few lines
    print("\nFirst 3 lines of fixed CSV:")
    with open(input_file, 'r') as f:
        for i, line in enumerate(f):
            if i < 3:
                print(f"  {line.strip()}")

if __name__ == "__main__":
    fix_cesm_csv()