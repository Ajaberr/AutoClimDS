import requests
import pandas as pd
import json
import time
from urllib.parse import urlparse, urljoin

# === USER SETTINGS ===
INPUT_FILE = 'parent_domain_counts_noaa_only.csv'  # NOAA-exclusive domains
OUTPUT_FILE = 'noaa_data_api_verification.csv'
TIMEOUT = 10
SLEEP = 0.5

# === Known data API indicators ===
DATA_API_PATTERNS = {
    'opendap': {
        'keywords': ['opendap', 'dods', 'thredds'],
        'test_endpoints': ['/catalog.html', '/catalog.xml', '/dodsC/'],
        'data_formats': ['.nc', '.hdf', '.grb']
    },
    'erddap': {
        'keywords': ['erddap'],
        'test_endpoints': ['/info/index.json', '/tabledap/index.json', '/griddap/index.json'],
        'data_formats': ['.csv', '.nc', '.json']
    },
    'wms': {
        'keywords': ['wms', 'mapserver', 'geoserver'],
        'test_endpoints': ['?service=WMS&request=GetCapabilities'],
        'data_formats': []
    },
    'wfs': {
        'keywords': ['wfs'],
        'test_endpoints': ['?service=WFS&request=GetCapabilities'],
        'data_formats': ['.gml', '.json']
    },
    'rest_api': {
        'keywords': ['api', 'rest', 'data'],
        'test_endpoints': ['/api', '/v1', '/v2', '/data'],
        'data_formats': ['.json', '.csv', '.xml']
    }
}

def identify_api_type(url, response_text=''):
    """Identify what type of data API this might be"""
    url_lower = url.lower()
    identified_types = []

    for api_type, patterns in DATA_API_PATTERNS.items():
        if any(kw in url_lower for kw in patterns['keywords']):
            identified_types.append(api_type)

    # Check response text for additional hints
    if response_text:
        text_lower = response_text.lower()
        if 'opendap' in text_lower or 'thredds' in text_lower:
            if 'opendap' not in identified_types:
                identified_types.append('opendap')
        if 'erddap' in text_lower:
            if 'erddap' not in identified_types:
                identified_types.append('erddap')
        if 'wms' in text_lower or 'getcapabilities' in text_lower:
            if 'wms' not in identified_types:
                identified_types.append('wms')

    return identified_types if identified_types else ['unknown']

def test_data_download(url, api_types):
    """Test if the API actually allows data downloads"""
    download_possible = False
    test_results = []

    for api_type in api_types:
        if api_type not in DATA_API_PATTERNS:
            continue

        patterns = DATA_API_PATTERNS[api_type]

        # Try test endpoints
        for endpoint in patterns['test_endpoints']:
            test_url = url.rstrip('/') + endpoint
            try:
                response = requests.get(test_url, timeout=TIMEOUT)
                if response.status_code == 200:
                    test_results.append(f"{api_type}:{endpoint} (200 OK)")
                    download_possible = True
                elif response.status_code == 401 or response.status_code == 403:
                    test_results.append(f"{api_type}:{endpoint} (Auth Required)")
            except:
                pass

    return download_possible, test_results

