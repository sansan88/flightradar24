import requests
import time
from datetime import datetime
import json
import os

# URL of the API
api_url = "http://192.168.1.171:8080/data/aircraft.json"
db_folder = "/usr/share/skyaware/html/db"

def fetch_aircraft_data():
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error fetching data: {e}")
        return None

def load_icao_ranges():
    with open('icao_ranges.json', 'r') as file:
        return json.load(file)

def find_icao_range(icao, icao_ranges):
    hexa = int(icao, 16)
    for icao_range in icao_ranges:
        start = int(icao_range['start'], 16)
        end = int(icao_range['end'], 16)
        if start <= hexa <= end:
            return icao_range
    return {'country': 'Unassigned', 'flag_image': 'blank.png'}

def lookup_hex_info(hex_code):
    try:
        for i in range(len(hex_code), 0, -1):
            file_name = hex_code[:i].upper() + ".json"
            file_path = os.path.join(db_folder, file_name)
            key = hex_code[i:].upper()

            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if key in data:
                        return data[key]
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error looking up hex info: {e}")

    return None

def search_flight(data, exact_terms, prefix_terms, icao_ranges, categories):
    if 'aircraft' not in data:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No aircraft data found")
        return []

    results = []
    for aircraft in data['aircraft']:
        if 'flight' in aircraft and 'hex' in aircraft:
            flight = aircraft['flight'].strip() # Flugzeug Kennung
            hex_code = aircraft['hex'].upper() # HEX Code für DB Abfrage
            category = aircraft.get('category') # Kategorie A4 / A5
            geom_rate = aircraft.get('geom_rate', 0) # Sinkflug
            if any(term == flight for term in exact_terms) or any(flight.startswith(prefix) for prefix in prefix_terms) and category in categories and geom_rate < -0.1:
                altitude_ft = aircraft.get('alt_geom', None)
                altitude_m = round(altitude_ft * 0.3048) if altitude_ft is not None else "N/A"
                details = lookup_hex_info(hex_code)
                country_info = find_icao_range(hex_code, icao_ranges)
                results.append((flight, altitude_m, hex_code, details, country_info))
    return results

def main():
    exact_terms = ["UAE8T", "UAE2MJ", "UAE36P", "UAE87Q"]
    prefix_terms = ["EDW","SWR","UEA","QTR"]
    categories = ["A4", "A5"]
    icao_ranges = load_icao_ranges()

    while True:
        data = fetch_aircraft_data()
        if data:
            found_flights = search_flight(data, exact_terms, prefix_terms, icao_ranges, categories)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if found_flights:
                for flight_info in found_flights:
                    flight, altitude_m, hex_code, details, country_info = flight_info
                    if details:
                        details_str = f"Registration: {details.get('r')}, ICAO Type: {details.get('t')}, Description: {details.get('desc')}, WTC: {details.get('wtc')}"
                    else:
                        details_str = ""
                    print(f"{timestamp} - Found flight: {flight}, Altitude: {altitude_m} meters, Hex: {hex_code}, Country: {country_info['country']}, {details_str}")
            else:
                print(f"{timestamp} - No matching flights found")

        time.sleep(2)

if __name__ == "__main__":
    main()

