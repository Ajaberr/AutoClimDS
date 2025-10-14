import json
import pandas as pd
from urllib.parse import urlparse
from collections import defaultdict

# === USER SETTINGS ===
INPUT_FILE_NASA = '../json_files/individual_cmr_data.json'  # NASA CMR data
INPUT_FILE_NOAA = '../noaa_json/noaa_nasa_enhanced_multi_query.json'  # NOAA OneStop data
OUTPUT_FILE_COMBINED = 'parent_domain_counts.csv'
OUTPUT_FILE_NASA = 'parent_domain_counts_nasa_only.csv'
OUTPUT_FILE_NOAA = 'parent_domain_counts_noaa_only.csv'

def get_parent_domain(url):
    """Extract parent domain from URL"""
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return None

def extract_urls_from_nasa(data_list):
    """Extract URLs from NASA CMR JSON"""
    all_urls = []
    for record in data_list:
        dataset = record.get("Dataset", {})
        # Get URLs from "Dataset" -> "links" array
        for link in dataset.get('links', []):
            url = link.get('href')
            if url and url.startswith(('http://', 'https://')):
                all_urls.append(url)
        # Get URLs from "RelatedUrl" array
        for link in record.get('RelatedUrl', []):
            url = link.get('url')
            if url and url.startswith(('http://', 'https://')):
                all_urls.append(url)
    return all_urls

def extract_urls_from_noaa(data_dict):
    """Extract URLs from NOAA OneStop JSON"""
    all_urls = []
    related_urls = data_dict.get("RelatedUrl", [])
    for url_obj in related_urls:
        url = url_obj.get('url')
        if url and url.startswith(('http://', 'https://')):
            all_urls.append(url)
    return all_urls

