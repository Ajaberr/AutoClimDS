import requests
import json
import time
import os
import pandas as pd
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from cesm_variables import get_cesm_component

# Try to import geopandas for boundary file processing
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

##############################
#  CONFIG
##############################
NASA_API_BASE_URL = "https://cmr.earthdata.nasa.gov/search"
HEADERS = {"User-Agent": "NASA-KG-Extractor/1.0"}

##############################
#  CONFIG: Mapbox Geocoding API
##############################
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "")

# Rate limiting for Mapbox (10 requests per second)
MAPBOX_REQUESTS_PER_SECOND = 10
_last_mapbox_request_times = []

##############################
#  (1) Fetch Data
##############################
def fetch_nasa_cmr_all_pages(page_size=200, max_pages=None):
    """
    Fetches dataset 'collections' from NASA's CMR API using both JSON and UMM-JSON formats.
    - page_size: results per page (default: 200)
    - max_pages: limit total pages (default: None for unlimited)
    Returns a list of all available dataset entries.
    """
    all_data = []
    page_num = 1

    while True:
        # Try both formats for each page
        json_data = []
        umm_json_data = []
        
        # 1. Fetch regular JSON format
        cmr_url_json = "https://cmr.earthdata.nasa.gov/search/collections.json"
        params = {"page_size": page_size, "page_num": page_num}
        
        try:
            response = requests.get(cmr_url_json, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if ("feed" in data and "entry" in data["feed"] and data["feed"]["entry"]):
                json_data = data["feed"]["entry"]
                print(f"Fetched {len(json_data)} entries from JSON format (page {page_num})")
        except Exception as e:
            print(f"Error fetching JSON format (page {page_num}): {e}")
        
        # 2. Fetch UMM-JSON format
        cmr_url_umm = "https://cmr.earthdata.nasa.gov/search/collections.umm_json"
        
        try:
            response = requests.get(cmr_url_umm, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "items" in data and data["items"]:
                umm_json_data = data["items"]
                print(f"Fetched {len(umm_json_data)} entries from UMM-JSON format (page {page_num})")
        except Exception as e:
            print(f"Error fetching UMM-JSON format (page {page_num}): {e}")
        
        # 3. Merge the data from both formats
        merged_entries = merge_formats(json_data, umm_json_data)
        
        if not merged_entries:
            print(f"No data found in either format for page {page_num}")
            break
            
        all_data.extend(merged_entries)
        print(f"Total datasets after merging: {len(all_data)}")

        page_num += 1
        time.sleep(0.2)  # small delay to avoid rapid requests

        if max_pages and page_num > max_pages:
            break

    return all_data


def merge_formats(json_entries, umm_entries):
    """
    Merge data from JSON and UMM-JSON formats, preferring non-empty values.
    """
    merged = []
    
    # Create a mapping of concept_id to UMM entry for easy lookup
    umm_map = {}
    for umm_item in umm_entries:
        if "meta" in umm_item and "concept-id" in umm_item["meta"]:
            concept_id = umm_item["meta"]["concept-id"]
            umm_map[concept_id] = umm_item
    
    # Process each JSON entry and merge with corresponding UMM data
    for json_entry in json_entries:
        concept_id = json_entry.get("id", "")
        umm_item = umm_map.get(concept_id, {})
        
        # Start with JSON data
        merged_entry = {}
        
        # Basic fields from JSON
        merged_entry["short_name"] = json_entry.get("short_name", "")
        merged_entry["title"] = json_entry.get("title", "")
        merged_entry["summary"] = json_entry.get("summary", "")
        merged_entry["links"] = json_entry.get("links", [])
        merged_entry["data_center"] = json_entry.get("data_center", "")
        merged_entry["dataset_id"] = json_entry.get("dataset_id", "")
        merged_entry["entry_id"] = json_entry.get("entry_id", "")
        merged_entry["version_id"] = json_entry.get("version_id", "")
        merged_entry["processing_level_id"] = json_entry.get("processing_level_id", "")
        merged_entry["online_access_flag"] = json_entry.get("online_access_flag", False)
        merged_entry["browse_flag"] = json_entry.get("browse_flag", False)
        merged_entry["organizations"] = json_entry.get("organizations", [])
        merged_entry["platforms"] = json_entry.get("platforms", [])
        merged_entry["consortiums"] = json_entry.get("consortiums", [])
        merged_entry["boxes"] = json_entry.get("boxes", [])
        merged_entry["polygons"] = json_entry.get("polygons", [])
        merged_entry["points"] = json_entry.get("points", [])
        merged_entry["time_start"] = json_entry.get("time_start", "")
        merged_entry["time_end"] = json_entry.get("time_end", "")
        merged_entry["updated"] = json_entry.get("updated", "")
        merged_entry["coordinate_system"] = json_entry.get("coordinate_system", "")
        merged_entry["concept_id"] = json_entry.get("id", "")
        merged_entry["original_format"] = json_entry.get("original_format", "")
        
        # Initialize fields that might come from UMM
        merged_entry["data_format"] = json_entry.get("data_format", "")
        merged_entry["science_keywords"] = json_entry.get("science_keywords", [])
        merged_entry["doi"] = json_entry.get("doi", "")
        merged_entry["doi_authority"] = json_entry.get("doi_authority", "")
        merged_entry["collection_data_type"] = json_entry.get("collection_data_type", "")
        merged_entry["data_set_language"] = json_entry.get("data_set_language", "en-US")
        merged_entry["archive_center"] = json_entry.get("archive_center", "")
        merged_entry["native_id"] = json_entry.get("native_id", "")
        merged_entry["granule_count"] = json_entry.get("granule_count", 0)
        merged_entry["day_night_flag"] = json_entry.get("day_night_flag", "")
        merged_entry["cloud_cover"] = json_entry.get("cloud_cover", "")
        merged_entry["projects"] = json_entry.get("projects", [])
        merged_entry["related_urls"] = json_entry.get("related_urls", [])
        merged_entry["contact_persons"] = json_entry.get("contact_persons", [])
        merged_entry["contact_groups"] = json_entry.get("contact_groups", [])
        merged_entry["variables"] = json_entry.get("variables", [])
        merged_entry["additional_attributes"] = json_entry.get("additional_attributes", [])
        
        # Now merge with UMM data if available
        if umm_item and "umm" in umm_item:
            umm = umm_item["umm"]
            
            # Fill in missing fields from UMM
            if not merged_entry["data_format"]:
                merged_entry["data_format"] = umm.get("DataFormat", "")
                
            if not merged_entry["science_keywords"]:
                merged_entry["science_keywords"] = umm.get("ScienceKeywords", [])
                
            if not merged_entry["doi"]:
                doi_info = umm.get("DOI", {})
                if doi_info:
                    merged_entry["doi"] = doi_info.get("DOI", "")
                    merged_entry["doi_authority"] = doi_info.get("Authority", "")
                    
            if not merged_entry["projects"]:
                merged_entry["projects"] = umm.get("Projects", [])
                
            if not merged_entry["related_urls"]:
                merged_entry["related_urls"] = umm.get("RelatedUrls", [])
                
            if not merged_entry["contact_persons"]:
                merged_entry["contact_persons"] = umm.get("ContactPersons", [])
                
            if not merged_entry["contact_groups"]:
                merged_entry["contact_groups"] = umm.get("ContactGroups", [])
                
            if not merged_entry["variables"]:
                merged_entry["variables"] = umm.get("Variables", [])
                
            if not merged_entry["additional_attributes"]:
                merged_entry["additional_attributes"] = umm.get("AdditionalAttributes", [])
                
            # Update processing level if not available
            if not merged_entry["processing_level_id"]:
                processing_level = umm.get("ProcessingLevel", {})
                if processing_level:
                    merged_entry["processing_level_id"] = processing_level.get("Id", "")
                    
            # Update collection data type if not available
            if not merged_entry["collection_data_type"]:
                merged_entry["collection_data_type"] = umm.get("CollectionDataType", "")
                
            # Update archive center if not available
            if not merged_entry["archive_center"]:
                merged_entry["archive_center"] = umm.get("ArchiveCenter", "")
                
            # Update data language if not available
            if not merged_entry["data_set_language"] or merged_entry["data_set_language"] == "en-US":
                merged_entry["data_set_language"] = umm.get("DataLanguage", "en-US")
                
            # Update temporal information if not available
            if not merged_entry["time_start"] or not merged_entry["time_end"]:
                temporal_extents = umm.get("TemporalExtents", [])
                if temporal_extents and "RangeDateTimes" in temporal_extents[0]:
                    range_times = temporal_extents[0]["RangeDateTimes"]
                    if range_times:
                        if not merged_entry["time_start"]:
                            merged_entry["time_start"] = range_times[0].get("BeginningDateTime", "")
                        if not merged_entry["time_end"]:
                            merged_entry["time_end"] = range_times[0].get("EndingDateTime", "")
                            
            # Update spatial information if not available
            if not merged_entry["boxes"] and not merged_entry["polygons"] and not merged_entry["points"]:
                spatial_extent = umm.get("SpatialExtent", {})
                if spatial_extent and "HorizontalSpatialDomain" in spatial_extent:
                    horizontal_domain = spatial_extent["HorizontalSpatialDomain"]
                    if "Geometry" in horizontal_domain:
                        geometry = horizontal_domain["Geometry"]
                        
                        # Extract bounding rectangles
                        if "BoundingRectangles" in geometry and geometry["BoundingRectangles"]:
                            boxes = []
                            for rect in geometry["BoundingRectangles"]:
                                box = f"{rect.get('SouthBoundingCoordinate', 0)} {rect.get('WestBoundingCoordinate', 0)} {rect.get('NorthBoundingCoordinate', 0)} {rect.get('EastBoundingCoordinate', 0)}"
                                boxes.append(box)
                            merged_entry["boxes"] = boxes
                            
                        # Extract points
                        if "Points" in geometry and geometry["Points"]:
                            points = []
                            for point in geometry["Points"]:
                                pt = f"{point.get('Latitude', 0)} {point.get('Longitude', 0)}"
                                points.append(pt)
                            merged_entry["points"] = points
                            
                        # Extract polygons
                        if "GPolygons" in geometry and geometry["GPolygons"]:
                            polygons = []
                            for poly in geometry["GPolygons"]:
                                if "Boundary" in poly and poly["Boundary"]:
                                    points = poly["Boundary"].get("Points", [])
                                    poly_points = []
                                    for point in points:
                                        poly_points.append(f"{point.get('Latitude', 0)} {point.get('Longitude', 0)}")
                                    polygons.append(poly_points)
                            merged_entry["polygons"] = polygons
        
        # Set data_center from organizations if available
        if merged_entry["organizations"] and not merged_entry["data_center"]:
            merged_entry["data_center"] = merged_entry["organizations"][0]
            
        merged.append(merged_entry)
    
    return merged


##############################
#  (2) Geometry Helpers
##############################
def extract_polygons(geom):
    """
    Ensure we only return Polygon or MultiPolygon.
    If 'geom' is a GeometryCollection, extract any polygons inside.
    Return None if there's nothing suitable.
    """
    if geom is None:
        return None

    gtype = geom.geom_type
    if gtype in ["Polygon", "MultiPolygon"]:
        return geom
    elif gtype == "GeometryCollection":
        polys = [g for g in geom.geoms if g.geom_type in ["Polygon", "MultiPolygon"]]
        if not polys:
            return None
        if len(polys) == 1:
            return polys[0]
        return unary_union(polys)
    else:
        return None


def parse_cmr_spatial(boxes=None, polygons=None, points=None):
    """
    Convert NASA CMR 'boxes', 'polygons', or 'points' into
    a single Polygon/MultiPolygon if possible.
    Skips or merges geometry as needed.
    """
    shapes = []

    # 1) Boxes -> Polygons
    if boxes:
        for b in boxes:
            coords = b.split()
            if len(coords) == 4:
                # [SouthLat, WestLon, NorthLat, EastLon]
                southLat, westLon, northLat, eastLon = map(float, coords)
                poly = Polygon([
                    (westLon, southLat),
                    (eastLon, southLat),
                    (eastLon, northLat),
                    (westLon, northLat),
                    (westLon, southLat),
                ])
                shapes.append(poly)

    # 2) Polygons
    if polygons:
        for poly_list in polygons:
            for poly_str in poly_list:
                coords = poly_str.split()
                if len(coords) < 6:
                    continue
                pairs = []
                for i in range(0, len(coords), 2):
                    lat = float(coords[i])
                    lon = float(coords[i+1])
                    pairs.append((lon, lat))
                if pairs and pairs[0] != pairs[-1]:
                    pairs.append(pairs[0])
                if len(pairs) > 2:
                    shapes.append(Polygon(pairs))

    # Skipping points in this example

    if not shapes:
        return None
    if len(shapes) == 1:
        merged_geom = shapes[0]
    else:
        merged_geom = unary_union(shapes)

    return extract_polygons(merged_geom)


##############################
#  (3) Mapbox Geocoding API Helpers
##############################
def mapbox_rate_limit():
    """Smart rate limiting for Mapbox API (10 requests per second)"""
    global _last_mapbox_request_times
    
    current_time = time.time()
    
    # Remove requests older than 1 second
    _last_mapbox_request_times = [t for t in _last_mapbox_request_times if current_time - t < 1.0]
    
    # If we've made 10 requests in the last second, wait
    if len(_last_mapbox_request_times) >= MAPBOX_REQUESTS_PER_SECOND:
        sleep_time = 1.0 - (current_time - _last_mapbox_request_times[0])
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    _last_mapbox_request_times.append(time.time())

def get_location_info_from_coords(lat, lon, max_retries=3):
    """
    Use Mapbox Geocoding API to get location information from coordinates (reverse geocoding).
    Returns a dictionary with address components.
    """
    # Check if coordinates are valid
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return {"country": "unavailable", "reason": "invalid_coordinates"}
    
    # Apply rate limiting
    mapbox_rate_limit()
    
    # Mapbox reverse geocoding URL
    url = f"{MAPBOX_BASE_URL}/{lon},{lat}.json"
    params = {
        'access_token': MAPBOX_ACCESS_TOKEN,
        'types': 'country,region,postcode,district,place,locality,neighborhood,address',
        'limit': 1
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract address information from Mapbox response
            location_info = {}
            
            if 'features' in data and data['features']:
                feature = data['features'][0]
                context = feature.get('context', [])
                
                # Parse Mapbox response structure
                place_name = feature.get('place_name', '')
                place_type = feature.get('place_type', [])
                
                # Extract location components from context
                for ctx in context:
                    ctx_type = ctx.get('id', '').split('.')[0] if ctx.get('id') else ''
                    ctx_text = ctx.get('text', '')
                    ctx_short_code = ctx.get('short_code', '')
                    
                    if ctx_type == 'country':
                        location_info['country'] = ctx_text
                        if ctx_short_code:
                            location_info['country_code'] = ctx_short_code.lower()
                    elif ctx_type == 'region':
                        location_info['state'] = ctx_text
                    elif ctx_type in ['place', 'locality']:
                        if not location_info.get('city'):
                            location_info['city'] = ctx_text
                    elif ctx_type == 'district':
                        location_info['county'] = ctx_text
                
                # Handle case where feature itself is the city/place
                if 'place' in place_type and not location_info.get('city'):
                    location_info['city'] = feature.get('text', '')
                
                # Set defaults for missing fields
                location_info.setdefault('city', '')
                location_info.setdefault('country', '')
                location_info.setdefault('country_code', '')
                location_info.setdefault('state', '')
                location_info.setdefault('county', '')
                
                # Try to get continent info from boundary data if available
                try:
                    from shapely.geometry import Point
                    point = Point(lon, lat)
                    boundary_classification = classify_location_offline_fast(point)
                    
                    if boundary_classification and boundary_classification.get("boundary_data"):
                        for record in boundary_classification["boundary_data"]:
                            for field_name, value in record.items():
                                field_upper = str(field_name).upper()
                                if 'CONTINENT' in field_upper and value:
                                    location_info['continent'] = str(value).title()
                                    break
                except Exception:
                    # If boundary data unavailable, leave continent empty
                    # Mapbox API might provide continent info directly
                    pass
                
                return location_info
                
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 + attempt)
                continue
           
    return {"country": "unavailable", "reason": "api_error"}




def load_country_continent_mapping():
    """Load country to continent mapping from countries.json"""
    try:
        import json
        import os
        countries_file = os.path.join(os.path.dirname(__file__), "countries.json")
        with open(countries_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load countries.json: {e}")
        return {}

def classify_location_from_bbox(boxes):
    """
    Classify location scope from bounding box using countries.json for continent mapping.
    Returns classification based on actual country-continent relationships.
    """
    if not boxes:
        return {"scope": "unclassified", "place_names": []}
    
    # Take the first bounding box
    coords = boxes[0].split()
    if len(coords) != 4:
        return {"scope": "unclassified", "place_names": []}
    
    try:
        south_lat, west_lon, north_lat, east_lon = map(float, coords)
        
        # Create geometry from bounding box
        from shapely.geometry import Polygon
        bbox_polygon = Polygon([
            (west_lon, south_lat),
            (east_lon, south_lat), 
            (east_lon, north_lat),
            (west_lon, north_lat),
            (west_lon, south_lat)
        ])
        
        # Use offline boundary classification to get actual geographic coverage
        classification = classify_location_offline_fast(bbox_polygon)
        
        if classification and classification.get("method") == "offline_boundaries_fast":
            # Get countries intersected by the bounding box
            countries = classification.get("countries", [])
            place_names = classification.get("place_names", [])
            
            if not countries:
                return {"scope": "ocean", "place_names": place_names}
            
            # Load country-continent mapping
            country_continent_map = load_country_continent_mapping()
            
            # Map countries to continents
            continents = set()
            for country in countries:
                # Try exact match first
                if country in country_continent_map:
                    continents.add(country_continent_map[country])
                else:
                    # Try fuzzy matching for country name variations
                    for country_key, continent in country_continent_map.items():
                        if country.lower() in country_key.lower() or country_key.lower() in country.lower():
                            continents.add(continent)
                            break
            
            # Determine scope based on continent coverage
            if len(continents) > 1:
                scope = "global"  # Spans multiple continents
            elif len(continents) == 1:
                if len(countries) > 1:
                    scope = "continental"  # Multiple countries, same continent
                else:
                    scope = "country"  # Single country
            else:
                # No continent mapping found, fall back to country count
                if len(countries) > 3:
                    scope = "multinational"
                elif len(countries) > 1:
                    scope = "regional"
                else:
                    scope = "country"
            
            return {
                "scope": scope,
                "place_names": place_names,
                "countries": countries,
                "continents": list(continents),
                "total_countries": len(countries),
                "total_continents": len(continents)
            }
        
        # Fallback to API-based classification if boundary data unavailable
        center_lat = (south_lat + north_lat) / 2
        center_lon = (west_lon + east_lon) / 2
        location_info = get_location_info_from_coords(center_lat, center_lon)
        
        if location_info.get("country") == "unavailable":
            return {"scope": "unclassified", "place_names": []}
        
        # Extract place names from API response
        place_names = []
        for key in ['city', 'town', 'village', 'municipality', 'county', 'state', 'country', 'continent']:
            if key in location_info and location_info[key]:
                place_names.append(location_info[key])
        
        place_names = list(dict.fromkeys(place_names))
        
        # Simple fallback classification
        return {
            "scope": "regional",
            "place_names": place_names
        }
        
    except Exception as e:
        return {"scope": "unclassified", "place_names": []}

def get_location_from_geometry(geometry):
    """
    Extract location information from a Shapely geometry using countries.json for continent mapping.
    """
    if geometry is None:
        return {"scope": "unclassified", "place_names": []}
    
    try:
        # Use offline boundary classification for data-driven analysis
        classification = classify_location_offline_fast(geometry)
        
        if classification and classification.get("method") == "offline_boundaries_fast":
            # Get countries intersected by the geometry
            countries = classification.get("countries", [])
            place_names = classification.get("place_names", [])
            
            if not countries:
                return {"scope": "ocean", "place_names": place_names}
            
            # Load country-continent mapping
            country_continent_map = load_country_continent_mapping()
            
            # Map countries to continents
            continents = set()
            for country in countries:
                # Try exact match first
                if country in country_continent_map:
                    continents.add(country_continent_map[country])
                else:
                    # Try fuzzy matching for country name variations
                    for country_key, continent in country_continent_map.items():
                        if country.lower() in country_key.lower() or country_key.lower() in country.lower():
                            continents.add(continent)
                            break
            
            # Determine scope based on continent coverage
            if len(continents) > 1:
                scope = "global"  # Spans multiple continents
            elif len(continents) == 1:
                if len(countries) > 1:
                    scope = "continental"  # Multiple countries, same continent
                else:
                    scope = "country"  # Single country
            else:
                # No continent mapping found, fall back to country count
                if len(countries) > 3:
                    scope = "multinational"
                elif len(countries) > 1:
                    scope = "regional"
                else:
                    scope = "country"
            
            return {
                "scope": scope,
                "place_names": place_names,
                "countries": countries,
                "continents": list(continents),
                "total_countries": len(countries),
                "total_continents": len(continents)
            }
        
        # Fallback to API-based classification if boundary data unavailable
        centroid = geometry.centroid
        lat, lon = centroid.y, centroid.x
        location_info = get_location_info_from_coords(lat, lon)
        
        if location_info.get("country") == "unavailable":
            return {"scope": "unclassified", "place_names": []}
        
        # Extract place names from API response
        place_names = []
        for key in ['city', 'town', 'village', 'municipality', 'county', 'state', 'country', 'continent']:
            if key in location_info and location_info[key]:
                place_names.append(location_info[key])
        
        place_names = list(dict.fromkeys(place_names))
        
        # Simple fallback classification
        return {
            "scope": "regional",
            "place_names": place_names
        }
        
    except Exception as e:
        return {"scope": "unclassified", "place_names": []}


def classify_location(coordinates, location_info=None):
    """
    Classify location based on coordinates using data-driven geographic analysis.
    Removes hardcoded country mappings in favor of boundary data.
    """
    lat, lon = coordinates
    
    # Create point geometry
    from shapely.geometry import Point
    point = Point(lon, lat)
    
    # Try to use boundary data for classification
    try:
        classification = classify_location_offline_fast(point)
        
        if classification and classification.get("method") == "offline_boundaries_fast":
            # Use actual boundary data for classification
            categories = []
            
            # Add place names from boundary data
            place_names = classification.get("place_names", [])
            boundary_data = classification.get("boundary_data", [])
            
            # Extract geographic information from boundary attributes
            for record in boundary_data:
                for field_name, value in record.items():
                    field_upper = str(field_name).upper()
                    value_str = str(value).strip() if value else ""
                    
                    # Look for continent, region, or other geographic classification fields
                    if any(geo_field in field_upper for geo_field in ['CONTINENT', 'REGION', 'SUBREGION']):
                        if value_str and value_str.lower() not in ['null', 'none', 'unknown', 'nan']:
                            categories.append(value_str.title())
            
            # Add coordinate-based classifications
            if lat > 66.5:  # Arctic Circle
                categories.append('Arctic')
            elif lat < -66.5:  # Antarctic Circle
                categories.append('Antarctic')
            elif abs(lat) <= 23.5:  # Tropics
                categories.append('Tropical')
            
            # Add place names as categories
            categories.extend(place_names)
            
            # Remove duplicates
            categories = list(dict.fromkeys(categories))
            
            return categories
    
    except Exception:
        pass
    
    # Fallback to API-based classification
    if location_info is None:
        location_info = get_location_info_from_coords(lat, lon)
    
    if location_info.get("country") == "unavailable":
        return ["Unknown"]
    
    # Extract available information without hardcoded mappings
    categories = []
    
    # Add available place information
    for key in ['continent', 'country', 'state', 'city']:
        if key in location_info and location_info[key]:
            categories.append(location_info[key].title())
    
    # Add coordinate-based classifications
    if lat > 66.5:
        categories.append('Arctic')
    elif lat < -66.5:
        categories.append('Antarctic')
    elif abs(lat) <= 23.5:
        categories.append('Tropical')
    
    # Ocean classification for coordinates in water
    if not categories or all(cat.lower() in ['ocean', 'sea'] for cat in categories):
        if abs(lat) < 10:
            categories.append('Equatorial Waters')
        elif lat > 50:
            categories.append('Northern Waters')
        elif lat < -50:
            categories.append('Southern Waters')
    
    # Remove duplicates and return
    return list(dict.fromkeys(categories)) if categories else ["Unknown"]


##############################
#  (3.5) Offline Boundary Detection
##############################
def load_boundary_data():
    """Load country boundary data from shapefile with spatial indexing"""
    global BOUNDARIES_DATA, BOUNDARIES_SINDEX
    if not GEOPANDAS_AVAILABLE:
        return None
        
    try:
        boundaries_path = os.path.join(os.path.dirname(__file__), "boundaries", "boundaries.shp")
        if os.path.exists(boundaries_path):
            BOUNDARIES_DATA = gpd.read_file(boundaries_path)
            
            # Pre-convert to EPSG:4326 if not already in that CRS
            if BOUNDARIES_DATA.crs != 'EPSG:4326':
                print(f"Converting boundary CRS from {BOUNDARIES_DATA.crs} to EPSG:4326...")
                BOUNDARIES_DATA = BOUNDARIES_DATA.to_crs('EPSG:4326')
            
            # Create spatial index for fast lookups
            print("Building spatial index for boundary data...")
            BOUNDARIES_SINDEX = BOUNDARIES_DATA.sindex
            
            print(f"Loaded {len(BOUNDARIES_DATA)} country boundaries with spatial index (CRS: {BOUNDARIES_DATA.crs})")
            return BOUNDARIES_DATA
        else:
            print(f"Boundary file not found at: {boundaries_path}")
            return None
    except Exception as e:
        print(f"Error loading boundary data: {e}")
        return None

# Global variables to cache boundary data and spatial index
BOUNDARIES_DATA = None
BOUNDARIES_SINDEX = None

def classify_location_offline_fast(geometry):
    """
    Fast location classification using spatial indexing and point-in-polygon.
    Much faster than full overlay operations.
    """
    global BOUNDARIES_DATA, BOUNDARIES_SINDEX
    
    if not GEOPANDAS_AVAILABLE:
        return {"scope": "unclassified", "place_names": [], "method": "no_geopandas"}
    
    if BOUNDARIES_DATA is None or BOUNDARIES_SINDEX is None:
        BOUNDARIES_DATA = load_boundary_data()
        
    if BOUNDARIES_DATA is None:
        return {"scope": "unclassified", "place_names": [], "method": "no_boundaries"}
    
    try:
        # Use centroid for point-in-polygon test (much faster)
        if geometry.geom_type in ['Point']:
            test_point = geometry
        else:
            test_point = geometry.centroid
            
        # Use spatial index to find potential intersecting countries (much faster than checking all 258)
        possible_matches_idx = list(BOUNDARIES_SINDEX.intersection(geometry.bounds))
        
        if not possible_matches_idx:
            return {"scope": "ocean", "place_names": ["Ocean"], "method": "offline_boundaries"}
        
        # Get only the potential matching countries for overlay (much smaller subset)
        potential_countries = BOUNDARIES_DATA.iloc[possible_matches_idx]
        
        # Create GeoDataFrame for the geometry
        test_gdf = gpd.GeoDataFrame([1], geometry=[geometry], crs='EPSG:4326')
        
        # Use overlay with only the potential matches (much faster than full dataset)
        intersects = gpd.overlay(test_gdf, potential_countries, how='intersection')
        
        if len(intersects) == 0:
            return {"scope": "ocean", "place_names": ["Ocean"], "method": "offline_boundaries"}
        
        # Extract country information from intersections
        intersecting_countries = []
        boundary_records = []
        
        # Find the country name field in the boundary data
        country_fields = ['NAME', 'CNTRY_NAME', 'COUNTRY', 'NAME_EN', 'ADMIN', 'SOVEREIGNT', 'NAME_LONG']
        country_field = None
        
        for field in country_fields:
            if field in potential_countries.columns:
                country_field = field
                break
        
        if country_field:
            # Get unique countries that intersect
            country_names = intersects[country_field].dropna().unique()
            for name in country_names:
                if name and str(name) != 'nan':
                    intersecting_countries.append(str(name))
        
        # Extract ALL available fields from the boundary data for additional geographic info
        for idx, row in intersects.iterrows():
            record_data = {}
            for col in intersects.columns:
                if col not in ['geometry'] and not str(col).startswith('index'):
                    value = row[col]
                    if value is not None and str(value) != 'nan' and str(value).strip():
                        record_data[str(col)] = str(value).strip()
            boundary_records.append(record_data)
        
        # Remove duplicates
        intersecting_countries = list(set(intersecting_countries))
        place_names = intersecting_countries.copy()
        
        # Extract additional geographic info
        additional_places = extract_geographic_info_from_boundaries(boundary_records)
        for place in additional_places:
            if place and place not in place_names:
                place_names.append(place)
        
        # Return raw data without classification - let upper functions handle scope determination
        return {
            "place_names": place_names,
            "countries": intersecting_countries,
            "total_countries": len(intersecting_countries),
            "boundary_data": boundary_records,
            "method": "offline_boundaries_fast"
        }
        
    except Exception as e:
        print(f"Error in fast offline classification: {str(e)}")
        return {"scope": "unclassified", "place_names": [], "method": "error"}

def classify_location_offline(geometry):
    """
    Classify location using offline boundary files.
    Uses fast spatial indexing and point-in-polygon operations.
    """
    # Use the fast version
    return classify_location_offline_fast(geometry)


def get_location_from_geometry_offline(geometry):
    """
    Extract location information from geometry using offline boundary files.
    Extracts all available geographic information from boundary data.
    """
    if geometry is None:
        return {"scope": "unclassified", "place_names": []}
    
    try:
        classification = classify_location_offline(geometry)
        
        # Extract additional geographic information from boundary data
        if classification.get("boundary_data"):
            additional_info = extract_geographic_info_from_boundaries(classification["boundary_data"])
            
            # Add any additional place names (continents, regions, etc.)
            for info in additional_info:
                if info and info not in classification["place_names"]:
                    classification["place_names"].append(info)
        
        return classification
        
    except Exception as e:
        print(f"Error in offline geometry classification: {e}")
        return {"scope": "unclassified", "place_names": []}


def extract_geographic_info_from_boundaries(boundary_records):
    """
    Extract all geographic information from boundary data records.
    Looks for continent, region, subregion, and other geographic identifiers
    in the actual boundary file fields instead of hardcoded mappings.
    """
    geographic_info = []
    
    if not boundary_records:
        return geographic_info
    
    # Fields that typically contain continent/region information
    geographic_fields = [
        'CONTINENT', 'CONTINENT_', 'CONT', 'REGION', 'REGION_WB', 'SUBREGION', 
        'SUB_REGION', 'REGION_UN', 'REGION_CB', 'GEOGRAPHIC', 'GEO_REGION',
        'WORLD_REGION', 'MAJOR_REGION', 'MACRO_REGION', 'AREA', 'ZONE'
    ]
    
    for record in boundary_records:
        for field_name, value in record.items():
            # Ensure field_name and value are strings
            field_name_str = str(field_name) if field_name is not None else ""
            value_str = str(value) if value is not None else ""
            
            # Check if this field contains geographic information
            field_upper = field_name_str.upper()
            
            # Look for continent/region fields
            if any(geo_field in field_upper for geo_field in geographic_fields):
                if value_str and value_str.strip() and value_str.lower() not in ['null', 'none', 'unknown', 'nan']:
                    cleaned_value = value_str.strip().title()
                    if cleaned_value not in geographic_info:
                        geographic_info.append(cleaned_value)
            
            # Look for fields that end with common geographic suffixes
            elif any(field_upper.endswith(suffix) for suffix in ['_REGION', '_CONTINENT', '_AREA', '_ZONE']):
                if value_str and value_str.strip() and value_str.lower() not in ['null', 'none', 'unknown', 'nan']:
                    cleaned_value = value_str.strip().title()
                    if cleaned_value not in geographic_info:
                        geographic_info.append(cleaned_value)
    
    return geographic_info


##############################
#  (4) Variable Extraction
##############################
def extract_cesm_variables(entry):
    """
    Extract variables directly from NASA CMR entry metadata without ML matching
    """
    variables = []
    
    # Extract science keywords if available
    science_keywords = entry.get("science_keywords", [])
    variables_from_keywords = []
    
    # Create variables from science keywords
    for keyword in science_keywords:
        if isinstance(keyword, dict):
            # Handle structured science keywords
            category = keyword.get("category", "")
            topic = keyword.get("topic", "")
            term = keyword.get("term", "")
            variable_term = keyword.get("variable_level_1", "")
            
            # Skip non-variable keywords
            if not variable_term and not term:
                continue
                
            # Create a variable node
            var_name = variable_term if variable_term else term
            dataset_id = entry.get("concept_id", entry.get("id", "unknown"))
            
            var_node = {
                "variable_id": f"{var_name}_{dataset_id}".replace(" ", "_"),
                "name": var_name,
                "standard_name": var_name,
                "long_name": f"{topic} {term} {variable_term}".strip(),
                "units": "unknown",
                "description": f"{category} > {topic} > {term} > {variable_term}".strip(),
                "source": "science_keywords",
                "dataset_id": dataset_id
            }
            
            variables.append(var_node)
        elif isinstance(keyword, str):
            # Handle string keywords
            variables_from_keywords.append(keyword)
    
    # Create variables from string keywords if needed
    if variables_from_keywords and not variables:
        for i, keyword in enumerate(variables_from_keywords):
            dataset_id = entry.get("concept_id", entry.get("id", "unknown"))
            var_node = {
                "variable_id": f"var_{i}_{dataset_id}".replace(" ", "_"),
                "name": keyword,
                "standard_name": keyword,
                "long_name": keyword,
                "units": "unknown",
                "description": keyword,
                "source": "keywords",
                "dataset_id": dataset_id
            }
            variables.append(var_node)
    
    # Extract variables from "variables" field if available
    if "variables" in entry and entry["variables"]:
        for var in entry["variables"]:
            if isinstance(var, dict):
                var_name = var.get("name", "unknown")
                dataset_id = entry.get("concept_id", entry.get("id", "unknown"))
                
                var_node = {
                    "variable_id": f"{var_name}_{dataset_id}".replace(" ", "_"),
                    "name": var_name,
                    "standard_name": var.get("standard_name", var_name),
                    "long_name": var.get("long_name", var_name),
                    "units": var.get("units", "unknown"),
                    "description": var.get("description", var_name),
                    "source": "variables",
                    "dataset_id": dataset_id
                }
                
                variables.append(var_node)
    
    # If no variables found, create a placeholder from the dataset title
    if not variables:
        title = entry.get("title", "")
        if title:
            words = title.split()
            potential_vars = [word for word in words if len(word) > 3 and word.isalpha()]
            
            if potential_vars:
                dataset_id = entry.get("concept_id", entry.get("id", "unknown"))
                var_node = {
                    "variable_id": f"title_var_{dataset_id}".replace(" ", "_"),
                    "name": potential_vars[0],
                    "standard_name": potential_vars[0],
                    "long_name": title,
                    "units": "unknown",
                    "description": f"Variable extracted from dataset title: {title}",
                    "source": "title",
                    "dataset_id": dataset_id
                }
                variables.append(var_node)
    
    # Return all variables (no artificial limit)
    return variables

def extract_cesm_components(entry):
    """
    Extract CESM components from NASA CMR entry
    """
    components = []
    used_components = set()  # Avoid duplicates
    
    # Get dataset ID for component linking
    dataset_id = entry.get("concept_id", "unknown")
    
    # Search for component indicators in various fields
    search_fields = [
        entry.get("title", ""),
        entry.get("summary", ""),
        entry.get("short_name", ""),
        " ".join(entry.get("science_keywords", [])) if entry.get("science_keywords") else "",
        " ".join(entry.get("platforms", [])) if entry.get("platforms") else ""
    ]
    
    combined_text = " ".join(search_fields).lower()
    
    # Check for component indicators
    component_indicators = {
        "atm": ["atmosphere", "atmospheric", "air", "wind", "precipitation", "cloud", "radiation", "weather", "climate", "cam", "temperature"],
        "ocn": ["ocean", "oceanic", "sea", "marine", "sst", "salinity", "current", "pop", "water temperature"],
        "lnd": ["land", "terrestrial", "soil", "vegetation", "surface", "clm", "runoff", "snow", "lai"],
        "ice": ["sea ice", "ice", "frozen", "cice", "arctic", "antarctic", "polar"],
        "rof": ["river", "discharge", "streamflow", "mosart", "runoff", "watershed"]
    }
    
    for comp_name, indicators in component_indicators.items():
        for indicator in indicators:
            if indicator in combined_text:
                comp_info = get_cesm_component(comp_name)
                if comp_info and comp_name not in used_components:
                    component_node = create_component_node(comp_info, dataset_id)
                    components.append(component_node)
                    used_components.add(comp_name)
                    break  # Only add each component once
    
    # If no components detected, try to infer from domain/discipline
    if not components:
        # Default to atmospheric component for most NASA datasets
        if any(term in combined_text for term in ["data", "satellite", "remote sensing", "earth"]):
            comp_info = get_cesm_component("atm")
            if comp_info:
                component_node = create_component_node(comp_info, dataset_id)
                components.append(component_node)
    
    return components


##############################
#  (4) Main Transformation
##############################
def transform_cmr_to_classes(all_entries):
    """
    1) Returns:
       original_output, individual_output, fail_count

    2) Creates all necessary classes for Neptune OpenCypher format
    """

    original_output = {
        "Dataset": [],
        "DataCategory": [],
        "DataFormat": [],
        "CoordinateSystem": [],
        "Location": [],
        "Station": [],
        "Organization": [],
        "Platform": [],
        "Consortium": [],
        "TemporalExtent": [],
        "Variable": [],      # NASA CMR variables (linked to datasets)
        "CESMVariable": [],  # CESM variables from CSV (separate category)
        "Component": [],     # Components will be extracted but not linked to datasets
        "Contact": [],       # Contact information
        "Project": [],       # Project information
        "RelatedUrl": [],    # Related URLs with types
        "SpatialResolution": [],   # Spatial resolution information
        "TemporalResolution": [],  # Temporal resolution information
        "Granule": [],       # Granule information
        "Instrument": [],    # Instrument information
        "ScienceKeyword": [], # Science keywords hierarchy
        "ProcessingLevel": [], # Processing level information
        "Relationship": []
    }

    individual_output = []
    geoms = []
    fail_count = 0
    
    # Extract metadata from all entries and link them to datasets
    all_cesm_variables = []  # CESM variables from CSV
    all_components = []
    all_contacts = []
    all_projects = []
    all_related_urls = []
    all_spatial_resolutions = []
    all_temporal_resolutions = []
    all_granules = []
    all_instruments = []     # NEW
    all_science_keywords = [] # NEW
    all_processing_levels = [] # NEW
    
    # Dictionaries to store metadata per dataset
    dataset_variables = {}  # dataset_id -> list of variables
    dataset_contacts = {}   # dataset_id -> list of contacts
    dataset_projects = {}   # dataset_id -> list of projects
    dataset_related_urls = {}  # dataset_id -> list of related URLs
    dataset_spatial_resolutions = {}  # dataset_id -> list of spatial resolutions
    dataset_temporal_resolutions = {}  # dataset_id -> list of temporal resolutions
    dataset_granules = {}   # dataset_id -> list of granules
    dataset_instruments = {}  # dataset_id -> list of instruments
    dataset_science_keywords = {}  # dataset_id -> list of science keywords
    dataset_processing_levels = {}  # dataset_id -> list of processing levels
    
    for entry in all_entries:
        dataset_id = entry.get("concept_id", entry.get("dataset_id", f"dataset_{len(original_output['Dataset'])}"))
        
        # Initialize per-dataset metadata lists
        dataset_variables[dataset_id] = []
        dataset_contacts[dataset_id] = []
        dataset_projects[dataset_id] = []
        dataset_related_urls[dataset_id] = []
        dataset_spatial_resolutions[dataset_id] = []
        dataset_temporal_resolutions[dataset_id] = []
        dataset_granules[dataset_id] = []
        dataset_instruments[dataset_id] = []
        dataset_science_keywords[dataset_id] = []
        dataset_processing_levels[dataset_id] = []
        
        # Extract variables from science keywords and variables field for this dataset
        science_keywords = entry.get("science_keywords", [])
        for keyword in science_keywords:
            if isinstance(keyword, dict):
                # Handle structured science keywords
                category = keyword.get("Category", "")
                topic = keyword.get("Topic", "")
                term = keyword.get("Term", "")
                variable_level_1 = keyword.get("VariableLevel1", "")
                
                # Skip non-variable keywords
                if not variable_level_1 and not term:
                    continue
                    
                # Create a variable node
                var_name = variable_level_1 if variable_level_1 else term
                var_id = f"var_{dataset_id}_{var_name}".replace(" ", "_").replace("-", "_")
                
                var_node = {
                    "variable_id": var_id,
                    "name": var_name,
                    "standard_name": var_name,
                    "long_name": f"{topic} {term} {variable_level_1}".strip(),
                    "units": "unknown",
                    "description": f"{category} > {topic} > {term} > {variable_level_1}".strip(),
                    "source": "science_keywords",
                    "variable_type": "nasa_cmr",  # Explicitly mark as NASA CMR variable
                    "dataset_id": dataset_id  # Link to dataset
                }
                
                dataset_variables[dataset_id].append(var_node)
                
                # Also store the science keyword hierarchy
                keyword_id = f"kw_{category}_{topic}_{term}".replace(" ", "_").lower()
                science_keyword_node = {
                    "keyword_id": keyword_id,
                    "category": category,
                    "topic": topic,
                    "term": term,
                    "variable_level_1": variable_level_1,
                    "variable_level_2": keyword.get("VariableLevel2", ""),
                    "variable_level_3": keyword.get("VariableLevel3", ""),
                    "detailed_variable": keyword.get("DetailedVariable", "")
                }
                
                # Check if this science keyword already exists
                if not any(kw["keyword_id"] == keyword_id for kw in all_science_keywords):
                    all_science_keywords.append(science_keyword_node)
        
        # Extract variables from "variables" field if available
        if "variables" in entry and entry["variables"]:
            for var in entry["variables"]:
                if isinstance(var, dict):
                    var_name = var.get("Name", "unknown")
                    var_id = f"var_{dataset_id}_{var_name}".replace(" ", "_").replace("-", "_")
                    
                    var_node = {
                        "variable_id": var_id,
                        "name": var_name,
                        "standard_name": var.get("StandardName", var_name),
                        "long_name": var.get("LongName", var_name),
                        "units": var.get("Units", "unknown"),
                        "description": var.get("Description", var_name),
                        "source": "variables",
                        "variable_type": "nasa_cmr",  # Explicitly mark as NASA CMR variable
                        "dataset_id": dataset_id  # Link to dataset
                    }
                    
                    dataset_variables[dataset_id].append(var_node)
        
        # Extract components
        # Search for component indicators in various fields
        search_fields = [
            entry.get("title", ""),
            entry.get("summary", ""),
            entry.get("short_name", ""),
            " ".join([str(k) for k in entry.get("science_keywords", [])]) if entry.get("science_keywords") else "",
            " ".join([str(p) for p in entry.get("platforms", [])]) if entry.get("platforms") else ""
        ]
        
        combined_text = " ".join(search_fields).lower()
        
        # Check for component indicators
        component_indicators = {
            "atm": ["atmosphere", "atmospheric", "air", "wind", "precipitation", "cloud", "radiation", "weather", "climate", "cam", "temperature"],
            "ocn": ["ocean", "oceanic", "sea", "marine", "sst", "salinity", "current", "pop", "water temperature"],
            "lnd": ["land", "terrestrial", "soil", "vegetation", "surface", "clm", "runoff", "snow", "lai"],
            "ice": ["sea ice", "ice", "frozen", "cice", "arctic", "antarctic", "polar"],
            "rof": ["river", "discharge", "streamflow", "mosart", "runoff", "watershed"],
            "glc": ["glacier", "ice sheet", "cism", "greenland", "antarctica"],
            "wav": ["wave", "wavewatch", "ocean waves", "sea state"]
        }
        
        for comp_name, indicators in component_indicators.items():
            for indicator in indicators:
                if indicator in combined_text:
                    comp_info = get_cesm_component(comp_name)
                    if comp_info:
                        component_id = f"comp_{comp_name}"
                        component_node = {
                            "component_id": component_id,
                            "name": comp_info["full_name"],
                            "abbreviation": comp_info["abbreviation"],
                            "description": comp_info["description"],
                            "domain": comp_info["domain"]
                        }
                        
                        # Check if this component already exists
                        if not any(c["component_id"] == component_id for c in all_components):
                            all_components.append(component_node)
                        break  # Only add each component once per entry
        
        # Extract contacts for this dataset
        # Process contact_persons
        if "contact_persons" in entry and entry["contact_persons"]:
            for contact in entry["contact_persons"]:
                if isinstance(contact, dict):
                    contact_id = f"contact_person_{dataset_id}_{len(dataset_contacts[dataset_id])}"
                    contact_node = {
                        "contact_id": contact_id,
                        "type": "person",
                        "name": contact.get("FirstName", "") + " " + contact.get("LastName", ""),
                        "roles": contact.get("Roles", []),
                        "email": contact.get("Email", ""),
                        "organization": contact.get("ContactInformation", {}).get("OrganizationName", "") if contact.get("ContactInformation") else "",
                        "phone": contact.get("ContactInformation", {}).get("ContactMechanisms", [{}])[0].get("Value", "") if contact.get("ContactInformation") and contact.get("ContactInformation").get("ContactMechanisms") else "",
                        "dataset_id": dataset_id
                    }
                    dataset_contacts[dataset_id].append(contact_node)
                    all_contacts.append(contact_node)
        
        # Process contact_groups
        if "contact_groups" in entry and entry["contact_groups"]:
            for group in entry["contact_groups"]:
                if isinstance(group, dict):
                    group_id = f"contact_group_{dataset_id}_{len(dataset_contacts[dataset_id])}"
                    group_node = {
                        "contact_id": group_id,
                        "type": "group",
                        "name": group.get("GroupName", ""),
                        "roles": group.get("Roles", []),
                        "email": group.get("ContactInformation", {}).get("ContactMechanisms", [{}])[0].get("Value", "") if group.get("ContactInformation") and group.get("ContactInformation").get("ContactMechanisms") else "",
                        "organization": group.get("ContactInformation", {}).get("OrganizationName", "") if group.get("ContactInformation") else "",
                        "dataset_id": dataset_id
                    }
                    dataset_contacts[dataset_id].append(group_node)
                    all_contacts.append(group_node)
        
        # Extract projects for this dataset
        if "projects" in entry and entry["projects"]:
            for project in entry["projects"]:
                if isinstance(project, dict):
                    project_name = project.get("ShortName", "")
                    if project_name:
                        project_id = f"project_{dataset_id}_{project_name.lower().replace(' ', '_')}"
                        project_node = {
                            "project_id": project_id,
                            "name": project_name,
                            "description": project.get("LongName", ""),
                            "dataset_id": dataset_id
                        }
                        
                        dataset_projects[dataset_id].append(project_node)
                        # Also add to global list (check for duplicates by name, not ID)
                        if not any(p["name"] == project_name for p in all_projects):
                            all_projects.append(project_node)
        
        # Extract related URLs for this dataset
        if "related_urls" in entry and entry["related_urls"]:
            for url_info in entry["related_urls"]:
                if isinstance(url_info, dict):
                    url = url_info.get("URL", "")
                    if url:
                        url_id = f"url_{dataset_id}_{len(dataset_related_urls[dataset_id])}"
                        url_node = {
                            "url_id": url_id,
                            "url": url,
                            "type": url_info.get("Type", ""),
                            "subtype": url_info.get("Subtype", ""),
                            "description": url_info.get("Description", ""),
                            "format": url_info.get("Format", ""),
                            "dataset_id": dataset_id
                        }
                        dataset_related_urls[dataset_id].append(url_node)
                        all_related_urls.append(url_node)
        
        # Extract spatial and temporal resolution information for this dataset
        spatial_resolution, temporal_resolution = extract_resolution_from_additional_attributes(entry)
        
        if spatial_resolution:
            spatial_id = f"spatial_{dataset_id}"
            spatial_node = {
                "spatial_id": spatial_id,
                "resolution": spatial_resolution,
                "units": extract_resolution_units(spatial_resolution),
                "dataset_id": dataset_id
            }
            dataset_spatial_resolutions[dataset_id].append(spatial_node)
            all_spatial_resolutions.append(spatial_node)
        
        if temporal_resolution:
            temporal_id = f"temporal_{dataset_id}"
            temporal_node = {
                "temporal_id": temporal_id,
                "resolution": temporal_resolution,
                "frequency": standardize_temporal_frequency(temporal_resolution),
                "dataset_id": dataset_id
            }
            dataset_temporal_resolutions[dataset_id].append(temporal_node)
            all_temporal_resolutions.append(temporal_node)
        
      
        
        # Extract instrument information for this dataset
        if "platforms" in entry and entry["platforms"]:
            for platform in entry["platforms"]:
                if isinstance(platform, dict) and "Instruments" in platform:
                    for instrument in platform["Instruments"]:
                        if isinstance(instrument, dict):
                            instrument_name = instrument.get("ShortName", "")
                            if instrument_name:
                                instrument_id = f"instrument_{dataset_id}_{instrument_name.lower().replace(' ', '_')}"
                                instrument_node = {
                                    "instrument_id": instrument_id,
                                    "name": instrument_name,
                                    "long_name": instrument.get("LongName", ""),
                                    "technique": instrument.get("Technique", ""),
                                    "platform": platform.get("ShortName", ""),
                                    "dataset_id": dataset_id
                                }
                                
                                dataset_instruments[dataset_id].append(instrument_node)
                                # Also add to global list (check for duplicates by name, not ID)
                                if not any(i["name"] == instrument_name for i in all_instruments):
                                    all_instruments.append(instrument_node)
        
        # Extract processing level information for this dataset
        if "processing_level_id" in entry and entry["processing_level_id"]:
            level_id = entry["processing_level_id"]
            processing_level_id = f"level_{dataset_id}_{level_id.lower().replace(' ', '_')}"
            
            processing_level_node = {
                "processing_level_id": processing_level_id,
                "id": level_id,
                "description": get_processing_level_description(level_id),
                "dataset_id": dataset_id
            }
            
            dataset_processing_levels[dataset_id].append(processing_level_node)
            # Also add to global list (check for duplicates by level_id, not processing_level_id)
            if not any(p["id"] == level_id for p in all_processing_levels):
                all_processing_levels.append(processing_level_node)
    
    # Add CESM variables from CSV file
    from cesm_variables import CESM_VARIABLES
    cesm_var_count = 0
    for var_name, var_info in CESM_VARIABLES.items():
        # Remove the limit to get all CESM variables
        cesm_var_node = {
            "variable_id": f"cesm_var_{var_name}",
            "name": var_name,
            "standard_name": var_info.get("standard_name", var_name),
            "long_name": var_info.get("description", var_name),
            "units": var_info.get("units", "unknown"),
            "description": var_info.get("description", ""),
            "domain": var_info.get("domain", ""),
            "component": var_info.get("component", ""),
            "variable_type": "cesm"  # Explicitly mark as CESM variable
        }
        
        all_cesm_variables.append(cesm_var_node)
        cesm_var_count += 1
    
    # Add all variables to output (linked to datasets)
    for dataset_id, variables in dataset_variables.items():
        for var in variables:
            original_output["Variable"].append(var)
    
    # Add CESM variables to output
    for var in all_cesm_variables:
        original_output["CESMVariable"].append(var)
    
    # Add components to output
    for comp in all_components:
        original_output["Component"].append(comp)
    
    # Add contacts to output
    for contact in all_contacts:
        original_output["Contact"].append(contact)
    
    # Add projects to output
    for project in all_projects:
        original_output["Project"].append(project)
    
    # Add related URLs to output
    for url in all_related_urls:
        original_output["RelatedUrl"].append(url)
    
    # Add spatial resolution to output
    for spatial in all_spatial_resolutions:
        original_output["SpatialResolution"].append(spatial)
    
    # Add temporal resolution to output
    for temporal in all_temporal_resolutions:
        original_output["TemporalResolution"].append(temporal)
    
    # Add granule info to output
    for granule in all_granules:
        original_output["Granule"].append(granule)
    
    # Add instruments to output
    for instrument in all_instruments:
        original_output["Instrument"].append(instrument)
    
    # Add science keywords to output
    for keyword in all_science_keywords:
        original_output["ScienceKeyword"].append(keyword)
    
    # Add processing levels to output
    for level in all_processing_levels:
        original_output["ProcessingLevel"].append(level)
    
    print(f"Extracted {len(original_output['Variable'])} NASA CMR variables (linked to datasets)")
    print(f"Extracted {len(original_output['CESMVariable'])} CESM variables from CSV")
    print(f"Extracted {len(original_output['Component'])} unique components (not linked to datasets)")
    print(f"Extracted {len(original_output['Contact'])} contacts")
    print(f"Extracted {len(original_output['Project'])} projects")
    print(f"Extracted {len(original_output['RelatedUrl'])} related URLs")
    print(f"Extracted {len(original_output['SpatialResolution'])} spatial resolution records")
    print(f"Extracted {len(original_output['TemporalResolution'])} temporal resolution records")
    print(f"Extracted {len(original_output['Instrument'])} instruments")
    print(f"Extracted {len(original_output['ScienceKeyword'])} science keywords")
    print(f"Extracted {len(original_output['ProcessingLevel'])} processing levels")
    
    for idx, entry in enumerate(all_entries):
        dataset_id = entry.get("concept_id", entry.get("dataset_id", f"dataset_{idx}"))
        
        # ---------------------------
        # (1) Dataset - Enhanced with essential fields
        # ---------------------------
        dataset_obj = {
            "short_name": entry.get("short_name", "N/A"),
            "title": entry.get("title", "N/A"),
            "links": entry.get("links", []),
            "data_center": entry.get("data_center", "N/A"),
            "dataset_id": entry.get("dataset_id", "N/A"),
            "entry_id": entry.get("entry_id", "N/A"),
            "version_id": entry.get("version_id", "N/A"),
            "processing_level_id": entry.get("processing_level_id", "N/A"),
            "online_access_flag": entry.get("online_access_flag", False),
            "browse_flag": entry.get("browse_flag", False),
            # Additional CMR fields
            "science_keywords": entry.get("science_keywords", []),
            "doi": entry.get("doi", ""),
            "doi_authority": entry.get("doi_authority", ""),
            "collection_data_type": entry.get("collection_data_type", ""),
            "data_set_language": entry.get("data_set_language", "en-US"),
            "archive_center": entry.get("archive_center", ""),
            "native_id": entry.get("native_id", ""),
            "granule_count": entry.get("granule_count", 0),
            "day_night_flag": entry.get("day_night_flag", ""),
            "cloud_cover": entry.get("cloud_cover", "")
        }
        original_output["Dataset"].append(dataset_obj)

        # ---------------------------
        # (2) DataCategory - with summary
        # ---------------------------
        data_category_obj = {
            "summary": entry.get("summary", "N/A")
        }
        original_output["DataCategory"].append(data_category_obj)

        # ---------------------------
        # (3) DataFormat - one per dataset
        # ---------------------------
        data_format = entry.get("data_format", "")
        original_format = entry.get("original_format", "")
        
        # Try to get the best format information from merged data
        if not data_format or data_format == "":
            # Try to infer from original_format
            if original_format and original_format != "":
                data_format = original_format
            else:
                data_format = "Unknown"
            
        data_format_obj = {
            "original_format": original_format,
            "data_format": data_format,
            "collection_data_type": entry.get("collection_data_type", "N/A"),
            "format_source": "merged" if entry.get("data_format") else "inferred"
        }
        original_output["DataFormat"].append(data_format_obj)

        # ---------------------------
        # (4) CoordinateSystem - coordinate reference system
        # ---------------------------
        coord_system_name = entry.get("coordinate_system", "N/A")
        coord_system_obj = {
            "name": coord_system_name,
            "projection_type": "Unknown",
            "datum": "Unknown",
            "units": "Unknown"
        }
        original_output["CoordinateSystem"].append(coord_system_obj)
        
        # ---------------------------
        # (5) Organizations - one per dataset (can have multiple orgs)
        # ---------------------------
        organizations = entry.get("organizations", [])
        # For now, take the first organization or create a default one
        org_name = organizations[0] if organizations else "Unknown"
        org_obj = {
            "name": org_name,
            "type": "organization"
        }
        original_output["Organization"].append(org_obj)

        # ---------------------------
        # (6) Platforms - one per dataset (can have multiple platforms)
        # ---------------------------
        platforms = entry.get("platforms", [])
        # Take first platform or create default
        platform_name = platforms[0] if platforms and isinstance(platforms[0], dict) else "Unknown"
        if isinstance(platform_name, dict):
            platform_name = platform_name.get("ShortName", "Unknown")
        platform_obj = {
            "name": platform_name,
            "type": "platform"
        }
        original_output["Platform"].append(platform_obj)

        # ---------------------------
        # (7) Consortiums - one per dataset (can have multiple consortiums)
        # ---------------------------
        consortiums = entry.get("consortiums", [])
        # Take first consortium or create default
        consortium_name = consortiums[0] if consortiums else "Unknown"
        consortium_obj = {
            "name": consortium_name,
            "type": "consortium"
        }
        original_output["Consortium"].append(consortium_obj)

        # ---------------------------
        # (8) Location - renamed from SpatialExtent, enhanced
        # ---------------------------
        boxes = entry.get("boxes", [])
        polygons = entry.get("polygons", [])
        points = entry.get("points", [])

        location_obj = {
            "boxes": boxes,
            "polygons": polygons,
            "points": points,
            "place_names": []  # Will be populated after spatial analysis
        }
        original_output["Location"].append(location_obj)

        # ---------------------------
        # (9) Station - enhanced with platform info
        # ---------------------------
        station_obj = {
            "id": f"station_{idx}",
            "platforms": platforms,
            "data_center": entry.get("data_center", "N/A")
        }
        original_output["Station"].append(station_obj)

        # ---------------------------
        # (10) TemporalExtent - enhanced
        # ---------------------------
        time_start_str = entry.get("time_start")
        time_end_str = entry.get("time_end")

        temporal_extent_obj = {
            "start_time": time_start_str,
            "end_time": time_end_str,
            "updated": entry.get("updated", None)
        }
        original_output["TemporalExtent"].append(temporal_extent_obj)

        # ---------------------------
        # (11) Variables - Get variables for this specific dataset
        # ---------------------------
        dataset_vars = dataset_variables.get(dataset_id, [])
        
        # ---------------------------
        # (12) Relationship - with all metadata linked to datasets
        # ---------------------------
        relationship_obj = {
            "hasDataCategory": [],
            "hasDataFormat": [],
            "usesCoordinateSystem": [],
            "hasLocation": [],
            "hasStation": [],
            "hasOrganization": [],
            "hasPlatform": [],
            "hasConsortium": [],
            "hasTemporalExtent": [],
            "hasVariable": [var["variable_id"] for var in dataset_vars],  # Link variables to dataset
            "hasCESMVariable": [],  # Empty - no CESM variables attached
            "hasComponent": [],  # Empty - no components attached
            # Additional relationships with actual data
            "hasContact": [contact["contact_id"] for contact in dataset_contacts.get(dataset_id, [])],
            "hasProject": [project["project_id"] for project in dataset_projects.get(dataset_id, [])],
            "hasRelatedUrl": [url["url_id"] for url in dataset_related_urls.get(dataset_id, [])],
            "hasSpatialResolution": [spatial["spatial_id"] for spatial in dataset_spatial_resolutions.get(dataset_id, [])],
            "hasTemporalResolution": [temporal["temporal_id"] for temporal in dataset_temporal_resolutions.get(dataset_id, [])],
            "hasGranule": [granule["granule_id"] for granule in dataset_granules.get(dataset_id, [])],
            "hasInstrument": [instrument["instrument_id"] for instrument in dataset_instruments.get(dataset_id, [])],
            "hasScienceKeyword": [keyword["keyword_id"] for keyword in dataset_science_keywords.get(dataset_id, [])],
            "hasProcessingLevel": [level["processing_level_id"] for level in dataset_processing_levels.get(dataset_id, [])]
        }
        original_output["Relationship"].append(relationship_obj)

        # ---------------------------
        # (13) Build the individual record with all metadata
        # ---------------------------
        individual_dataset_dict = {
            "Dataset": dataset_obj,
            "DataCategory": data_category_obj,
            "DataFormat": data_format_obj,
            "CoordinateSystem": coord_system_obj,
            "Location": location_obj,
            "Station": station_obj,
            "TemporalExtent": temporal_extent_obj,
            "Variable": dataset_vars,  # Variables linked to this dataset
            "CESMVariable": [],  # Empty - no CESM variables attached to individual datasets
            "Component": [],  # Empty - no components attached to individual datasets
            "Contact": dataset_contacts.get(dataset_id, []),
            "Project": dataset_projects.get(dataset_id, []),
            "RelatedUrl": dataset_related_urls.get(dataset_id, []),
            "SpatialResolution": dataset_spatial_resolutions.get(dataset_id, []),
            "TemporalResolution": dataset_temporal_resolutions.get(dataset_id, []),
            "Granule": dataset_granules.get(dataset_id, []),
            "Instrument": dataset_instruments.get(dataset_id, []),
            "ScienceKeyword": dataset_science_keywords.get(dataset_id, []),
            "ProcessingLevel": dataset_processing_levels.get(dataset_id, []),
            "Relationship": relationship_obj
        }
        individual_output.append(individual_dataset_dict)

        # ---------------------------
        # (14) Parse geometry for spatial classification
        # ---------------------------
        geometry = parse_cmr_spatial(boxes, polygons, points)
        if geometry is None:
            fail_count += 1
            continue

        geoms.append({"dataset_index": idx, "geometry": geometry})

    # ---------------------------
    # (15) Location classification (with Mapbox API - OPTIONAL)
    # ---------------------------
    # Set to False to skip geocoding during dataset creation
    # Location info can be added later via KG agent tools
    use_geocoding_api = False
    
    if use_geocoding_api:
        print(f"Classifying {len(geoms)} datasets with Mapbox API...")
        
        for geom_info in geoms:
            dataset_index = geom_info["dataset_index"]
            geometry = geom_info["geometry"]
            
            boxes = original_output["Location"][dataset_index]["boxes"]
            polygons = original_output["Location"][dataset_index]["polygons"]
            points = original_output["Location"][dataset_index]["points"]
            
            # Try API-based classification first
            classification = get_location_from_geometry(geometry)
            
            # If API fails, try bbox-based classification
            if classification["scope"] == "unclassified":
                classification = classify_location_from_bbox(boxes)
         
            # Update the data structures
            scope = classification["scope"]
            place_names = classification["place_names"]
            
            original_output["Location"][dataset_index]["place_names"] = place_names
            individual_output[dataset_index]["Location"]["place_names"] = place_names
            
            # Only print progress every 50 datasets
            if (dataset_index + 1) % 50 == 0 or dataset_index == len(geoms) - 1:
                print(f"Processed {dataset_index + 1}/{len(geoms)} locations")
    else:
        print(f"Using fast offline boundary classification for {len(geoms)} datasets...")
        
        # Process in batches for better performance
        batch_size = 100
        for batch_start in range(0, len(geoms), batch_size):
            batch_end = min(batch_start + batch_size, len(geoms))
            batch_geoms = geoms[batch_start:batch_end]
            
            # Process batch
            for geom_info in batch_geoms:
                dataset_index = geom_info["dataset_index"]
                geometry = geom_info["geometry"]
                
                # Use fast offline boundary classification
                classification = get_location_from_geometry_offline(geometry)
                
                scope = classification.get("scope", "unclassified")
                place_names = classification.get("place_names", [])
                
                original_output["Location"][dataset_index]["place_names"] = place_names
                individual_output[dataset_index]["Location"]["place_names"] = place_names
            
            # Print progress for each batch
            print(f"Processed {batch_end}/{len(geoms)} locations (fast offline) - {(batch_end/len(geoms)*100):.1f}% complete")

    return original_output, individual_output, fail_count


# Helper function to get processing level descriptions
def get_processing_level_description(level_id):
    """
    Returns a description for NASA processing levels.
    """
    processing_levels = {
        "0": "Raw data, unprocessed instrument and payload data at full resolution",
        "1": "Level 0 data that has been processed to sensor units",
        "1A": "Reconstructed, unprocessed instrument data at full resolution",
        "1B": "Level 1A data that has been processed to sensor units",
        "2": "Derived geophysical variables at the same resolution as the Level 1 source data",
        "3": "Variables mapped on uniform space-time grid scales",
        "4": "Model output or results from analyses of lower-level data",
        "NA": "Not applicable"
    }
    
    return processing_levels.get(level_id, "Unknown processing level")


def create_component_node(comp_info, dataset_id=None):
    """
    Creates a component node from component information.
    
    Args:
        comp_info: Dictionary with component information
        dataset_id: Optional dataset ID to associate with the component
    
    Returns:
        Dictionary representing a component node
    """
    component_node = {
        "component_id": f"comp_{comp_info['abbreviation'].lower()}",
        "name": comp_info["full_name"],
        "abbreviation": comp_info["abbreviation"],
        "description": comp_info["description"],
        "domain": comp_info["domain"]
    }
    
    # Add dataset ID if provided
    if dataset_id:
        component_node["dataset_id"] = dataset_id
        
    return component_node


# Helper function to extract units from resolution string
def extract_resolution_units(resolution_str):
    """
    Extracts units from a resolution string.
    """
    if not resolution_str:
        return "unknown"
        
    # Common spatial resolution units
    units = {
        "km": "kilometers",
        "m": "meters",
        "deg": "degrees",
        "degree": "degrees",
        "degrees": "degrees",
        "arcmin": "arcminutes",
        "arcsec": "arcseconds"
    }
    
    # Check for units in the string
    for unit_abbr, unit_full in units.items():
        if unit_abbr in resolution_str.lower():
            return unit_full
            
    return "unknown"


# Helper function to standardize temporal frequency
def standardize_temporal_frequency(temporal_str):
    """
    Standardizes temporal frequency from a resolution string.
    """
    if not temporal_str:
        return "unknown"
        
    # Common temporal frequencies
    frequencies = {
        "daily": "daily",
        "day": "daily",
        "weekly": "weekly",
        "week": "weekly",
        "monthly": "monthly",
        "month": "monthly",
        "yearly": "yearly",
        "year": "yearly",
        "annual": "yearly",
        "hourly": "hourly",
        "hour": "hourly",
        "minute": "minutely",
        "second": "secondly",
        "3-hour": "3-hourly",
        "6-hour": "6-hourly",
        "12-hour": "12-hourly"
    }
    
    # Check for frequency in the string
    for freq_key, freq_std in frequencies.items():
        if freq_key in temporal_str.lower():
            return freq_std
            
    return "unknown"


def extract_sentence_with_resolution(text, patterns):
    """
    Extract the full sentence containing resolution information.
    
    Args:
        text: Text to search in
        patterns: List of regex patterns to match
    
    Returns:
        str: Full sentence containing resolution info, or empty string
    """
    import re
    
    if not text:
        return ""
    
    # Split text into sentences (handle multiple delimiters)
    sentences = re.split(r'[.!?;]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        for pattern in patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return sentence
    
    return ""


def extract_resolution_from_additional_attributes(entry):
    """
    Extract spatial and temporal resolution from additional attributes and other metadata fields.
    Enhanced to capture full sentence context and comprehensive patterns.
    
    Args:
        entry: Dataset entry dictionary
    
    Returns:
        tuple: (spatial_resolution, temporal_resolution)
    """
    spatial_resolution = ""
    temporal_resolution = ""
    
    # Try to get from direct fields first
    if "spatial_resolution" in entry and entry["spatial_resolution"]:
        spatial_resolution = str(entry["spatial_resolution"])
    
    if "temporal_resolution" in entry and entry["temporal_resolution"]:
        temporal_resolution = str(entry["temporal_resolution"])
    
    # Check additional attributes if direct fields are empty
    if ("additional_attributes" in entry and entry["additional_attributes"] and 
            (not spatial_resolution or not temporal_resolution)):
        
        for attr in entry["additional_attributes"]:
            if not isinstance(attr, dict):
                continue
                
            # Check for spatial resolution attributes (expanded list)
            attr_name = attr.get("Name", "").lower()
            if not spatial_resolution and attr_name in [
                "spatial_resolution", "resolution", "grid_resolution", "grid_spacing",
                "cell_size", "pixel_size", "horizontal_resolution", "spatial_scale",
                "grid_size", "resolution_horizontal", "dx", "dy", "lat_resolution",
                "lon_resolution", "latitude_resolution", "longitude_resolution"
            ]:
                spatial_resolution = str(attr.get("Value", ""))
            
            # Check for temporal resolution attributes (expanded list)
            if not temporal_resolution and attr_name in [
                "temporal_resolution", "time_resolution", "frequency", "time_step",
                "temporal_coverage", "temporal_frequency", "time_interval",
                "sampling_frequency", "dt", "timestep", "time_spacing"
            ]:
                temporal_resolution = str(attr.get("Value", ""))
    
    # Try to extract from summary if still empty - COMPREHENSIVE PATTERNS
    if (not spatial_resolution or not temporal_resolution):
        # Search in multiple fields
        search_fields = [
            entry.get("summary", ""),
            entry.get("title", ""),
            entry.get("short_name", ""),
            " ".join([str(k) for k in entry.get("science_keywords", [])]) if entry.get("science_keywords") else ""
        ]
        
        combined_text = " ".join(search_fields)
        
        # Look for spatial resolution patterns in text
        if not spatial_resolution:
            spatial_patterns = [
                # Direct measurements with units
                r"\d+(?:\.\d+)?\s*(?:km|kilometer|kilometers|metre|meters|m)\s*(?:spatial\s*)?(?:resolution|grid|cell|pixel)",
                r"(?:spatial\s*)?(?:resolution|grid|cell|pixel)\s*(?:of\s*)?\d+(?:\.\d+)?\s*(?:km|kilometer|kilometers|metre|meters|m)",
                r"\d+(?:\.\d+)?\s*(?:km|m|meter|meters|metre|metres)",
                
                # Degree-based measurements
                r"\d+(?:\.\d+)?\s*(?:degree|degrees|deg|°)\s*(?:spatial\s*)?(?:resolution|grid|cell)",
                r"(?:spatial\s*)?(?:resolution|grid|cell)\s*(?:of\s*)?\d+(?:\.\d+)?\s*(?:degree|degrees|deg|°)",
                r"\d+(?:\.\d+)?\s*(?:degree|degrees|deg|°)",
                
                # Arc measurements
                r"\d+(?:\.\d+)?\s*(?:arcmin|arcminute|arcminutes|arcsec|arcsecond|arcseconds)",
                r"(?:resolution|grid)\s*(?:of\s*)?\d+(?:\.\d+)?\s*(?:arcmin|arcminute|arcminutes|arcsec|arcsecond|arcseconds)",
                
                # Fractional degrees
                r"1/\d+\s*(?:degree|degrees|deg|°)",
                r"0\.\d+\s*(?:degree|degrees|deg|°)",
                
                # Grid descriptions
                r"\d+\s*x\s*\d+\s*(?:km|m|degree|deg|°)",
                r"grid\s+(?:size|resolution|spacing)\s*(?:of\s*)?\d+(?:\.\d+)?\s*(?:km|m|degree|deg|°|x)",
                r"(?:horizontal|spatial)\s+resolution\s+(?:of\s*)?\d+(?:\.\d+)?\s*(?:km|m|degree|deg|°)",
                
                # Common formats
                r"\d+(?:\.\d+)?\s*(?:km|m|degree|deg)\s+(?:spatial\s*)?(?:resolution|grid)",
                r"at\s+\d+(?:\.\d+)?\s*(?:km|m|degree|deg|°)",
                r"(?:pixel|cell)\s+size\s*(?:of\s*)?\d+(?:\.\d+)?\s*(?:km|m|degree|deg|°)"
            ]
            
            spatial_resolution = extract_sentence_with_resolution(combined_text, spatial_patterns)
        
        # Look for temporal resolution patterns in text
        if not temporal_resolution:
            temporal_patterns = [
                # Common frequencies
                r"daily|day|diurnal",
                r"weekly|week",
                r"monthly|month",
                r"yearly|annual|year",
                r"hourly|hour",
                r"minutely|minute",
                r"secondly|second",
                
                # Multi-unit frequencies  
                r"\d+-(?:day|daily|week|weekly|month|monthly|year|yearly|annual|hour|hourly|minute|second)",
                r"(?:every\s+)?\d+\s+(?:day|days|week|weeks|month|months|year|years|hour|hours|minute|minutes|second|seconds)",
                r"(?:every\s+)?(?:other\s+)?(?:day|week|month|year|hour|minute|second)",
                
                # Sub-daily frequencies
                r"3-hour|3-hourly|6-hour|6-hourly|12-hour|12-hourly|24-hour|24-hourly",
                r"half-hour|half-hourly|quarter-hour|quarter-hourly",
                
                # Time steps and intervals
                r"time\s+(?:step|interval|resolution|frequency)\s*(?:of\s*)?\d+\s*(?:day|days|hour|hours|minute|minutes|second|seconds)",
                r"temporal\s+(?:resolution|frequency|interval|spacing)\s*(?:of\s*)?\d*\s*(?:day|days|hour|hours|minute|minutes|second|seconds|daily|weekly|monthly|yearly|annual)",
                r"(?:sampling|measurement)\s+(?:frequency|interval|rate)\s*(?:of\s*)?\d*\s*(?:day|days|hour|hours|minute|minutes|second|seconds|times|per)",
                
                # Specific intervals
                r"(?:at\s+)?\d+\s*(?:hz|hertz)",
                r"(?:every\s+)?\d+\s*(?:times\s+per\s+)?(?:day|week|month|year|hour|minute|second)",
                r"(?:once|twice|multiple times)\s+(?:per\s+)?(?:day|week|month|year|hour|minute|second)",
                
                # Instantaneous or snapshot
                r"instantaneous|snapshot|single\s+time",
                r"one-time|once-off",
                
                # Continuous
                r"continuous|real-time|near-real-time|ongoing",
                
                # Seasonal/irregular
                r"seasonal|irregular|sporadic|campaign-based|event-based"
            ]
            
            temporal_resolution = extract_sentence_with_resolution(combined_text, temporal_patterns)
    
    # Clean up and normalize extracted resolutions
    if spatial_resolution:
        spatial_resolution = spatial_resolution.strip()
        # If we got a full sentence, try to extract just the resolution part for storage
        if len(spatial_resolution) > 50:  # Likely a full sentence
            import re
            # Try to extract the core resolution value while keeping context
            match = re.search(r"\d+(?:\.\d+)?\s*(?:km|m|meter|metre|degree|deg|°|arcmin|arcsec)", spatial_resolution, re.IGNORECASE)
            if match:
                # Store both the extracted value and full context
                core_value = match.group(0)
                spatial_resolution = f"{core_value} (Context: {spatial_resolution[:100]}...)" if len(spatial_resolution) > 100 else spatial_resolution
    
    if temporal_resolution:
        temporal_resolution = temporal_resolution.strip()
        # Similar processing for temporal resolution
        if len(temporal_resolution) > 50:  # Likely a full sentence
            import re
            # Try to extract the core resolution value while keeping context
            match = re.search(r"(?:\d+-)?(?:daily|weekly|monthly|yearly|annual|hourly|minutely|secondly|\d+\s*(?:day|week|month|year|hour|minute|second))", temporal_resolution, re.IGNORECASE)
            if match:
                core_value = match.group(0)
                temporal_resolution = f"{core_value} (Context: {temporal_resolution[:100]}...)" if len(temporal_resolution) > 100 else temporal_resolution
    
    return spatial_resolution, temporal_resolution


##############################
#  (5) Main
##############################
def main():
    # 0) Ensure output directory exists
    os.makedirs("json_files", exist_ok=True)
    
    # 1) Fetch NASA CMR data (unlimited)
    all_data = fetch_nasa_cmr_all_pages(page_size=200, max_pages=None)  # Fetch all available datasets
    print(f"Total collections fetched: {len(all_data)}")
    
    print(f"Processing all {len(all_data)} datasets")

    # 2) Transform & classify
    (
        structured_data_original,
        structured_data_individual,
        fail_count
    ) = transform_cmr_to_classes(all_data)

    # 3) Print summary of created classes
    print("\n=== CREATED CLASSES SUMMARY ===")
    for class_name, class_data in structured_data_original.items():
        print(f"{class_name}: {len(class_data)} instances")
    
    print(f"\nGeometry processing: {fail_count} datasets had invalid or unsupported geometry.")

    # 4) Save the parallel-lists format (matches your json_to_csvs.py expectations)
    output_file_original = "json_files/structured_cmr_data.json"
    with open(output_file_original, "w", encoding="utf-8") as f:
        json.dump(structured_data_original, f, indent=2)
    print(f"\nSaved structured data to {output_file_original}")

    # 5) Save the individual-records format (for analysis)
    output_file_individual = "json_files/individual_cmr_data.json"
    with open(output_file_individual, "w", encoding="utf-8") as f:
        json.dump(structured_data_individual, f, indent=2)
    print(f"Saved individual-record data to {output_file_individual}")

    # 6) Save original NASA CMR data for reference
    output_file_raw = "json_files/nasa_cmr.json"
    with open(output_file_raw, "w", encoding="utf-8") as f:
        json.dump({"feed": {"entry": all_data}}, f, indent=2)
    print(f"Saved raw NASA CMR data to {output_file_raw}")

    # 7) Print files that can be used with json_to_csvs.py
    print(f"\n=== READY FOR NEPTUNE ===")
    print(f"Use this file with your json_to_csvs.py script:")
    print(f"  python json_to_csvs.py --input {output_file_original}")
    
    # 8) Show sample of enhanced dataset info
    if structured_data_original["Dataset"]:
        sample_dataset = structured_data_original["Dataset"][0]
        print(f"\n=== SAMPLE ENHANCED DATASET ===")
        for key, value in sample_dataset.items():
            if key != "links":  # Skip links as they're verbose
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
