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

def build_url(source, destination, date, adults=1, children=0, infants=0, cabin=0, currency="INR"):
    """
    Constructs a dynamic URL for EaseMyTrip flight search.
    
    Parameters:
        source (str): Source airport code (e.g., 'BOM').
        destination (str): Destination airport code (e.g., 'DEL').
        date (str): Travel date in DD/MM/YYYY format (e.g., '28/01/2025').
        adults (int): Number of adult passengers.
        children (int): Number of child passengers.
        infants (int): Number of infant passengers.
        cabin (int): Cabin class (0 for economy, 1 for business, etc.).
        currency (str): Currency for price display (default: 'INR').
    
    Returns:
        str: The constructed URL.
    """
    source = re.search(r'\((\w{3})\)', source).group(1)
    destination = re.search(r'\((\w{3})\)', destination).group(1)
    
    base_url = "https://flight.easemytrip.com/FlightList/Index"
    search_param = f"{source}-{quote(source)}-India|{destination}-{quote(destination)}-India|{date}"
    px_param = f"{adults}-{children}-{infants}"
    
    # Construct the full URL
    full_url = (
        f"{base_url}?srch={search_param}&px={px_param}&cbn={cabin}&ar=undefined&isow=true&isdm=true"
        f"&lang=en-us&IsDoubleSeat=false&CCODE=IN&curr={currency}&apptype=B2C"
    )
    return full_url
def scrape_emt(source, destination, travel_date):
    # Example usage
    # source = "BOM"  # Mumbai
    # destination = "DEL"  # Delhi
    # travel_date = "30/01/2025"

    url = build_url(source, destination, travel_date)
    chrome_options = Options()
    options = [
        "--headless"
    ]
    for option in options:
        chrome_options.add_argument(option)
        
    # Set up ChromeDriver
    service = Service('D:/SeleniumDrivers/chromedriver.exe')

    # Create the WebDriver instance with the Service
    driver = webdriver.Chrome(options = chrome_options, service=service)

    # Open the EaseMyTrip URL
    driver.get(url)

    # Wait for the JavaScript to load
    time.sleep(5)

    # Get page source
    html = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    # Extract prices
    airline = soup.find_all('span', class_ = 'txt-r4 ng-binding')
    prices = soup.find_all('div', class_='txt-r6-n ng-scope')
    flight_time = soup.find_all('span', class_ = 'txt-r2-n ng-binding')
    flight_time = soup.find_all('span', class_ = 'txt-r2-n ng-binding')
    airline_codes = [span.text for span in soup.find_all("span", {"ng-bind": "GetFltDtl(s.b[0].FL[0]).AC"})]
    flight_numbers = [span.text for span in soup.find_all("span", {"ng-bind": "GetFltDtl(s.b[0].FL[0]).FN"})]

    airline_list = []
    price_list = []
    time_list = []
    departure_time = []
    arrival_time = []
    flight_name_list = [f"{ac}-{fn}" for ac, fn in zip(airline_codes, flight_numbers)]

    # Extract prices
    for name in airline:
        airline_list.append(name.text)
    for price in prices:
        price_list.append(price.text)
    for time_ in flight_time:
        time_list.append(time_.text)

    for x in range(0, len(time_list)-1,2):
            departure_time.append(time_list[x])
            arrival_time.append(time_list[x+1])
        
    price_list = [num.strip().replace(',', '') for num in price_list]

    mapped_list = list(zip(flight_name_list, airline_list, departure_time, arrival_time, price_list, ["EaseMyTrip"] * len(flight_name_list)))
    return mapped_list