def check_noaa_domain(url):
    """Comprehensive check of NOAA domain for data API capabilities"""
    result = {
        'parent_domain': url,
        'status_code': None,
        'auth_required': 'Unknown',
        'api_type': 'Unknown',
        'data_downloadable': 'Unknown',
        'test_results': '',
        'content_type': 'N/A',
        'error': None
    }

    try:
        print(f"  Testing: {url}")

        # Try GET request
        response = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        status = response.status_code
        result['status_code'] = status
        result['content_type'] = response.headers.get('Content-Type', 'N/A')

        # Check authentication
        if status in [401, 403]:
            result['auth_required'] = 'Yes'
        elif 200 <= status < 300:
            result['auth_required'] = 'No'

        # Identify API type
        response_text = response.text[:5000] if hasattr(response, 'text') else ''
        api_types = identify_api_type(url, response_text)
        result['api_type'] = ', '.join(api_types)

        # Test if data is downloadable
        if result['auth_required'] == 'No':
            download_possible, test_results = test_data_download(url, api_types)
            result['data_downloadable'] = 'Yes' if download_possible else 'Unknown'
            result['test_results'] = '; '.join(test_results) if test_results else 'No test endpoints succeeded'
        elif result['auth_required'] == 'Yes':
            result['data_downloadable'] = 'Unknown - Auth Required'
            result['test_results'] = 'Cannot verify without credentials'

    except requests.Timeout:
        result['error'] = 'Timeout'
    except requests.ConnectionError:
        result['error'] = 'Connection Error'
    except Exception as e:
        result['error'] = str(e)[:100]

    return result

def main():
    print("=" * 70)
    print("Checking NOAA-Exclusive Domains for Data API Capabilities")
    print("=" * 70)

    # Read NOAA-exclusive domains
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"\n📂 Loaded {len(df)} NOAA-exclusive parent domains from {INPUT_FILE}")
    except FileNotFoundError:
        print(f"❌ Error: {INPUT_FILE} not found.")
        print(f"   Please run count_parent_domains.py first.")
        return

    domains = df['parent_domain'].tolist()
    results = []

    print(f"\n🔍 Testing each domain for API capabilities and data download support...\n")

    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}")
        result = check_noaa_domain(domain)
        results.append(result)

        # Print summary
        print(f"  → Status: {result['status_code']} | Auth: {result['auth_required']} | Type: {result['api_type']}")
        print(f"  → Data Downloadable: {result['data_downloadable']}")
        if result['test_results']:
            print(f"  → Tests: {result['test_results']}")
        print()

        time.sleep(SLEEP)

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_FILE, index=False)

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(results_df)
    downloadable = len(results_df[results_df['data_downloadable'] == 'Yes'])
    auth_required = len(results_df[results_df['auth_required'] == 'Yes'])
    public_access = len(results_df[results_df['auth_required'] == 'No'])

    print(f"Total NOAA-exclusive domains: {total}")
    print(f"  ✅ Public access (no auth): {public_access} ({public_access/total*100:.1f}%)")
    print(f"  🔒 Authentication required: {auth_required} ({auth_required/total*100:.1f}%)")
    print(f"  📥 Data downloadable (verified): {downloadable} ({downloadable/total*100:.1f}%)")

    # API type breakdown
    print("\n" + "=" * 70)
    print("API Types Identified:")
    print("=" * 70)

    api_type_counts = {}
    for _, row in results_df.iterrows():
        api_types = row['api_type'].split(', ')
        for api_type in api_types:
            api_type_counts[api_type] = api_type_counts.get(api_type, 0) + 1

    for api_type, count in sorted(api_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {api_type}: {count}")

    # Show downloadable data APIs
    downloadable_df = results_df[results_df['data_downloadable'] == 'Yes']
    if len(downloadable_df) > 0:
        print("\n" + "=" * 70)
        print(f"✅ Verified Data-Downloadable APIs ({len(downloadable_df)}):")
        print("=" * 70)
        for _, row in downloadable_df.iterrows():
            print(f"  • {row['parent_domain']}")
            print(f"    Type: {row['api_type']} | {row['test_results']}")

    # Show APIs needing auth
    auth_df = results_df[results_df['auth_required'] == 'Yes']
    if len(auth_df) > 0:
        print("\n" + "=" * 70)
        print(f"🔒 APIs Requiring Authentication ({len(auth_df)}):")
        print("=" * 70)
        for _, row in auth_df.iterrows():
            print(f"  • {row['parent_domain']} (Type: {row['api_type']})")

    print("\n" + "=" * 70)
    print(f"✅ Results saved to: {OUTPUT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
