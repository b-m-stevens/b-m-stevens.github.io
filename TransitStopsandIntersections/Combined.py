# This python code was developed to create a map that visually combines the top 45 transit stops and intersections with the highest crash frequencies. The code takes .csv files with latitude and longitude values of all crashes, VRU crashes, transit stops, and intersections as input. 
# This code projected all the latitude and longitude data into WGS84 projection for cohesion.

#Map Crashes, VRU Crashes, Intersections
import geopandas as gpd
import folium
import pandas as pd
import io
from branca.element import Element
from PIL import Image

# Load the intersection crash data (used to find top intersections)
try:
    df_intersection_crashes = pd.read_csv('Crashes1400ftIntersectionNI.csv')
except FileNotFoundError:
    print("Error: Crashes1400ftIntersectionNI.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Load the all crashes bus stop data (used to find top bus stops for all crashes)
try:
    df_all_crashes = pd.read_csv('Crashes1400ftBusStopNICC.csv')
except FileNotFoundError:
    print("Error: Crashes1400ftBusStopNICC.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Load the VRU crashes bus stop data (used to find top bus stops for VRU crashes)
try:
    df_vru_crashes = pd.read_csv('VRUCrashes1400ftBusStopNICCNM.csv')
except FileNotFoundError:
    print("Error: VRUCrashes1400ftBusStopNICCNM.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Load the bus stop intersection data (used to get location and info for bus stops)
try:
    df_stops = pd.read_csv('BusStops1400ftIntersectionNI.csv')
except FileNotFoundError:
    print("Error: BusStops1400ftIntersectionNI.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Load the VRU crashes bus stop data (used to find top bus stops for VRU crashes)
try:
    df_vru_intersection_crashes = pd.read_csv('VRUCrashes1400ftIntersectionNINM.csv')
except FileNotFoundError:
    print("Error: VRUCrashes1400ftIntersectionNINM.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Find top 45 intersections based on crash counts
near_fid_counts_intersections = df_intersection_crashes['NEAR_FID'].value_counts()
top_45_near_fids_intersections = near_fid_counts_intersections.head(45).index.tolist()
# Use the original DataFrame to get location information for intersections
top_intersections_df = df_intersection_crashes[df_intersection_crashes['NEAR_FID'].isin(top_45_near_fids_intersections)].drop_duplicates(subset=['NEAR_FID']).copy()

# Find top 45 intersections based on VRU crash counts
near_fid_counts_vru_intersections = df_vru_intersection_crashes['NEAR_FID'].value_counts()
top_45_near_fids_vru_intersections = near_fid_counts_vru_intersections.head(45).index.tolist()
# Use the original DataFrame to get location information for intersections
top_intersections_vru_df = df_vru_intersection_crashes[df_vru_intersection_crashes['NEAR_FID'].isin(top_45_near_fids_vru_intersections)].drop_duplicates(subset=['NEAR_FID']).copy()

# Find top 45 bus stops based on all crash counts
near_fid_counts_all_crashes = df_all_crashes['NEAR_FID'].value_counts()
top_45_near_fids_all_crashes = near_fid_counts_all_crashes.head(45).index.tolist()
# Get the location and info for these bus stops from df_stops
top_all_crashes_stops_df = df_stops[df_stops['OBJECTID'].isin(top_45_near_fids_all_crashes)].copy()

# Find top 45 bus stops based on VRU crash counts
near_fid_counts_vru_crashes = df_vru_crashes['NEAR_FID'].value_counts()
top_45_near_fids_vru_crashes = near_fid_counts_vru_crashes.head(45).index.tolist()
# Get the location and info for these bus stops from df_stops
top_vru_crashes_stops_df = df_stops[df_stops['OBJECTID'].isin(top_45_near_fids_vru_crashes)].copy()

#Print Bus Stop and Intersection IDs
print("Intersections with the most crashes")
print(top_45_near_fids_intersections)
print("Intersections with the most VRU crashes")
print(top_45_near_fids_vru_intersections)
print("Bus Stops with the most crashes")
print(top_45_near_fids_all_crashes)
print("Bus Stops with the most VRU crashes")
print(top_45_near_fids_vru_crashes)

# Convert to GeoDataFrame (assuming 'Latitude' and 'Longitude' columns exist in top_intersections_df, and 'latitude' and 'longitude' in bus stop dataframes)
# Explicitly extract Latitude and Longitude Series for GeoDataFrame creation
latitude_series = top_intersections_df['Latitude']
longitude_series = top_intersections_df['Longitude']

#Create variables for GeoDataFrame for VRU Intersections
latitude_vru_series = top_intersections_vru_df['Latitude']
longitude_vru_series = top_intersections_vru_df['Longitude']

gdf_intersections = gpd.GeoDataFrame(
    top_intersections_df, geometry=gpd.points_from_xy(top_intersections_df['Longitude'], top_intersections_df['Latitude']))

gdf_vru_intersections = gpd.GeoDataFrame(
    top_intersections_vru_df, geometry=gpd.points_from_xy(top_intersections_vru_df['Longitude'], top_intersections_vru_df['Latitude']))

gdf_all_crashes_stops = gpd.GeoDataFrame(
    top_all_crashes_stops_df, geometry=gpd.points_from_xy(top_all_crashes_stops_df['longitude'], top_all_crashes_stops_df['latitude']))

gdf_vru_crashes_stops = gpd.GeoDataFrame(
    top_vru_crashes_stops_df, geometry=gpd.points_from_xy(top_vru_crashes_stops_df['longitude'], top_vru_crashes_stops_df['latitude']))

# Create a base map centered around the mean location of all points
all_points = pd.concat([gdf_intersections[['Latitude', 'Longitude']], gdf_vru_intersections[['Latitude', 'Longitude']], gdf_all_crashes_stops[['latitude', 'longitude']].rename(columns={'latitude': 'Latitude', 'longitude': 'Longitude'}), gdf_vru_crashes_stops[['latitude', 'longitude']].rename(columns={'latitude': 'Latitude', 'longitude': 'Longitude'})])
map_center = [all_points['Latitude'].mean(), all_points['Longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=10)
# 1. Add Scale Bar
# ScaleBar(position='bottomleft').add_to(m) # Removed due to ImportError

# 2. Add North Arrow (Injected HTML)
north_arrow_html = '''
<div style="
    position: fixed;
    top: 30px; right: 30px; width: 40px; height: 40px;
    z-index: 9999; pointer-events: none;
    ">
    <img src="https://freesvg.org/img/north-arrow-2.png"
         style="width:100%; height:100%;">
</div>
'''
m.get_root().html.add_child(Element(north_arrow_html))
# Create the HTML for the legend
legend_html = '''
{% macro html(this, kwargs) %}
<div style="
    position: fixed;
    bottom: 50px; right: 50px; width: 280px; height: 140px;
    background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
    padding: 10px;
    border-radius: 5px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    ">
    <b>Map Legend</b><br>
    <i class="fa fa-map-marker" style="color:red"></i>&nbsp; Intersections (Most Crashes)<br>
    <i class="fa fa-map-marker" style="color:orange"></i>&nbsp; Intersections (Most VRU Crashes)<br>
    <i class="fa fa-bus" style="color:blue"></i>&nbsp; Bus Stops (Most Crashes)<br>
    <i class="fa fa-user" style="color:green"></i>&nbsp; Bus Stops (Most VRU Crashes)
</div>
{% endmacro %}
'''

# Create a MacroElement and add it to the map
from branca.element import Template, MacroElement

legend = MacroElement()
legend._template = Template(legend_html)

m.get_root().add_child(legend)

# Create FeatureGroups for each category to add to LayerControl
intersections_fg = folium.FeatureGroup(name='Intersections with most crashes (Red)').add_to(m)
vru_intersections_fg = folium.FeatureGroup(name='Intersections with most VRU crashes (Orange)').add_to(m)
all_crashes_stops_fg = folium.FeatureGroup(name='Bus Stops with most crashes (Blue)').add_to(m)
vru_crashes_stops_fg = folium.FeatureGroup(name='Bus Stops with most VRU crashes (Green)').add_to(m)

# Add markers for each of the top intersections (Red)
for idx, row in gdf_intersections.iterrows():
    popup_content = f"Intersection ID: {row['NEAR_FID']}<br>Crashes: {near_fid_counts_intersections.get(row['NEAR_FID'], 'N/A')}"
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(f"<div style='width:150px;'>{popup_content}</div>"),
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(intersections_fg)

# Add markers for each of the top VRU intersections (Orange)
for idx, row in gdf_vru_intersections.iterrows():
    popup_content = f"Intersection (VRU Crashes) ID: {int(row['NEAR_FID'])}<br>Crashes: {near_fid_counts_intersections.get(row['NEAR_FID'], 'N/A')}"
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(f"<div style='width:200px;'>{popup_content}</div>"),
        icon=folium.Icon(color='orange', icon='info-sign')
    ).add_to(vru_intersections_fg)

# Add markers for each of the top bus stops for all crashes (Blue)
for idx, row in gdf_all_crashes_stops.iterrows():
     # Get the crash count for this bus stop
    crash_count = near_fid_counts_all_crashes.get(row['OBJECTID'], 'N/A')
    popup_content = f"Bus Stop ID: {row['OBJECTID']}<br>All Crashes: {crash_count}<br>Land Use: {row['STOP_LandT']}"
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(f"<div style='width:150px;'>{popup_content}</div>"),
        icon=folium.Icon(color='blue', icon='bus')
    ).add_to(all_crashes_stops_fg)

# Add markers for each of the top bus stops for VRU crashes (Green)
for idx, row in gdf_vru_crashes_stops.iterrows():
    # Get the VRU crash count for this bus stop
    vru_crash_count = near_fid_counts_vru_crashes.get(row['OBJECTID'], 'N/A')
    popup_content = f"Bus Stop ID: {row['OBJECTID']}<br>VRU Crashes: {vru_crash_count}<br>Land Use: {row['STOP_LandT']}"
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(f"<div style='width:150px;'>{popup_content}</div>"),
        icon=folium.Icon(color='green', icon='user') # Using a user icon for VRU (Vulnerable Road User)
    ).add_to(vru_crashes_stops_fg)

# Add a layer control to the map to toggle layers
#folium.LayerControl(collapsed=False).add_to(m)

print("Red=Intersections with the most crashes")
print("Orange=Intersections with the most VRU crashes")
print("Blue=Bus Stops with the most crashes")
print("Green=Bus Stops with the most VRU crashes")

# Display the map
m.save("Crash_Analysis_Map.html")

# Export to PNG (Requires Selenium and a Webdriver like ChromeDriver)
#try:
    #img_data = m._to_png(5) # 5 second delay to let tiles load
    #with open('Crash_Analysis_Map.png', 'wb') as f:
        #f.write(img_data)
    #print("Map successfully exported as PNG.")
#except Exception as e:
    #print(f"PNG export failed: {e}")
    #print("Note: PNG export requires Selenium and a Webdriver (Chrome/Firefox) installed.")

# Display the Map
m
