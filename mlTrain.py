!pip install streamlit_folium
import streamlit as st
import pandas as pd
import folium
import math
from streamlit_folium import folium_static

# Fixed file locations
file_location_1 = 'location of connectivity.csv'  # Location of the csv file with connectivity data
file_location_2 = 'location of request.csv'  # Location of the csv file with request data
file_location_3 = 'Location of transaction.csv'  # Location of the csv file with transaction data

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


def home_page():
    st.markdown("<h1 style='color:green;'>Detection System - SIM Swap</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:orange;'>Welcome to the Home Page.</h1>", unsafe_allow_html=True)
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

def search_page(data_1, data_2, data_3, lat_column_1, lon_column_1, lat_column_2, lon_column_2, lat_column_3, lon_column_3):
    st.title("Search Section")

    # Search Section
    st.header("Search Section")

    # Get a list of all unique locations from data_2 (Location of Request for SIM Swap)
    locations = data_2['Location'].dropna().unique()

    # Create a selectbox for the user to select a location
    selected_location = st.selectbox("Select Location", options=locations, index=None)

    # Create a text input for the user to search for a name
    search_name = st.text_input("Enter Name or ID number for Search:")

    # Add a text input for entering ID number
    id_number = st.text_input("Enter ID Number for SIM Swap:")

    search_button_key = "search_button_key_col1"  # Unique key for the search button in column 1

    if st.button("Search", key=search_button_key):
        if not search_name:
            st.error("Please enter a name for the search.")
        elif not selected_location:
            st.error("Please select a location.")
        else:
            # Filter data based on the provided name
            search_result_1 = data_1[data_1['First Name'].str.contains(search_name, case=False, na=False)]
            search_result_3 = data_3[data_3['ID No.'].astype(str).str.contains(search_name, case=False, na=False)]

            # Combine search results into a single DataFrame
            combined_search_data = pd.concat([search_result_1, search_result_3])

            # Convert latitude and longitude columns to numeric
            combined_search_data[lat_column_1] = pd.to_numeric(combined_search_data[lat_column_1], errors='coerce')
            combined_search_data[lon_column_1] = pd.to_numeric(combined_search_data[lon_column_1], errors='coerce')

            # Drop rows with NaN values in latitude or longitude columns
            combined_search_data = combined_search_data.dropna(subset=[lat_column_1, lon_column_1])

            # Check if search results are empty after dropping NaN values
            if combined_search_data.empty:
                st.warning(f"No matching records found for '{search_name}'.")
            else:
                # Display all search results on the map
                    # Display all search results on the map
                # Display all search results on the map
                st.write("### Search Results Map")

                # Create a folium map for all search results
                map_center = [combined_search_data[lat_column_1].mean(), combined_search_data[lon_column_1].mean()]
                my_map = folium.Map(location=map_center, zoom_start=10, tiles="OpenStreetMap")

                # Plot selected location
                selected_lat = data_2[data_2['Location'] == selected_location][lat_column_2].iloc[0]
                selected_lon = data_2[data_2['Location'] == selected_location][lon_column_2].iloc[0]
                selected_name = selected_location
                folium.Marker([selected_lat, selected_lon], popup=f"Selected Location: {selected_name}",
                            icon=folium.Icon(color='green')).add_to(my_map)

                # Plot recent transaction location
                recent_transaction_lat = data_3[lat_column_3].mean()
                recent_transaction_lon = data_3[lon_column_3].mean()
                recent_transaction_name = data_3['Location Name'].iloc[0]  # Assuming the column name is 'Location Name'
                folium.Marker([recent_transaction_lat, recent_transaction_lon], popup=f"{recent_transaction_name}",
                            icon=folium.Icon(color='blue')).add_to(my_map)

                # Plot connectivity location
                connectivity_lat = data_1[lat_column_1].mean()
                connectivity_lon = data_1[lon_column_1].mean()
                connectivity_name = data_1['Location Name'].iloc[0]  # Assuming the column name is 'Location Name'
                folium.Marker([connectivity_lat, connectivity_lon], popup=f"{connectivity_name}",
                            icon=folium.Icon(color='red')).add_to(my_map)

                # Plot search result locations
                for index, row in combined_search_data.iterrows():
                    location_name = row['Location Name']  # Assuming the column name is 'Location Name'
                    folium.Marker([row[lat_column_1], row[lon_column_1]], popup=f"Location: {location_name}",
                                icon=folium.Icon(color='orange')).add_to(my_map)

                # Draw lines to form a triangle between locations
                folium.PolyLine(locations=[[selected_lat, selected_lon], [recent_transaction_lat, recent_transaction_lon]],
                                color='black', weight=2.5, opacity=1).add_to(my_map)

                folium.PolyLine(locations=[[recent_transaction_lat, recent_transaction_lon], [connectivity_lat, connectivity_lon]],
                                color='black', weight=2.5, opacity=1).add_to(my_map)

                folium.PolyLine(locations=[[connectivity_lat, connectivity_lon], [selected_lat, selected_lon]],
                                color='black', weight=2.5, opacity=1).add_to(my_map)

                # Display the map
                folium_static(my_map)

                # Calculate distances and area, and display them
                distance_to_connectivity = calculate_distance(selected_lat, selected_lon, connectivity_lat, connectivity_lon)
                distance_to_transaction = calculate_distance(selected_lat, selected_lon, recent_transaction_lat, recent_transaction_lon)
                distance_between_locations = calculate_distance(recent_transaction_lat, recent_transaction_lon, connectivity_lat, connectivity_lon)
                area_covered = calculate_area(selected_lat, selected_lon, recent_transaction_lat, recent_transaction_lon, connectivity_lat, connectivity_lon)

                st.write("### Distances:")
                st.write(f"Distance to the location of most recent connectivity ({selected_location}): {distance_to_connectivity:.2f} km")
                st.write(f"Distance to the location of recent transaction: {distance_to_transaction:.2f} km")
                st.write(f"Distance between the recent transaction and connectivity locations: {distance_between_locations:.2f} km")
                st.write("### Area Covered:")
                st.write(f"The area covered by the triangle formed by the three locations is: {area_covered:.2f} square kilometers")

                # Perform SIM swap and display results (if applicable)
                if distance_to_transaction > 100:
                    st.warning("SIM swap is not allowed due to location variance.")
                else:
                    # Display search results
                    st.write("### Search Results:")
                    st.write(combined_search_data[['First Name', 'Last Name', 'ID No.','Phone Number']])

                    # SIM Swap Section
                    st.header("SIM Swap Section")
                    st.write("Here you can perform SIM swap between two numbers.")

                    if not combined_search_data.empty and id_number:
                        transaction_id_numbers = data_3['ID No.'].astype(str).tolist()
                        if id_number in transaction_id_numbers:
                            st.write(f"ID number {id_number} is valid. Proceed with SIM swap.")
                            first_number = combined_search_data.iloc[0]['Phone Number']
                            st.write(f"The first number from search results: {first_number}")
                            number2 = st.text_input("Enter the second number:")
                            if st.button("Swap"):
                                if not number2:
                                    st.error("Please enter the second number.")
                                else:
                                    st.write(f"You have requested to swap {first_number} with {number2}.")
                                    # Perform SIM swap here using the numbers provided
                        else:
                            st.error(f"ID number {id_number} is not valid for SIM swap.")
                    else:
                        st.warning("Please enter a valid ID number.")

def main():
    st.set_page_config(page_title="SIM Swap Detection.", page_icon=":earth_americas:")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='color:green;'>Detection System - SIM Swap.</h1>", unsafe_allow_html=True)
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
        # Load data from the first CSV file
        data_1 = load_data(file_location_1, "The Location of most recent connectivity")

        # Load data from the second CSV file
        data_2 = load_data(file_location_2, "The Location of Request for Swap")

        # Load data from the third CSV file
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
