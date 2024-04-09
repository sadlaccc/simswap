import streamlit as st
import pandas as pd
import folium
import math
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


def home_page():
    st.markdown("<h1 style='color:green;'>SS Detection System</h1>", unsafe_allow_html=True)
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
                recent_transaction_name = data_3['Location Name'].iloc[0]  # 'Location Name'
                folium.Marker([recent_transaction_lat, recent_transaction_lon], popup=f"{recent_transaction_name}",
                            icon=folium.Icon(color='blue')).add_to(my_map)

                # Plot connectivity location
                connectivity_lat = data_1[lat_column_1].mean()
                connectivity_lon = data_1[lon_column_1].mean()
                connectivity_name = data_1['Location Name'].iloc[0]  #  'Location Name'
                folium.Marker([connectivity_lat, connectivity_lon], popup=f"{connectivity_name}",
                            icon=folium.Icon(color='red')).add_to(my_map)

                # Plot search result locations
                for index, row in combined_search_data.iterrows():
                    location_name = row['Location Name']  # Assuming the column name is 'Location Name'
                    
                # Draw lines to form a triangle between locations
                folium.PolyLine(locations=[[selected_lat, selected_lon], [recent_transaction_lat, recent_transaction_lon]],
                                color='black', weight=2.5, opacity=1).add_to(my_map)

                folium.PolyLine(locations=[[recent_transaction_lat, recent_transaction_lon], [connectivity_lat, connectivity_lon]],
                                color='black', weight=2.5, opacity=1).add_to(my_map)

                folium.PolyLine(locations=[[connectivity_lat, connectivity_lon], [selected_lat, selected_lon]],
                                color='black', weight=2.5, opacity=1).add_to(my_map)

                # Display the map
                folium_static(my_map)

                
                st.write("### Distances:")# Create a dictionary with the data
                data = {
                    "Type of Location": [f"Location of Request of Request of S.S)", f"Location of Recent Transaction)", "Location of Recent Connectivity"],
                    "Addresses": [selected_location, recent_transaction_name, connectivity_name],
                    "Name. (Analysis.)": ["A", "B", "C"]
                }
               
                # Calculate distances and area, and display them
                distance_to_connectivity = calculate_distance(selected_lat, selected_lon, connectivity_lat, connectivity_lon)
                distance_to_transaction = calculate_distance(selected_lat, selected_lon, recent_transaction_lat, recent_transaction_lon)
                distance_between_locations = calculate_distance(recent_transaction_lat, recent_transaction_lon, connectivity_lat, connectivity_lon)
                area_covered = calculate_area(selected_lat, selected_lon, recent_transaction_lat, recent_transaction_lon, connectivity_lat, connectivity_lon)
                
                # Create a DataFrame from the dictionary
                df = pd.DataFrame(data)
                # Create a dictionary with the location names and their corresponding codes
                location_data = {
                    
                    "Location Code": ["A", "B", "C"]
                }

                # Create a DataFrame from the location data
                location_df = pd.DataFrame(location_data)

                # Create a dictionary with the distance data
                distance_data = {
                    "From": ["A", "A", "B"],
                    "To": ["B", "C", "C"],
                    "Distance (km)": [distance_to_transaction, distance_to_connectivity, distance_between_locations]
                }

                # Create a DataFrame from the distance data
                distance_df = pd.DataFrame(distance_data)

               
                # Create a new DataFrame combining the location names and distances
                combined_df = pd.merge(distance_df, location_df, left_on='From', right_on='Location Code', how='left')
                combined_df.rename(columns={'Location Name': 'From Name', 'Location Code': 'From '}, inplace=True)
                combined_df = pd.merge(combined_df, location_df, left_on='To', right_on='Location Code', how='left')
                combined_df.rename(columns={'Location Name': 'To Name', 'Location Code': 'To '}, inplace=True)

                # Rearrange the columns
                combined_df = combined_df[['From', 'To', 'Distance (km)']]

                # Display all columns
                 # Display the combined DataFrame as a table
                st.write("Location Names and Distances:")
                st.write(df)
                st.write("Distances Between Locations")
                st.write(combined_df)

       
                # Define location names
                location_names = ["Location of Request", "Location of Transaction", "Location of Connectivity"]

                # Define the distances
                distances = [distance_to_transaction, distance_to_connectivity, distance_between_locations]

                # Find the longest distance and its index
                max_distance_index = distances.index(max(distances))

                # Define the coordinates of the vertices based on the longest distance
                if max_distance_index == 0:
                    # Transaction to Connectivity is the longest distance
                    B = (0, 0)
                    A = (distances[0], 0)
                    C = (distances[2], distances[1])
                elif max_distance_index == 1:
                    # Request to Connectivity is the longest distance
                    C = (0, 0)
                    A = (distances[2], 0)
                    B = (distances[0], distances[1])
                else:
                    # Request to Transaction is the longest distance
                    A = (0, 0)
                    B = (distances[1], 0)
                    C = (distances[0], distances[2])

                # Plot the triangle
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.plot([A[0], B[0]], [A[1], B[1]], 'b-', label=f'Distance AB: {format(distances[0], ".2f")} km')  # Line AB
                ax.plot([B[0], C[0]], [B[1], C[1]], 'r-', label=f'Distance BC: {format(distances[1], ".2f")}km')  # Line BC
                ax.plot([C[0], A[0]], [C[1], A[1]], 'g-', label=f'Distance CA: {format(distances[2], ".2f")}km')  # Line CA
                ax.plot(A[0], A[1], 'ko')  # Point A
                ax.text(A[0], A[1], 'A\n' + location_names[0], ha='right', va='bottom')
                ax.plot(B[0], B[1], 'ko')  # Point B
                ax.text(B[0], B[1], 'B\n' + location_names[1], ha='right', va='top')
                ax.plot(C[0], C[1], 'ko')  # Point C
                ax.text(C[0], C[1], 'C\n' + location_names[2], ha='left', va='top')

                # Set axis labels
                ax.set_xlabel('X (km)')
                ax.set_ylabel('Y (km)')

                # Set aspect ratio to equal
                ax.set_aspect('equal', adjustable='box')

                # Show grid lines
                ax.grid(True)

                # Add legend
                ax.legend()

                # Add title
                ax.set_title('Triangle formed by the three locations')

                # Show plot
                st.pyplot(fig)
                
                #Display the Area Covered
                st.write("### The area covered:")
                st.markdown(f"<p style='font-size:20px'>{area_covered,}, "Squared Kilometres", </p>", unsafe_allow_html=True)
                
                

                # Perform SIM swap and display results (if applicable)
                if distance_to_transaction > 1000:
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

        selected_page = st.sidebar.radio("Select Page", ["Home", "Search"])

        if selected_page == "Home":
            home_page()
        elif selected_page == "Maps":
            maps_page(data_1, data_2, data_3, lat_column_1, lon_column_1, lat_column_2, lon_column_2, lat_column_3, lon_column_3)
        elif selected_page == "Search":
            search_page(data_1, data_2, data_3, lat_column_1, lon_column_1, lat_column_2, lon_column_2, lat_column_3, lon_column_3)

if __name__ == "__main__":
    main()
