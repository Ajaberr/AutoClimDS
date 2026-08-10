import json
import pandas as pd
import requests
import time
from urllib.parse import urlparse
from collections import defaultdict

# === USER SETTINGS ===
INPUT_FILE_NOAA = '../noaa_json/noaa_nasa_enhanced_multi_query.json'
VERIFICATION_FILE = 'noaa_data_api_verification.csv'
OUTPUT_FILE = 'noaa_unknown_auth_child_verification.csv'
TIMEOUT = 15
SLEEP = 1.0
MAX_CHILDREN_PER_PARENT = 5  # Test up to 5 child URLs per parent domain

def get_parent_domain(url):
    """Extract parent domain from URL"""
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return None

def extract_urls_from_noaa(data_dict):
    """Extract URLs from NOAA OneStop JSON"""
    all_urls = []
    related_urls = data_dict.get("RelatedUrl", [])
    for url_obj in related_urls:
        url = url_obj.get('url')
        if url and url.startswith(('http://', 'https://')):
            all_urls.append(url)
    return all_urls

def is_data_file(url):
    """Check if URL looks like a data file"""
    data_extensions = [
        '.nc', '.nc4', '.hdf', '.hdf5', '.h5',  # NetCDF/HDF
        '.csv', '.tsv', '.txt',  # Text formats
        '.json', '.xml',  # Structured data
        '.tif', '.tiff', '.geotiff',  # Geospatial
        '.grib', '.grib2', '.grb',  # GRIB
        '.zarr',  # Zarr
        '.mat',  # MATLAB
    ]

    url_lower = url.lower()
    # Also exclude image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.ico']
    if any(url_lower.endswith(ext) for ext in image_extensions):
        return False

    return any(url_lower.endswith(ext) or ext + '?' in url_lower for ext in data_extensions)

def is_api_endpoint(url):
    """Check if URL looks like an API endpoint"""
    api_indicators = [
        '/erddap/', '/griddap/', '/tabledap/',  # ERDDAP
        '/dodsC/', '/thredds/', '/catalog',  # OPeNDAP/THREDDS
        '/api/', '/v1/', '/v2/', '/data/',  # REST API
        '?service=', '?request=',  # OGC services
    ]
    return any(indicator in url.lower() for indicator in api_indicators)

def check_child_url(url):
    """Check if a child URL is accessible and what type of resource it is"""
    result = {
        'url': url,
        'parent_domain': get_parent_domain(url),
        'status_code': None,
        'content_type': 'N/A',
        'content_length': 0,
        'is_data_file': is_data_file(url),
        'is_api_endpoint': is_api_endpoint(url),
        'accessible': False,
        'downloadable': False,
        'error': None
    }

    try:
        # Use HEAD request first to avoid downloading large files
        headers = {
            'User-Agent': 'ClimateKG-DataVerification/1.0 (research@example.com)'
        }

        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)

        # If HEAD fails, try GET with range to get just first bytes
        if response.status_code >= 400:
            headers['Range'] = 'bytes=0-1023'  # Get only first 1KB
            response = requests.get(url, timeout=TIMEOUT, headers=headers, stream=True)

        result['status_code'] = response.status_code
        result['content_type'] = response.headers.get('Content-Type', 'N/A')
        result['content_length'] = int(response.headers.get('Content-Length', 0))
        result['accessible'] = 200 <= response.status_code < 400

        # Consider it downloadable if it's accessible and looks like data
        if result['accessible']:
            ct = result['content_type'].lower()
            is_data_content = any(data_type in ct for data_type in [
                'netcdf', 'hdf', 'application/x-netcdf', 'application/x-hdf',
                'text/csv', 'application/csv', 'text/plain',
                'application/json', 'application/xml',
                'application/octet-stream',  # Generic binary
                'image/tiff',  # GeoTIFF
            ])
            result['downloadable'] = is_data_content or result['is_data_file']

    except requests.Timeout:
        result['error'] = 'Timeout'
    except requests.ConnectionError:
        result['error'] = 'Connection Error'
    except Exception as e:
        result['error'] = str(e)[:100]

    return result

