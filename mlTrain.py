import time
start_time = time.time()
import streamlit as st
import pandas as pd
import folium
import random
import math
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
from streamlit_folium import folium_static

# Fixed file locations
file_location_1 = 'location of connectivity.csv'  # Location of the csv file with connectivity data
file_location_2 = 'location of request.csv'  # Location of the csv file with request data
file_location_3 = 'location of transaction.csv'  # Location of the csv file with transaction data

def load_data(file_path, file_name):
    data = pd.read_csv(file_path)
    data['File'] = file_name  # Add 'File' column
    return data

def auto_select_lat_lon_columns(data):
    lat_column = next((col for col in data.columns if 'lat' in col.lower()), None)
    lon_column = next((col for col in data.columns if 'lon' in col.lower()), None)
    return lat_column, lon_column

def display_map_with_lines(data, lat_column, lon_column, title):
    map_center = [data[lat_column].mean(), data[lon_column].mean()]
    my_map = folium.Map(location=map_center, zoom_start=10, tiles="OpenStreetMap")

    # Add markers for each location
    for index, row in data.iterrows():
        color = 'green' if 'most recent connectivity' in row['File'].lower() else ('red' if 'request for sim swap' in row['File'].lower() else 'blue')
        folium.Marker([row[lat_column], row[lon_column]],
                      popup=f"ID No.: {row['ID No.']}, File: {row['File']}",
                      icon=folium.Icon(color=color)).add_to(my_map)

    # Add lines between locations
    for i in range(len(data) - 1):
        start_point = (data.iloc[i][lat_column], data.iloc[i][lon_column])
        end_point = (data.iloc[i + 1][lat_column], data.iloc[i + 1][lon_column])
        folium.PolyLine([start_point, end_point], color='blue').add_to(my_map)

    st.write(f"### {title}")
    folium_static(my_map)

def authenticate(username, password):
    # Hardcoded credentials for demonstration purposes
    valid_username = "demo_user"
    valid_password = "demo_pass"

    return username == valid_username and password == valid_password

def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate the change in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Use the Haversine formula to calculate distance
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

def calculate_area(lat1, lon1, lat2, lon2, lat3, lon3):
    # Calculate the lengths of the three sides of the triangle
    side1 = calculate_distance(lat1, lon1, lat2, lon2)
    side2 = calculate_distance(lat2, lon2, lat3, lon3)
    side3 = calculate_distance(lat3, lon3, lat1, lon1)

    # Calculate the semi-perimeter
    s = (side1 + side2 + side3) / 2

    # Use Heron's formula to calculate the area of the triangle
    area = math.sqrt(s * (s - side1) * (s - side2) * (s - side3))

    return area

def calculate_search_speed(start_date_request, start_time_request, end_date_connectivity, end_time_connectivity, distance):
    # Combine date and time strings to create datetime objects
    start_datetime_str = f"{start_date_request} {start_time_request}"
    end_datetime_str = f"{end_date_connectivity} {end_time_connectivity}"
    
    # Convert datetime strings to datetime objects
    start_datetime = datetime.strptime(start_datetime_str, "%m/%d/%Y %H:%M")
    end_datetime = datetime.strptime(end_datetime_str, "%m/%d/%Y %H:%M")
    
    # Calculate the time taken for the search operation in seconds
    time_taken = (end_datetime - start_datetime).total_seconds()
    
    # Calculate the speed in km/h
    speed = (distance / 1000) / (time_taken / 3600)
    
    return speed

def verify_sim_swap(request_df, connectivity_df, transaction_df, threshold_speed):
    request_time = datetime.strptime(request_df['Date'].iloc[0] + ' ' + request_df['Time'].iloc[0], '%m/%d/%Y %H:%M')
    connectivity_time = datetime.strptime(connectivity_df['Date'].iloc[0] + ' ' + connectivity_df['Time'].iloc[0], '%m/%d/%Y %H:%M')
    transaction_time = datetime.strptime(transaction_df['Date'].iloc[0] + ' ' + transaction_df['Time'].iloc[0], '%m/%d/%Y %H:%M')

    distance_req_conn = calculate_distance(request_df['Latitude'].iloc[0], request_df['Longitude'].iloc[0], connectivity_df['Latitude'].iloc[0], connectivity_df['Longitude'].iloc[0])
    distance_req_trans = calculate_distance(request_df['Latitude'].iloc[0], request_df['Longitude'].iloc[0], transaction_df['Latitude'].iloc[0], transaction_df['Longitude'].iloc[0])

    time_diff_conn = (request_time - connectivity_time).total_seconds() / 3600  # in hours
    time_diff_trans = (request_time - transaction_time).total_seconds() / 3600  # in hours

    if request_time > connectivity_time:
        speed = distance_req_trans / time_diff_trans if time_diff_trans != 0 else float('inf')
    else:
        speed = distance_req_conn / time_diff_conn if time_diff_conn != 0 else float('inf')

    validity = "valid" if speed <= threshold_speed else "suspicious"

    return speed, distance_req_conn, distance_req_trans, validity

