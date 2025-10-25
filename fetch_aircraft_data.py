import requests
import time
from datetime import datetime
import json
import os
import subprocess
import signal
import sys
from collections import OrderedDict

# URL of the API
api_url = "http://localhost:8080/data/aircraft.json"
db_folder = "/usr/share/skyaware/html/db"

# Cache configuration
MAX_CACHE_SIZE = 1000
CACHE_TTL = 3600  # 1 hour in seconds

class LRUCache:
    """LRU Cache with TTL support"""
    def __init__(self, max_size=1000, ttl=3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
    
    def get(self, key):
        if key in self.cache:
            # Check if expired
            if time.time() - self.timestamps[key] > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, key, value):
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self):
        self.cache.clear()
        self.timestamps.clear()

# Global caches
flight_route_cache = LRUCache(MAX_CACHE_SIZE, CACHE_TTL)
aircraft_details_cache = LRUCache(MAX_CACHE_SIZE, CACHE_TTL)

def fetch_aircraft_data():
    try:
        response = requests.get(api_url, timeout=10)
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

def fetch_flight_route(callsign, cache):
    cached_result = cache.get(callsign)
    if cached_result is not None:
        print(f"get callsign {callsign} from cache")
        return cached_result

    url = f"https://api.adsbdb.com/v0/callsign/{callsign}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        flightroute = response.json().get('response', {}).get('flightroute', {})
        cache.set(callsign, flightroute)
        return flightroute
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error fetching flight route: {e}")
        return None

def get_aircraft_details(hex_code, cache):
    cached_result = cache.get(hex_code)
    if cached_result is not None:
        print(f"get hex {hex_code} from cache")
        return cached_result

    url = f"https://api.adsbdb.com/v0/aircraft/{hex_code}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        aircraft_details = response.json().get('response', {}).get('aircraft', {})
        cache.set(hex_code, aircraft_details)
        return aircraft_details
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error fetching aircraft details: {e}")
        return None

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
            #if any(term == flight for term in exact_terms) or any(flight.startswith(prefix) for prefix in prefix_terms) and category in categories and geom_rate < -0.1 and alti>
            if category in categories and geom_rate < -0.1 and altitude_ft < 15000:
                altitude_m = round(altitude_ft * 0.3048) if altitude_ft is not None else "N/A"
                details = lookup_hex_info(hex_code)
                country_info = find_icao_range(hex_code, icao_ranges)
                results.append((flight, altitude_m, hex_code, details, country_info))
    return results

def cleanup_subprocess(process):
    """Safely terminate subprocess"""
    if process and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    exact_terms = ["UAE8T", "UAE2MJ", "UAE36P", "UAE87Q"]
    prefix_terms = ["EDW", "SWR", "UEA", "SIA", "QTR", "KAL", "THA", "ETD", "CAP", "THY", "ETH", "AIC"]
    categories = ["A4", "A5"]
    icao_ranges = load_icao_ranges()

    current_process = None
    error_count = 0
    max_errors = 5

    while True:
        try:
            data = fetch_aircraft_data()
            if data:
                found_flights = search_flight(data, exact_terms, prefix_terms, icao_ranges, categories)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if found_flights:
                    for flight_info in found_flights:
                        flight, altitude_m, hex_code, details, country_info = flight_info

                        flight_route = fetch_flight_route(flight, flight_route_cache)
                        if flight_route:
                            origin_iata = flight_route.get('origin', {}).get('iata_code', 'Unknown')
                            origin_name = flight_route.get('origin', {}).get('name', 'Unknown')
                        else:
                            origin_iata = "Unknown"
                            origin_name = "Unknown"

                        aircraft_details = get_aircraft_details(hex_code, aircraft_details_cache)
                        if aircraft_details:
                            aircraft_type = aircraft_details.get('type', 'Unknown')
                            aircraft_manufacturer = aircraft_details.get('manufacturer', 'Unknown')
                            aircraft_registered_owner = aircraft_details.get('registered_owner', 'Unknown')
                        else:
                            aircraft_type = "Unknown"
                            aircraft_manufacturer = "Unknown"
                            aircraft_registered_owner = "Unknown"

                        if details:
                            details_str = f"Registration: {details.get('r')}, ICAO Type: {details.get('t')}, Description: {details.get('desc')}, WTC: {details.get('wtc')}"
                        else:
                            details_str = ""

                        print(f"{timestamp} - Found flight: {flight}, Altitude: {altitude_m} meters, Hex: {hex_code}, Country: {country_info['country']}, {details_str}")
                        print(f"Aircraft details: {aircraft_type} {aircraft_manufacturer}")

                        text_top = f"{aircraft_manufacturer} {aircraft_type} {aircraft_registered_owner}"
                        text_center = f"{origin_iata} {origin_name}"
                        text_bottom = f"{altitude_m}m {altitude_m}m {altitude_m}m {altitude_m}m {altitude_m}m"

                        # Ensure text is string type
                        text_top = str(text_top)
                        text_center = str(text_center)
                        text_bottom = str(text_bottom)

                        # Clean up any existing process
                        cleanup_subprocess(current_process)
                        
                        # Start new process
                        current_process = subprocess.Popen(['python3', 'rgbtext.py', '--top', text_top, '--center', text_center, '--bottom', text_bottom])
                        time.sleep(6)
                        cleanup_subprocess(current_process)
                        current_process = None
                else:
                    print(f"{timestamp} - No matching flights found")
                    time.sleep(2)
            else:
                print(f"{timestamp} - No data received from API")
                time.sleep(5)
                
            # Reset error count on successful iteration
            error_count = 0
            
        except Exception as e:
            error_count += 1
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Error in main loop: {e}")
            
            if error_count >= max_errors:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Too many errors ({error_count}), clearing caches and restarting...")
                flight_route_cache.clear()
                aircraft_details_cache.clear()
                error_count = 0
            
            # Clean up any running process on error
            cleanup_subprocess(current_process)
            current_process = None
            
            time.sleep(10)  # Wait longer on errors

if __name__ == "__main__":
    main()
