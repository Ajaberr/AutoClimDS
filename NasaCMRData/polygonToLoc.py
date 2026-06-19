import geopandas as gpd
import json
from shapely.geometry import Polygon

def polygon_coordinates_to_shapely(nasa_polygon_coords):
    """Convert lat/lon pairs into a Shapely Polygon."""
    if nasa_polygon_coords[0] != nasa_polygon_coords[-1]:
        nasa_polygon_coords.append(nasa_polygon_coords[0])
    shapely_coords = [(lon, lat) for (lat, lon) in nasa_polygon_coords]
    return Polygon(shapely_coords)

def find_admin_areas_for_polygon(nasa_poly, admin_shapefile_path):
    """
    Intersect the NASA polygon with a shapefile that (ideally) includes
    city/country/continent boundaries, returning a GeoDataFrame of matches.
    """
    admin_gdf = gpd.read_file(admin_shapefile_path)
    nasa_poly_gdf = gpd.GeoDataFrame(index=[0], crs=admin_gdf.crs, geometry=[nasa_poly])
    intersected = gpd.overlay(nasa_poly_gdf, admin_gdf, how='intersection')
    return intersected

def classify_bbox_scope(intersected_gdf):
    """
    Classify the bounding box as 'city', 'country', 'continent', or 'global'.
    Then also return which specific city/country/continent names were found.

    Custom logic:
      - If exactly one city => 'city'
      - If multiple cities but only one country => 'country'
      - If multiple countries but only one continent => 'continent'
      - If multiple continents => 'global'
      - Otherwise => 'unclassified'

    Adjust the CITY_COL, COUNTRY_COL, CONTINENT_COL to match your shapefile.
    """
    # Change these to match your dataset:
    CITY_COL = 'NAME_2'      # or 'CITY_NAME', 'NAME_1', etc.
    COUNTRY_COL = 'ADMIN'    # or 'NAME_0', 'SOVEREIGNT', etc.
    CONTINENT_COL = 'CONTINENT'

    # Collect all intersected city/country/continent names
    cities = set()
    countries = set()
    continents = set()

    for _, row in intersected_gdf.iterrows():
        city_val = row.get(CITY_COL)
        country_val = row.get(COUNTRY_COL)
        continent_val = row.get(CONTINENT_COL)

        if city_val:
            cities.add(city_val)
        if country_val:
            countries.add(country_val)
        if continent_val:
            continents.add(continent_val)

    # Now apply the classification logic:
    if len(cities) == 1 and len(countries) == 1:
        scope = 'city'
    elif len(countries) > 1 and len(continents) == 1:
        scope = 'continent'
    elif len(continents) > 1:
        scope = 'global'
    elif len(cities) > 1 or len(countries) == 1:
        # i.e. multiple cities but only 1 country => 'country'
        scope = 'country'
    else:
        scope = 'unclassified'

    return {
        'scope': scope,
        'cities': list(cities), 
        'countries': list(countries),
        'continents': list(continents)
    }

def save_results_to_json(result_gdf, classification_info, output_file="admin_intersections.json"):
    """
    - Add bounding box scope classification to each row in the GeoDataFrame.
    - Also store which city/country/continent names were found overall.
    - Save everything to a JSON file.
    """
    scope_label = classification_info['scope']

    # We'll add new columns for clarity. For multiple values, join them with commas, etc.
    result_gdf['bbox_scope'] = scope_label
    result_gdf['bbox_cities'] = ', '.join(classification_info['cities'])
    result_gdf['bbox_countries'] = ', '.join(classification_info['countries'])
    result_gdf['bbox_continents'] = ', '.join(classification_info['continents'])

    # Convert to GeoJSON string
    result_json_str = result_gdf.to_json()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result_json_str)

    print(f"Results saved to {output_file}")
    print(f'Bounding Box Scope: {scope_label}')
    print(f'Intersected Cities: {classification_info["cities"]}')
    print(f'Intersected Countries: {classification_info["countries"]}')
    print(f'Intersected Continents: {classification_info["continents"]}')

if __name__ == "__main__":
    # EXAMPLE bounding box around part of Karachi
    nasa_polygon_coords = [
        (24.8237, 66.9541),
        (24.8837, 66.9541),
        (24.8837, 67.0561),
        (24.8237, 67.0561),
        (24.8237, 66.9541)
    ]
    karachi_polygon = polygon_coordinates_to_shapely(nasa_polygon_coords)

    # Point to your shapefile that includes city/country/continent data
    admin_shapefile_path = "NasaKG/boundaries/boundaries.shp"

    # 1) Intersect bounding box with admin boundaries
    result_gdf = find_admin_areas_for_polygon(karachi_polygon, admin_shapefile_path)

    # 2) Classify the bounding box scope & extract the actual city/country/continent names
    classification_info = classify_bbox_scope(result_gdf)

    # 3) Print in console
    print("=== Intersection Results ===")
    print(result_gdf)
    print("=== BBox Classification Info ===")
    print(classification_info)

    # 4) Save to JSON with the scope classification and name details
    save_results_to_json(result_gdf, classification_info, "admin_intersections.json")
    admin_gdf = gpd.read_file("NasaKG/boundaries/boundaries.shp")
    print(admin_gdf.columns)     # Shows all column names
    print(admin_gdf["ADMIN"])
    print(admin_gdf["CONTINENT"])
