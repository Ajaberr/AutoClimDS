import pandas as pd
import json

# --- CONFIGURATION ---
INPUT_FILE = r'C:\Users\ayon-\Desktop\individual_cmr_data.json'  # Make sure your JSON file is named this
OUTPUT_FILE = r'C:\Users\ayon-\Desktop\datasets_with_urls1.csv' 
# ---------------------

def flatten_and_extract_urls(data_list):
    """
    Processes a list of nested JSON objects to flatten key metadata and extract all URLs.
    """
    flattened_records = []
    
    for record in data_list:
        # --- 1. Extract Core Metadata ---
        dataset = record.get("Dataset", {})
        temporal = record.get("TemporalExtent", {})
        location = record.get("Location", {})
        
        # --- 2. Extract and Consolidate Multi-Value Fields ---
        
        # Consolidate Contact Names
        contact_names = [
            contact.get('name', '')
            for contact in record.get("Contact", [])
        ]
        
        # Consolidate Place Names
        place_names = location.get("place_names", [])

        # Clean up the summary text
        summary_text = record.get("DataCategory", {}).get("summary", "")
        summary_text = summary_text.replace('\n', ' ').strip()
        
        # --- 3. Extract All Related URLs (http/https links) ---
        all_urls = []
        
        # Get URLs from "Dataset" -> "links" array (uses 'href')
        for link in dataset.get('links', []):
            url = link.get('href')
            if url and url.startswith(('http://', 'https://')):
                all_urls.append(url)
                
        # Get URLs from "RelatedUrl" array (uses 'url')
        for link in record.get('RelatedUrl', []):
            url = link.get('url')
            if url and url.startswith(('http://', 'https://')):
                all_urls.append(url)
        
        # --- 4. Create a Base Record Dictionary ---
        base_record = {
            'short_name': dataset.get('short_name'),
            'title': dataset.get('title'),
            'data_center': dataset.get('data_center'),
            'doi': dataset.get('doi'),
            'temporal_start': temporal.get('start_time'),
            'temporal_end': temporal.get('end_time'),
            'contact_names': ", ".join(contact_names),
            'location_place_names': ", ".join(place_names),
            'summary': summary_text
        }
        
        # --- 5. Add URLs as sequential columns ---
        # Add a column for each extracted URL (e.g., related_url_1, related_url_2)
        for i, url in enumerate(all_urls):
            base_record[f'related_url_{i+1}'] = url
            
        flattened_records.append(base_record)
        
    return flattened_records

# --- MAIN EXECUTION ---
try:
    # 1. Read the JSON file
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data_from_file = json.load(f)
        
    if not isinstance(data_from_file, list):
        # Handle the case where the file contains a single object, not a list
        data_from_file = [data_from_file]

    # 2. Flatten the data and extract URLs
    csv_data = flatten_and_extract_urls(data_from_file)

    # 3. Convert to a Pandas DataFrame and save as CSV
    df = pd.DataFrame(csv_data)
    
    # Fill any empty cells with an empty string for clean CSV output
    df = df.fillna('')
    
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    print(f"✅ Success! Data from '{INPUT_FILE}' saved to '{OUTPUT_FILE}'.")
    print(f"Total records processed: {len(df)}")
    
except FileNotFoundError:
    print(f"❌ Error: The file '{INPUT_FILE}' was not found. Please check the file name and path.")
except json.JSONDecodeError:
    print(f"❌ Error: Could not parse '{INPUT_FILE}'. Check if the JSON is valid.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")