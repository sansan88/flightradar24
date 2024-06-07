import requests
import time
from datetime import datetime
import json
import os

# URL of the API
api_url = "http://192.168.1.171/dump1090/data/aircraft.json"
db_folder = "/usr/share/dump1090-mutability/html/db"  # Path to the folder containing JSON files

def fetch_aircraft_data():
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error fetching data: {e}")
        return None

def search_flight(data, exact_terms, prefix_terms):
    if 'aircraft' not in data:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No aircraft data found")
        return []

    results = []
    for aircraft in data['aircraft']:
        if 'flight' in aircraft and 'hex' in aircraft:
            flight = aircraft['flight']
            hex_code = aircraft['hex'].upper()
            if any(term == flight for term in exact_terms) or any(flight.startswith(prefix) for prefix in prefix_terms):
                altitude_ft = aircraft.get('altitude', None)
                altitude_m = round(altitude_ft * 0.3048, 2) if altitude_ft is not None else "N/A"
                details = lookup_hex_info(hex_code)
                results.append((flight, altitude_m, hex_code, details))
    return results

def lookup_hex_info(hex_code):
    try:
        # Perform reverse lookup from most specific to least specific
        for i in range(len(hex_code), 0, -1):
            file_name = hex_code[:i].upper() + ".json"
            file_path = os.path.join(db_folder, file_name)
            key = hex_code[i:].upper()

            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if key in data:
                        return data[key]
                    # else:
                        # print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Key {key} not found in file {file_name}")
            # else:
                # print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - File {file_name} not found in folder {db_folder}")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error looking up hex info: {e}")

    return None

def main():
    exact_terms = ["UAE8T", "UAE2MJ", "UAE36P", "UAE87Q"]
    prefix_terms = ["SWR"]

    while True:
        data = fetch_aircraft_data()
        if data:
            found_flights = search_flight(data, exact_terms, prefix_terms)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if found_flights:
                for flight_info in found_flights:
                    flight, altitude_m, hex_code, details = flight_info
                    if details:
                        details_str = f"Details: r: {details.get('r')}, t: {details.get('t')}"
                    else:
                        details_str = "Details not found"
                    print(f"{timestamp} - Found flight: {flight}, Altitude: {altitude_m} meters, Hex: {hex_code}, {details_str}")
            else:
                print(f"{timestamp} - No matching flights found")

        time.sleep(2)

if __name__ == "__main__":
    main()