def main():
    print("=" * 70)
    print("Verifying Child URLs for Unknown/Auth-Required NOAA Domains")
    print("=" * 70)

    # Read verification results to find Unknown and Auth-Required domains
    print("\n📂 Reading verification results...")
    try:
        verification_df = pd.read_csv(VERIFICATION_FILE)

        # Filter for Unknown or Auth Required
        unknown_domains = verification_df[
            (verification_df['data_downloadable'] == 'Unknown') |
            (verification_df['data_downloadable'].str.contains('Unknown', na=False)) |
            (verification_df['auth_required'] == 'Yes')
        ]['parent_domain'].tolist()

        print(f"   Found {len(unknown_domains)} domains needing verification:")
        print(f"   - Unknown data accessibility")
        print(f"   - Authentication required\n")

        if len(unknown_domains) == 0:
            print("❌ No domains need verification")
            return

    except FileNotFoundError:
        print(f"❌ Error: {VERIFICATION_FILE} not found")
        return

    # Read NOAA data to get all URLs
    print("📂 Reading NOAA OneStop data...")
    try:
        with open(INPUT_FILE_NOAA, 'r', encoding='utf-8') as f:
            noaa_data = json.load(f)

        all_urls = extract_urls_from_noaa(noaa_data)
        print(f"   Found {len(all_urls)} total URLs from NOAA\n")
    except FileNotFoundError:
        print(f"❌ Error: {INPUT_FILE_NOAA} not found")
        return
    except Exception as e:
        print(f"❌ Error reading NOAA data: {e}")
        return

    # Group URLs by parent domain
    parent_to_children = defaultdict(list)
    for url in all_urls:
        parent = get_parent_domain(url)
        if parent in unknown_domains:
            parent_to_children[parent].append(url)

    print(f"🔍 Testing up to {MAX_CHILDREN_PER_PARENT} child URLs per domain")
    print(f"   Total domains with children: {len(parent_to_children)}\n")

    results = []

    # Sort by child count (descending) to test high-value domains first
    sorted_parents = sorted(parent_to_children.items(),
                          key=lambda x: len(x[1]),
                          reverse=True)

    for i, (parent, children) in enumerate(sorted_parents, 1):
        print(f"[{i}/{len(sorted_parents)}] {parent} ({len(children)} children)")

        # Prioritize testing data files and API endpoints
        data_files = [url for url in children if is_data_file(url)]
        api_endpoints = [url for url in children if is_api_endpoint(url) and not is_data_file(url)]
        other_urls = [url for url in children if url not in data_files and url not in api_endpoints]

        # Sample URLs to test - prioritize data files
        urls_to_test = []
        urls_to_test.extend(data_files[:3])  # Up to 3 data files
        urls_to_test.extend(api_endpoints[:1])  # 1 API endpoint
        urls_to_test.extend(other_urls[:1])  # 1 other URL

        # If we don't have enough, just take first N
        if len(urls_to_test) < MAX_CHILDREN_PER_PARENT:
            urls_to_test.extend(children[:MAX_CHILDREN_PER_PARENT])

        urls_to_test = list(dict.fromkeys(urls_to_test))[:MAX_CHILDREN_PER_PARENT]  # Remove duplicates

        print(f"  Testing {len(urls_to_test)} child URLs:")
        print(f"    - Data files: {sum(1 for u in urls_to_test if is_data_file(u))}")
        print(f"    - API endpoints: {sum(1 for u in urls_to_test if is_api_endpoint(u) and not is_data_file(u))}")
        print(f"    - Other: {sum(1 for u in urls_to_test if not is_data_file(u) and not is_api_endpoint(u))}")

        accessible_count = 0
        downloadable_count = 0

        for j, child_url in enumerate(urls_to_test, 1):
            # Show first 80 chars of URL
            url_display = child_url if len(child_url) <= 80 else child_url[:77] + "..."
            print(f"    [{j}/{len(urls_to_test)}] {url_display}")

            result = check_child_url(child_url)
            results.append(result)

            if result['accessible']:
                accessible_count += 1
                downloadable_icon = "📥" if result['downloadable'] else "📄"
                print(f"      ✅ {downloadable_icon} {result['status_code']} | {result['content_type']}")
                if result['content_length'] > 0:
                    print(f"         Size: {result['content_length']:,} bytes")
                if result['downloadable']:
                    downloadable_count += 1
            else:
                status = result['error'] if result['error'] else f"HTTP {result['status_code']}"
                print(f"      ❌ {status}")

            time.sleep(SLEEP)

        print(f"  → {accessible_count}/{len(urls_to_test)} accessible, {downloadable_count} downloadable\n")

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_FILE, index=False)

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY - Unknown/Auth-Required Domain Child URLs")
    print("=" * 70)

    total = len(results_df)
    accessible = len(results_df[results_df['accessible'] == True])
    downloadable = len(results_df[results_df['downloadable'] == True])

    print(f"Total child URLs tested: {total}")
    print(f"  ✅ Accessible: {accessible} ({accessible/total*100:.1f}%)")
    print(f"  📥 Downloadable data: {downloadable} ({downloadable/total*100:.1f}%)")
    print(f"  ❌ Not accessible: {total-accessible} ({(total-accessible)/total*100:.1f}%)")

    # Group by parent domain
    parent_summary = results_df.groupby('parent_domain').agg({
        'accessible': 'sum',
        'downloadable': 'sum',
        'url': 'count'
    }).rename(columns={'url': 'tested'})

    parent_summary = parent_summary.sort_values('downloadable', ascending=False)

    print(f"\n📊 Results by Parent Domain:")
    print(f"{'Parent Domain':<50} | {'Tested':<6} | {'Access':<6} | {'Download':<8}")
    print("-" * 80)
    for parent, row in parent_summary.iterrows():
        parent_short = parent if len(parent) <= 50 else parent[:47] + "..."
        print(f"{parent_short:<50} | {int(row['tested']):<6} | {int(row['accessible']):<6} | {int(row['downloadable']):<8}")

    # Show domains with downloadable data
    downloadable_domains = parent_summary[parent_summary['downloadable'] > 0]
    if len(downloadable_domains) > 0:
        print(f"\n✅ Domains with verified downloadable data ({len(downloadable_domains)}):")
        for parent in downloadable_domains.index:
            count = int(downloadable_domains.loc[parent, 'downloadable'])
            print(f"  • {parent} ({count} downloadable URLs)")

    # Show sample downloadable URLs
    downloadable_df = results_df[results_df['downloadable'] == True]
    if len(downloadable_df) > 0:
        print(f"\n📥 Sample downloadable data URLs ({min(10, len(downloadable_df))}):")
        for idx, row in downloadable_df.head(10).iterrows():
            print(f"  • {row['url']}")
            print(f"    Type: {row['content_type']} | Size: {row['content_length']:,} bytes")

    print("\n" + "=" * 70)
    print(f"✅ Results saved to: {OUTPUT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
