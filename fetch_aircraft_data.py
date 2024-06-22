#!/usr/bin/env python
import requests
import time
from datetime import datetime
import json
import os
import subprocess

# URL of the API
api_url = "http://localhost:8080/data/aircraft.json"
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

def fetch_aircraft_details(hex_code):
    url = f"https://api.adsbdb.com/v0/aircraft/{hex_code}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('response', {}).get('aircraft', {})
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error fetching aircraft details: {e}")
        return {}
def fetch_flight_route(callsign):
    url = f"https://api.adsbdb.com/v0/callsign/{callsign}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('response', {}).get('flightroute', {}).get('origin',{})
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error fetching flight route: {e}")
        return {}

def search_flight(data, exact_terms, prefix_terms, icao_ranges, categories):
    if 'aircraft' not in data:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - No aircraft data found")
        return []

    results = []
    for aircraft in data['aircraft']:
        if 'flight' in aircraft and 'hex' in aircraft:
            flight = aircraft['flight'].strip()
            hex_code = aircraft['hex'].upper()
            category = aircraft.get('category')
            geom_rate = aircraft.get('geom_rate', 0)
            altitude_ft = aircraft.get('alt_geom', 30000)
            if any(term == flight for term in exact_terms) or any(flight.startswith(prefix) for prefix in prefix_terms) and category in categories and geom_rate < -0.1 and altitude_ft < 8000:
                altitude_ft = aircraft.get('alt_geom', None)
                altitude_m = round(altitude_ft * 0.3048) if altitude_ft is not None else "N/A"
                details = lookup_hex_info(hex_code)
                country_info = find_icao_range(hex_code, icao_ranges)
                results.append((flight, altitude_m, hex_code, details, country_info))
    return results

def main():
    exact_terms = ["UAE8T", "UAE2MJ", "UAE36P", "UAE87Q"]
    prefix_terms = ["EDW", "SWR", "UEA", "SIA", "QTR", "KAL", "THA", "ETD", "CAP", "THY", "ETH", "AIC"]
    categories = ["A3", "A4", "A5"]
    icao_ranges = load_icao_ranges()

    while True:
        data = fetch_aircraft_data()
        if data:
            found_flights = search_flight(data, exact_terms, prefix_terms, icao_ranges, categories)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if found_flights:
                for flight_info in found_flights:
                    flight, altitude_m, hex_code, details, country_info = flight_info
                    aircraft_details = fetch_aircraft_details(hex_code)
                    flight_origin = fetch_flight_route(flight)

                    text_top = f"Aircraft Details {flight}"
                    text_center = {country_info['country']}
                    text_bottom = "Altitude"

                    if details:
                        details_str = f"Registration: {details.get('r')}, ICAO Type: {details.get('t')}, Description: {details.get('desc')}, WTC: {details.get('wtc')}"
                        text_top = {details.get('t')}
                    else:
                        details_str = ""

                    print(f"{timestamp} - Found flight: {flight}, Altitude: {altitude_m} meters, Hex: {hex_code}, Country: {country_info['country']}, {details_str}")

                    if aircraft_details:
                        print(f"Aircraft details: {aircraft_details.get('manufacturer')} {aircraft_details.get('type')} ")
                        text_top = f"{aircraft_details.get('manufacturer')} {aircraft_details.get('type')} {aircraft_details.get('registered_owner')}"
                    if flight_origin:
                        print(f"Flight route: {flight_origin.get('municipality')}")
                        text_center = f"{flight_origin.get('iata_code')} {flight_origin.get('name')}"

                    text_bottom = f"{altitude_m}m {altitude_m}m {altitude_m}m"
                    #text_to_display = f"{details.get('t')} {altitude_m}m {flight}"
                    process = subprocess.Popen(['python', 'rgbtext.py', '--top', text_top, '--center', text_center, '--bottom', text_bottom])
                    #process = subprocess.Popen(['python', 'runtext.py', '--text', text_to_display])
                    time.sleep(6)
                    process.terminate()
                    try:
                        process.wait(timeout=0)
                    except subprocess.TimeoutExpired:
                        process.kill()
            else:
                print(f"{timestamp} - No matching flights found")
                time.sleep(2)
        time.sleep(2)

if __name__ == "__main__":
    main()