def main():
    print("=" * 60)
    print("Counting Parent Domains from JSON Links")
    print("=" * 60)

    all_urls = []
    nasa_urls = []
    noaa_urls = []

    # Read NASA data
    print("\n📂 Reading NASA CMR data...")
    try:
        with open(INPUT_FILE_NASA, 'r', encoding='utf-8') as f:
            nasa_data = json.load(f)
            if not isinstance(nasa_data, list):
                nasa_data = [nasa_data]
            nasa_urls = extract_urls_from_nasa(nasa_data)
            all_urls.extend(nasa_urls)
            print(f"   Found {len(nasa_urls)} URLs from NASA")
    except FileNotFoundError:
        print(f"   ⚠️  Warning: {INPUT_FILE_NASA} not found, skipping NASA data")
    except Exception as e:
        print(f"   ⚠️  Warning: Error reading NASA data: {e}")

    # Read NOAA data
    print("\n📂 Reading NOAA OneStop data...")
    try:
        with open(INPUT_FILE_NOAA, 'r', encoding='utf-8') as f:
            noaa_data = json.load(f)
            if isinstance(noaa_data, list):
                print("   ⚠️  Warning: NOAA format expects a dictionary, got a list")
            else:
                noaa_urls = extract_urls_from_noaa(noaa_data)
                all_urls.extend(noaa_urls)
                print(f"   Found {len(noaa_urls)} URLs from NOAA")
    except FileNotFoundError:
        print(f"   ⚠️  Warning: {INPUT_FILE_NOAA} not found, skipping NOAA data")
    except Exception as e:
        print(f"   ⚠️  Warning: Error reading NOAA data: {e}")

    if not all_urls:
        print("\n❌ Error: No URLs found in either data source")
        return

    print(f"\n🔗 Total URLs found: {len(all_urls)}")

    # Count URLs by parent domain
    parent_counts = defaultdict(int)
    parent_sources = defaultdict(lambda: {'nasa': 0, 'noaa': 0})

    # Count from NASA URLs
    for url in nasa_urls:
        parent = get_parent_domain(url)
        if parent:
            parent_counts[parent] += 1
            parent_sources[parent]['nasa'] += 1

    # Count from NOAA URLs
    for url in noaa_urls:
        parent = get_parent_domain(url)
        if parent:
            parent_counts[parent] += 1
            parent_sources[parent]['noaa'] += 1

    print(f"🌐 Unique parent domains: {len(parent_counts)}")

    # Create results list
    results = []
    for parent, count in sorted(parent_counts.items(), key=lambda x: x[1], reverse=True):
        results.append({
            'parent_domain': parent,
            'total_child_urls': count,
            'nasa_urls': parent_sources[parent]['nasa'],
            'noaa_urls': parent_sources[parent]['noaa']
        })

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    # Save combined to CSV
    results_df.to_csv(OUTPUT_FILE_COMBINED, index=False)

    # Create NASA-exclusive DataFrame (only in NASA, NOT in NOAA)
    nasa_exclusive_results = []
    for parent, count in sorted(parent_counts.items(), key=lambda x: x[1], reverse=True):
        if parent_sources[parent]['nasa'] > 0 and parent_sources[parent]['noaa'] == 0:
            nasa_exclusive_results.append({
                'parent_domain': parent,
                'total_child_urls': parent_sources[parent]['nasa']
            })
    nasa_exclusive_df = pd.DataFrame(nasa_exclusive_results)
    nasa_exclusive_df.to_csv(OUTPUT_FILE_NASA, index=False)

    # Create NOAA-exclusive DataFrame (only in NOAA, NOT in NASA)
    noaa_exclusive_results = []
    for parent, count in sorted(parent_counts.items(), key=lambda x: x[1], reverse=True):
        if parent_sources[parent]['noaa'] > 0 and parent_sources[parent]['nasa'] == 0:
            noaa_exclusive_results.append({
                'parent_domain': parent,
                'total_child_urls': parent_sources[parent]['noaa']
            })
    noaa_exclusive_df = pd.DataFrame(noaa_exclusive_results)
    noaa_exclusive_df.to_csv(OUTPUT_FILE_NOAA, index=False)

    # Print summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"Total parent domains: {len(results_df)}")
    print(f"Total child URLs: {results_df['total_child_urls'].sum()}")
    print(f"  From NASA: {results_df['nasa_urls'].sum()}")
    print(f"  From NOAA: {results_df['noaa_urls'].sum()}")
    print(f"\nAverage child URLs per parent: {results_df['total_child_urls'].mean():.1f}")
    print(f"Median child URLs per parent: {results_df['total_child_urls'].median():.0f}")
    print(f"Max child URLs for one parent: {results_df['total_child_urls'].max()}")

    print("\n" + "=" * 60)
    print("TOP 10 PARENT DOMAINS (by child URL count)")
    print("=" * 60)

    top_10 = results_df.head(10)
    for idx, row in top_10.iterrows():
        print(f"{row['total_child_urls']:>6} URLs | {row['parent_domain']}")
        if row['nasa_urls'] > 0 and row['noaa_urls'] > 0:
            print(f"         └─ NASA: {row['nasa_urls']}, NOAA: {row['noaa_urls']}")
        elif row['nasa_urls'] > 0:
            print(f"         └─ NASA only")
        else:
            print(f"         └─ NOAA only")

    print("\n" + "=" * 60)
    print(f"✅ Results saved to:")
    print(f"   - Combined: {OUTPUT_FILE_COMBINED} ({len(results_df)} parent domains)")
    print(f"   - NASA exclusive: {OUTPUT_FILE_NASA} ({len(nasa_exclusive_df)} parent domains - not in NOAA)")
    print(f"   - NOAA exclusive: {OUTPUT_FILE_NOAA} ({len(noaa_exclusive_df)} parent domains - not in NASA)")
    print("=" * 60)

    # Additional breakdown
    nasa_only = len(results_df[results_df['noaa_urls'] == 0])
    noaa_only = len(results_df[results_df['nasa_urls'] == 0])
    both = len(results_df[(results_df['nasa_urls'] > 0) & (results_df['noaa_urls'] > 0)])

    print(f"\nParent domain sources:")
    print(f"  NASA only: {nasa_only}")
    print(f"  NOAA only: {noaa_only}")
    print(f"  Both NASA & NOAA: {both}")

if __name__ == "__main__":
    main()
