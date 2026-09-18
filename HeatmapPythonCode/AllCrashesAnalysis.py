import geopandas as gpd
import folium
from folium.plugins import HeatMap
import numpy as np
import pandas as pd # Import pandas

# Load data
# For bus_stops from CSV, first load as pandas DataFrame, then convert to GeoDataFrame
bus_stops_df = pd.read_csv("BusStopsCC.csv")
# Assuming 'longitude' and 'latitude' columns exist in the CSV for bus stop coordinates
# And assuming these coordinates are in WGS84 (EPSG:4326)
# If your CSV uses different column names for longitude/latitude (e.g., 'X', 'Y', 'lon', 'lat'),
# please update 'longitude' and 'latitude' below to match.
geometry_bus_stops = gpd.points_from_xy(bus_stops_df['longitude'], bus_stops_df['latitude'])
bus_stops = gpd.GeoDataFrame(bus_stops_df, geometry=geometry_bus_stops, crs="EPSG:4326")

# Accidents data from CSV
accidents_df = pd.read_csv("Crashes250ftBusStopNICC.csv")
# Assuming 'Longitude' and 'Latitude' columns in Crashes1400ftBusStopNICC.csv represent coordinates
# And assuming these coordinates are in WGS84 (EPSG:4326)
# If your CSV uses different column names for longitude/latitude, please update them.
geometry_accidents = gpd.points_from_xy(accidents_df['Longitude'], accidents_df['Latitude'])
accidents = gpd.GeoDataFrame(accidents_df, geometry=geometry_accidents, crs="EPSG:4326")

# Reproject bus_stops to match accidents' CRS (UTM Zone 12N)
# Now both are GeoDataFrames and 'to_crs' should work
bus_stops = bus_stops.to_crs(epsg=32612)
accidents = accidents.to_crs(epsg=32612)

# Drop rows with missing geometries
bus_stops = bus_stops.dropna(subset=['geometry'])
accidents = accidents.dropna(subset=['geometry'])

# Filter out points near (0, 0) in UTM (meters)
tolerance = 10  # 10 meters
bus_stops = bus_stops[~((bus_stops.geometry.x.abs() < tolerance) & (bus_stops.geometry.y.abs() < tolerance))]
accidents = accidents[~((accidents.geometry.x.abs() < tolerance) & (accidents.geometry.y.abs() < tolerance))]

# Convert accidents to lat/lon (EPSG:4326) for Folium
accidents = accidents.to_crs(epsg=4326)
bus_stops = bus_stops.to_crs(epsg=4326)

# Calculate the center of the map (using the mean of accidents' coordinates)
center_lat = accidents.geometry.y.mean()
center_lon = accidents.geometry.x.mean()

# Create a Folium map centered on the UTA area
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=10,
    tiles='CartoDB Positron'  # Try a reliable basemap provider
)

# Alternative basemap options if CartoDB fails:
# tiles='OpenStreetMap'
# tiles='Esri_WorldStreetMap' (requires an API key in some cases)

# Prepare heatmap data (list of [lat, lon] points)
heat_data = [[point.y, point.x] for point in accidents.geometry]

# Add heatmap
HeatMap(
    heat_data,
    radius=15,
    blur=20,
    max_zoom=18,
    min_opacity=1,
    max_val=5
).add_to(m)

# Add bus stops as markers
for idx, row in bus_stops.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.7,
        popup=f"Bus Stop: {row.get('stopname', 'Unknown')}"  # Adjust 'stopname' to your column name
    ).add_to(m)

from folium.features import DivIcon

# Add a custom legend for the heatmap
legend_html = '''
<div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; padding: 10px; background-color: white; border: 2px solid black;">
    <p><strong>Legend</strong></p>
    <p><span style="color: blue;">&#9679;</span> Bus Stop</p>
    <p><u>Accident Density</u></p>
    <p><span style="color: red;">&#9632;</span> High</p>
    <p><span style="color: orange;">&#9632;</span> Medium-High</p>
    <p><span style="color: lime;">&#9632;</span> Medium-Low</p>
    <p><span style="color: blue;">&#9632;</span> Low</p>
    <hr style="margin: 4px 0;">
</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))
# Save again after adding the legend

# Save the map to an HTML file
m.save("uta_accident_heatmap_j26.html")
print("Map saved as uta_accident_heatmap_j26.html. Open it in a web browser to view.")
