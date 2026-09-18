# This python code was developed to find the top 45 intersection with the highest crash frequencies and create maps and histograms that depict the relationships between the crashes and the transit stops. The histogram output also shows the nearest transit stop location. 

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the crash data, change the spatial threshold or dataset here
try:
    df = pd.read_csv('Crashes250ftIntersectionNI.csv')
except FileNotFoundError:
    print("Error: Crashes250ftIntersectionNI.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Load the bus stop intersection data
try:
    df_stops = pd.read_csv('BusStops250ftIntersectionNI.csv')
except FileNotFoundError:
    print("Error: BusStops250ftIntersectionNI.csv not found. Please make sure the file is in the correct directory.")
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
    stop_info_row = df_stops[df_stops['NEAR_FID'] == fid]
    if not stop_info_row.empty:
        bus_stop_distance = stop_info_row['NEAR_DIST'].iloc[0]
        stop_landt = stop_info_row['STOP_LandT'].iloc[0]
    else:
        bus_stop_distance = "N/A" # Handle cases where the FID is not found in the stops data
        stop_landt = "N/A"

    print(f"\nIntersection ID: {fid}")
    print(f"Number of entries: {num_entries}")
    print(f"Average Crash Distance: {mean_near_dist:.2f}")
    if isinstance(bus_stop_distance, (int, float)):
        print(f"Bus Stop distance to nearest intersection: {bus_stop_distance:.2f}")
    else:
        print(f"Bus Stop distance to nearest intersection: {bus_stop_distance}")
    print(f"Land Use Type: {stop_landt}")

    # Create the histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df_fid[df_fid['NEAR_DIST'] <= 250], x='NEAR_DIST', kde=True) #limit the crashes to 250ft
    plt.xlim(-10, 275)   # sets x-axis from 0 to 275 ft

    # Add a vertical line for the bus stop distance to the nearest intersection
    if isinstance(bus_stop_distance, (int, float)):
        plt.axvline(bus_stop_distance, color='green', linestyle='-', linewidth=2, label=f'Bus Stop Location: {bus_stop_distance:.2f} ft from intersection')
        plt.legend()

    # Add a vertical line at x=0 for the intersection
    plt.axvline(x=0, color='red', linestyle='dashed', label='Intersection')
    plt.legend()

    # plt.title(f'Histogram of Distance to nearest intersection for Intersection ID: {fid}')
    plt.xlabel('Crashes Distance to Intersection (ft)')
    plt.ylabel('Frequency')
    plt.show()
# Install necessary libraries for mapping
%pip install geopandas folium
import geopandas as gpd
import folium
import pandas as pd

# Load the crash data
try:
    df = pd.read_csv('Crashes250ftIntersectionNI.csv')
except FileNotFoundError:
    print("Error: Crashes250ftIntersectionNI.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Load the bus stop intersection data
try:
    df_stops = pd.read_csv('BusStops1400ftIntersectionNI.csv')
except FileNotFoundError:
    print("Error: BusStops1400ftIntersectionNI.csv not found. Please make sure the file is in the correct directory.")
    exit()

# Calculate the mean Latitude and Longitude for each NEAR_FID
# This gives a more accurate center point for each intersection
intersection_locations = df[df['NEAR_FID'].isin(top_45_near_fids)].groupby('NEAR_FID')[['Latitude', 'Longitude']].mean().reset_index()

# Merge with the crash counts for popup info
top_intersections_df = intersection_locations.merge(near_fid_counts.rename('Crash_Count'), left_on='NEAR_FID', right_index=True)

# Convert to GeoDataFrame (assuming 'LATITUDE' and 'LONGITUDE' columns exist in df)
# Replace 'LATITUDE' and 'LONGITUDE' with the actual column names in your df if they are different
gdf_intersections = gpd.GeoDataFrame(
    top_intersections_df, geometry=gpd.points_from_xy(top_intersections_df['Longitude'], top_intersections_df['Latitude']))

# Create a base map centered around the mean location of the intersections
map_center = [gdf_intersections['Latitude'].mean(), gdf_intersections['Longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=10)

# Add markers for each of the top intersections
for idx, row in gdf_intersections.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"Intersection ID: {row['NEAR_FID']}<br>Crashes: {row['Crash_Count']}",
        icon=folium.Icon(color='red', icon='info-sign') # Changed color to red for intersections
    ).add_to(m)

# Display the map
m