def home_page():
    st.markdown("<h1 style='color:green;'>SS Detection System - Homepage</h1>", unsafe_allow_html=True)
    st.write("Navigate to different sections using the sidebar.")

def maps_page(data_1, data_2, data_3, lat_column_1, lon_column_1, lat_column_2, lon_column_2, lat_column_3, lon_column_3):
    st.markdown("<h1 style='color:orange;'>Maps Section.</h1>", unsafe_allow_html=True)

    subpage_selection = st.radio("Select Subpage", ["The Location of most recent connectivity",
                                                    "The Location of Request for SIM Swap",
                                                    "Location of Latest Transaction"])

    if subpage_selection == "The Location of most recent connectivity":
        display_map_with_lines(data_1, lat_column_1, lon_column_1, "Map - The Location of most recent connectivity")
    elif subpage_selection == "The Location of Request for SIM Swap":
        display_map_with_lines(data_2, lat_column_2, lon_column_2, "Map - The Location of Request for SIM Swap")
    elif subpage_selection == "Location of Latest Transaction":
        display_map_with_lines(data_3, lat_column_3, lon_column_3, "Map - Location of Latest Transaction")
def generate_dummy_locations(true_lat, true_lon, k=5, radius=0.01):
    """Generate k locations, including the true location and k-1 dummy locations."""
    try:
        locations = [(true_lat, true_lon)]  # Include true location
        for _ in range(k - 1):
            lat_offset = random.uniform(-radius, radius)
            lon_offset = random.uniform(-radius, radius)
            dummy_lat = true_lat + lat_offset
            dummy_lon = true_lon + lon_offset
            locations.append((dummy_lat, dummy_lon))
        return locations
    except Exception as e:
        st.error(f"Error generating dummy locations: {e}")
        return [(true_lat, true_lon)]

