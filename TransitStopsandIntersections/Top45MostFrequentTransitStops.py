# This python code was developed to find the top 45 transit stops with the highest crash frequencies and create maps and histograms that depict the relationships between the crashes and the transit stops. The histogram output also shows the nearest intersection location.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the crash data, change the spatial threshold or dataset 
here
try:
    df = pd.read_csv('Crashes1400ftBusStopNICC.csv')
except FileNotFoundError:
    print("Error: Crashes1400ftBusStop.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Load the bus stop intersection data
try:
    df_stops = pd.read_csv('BusStops1400ftIntersectionNI.csv')
except FileNotFoundError:
    print("Error: BusStops1400ftIntersection.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Sort the crash data by NEAR_FID (optional based on the task, but good practice for grouping)
df_sorted = df.sort_values(by='NEAR_FID')

# Count the number of entries for each unique NEAR_FID
near_fid_counts = df_sorted['NEAR_FID'].value_counts()

# Take the top 45 most frequent NEAR_FID values
top_45_near_fids = near_fid_counts.head(45).index.tolist()

print("Top 45 most frequent NEAR_FID values:")
print(top_45_near_fids)

# Create a histogram for each of the top 10 NEAR_FID values
for fid in top_45_near_fids:
    # Filter the crash DataFrame for the current NEAR_FID
    df_fid = df_sorted[df_sorted['NEAR_FID'] == fid]

    # Calculate the number of entries and the mean NEAR_DIST from crash data
    num_entries = len(df_fid)
    mean_near_dist = df_fid['NEAR_DIST'].mean()

    # Find the bus stop distance to the nearest intersection and STOP_LandT
    stop_info_row = df_stops[df_stops['OBJECTID'] == fid]
    if not stop_info_row.empty:
        bus_stop_distance = stop_info_row['NEAR_DIST'].iloc[0]
        stop_landt = stop_info_row['STOP_LandT'].iloc[0]
    else:
        bus_stop_distance = "N/A" # Handle cases where the FID is not found in the stops data
        stop_landt = "N/A"

    print(f"Bus Stop ID: {fid}")
    print(f"Number of entries: {num_entries}")
    print(f"Average Crash Distance: {mean_near_dist:.2f}")
    if isinstance(bus_stop_distance, (int, float)):
        print(f"Bus Stop distance to nearest intersection: {bus_stop_distance:.2f}")
    else:
        print(f"Bus Stop distance to nearest intersection: {bus_stop_distance}")
    print(f"Land Use Type: {stop_landt}")

    # Create the histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df_fid, x='NEAR_DIST', kde=True)
    plt.xlabel('Crashes Distance to Nearest Bus Stop')
    plt.xlim(-50, 1400)   # sets x-axis from 0 to 1400 ft
    plt.ylabel('Frequency')

    # Add a vertical line at x=0 for the bus stop location
    plt.axvline(x=0, color='green', linestyle='-', label='Bus Stop')

    # Add a vertical line for the bus stop distance to the nearest intersection
    if isinstance(bus_stop_distance, (int, float)):
        plt.axvline(bus_stop_distance, color='red', linestyle='dashed', linewidth=2, label=f'Intersection Location: {bus_stop_distance:.2f} ft from bus stop')
        # Add a 400ft buffer around the intersection location
        # Add If statement if bus stop distance is less than 400 (so xmin-400 will be lesser than 0)
        if bus_stop_distance < 400:
          plt.axvspan(xmin=0, xmax=bus_stop_distance + 400, color='red', alpha=0.2, label='Intersection Influence Area')
        else:
          plt.axvspan(xmin=bus_stop_distance - 400, xmax=bus_stop_distance + 400, color='red', alpha=0.2, label='Intersection Influence Area')
        plt.legend()

    # plt.title(f'Histogram of distance to nearest bus stop for Bus Stop ID: {fid}')
    plt.xlabel('Crash Distance to Nearest Bus Stop (ft)')
    plt.ylabel('Crash Frequency')
    plt.show()
# Install necessary libraries for mapping
%pip install geopandas folium
import geopandas as gpd
import folium

# Merge df_stops with the top_45_near_fids to get the locations of the top bus stops
top_stops_df = df_stops[df_stops['OBJECTID'].isin(top_45_near_fids)].copy()

# Convert to GeoDataFrame (assuming 'LATITUDE' and 'LONGITUDE' columns exist in df_stops)
# Replace 'LATITUDE' and 'LONGITUDE' with the actual column names in your df_stops if they are different
gdf_stops = gpd.GeoDataFrame(
    top_stops_df, geometry=gpd.points_from_xy(top_stops_df['longitude'], top_stops_df['latitude']))

# Create a base map centered around the mean location of the bus stops
map_center = [gdf_stops['latitude'].mean(), gdf_stops['longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=10)

# Add markers for each of the top bus stops
for idx, row in gdf_stops.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"Bus Stop ID: {row['OBJECTID']}<br>Land Use Type: {row['STOP_LandT']}<br>Crashes: {near_fid_counts.get(row['OBJECTID'], 'N/A')}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

# Display the map
m
