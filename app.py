import streamlit as st
from emt import scrape_emt
from mmt import scrape_mmt
import pandas as pd
import numpy as np
import plotly.express as px
import warnings
from io import BytesIO
import openpyxl
from datetime import datetime
warnings.simplefilter(action='ignore', category=UserWarning)

# Function to handle navigation
def switch_page(page):
    st.session_state["page"] = page
    st.rerun()  # Ensures Streamlit recognizes the page change immediately

# Initialize session state variables if not present
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "flight_data" not in st.session_state:
    st.session_state["flight_data"] = []

def home_page():
    indian_airports = [
    "Agartala (IXA)",
    "Ahmedabad (AMD)",
    "Amritsar (ATQ)",
    "Bengaluru (BLR)",
    "Bhubaneswar (BBI)",
    "Chandigarh (IXC)",
    "Chennai (MAA)",
    "Coimbatore (CJB)",
    "Delhi (DEL)",
    "Goa (GOI)",
    "Guwahati (GAU)",
    "Hyderabad (HYD)",
    "Jaipur (JAI)",
    "Kochi (COK)",
    "Kolkata (CCU)",
    "Kozhikode (CCJ)",
    "Lucknow (LKO)",
    "Madurai (IXM)",
    "Mangaluru (IXE)",
    "Mumbai (BOM)",
    "Nagpur (NAG)",
    "Pune (PNQ)",
    "Srinagar (SXR)",
    "Thiruvananthapuram (TRV)",
    "Tiruchirappalli (TRZ)",
    "Varanasi (VNS)",
    "Vijayawada (VGA)",
    "Visakhapatnam (VTZ)"
]
    st.markdown(
    """
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #ffffff;  /* White text */
        background: #8B4513; /* Darker Chocolate background */
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

    st.markdown('<div class="title">✈️ Flight Search</div>', unsafe_allow_html=True)

    source = st.selectbox("Select a Source:", indian_airports, index = 0)
    destination = st.selectbox("Select a Destination:", indian_airports, index = 0)
    valid_source_dest = source != "Select an airport" and destination != "Select an airport" and source != destination
    if not valid_source_dest and source != "Select an airport" and destination != "Select an airport":
        st.warning("Source and Destination must be different.")
    
    today = datetime.today().date()

    # Create a date input widget with a restriction to future dates
    date_input = st.date_input("Select Travel Date", min_value=today)

    # Check if the selected date is a future date
    if date_input < today:
        st.warning("Please select a future date.")
    else:
        # Format the selected date in DD/MM/YYYY format
        travel_date = date_input.strftime("%d/%m/%Y")
        
    valid_date = date_input >= today

    # Enable Button Only if All Conditions are Met
    search_enabled = valid_source_dest and valid_date
    search_button = st.button("Search", disabled=not search_enabled)
    
    if search_button:
        if source and destination and travel_date:
            # Run scraping only once and store data
            flights1 = scrape_emt(source, destination, travel_date)
            flights2 = scrape_mmt(source, destination, travel_date)

            # Combine results from both websites
            all_flights = flights1 + flights2

            # Store data in session state
            st.session_state["flight_data"] = all_flights
            st.session_state["source"] = source
            st.session_state["destination"] = destination
            st.session_state["travel_date"] = travel_date

            # Navigate to the dashboard
            switch_page("dashboard")  # Now it will switch properly
        else:
            st.warning("Please enter source, destination, and travel date")

def dashboard_page():
    st.title(f"Flights from {st.session_state['source']} to {st.session_state['destination']}")
    
    flights = st.session_state.get("flight_data", [])
    if not flights:
        st.write("No flight data available.")
        return

    df = pd.DataFrame(flights, columns=["Flight Name", "Airline", "Departure Time", "Arrival Time", "Price", "Platform"])

    # Sample DataFrame with flight details

    df['Price'] = df['Price'].str.replace('₹', '', regex=False)
    df['Price'] = df['Price'].str.replace(',', '', regex=False)
    # Optionally, convert the prices to float after removing the symbol
    df['Price'] = df['Price'].astype(int)

    df['Departure Time'] = pd.to_datetime(df['Departure Time'], errors='coerce')
    df['Departure Time'] = df['Departure Time'].dt.strftime('%H:%M')
    df['Arrival Time'] = df['Arrival Time'].str.replace(r'\+ 1 DAY', '', regex=True)
    df['Arrival Time'] = pd.to_datetime(df['Arrival Time'], errors='coerce')
    df['Arrival Time'] = df['Arrival Time'].dt.strftime('%H:%M')

    # Extract min and max prices
    min_price, max_price = df['Price'].min(), df['Price'].max()

    # Streamlit Sidebar Filters
    st.sidebar.header("Filter Options")

    # Departure Time Filters
    departure_options = ["Before 6 AM", "6 AM - 12 PM", "12 PM - 6 PM", "After 6 PM"]
    st.sidebar.subheader("Select Departure Time")
    departure_selected = [st.sidebar.checkbox(opt, value=True, key=f'dep_{i}') for i, opt in enumerate(departure_options)]

    # Arrival Time Filters
    st.sidebar.subheader("Select Arrival Time")
    arrival_options = ["Before 6 AM", "6 AM - 12 PM", "12 PM - 6 PM", "After 6 PM"]
    arrival_selected = [st.sidebar.checkbox(opt, value=True, key=f'arr_{i}') for i, opt in enumerate(arrival_options)]

    # Price Range Slider
    st.sidebar.subheader("Select Price Range")
    price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))

    def filter_time(time, selected):
        hour = int(time.split(":")[0])
        if hour < 6 and selected[0]:
            return True
        elif 6 <= hour < 12 and selected[1]:
            return True
        elif 12 <= hour < 18 and selected[2]:
            return True
        elif hour >= 18 and selected[3]:
            return True
        return False

    # Apply Filters
    df_filtered = df[(df['Price'] >= price_range[0]) & (df['Price'] <= price_range[1])]
    df_filtered = df_filtered[df_filtered['Departure Time'].apply(lambda x: filter_time(x, departure_selected))]
    df_filtered = df_filtered[df_filtered['Arrival Time'].apply(lambda x: filter_time(x, arrival_selected))]
    # Streamlit Layout with Custom Styling
    xvalue = st.selectbox("Select the X axis", ['Departure Time', 'Arrival Time', 'Airline', 'Platform'])
    fig = px.scatter(df_filtered, 
                 x=xvalue, 
                 y="Price", 
                 color="Platform",
                 color_discrete_map={"MakeMytrip": "red", "EaseMyTrip": "blue"},
                 hover_data=["Flight Name", "Airline", "Departure Time", "Arrival Time", "Price", "Platform"])

    # Adjust the size of the plot for better visibility
    fig.update_layout(
        autosize=True,  # Automatically adjust size
        width=1500,  # Set custom width
        height=600,  # Set custom height
        title=f"Flight Prices vs {xvalue}"
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    if df_filtered.empty:
        st.warning('No Flights Available for the applied filters', icon="⚠️")
    else:
        st.dataframe("Flight Dashboard", df_filtered)
        
        # Option to go back to the search page
        if st.button("Back to Search"):
            switch_page("home")

# Page Navigation Logic
if st.session_state["page"] == "home":
    home_page()
elif st.session_state["page"] == "dashboard":
    dashboard_page()