def search_page(data_1, data_2, data_3, lat_column_1, lon_column_1, lat_column_2, lon_column_2, lat_column_3, lon_column_3):
    st.title("Search Section")

    # Debugging: Verify data
    try:
        st.write("Debug: Data shapes", data_1.shape, data_2.shape, data_3.shape)
        st.write("Debug: data_3 columns", data_3.columns.tolist())
    except Exception as e:
        st.error(f"Error accessing datasets: {e}")
        return

    # Dummy location configuration
    st.subheader("Dummy Location Settings")
    use_dummy_locations = st.checkbox("Enable Dummy Locations", value=False)
    k = st.slider("Number of Locations (1 Real + k-1 Dummy)", min_value=1, max_value=20, value=5, disabled=not use_dummy_locations)
    radius = st.slider("Radius for Dummy Locations (degrees)", min_value=0.001, max_value=0.1, value=0.01, disabled=not use_dummy_locations)

    try:
        locations = data_2['Location'].dropna().unique()
    except Exception as e:
        st.error(f"Error accessing locations: {e}")
        return

    selected_location = st.selectbox("Select Location. (Location of Request for SIM Swap) *", options=locations, index=None)
    search_name = st.text_input("Enter Name or ID number for Search *")
    id_number = st.text_input("Enter Your ID Number for SIM Swap *")
    speed_threshold = st.number_input("Enter Speed Threshold (km/h) *", min_value=0.0, step=0.1)

    search_button_key = "search_button_key_col1"

    # Performance analysis section
    st.subheader("Performance Analysis")
    analyze_performance = st.checkbox("Analyze Performance Across Configurations", value=False)
    k_values = [0, 5, 10]  # Reduced for faster testing
    radius_values = [0.01, 0.05]

    performance_results = []

    if st.button("Search", key=search_button_key):
        start_time = time.time()

        # Input validation
        input_validation_start = time.time()
        if not search_name or not selected_location or not id_number or speed_threshold is None:
            st.error("All fields marked with * are required.")
            print(f"Input Validation Time: {time.time() - input_validation_start:.6f} seconds")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return
        input_validation_time = time.time() - input_validation_start
        print(f"Input Validation Time: {input_validation_time:.6f} seconds")

        # ID check against transaction file
        id_check_start = time.time()
        try:
            transaction_id_numbers = data_3['ID No.'].astype(str).tolist()
            if id_number.strip() not in transaction_id_numbers:
                st.error("The ID number entered is not found in the transaction data.")
                print(f"ID Check Time: {time.time() - id_check_start:.6f} seconds")
                print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
                return
        except Exception as e:
            st.error(f"Error checking ID: {e}")
            print(f"ID Check Time: {time.time() - id_check_start:.6f} seconds")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return
        id_check_time = time.time() - id_check_start
        print(f"ID Check Time: {id_check_time:.6f} seconds")

        # Search operation
        search_start = time.time()
        try:
            search_result_1 = data_1[data_1['First Name'].str.contains(search_name, case=False, na=False)]
            search_result_3 = data_3[data_3['ID No.'].astype(str).str.contains(search_name, case=False, na=False)]
            combined_search_data = pd.concat([search_result_1, search_result_3])
        except Exception as e:
            st.error(f"Error during search: {e}")
            print(f"Search Operation Time: {time.time() - search_start:.6f} seconds")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return
        search_time = time.time() - search_start
        print(f"Search Operation Time: {search_time:.6f} seconds")

        if combined_search_data.empty:
            st.warning(f"No matching records found for '{search_name}'.")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return

        # Performance analysis loop
        if analyze_performance:
            for k_test in k_values:
                for radius_test in radius_values:
                    test_start = time.time()
                    map_render_start = time.time()
                    try:
                        my_map = folium.Map(location=[combined_search_data[lat_column_1].mean(), combined_search_data[lon_column_1].mean()], zoom_start=10, tiles="OpenStreetMap")

                        # Plot selected location
                        selected_lat = data_2[data_2['Location'] == selected_location][lat_column_2].iloc[0]
                        selected_lon = data_2[data_2['Location'] == selected_location][lon_column_2].iloc[0]
                        selected_locations = [(selected_lat, selected_lon)] if k_test == 0 else generate_dummy_locations(selected_lat, selected_lon, k_test, radius_test)
                        for i, (lat, lon) in enumerate(selected_locations):
                            popup = f"Selected Location: {selected_location}" if i == 0 else f"Dummy Location {i}"
                            color = 'green' if i == 0 else 'gray'
                            folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color)).add_to(my_map)

                        # Plot recent transaction location
                        recent_transaction_lat = data_3[lat_column_3].mean()
                        recent_transaction_lon = data_3[lon_column_3].mean()
                        recent_transaction_name = data_3['Location Name'].iloc[0]
                        transaction_locations = [(recent_transaction_lat, recent_transaction_lon)] if k_test == 0 else generate_dummy_locations(recent_transaction_lat, recent_transaction_lon, k_test, radius_test)
                        for i, (lat, lon) in enumerate(transaction_locations):
                            popup = f"{recent_transaction_name}" if i == 0 else f"Dummy Transaction {i}"
                            color = 'blue' if i == 0 else 'gray'
                            folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color)).add_to(my_map)

                        # Plot connectivity location
                        connectivity_lat = data_1[lat_column_1].mean()
                        connectivity_lon = data_1[lon_column_1].mean()
                        connectivity_name = data_1['Location Name'].iloc[0]
                        connectivity_locations = [(connectivity_lat, connectivity_lon)] if k_test == 0 else generate_dummy_locations(connectivity_lat, connectivity_lon, k_test, radius_test)
                        for i, (lat, lon) in enumerate(connectivity_locations):
                            popup = f"{connectivity_name}" if i == 0 else f"Dummy Connectivity {i}"
                            color = 'red' if i == 0 else 'gray'
                            folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color)).add_to(my_map)

                        # Draw lines between true locations
                        folium.PolyLine(locations=[[selected_lat, selected_lon], [recent_transaction_lat, recent_transaction_lon]], color='red', weight=2.5, opacity=1).add_to(my_map)
                        folium.PolyLine(locations=[[recent_transaction_lat, recent_transaction_lon], [connectivity_lat, connectivity_lon]], color='red', weight=2.5, opacity=1).add_to(my_map)
                        folium.PolyLine(locations=[[connectivity_lat, connectivity_lon], [selected_lat, selected_lon]], color='red', weight=2.5, opacity=1).add_to(my_map)
                    except Exception as e:
                        st.error(f"Error rendering map for k={k_test}, radius={radius_test}: {e}")
                        continue
                    map_render_time = time.time() - map_render_start

                    # Distance calculation
                    distance_calc_start = time.time()
                    try:
                        distance_to_connectivity = calculate_distance(selected_lat, selected_lon, connectivity_lat, connectivity_lon)
                        distance_to_transaction = calculate_distance(selected_lat, selected_lon, recent_transaction_lat, recent_transaction_lon)
                        distance_between_locations = calculate_distance(recent_transaction_lat, recent_transaction_lon, connectivity_lat, connectivity_lon)
                        area_covered = calculate_area(selected_lat, selected_lon, recent_transaction_lat, recent_transaction_lon, connectivity_lat, connectivity_lon)
                    except Exception as e:
                        st.error(f"Error calculating distances: {e}")
                        continue
                    distance_calc_time = time.time() - distance_calc_start

                    # Speed calculation
                    speed_calc_start = time.time()
                    try:
                        request_date = data_2['Date'].iloc[0]
                        request_time = data_2['Time'].iloc[0]
                        connectivity_date = data_1['Date'].iloc[0]
                        connectivity_time = data_1['Time'].iloc[0]
                        request_datetime = datetime.strptime(f"{request_date} {request_time}", "%m/%d/%Y %H:%M")
                        connectivity_datetime = datetime.strptime(f"{connectivity_date} {connectivity_time}", "%m/%d/%Y %H:%M")
                        time_diff = abs((request_datetime - connectivity_datetime).total_seconds() / 3600)
                        speed = distance_to_connectivity / time_diff
                    except Exception as e:
                        st.error(f"Error calculating speed: {e}")
                        continue
                    speed_calc_time = time.time() - speed_calc_start

                    total_test_time = time.time() - test_start

                    # Store results
                    performance_results.append({
                        'k': k_test,
                        'Radius': radius_test,
                        'Input Validation Time (s)': input_validation_time,
                        'ID Check Time (s)': id_check_time,
                        'Search Operation Time (s)': search_time,
                        'Map Rendering Time (s)': map_render_time,
                        'Distance Calculation Time (s)': distance_calc_time,
                        'Speed Calculation Time (s)': speed_calc_time,
                        'Total Processing Time (s)': total_test_time
                    })

            # Display performance table
            if performance_results:
                st.write("### Performance Results")
                results_df = pd.DataFrame(performance_results)
                st.dataframe(results_df)

        # Regular execution
        map_render_start = time.time()
        try:
            st.write("### Search Results Map")
            my_map = folium.Map(location=[combined_search_data[lat_column_1].mean(), combined_search_data[lon_column_1].mean()], zoom_start=10, tiles="OpenStreetMap")

            # Plot selected location
            selected_lat = data_2[data_2['Location'] == selected_location][lat_column_2].iloc[0]
            selected_lon = data_2[data_2['Location'] == selected_location][lon_column_2].iloc[0]
            selected_locations = [(selected_lat, selected_lon)] if not use_dummy_locations else generate_dummy_locations(selected_lat, selected_lon, k, radius)
            for i, (lat, lon) in enumerate(selected_locations):
                popup = f"Selected Location: {selected_location}" if i == 0 else f"Dummy Location {i}"
                color = 'green' if i == 0 else 'gray'
                folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color)).add_to(my_map)

            # Plot recent transaction location
            recent_transaction_lat = data_3[lat_column_3].mean()
            recent_transaction_lon = data_3[lon_column_3].mean()
            recent_transaction_name = data_3['Location Name'].iloc[0]
            transaction_locations = [(recent_transaction_lat, recent_transaction_lon)] if not use_dummy_locations else generate_dummy_locations(recent_transaction_lat, recent_transaction_lon, k, radius)
            for i, (lat, lon) in enumerate(transaction_locations):
                popup = f"{recent_transaction_name}" if i == 0 else f"Dummy Transaction {i}"
                color = 'blue' if i == 0 else 'gray'
                folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color)).add_to(my_map)

            # Plot connectivity location
            connectivity_lat = data_1[lat_column_1].mean()
            connectivity_lon = data_1[lon_column_1].mean()
            connectivity_name = data_1['Location Name'].iloc[0]
            connectivity_locations = [(connectivity_lat, connectivity_lon)] if not use_dummy_locations else generate_dummy_locations(connectivity_lat, connectivity_lon, k, radius)
            for i, (lat, lon) in enumerate(connectivity_locations):
                popup = f"{connectivity_name}" if i == 0 else f"Dummy Connectivity {i}"
                color = 'red' if i == 0 else 'gray'
                folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color)).add_to(my_map)

            # Draw lines between true locations
            folium.PolyLine(locations=[[selected_lat, selected_lon], [recent_transaction_lat, recent_transaction_lon]], color='red', weight=2.5, opacity=1).add_to(my_map)
            folium.PolyLine(locations=[[recent_transaction_lat, recent_transaction_lon], [connectivity_lat, connectivity_lon]], color='red', weight=2.5, opacity=1).add_to(my_map)
            folium.PolyLine(locations=[[connectivity_lat, connectivity_lon], [selected_lat, selected_lon]], color='red', weight=2.5, opacity=1).add_to(my_map)

            folium_static(my_map)
        except Exception as e:
            st.error(f"Error rendering map: {e}")
            print(f"Map Rendering Time: {time.time() - map_render_start:.6f} seconds")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return
        map_render_time = time.time() - map_render_start
        print(f"Map Rendering Time: {map_render_time:.6f} seconds")

        # Distance calculation
        distance_calc_start = time.time()
        try:
            distance_to_connectivity = calculate_distance(selected_lat, selected_lon, connectivity_lat, connectivity_lon)
            distance_to_transaction = calculate_distance(selected_lat, selected_lon, recent_transaction_lat, recent_transaction_lon)
            distance_between_locations = calculate_distance(recent_transaction_lat, recent_transaction_lon, connectivity_lat, connectivity_lon)
            area_covered = calculate_area(selected_lat, selected_lon, recent_transaction_lat, recent_transaction_lon, connectivity_lat, connectivity_lon)
            st.write("### Distances:")
            st.write(f"Distance from Request to Connectivity: {distance_to_connectivity:.2f} km")
            st.write(f"Distance from Request to Transaction: {distance_to_transaction:.2f} km")
            st.write(f"Distance between Transaction and Connectivity: {distance_between_locations:.2f} km")
            st.write(f"Area Covered: {area_covered:.2f} sq km")
        except Exception as e:
            st.error(f"Error calculating distances: {e}")
            print(f"Distance Calculation Time: {time.time() - distance_calc_start:.6f} seconds")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return
        distance_calc_time = time.time() - distance_calc_start
        print(f"Distance Calculation Time: {distance_calc_time:.6f} seconds")

        # Speed calculation
        speed_calc_start = time.time()
        try:
            request_date = data_2['Date'].iloc[0]
            request_time = data_2['Time'].iloc[0]
            connectivity_date = data_1['Date'].iloc[0]
            connectivity_time = data_1['Time'].iloc[0]
            request_datetime = datetime.strptime(f"{request_date} {request_time}", "%m/%d/%Y %H:%M")
            connectivity_datetime = datetime.strptime(f"{connectivity_date} {connectivity_time}", "%m/%d/%Y %H:%M")
            time_diff = abs((request_datetime - connectivity_datetime).total_seconds() / 3600)
            speed = distance_to_connectivity / time_diff
            st.write(f"The calculated speed from Connectivity to Request is: {speed:.2f} km/h")
            validity = "valid" if speed <= speed_threshold else "suspicious"
            st.write(f"The SIM swap request is marked as **{validity}**.")
        except Exception as e:
            st.error(f"Error calculating speed: {e}")
            print(f"Speed Calculation Time: {time.time() - speed_calc_start:.6f} seconds")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return
        speed_calc_time = time.time() - speed_calc_start
        print(f"Speed Calculation Time: {speed_calc_time:.6f} seconds")

        # Display search results
        result_display_start = time.time()
        try:
            st.write("### Search Results:")
            st.write(combined_search_data[['First Name', 'Last Name', 'ID No.', 'Phone Number']])
        except Exception as e:
            st.error(f"Error displaying results: {e}")
            print(f"Result Display Time: {time.time() - result_display_start:.6f} seconds")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return
        result_display_time = time.time() - result_display_start
        print(f"Result Display Time: {result_display_time:.6f} seconds")

        # SIM Swap Section
        sim_swap_start = time.time()
        try:
            st.header("SIM Swap Section")
            st.write("Here you can perform SIM swap between two numbers.")
            if not combined_search_data.empty:
                if id_number in transaction_id_numbers:
                    if validity == "valid":
                        st.write(f"ID number {id_number} is valid. Proceed with SIM swap.")
                        first_number = combined_search_data.iloc[0]['Phone Number']
                        st.write(f"The first number from search results: {first_number}")
                        number2 = st.text_input("Enter the second number:")
                        if st.button("Swap"):
                            if not number2:
                                st.error("Please enter the second number.")
                            else:
                                st.write(f"You have requested to swap {first_number} with {number2}.")
                                # Perform SIM swap here
                    else:
                        st.error("SIM swap cannot proceed as the request is marked suspicious.")
                else:
                    st.error(f"ID number {id_number} is not found in the transaction data.")
            else:
                st.warning("No matching user data found for SIM swap.")
        except Exception as e:
            st.error(f"Error in SIM swap section: {e}")
            print(f"SIM Swap Section Time: {time.time() - sim_swap_start:.6f} seconds")
            print(f"Total Processing Time: {time.time() - start_time:.6f} seconds")
            return
        sim_swap_time = time.time() - sim_swap_start
        print(f"SIM Swap Section Time: {sim_swap_time:.6f} seconds")

        total_time = time.time() - start_time
        print(f"Total Processing Time: {total_time:.6f} seconds")

        # Add user configuration to performance results if not in analysis mode
        if not analyze_performance:
            performance_results.append({
                'k': k if use_dummy_locations else 0,
                'Radius': radius if use_dummy_locations else 0,
                'Input Validation Time (s)': input_validation_time,
                'ID Check Time (s)': id_check_time,
                'Search Operation Time (s)': search_time,
                'Map Rendering Time (s)': map_render_time,
                'Distance Calculation Time (s)': distance_calc_time,
                'Speed Calculation Time (s)': speed_calc_time,
                'Result Display Time (s)': result_display_time,
                'SIM Swap Section Time (s)': sim_swap_time,
                'Total Processing Time (s)': total_time
            })
            st.write("### Performance Results")
            results_df = pd.DataFrame(performance_results)
            st.dataframe(results_df)
