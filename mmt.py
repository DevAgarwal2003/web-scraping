from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def build_url(source, destination, date, adults=1, children=0, infants=0, trip_type="O", cabin_class="E", lang="eng"):
    """
    Constructs a dynamic URL for MakeMyTrip flight search.

    Parameters:
        source (str): Source airport code (e.g., 'BOM').
        destination (str): Destination airport code (e.g., 'DEL').
        date (str): Travel date in DD/MM/YYYY format (e.g., '30/01/2025').
        adults (int): Number of adult passengers (default: 1).
        children (int): Number of child passengers (default: 0).
        infants (int): Number of infant passengers (default: 0).
        trip_type (str): Type of trip ('O' for one-way, 'R' for round trip).
        cabin_class (str): Cabin class ('E' for Economy, 'B' for Business).
        lang (str): Language code (default: 'eng').

    Returns:
        str: The constructed MakeMyTrip URL.
    """
    source = re.search(r'\((\w{3})\)', source).group(1)
    destination = re.search(r'\((\w{3})\)', destination).group(1)
    
    base_url = "https://www.makemytrip.com/flight/search"
    itinerary = f"{source}-{destination}-{date}"
    pax_type = f"A-{adults}_C-{children}_I-{infants}"
    intl = "false"  # Assuming domestic travel

    # Construct the full URL
    full_url = (
        f"{base_url}?itinerary={quote(itinerary)}&tripType={trip_type}&paxType={quote(pax_type)}"
        f"&intl={intl}&cabinClass={cabin_class}&lang={lang}"
    )
    return full_url

def scrape_mmt(source, destination, travel_date):
    # Example usage
    # source = "BOM"  # Mumbai
    # destination = "DEL"  # Delhi
    # travel_date = "30/01/2025"

    url = build_url(source, destination, travel_date)

    chrome_options = Options()

    # Set up ChromeDriver
    service = Service('D:/SeleniumDrivers/chromedriver.exe')

    options = [
        "--disable-gpu",
        "--window-size=1920,1200",
        "--ignore-certificate-errors",
        "--disable-extensions",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features",
        "--disable-blink-features=AutomationControlled",
        "--disable-3d-apis",
        "--enable-unsafe-swiftshader"
    ]
    for option in options:
        chrome_options.add_argument(option)

    driver = webdriver.Chrome(options=chrome_options,service=service)

    driver.get(url)
    time.sleep(10)

    # Get page source
    html = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    # Extract prices
    airline = soup.find_all('p', class_ = 'boldFont blackText airlineName')
    prices = soup.find_all('span', class_='fontSize18 blackFont')
    flight_time = soup.find_all('p', class_ = 'appendBottom2 flightTimeInfo')
    flight_name = soup.find_all('p', class_ = 'fliCode')

    airline_list = []
    price_list = []
    time_list = []
    departure_time = []
    arrival_time = []
    flight_name_list = []

    for name in airline:
        airline_list.append(name.text)
    for price in prices:
        price_list.append(price.text)
    for time_ in flight_time:
        time_list.append(time_.text)
    for name in flight_name:
        flight_name_list.append(name.text)
        
    for x in range(0, len(time_list)-1,2):
            departure_time.append(time_list[x])
            arrival_time.append(time_list[x+1])
        
    mapped_list = list(zip(flight_name_list, airline_list, departure_time, arrival_time, price_list, ["MakeMyTrip"] * len(flight_name_list)))

    # Printing the result
    return mapped_list
