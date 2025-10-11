import pandas as pd
import glob
import os

# --- CONFIGURATION ---

# IMPORTANT: Change this path if your CSV files are not in the same directory as this script.
# If they are in the same folder, keep it as '.'
folder_path = r'C:\Users\ayon-\Desktop\Responses\Batch FileChecks' 

# The pattern to match your batch files (e.g., api_check_results_batch_1.csv, api_check_results_batch_2.csv)
file_pattern = 'api_check_results_batch_*.csv'

# Column names based on the image you provided
ASSUMED_STATUS_COLUMN = 'Assumed Status'
PARENT_DOMAIN_COLUMN = 'Parent Domain'
TARGET_STATUS = 'Assumed Working'
OUTPUT_FILENAME = 'assumed_working_parent_domains.csv'

# --- MAIN LOGIC ---

def process_and_filter_data(path, pattern):
    """
    Merges all matching CSV files, filters for the target status,
    and extracts unique parent domains.
    """
    # 1. Find all matching files
    search_path = os.path.join(path, pattern)
    all_files = glob.glob(search_path)
    
    if not all_files:
        print(f"Error: No CSV files found matching the pattern '{search_path}'.")
        return None

    print(f"Found {len(all_files)} files to process. Starting merge...")
    
    # 2. Read and merge all files
    df_list = []
    for filename in all_files:
        try:
            # Read only the necessary columns to save memory and time
            df = pd.read_csv(filename, usecols=[PARENT_DOMAIN_COLUMN, ASSUMED_STATUS_COLUMN])
            df_list.append(df)
        except KeyError as e:
            print(f"Warning: Skipping file '{filename}'. Column check failed. Missing column: {e}")
            continue
        except Exception as e:
            print(f"Warning: Could not read file '{filename}'. Error: {e}")
            continue

    if not df_list:
        print("Error: Could not read any files successfully.")
        return None

    combined_df = pd.concat(df_list, ignore_index=True)
    total_rows = len(combined_df)
    print(f"Merge complete. Total rows combined: {total_rows}")

    # 3. Filter the combined DataFrame
    # Filter for rows where the Assumed Status is 'Assumed Working'
    print(f"Filtering for rows where '{ASSUMED_STATUS_COLUMN}' is '{TARGET_STATUS}'...")
    
    # Clean up whitespace issues in the column for robust filtering
    combined_df[ASSUMED_STATUS_COLUMN] = combined_df[ASSUMED_STATUS_COLUMN].str.strip()
    
    # Apply the filter
    working_df = combined_df[combined_df[ASSUMED_STATUS_COLUMN] == TARGET_STATUS]
    
    working_rows = len(working_df)
    print(f"Found {working_rows} rows that meet the condition.")
    
    if working_rows == 0:
        print("No 'Assumed Working' results found. Exiting.")
        return None

    # 4. Extract unique Parent Domains
    unique_domains = working_df[PARENT_DOMAIN_COLUMN].dropna().unique()
    num_unique_domains = len(unique_domains)
    print(f"Extracted {num_unique_domains} unique '{PARENT_DOMAIN_COLUMN}' values.")
    
    # Create the final DataFrame
    final_df = pd.DataFrame({PARENT_DOMAIN_COLUMN: unique_domains})
    
    return final_df

# Run the process
if __name__ == "__main__":
    final_result_df = process_and_filter_data(folder_path, file_pattern)
    
    if final_result_df is not None:
        # 5. Save the final CSV
        final_result_df.to_csv(OUTPUT_FILENAME, index=False)
        print("-" * 50)
        print(f"Success! The final list of unique parent links is saved to: {OUTPUT_FILENAME}")
        print("-" * 50)
    else:
        print("-" * 50)
        print("Process finished with no output file generated.")
        print("-" * 50)