def main():
    st.set_page_config(page_title="SIM Swap .", page_icon=":earth_americas:")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='color:green;'>SS - Detection System.</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='color:orange;'>Sign In.</h1>", unsafe_allow_html=True)

        # Sidebar for authentication
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")

        sign_in_button_key = "sign_in_button_key"  # Unique key for the sign-in button

        if st.button("Sign In", key=sign_in_button_key):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.success("Authentication successful! You can now access the system.")

            else:
                st.error("Authentication failed. Please check your username and password.")
    else:
        # Load data from the CSV files
        data_1 = load_data(file_location_1, "The Location of most recent connectivity")
        data_2 = load_data(file_location_2, "The Location of Request for Swap")
        data_3 = load_data(file_location_3, "Location of Latest Transaction")

        # Automatically select latitude and longitude columns
        lat_column_1, lon_column_1 = auto_select_lat_lon_columns(data_1)
        lat_column_2, lon_column_2 = auto_select_lat_lon_columns(data_2)
        lat_column_3, lon_column_3 = auto_select_lat_lon_columns(data_3)
    
        # Show the main content of the app after successful authentication
        st.sidebar.title("Navigation")
        home_button_key = "home_button_key"  # Unique key for the home button
        maps_button_key = "maps_button_key"  # Unique key for the maps button
        search_button_key = "search_button_key"  # Unique key for the search button

        selected_page = st.sidebar.radio("Select Page", ["Home", "Maps", "Search"])

        if selected_page == "Home":
            home_page()
        elif selected_page == "Maps":
            maps_page(data_1, data_2, data_3, lat_column_1, lon_column_1, lat_column_2, lon_column_2, lat_column_3, lon_column_3)
        elif selected_page == "Search":
            search_page(data_1, data_2, data_3, lat_column_1, lon_column_1, lat_column_2, lon_column_2, lat_column_3, lon_column_3)

if __name__ == "__main__":
    main()
end_time = time.time()
elapsed_time = end_time - start_time
print(f'Processing time: {elapsed_time:.6f} seconds')
