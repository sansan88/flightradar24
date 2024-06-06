import requests
import time

# URL of the API
api_url = "http://192.168.1.171/dump1090/data/aircraft.json"

def fetch_aircraft_data():
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def search_flight(data, search_terms):
    if 'aircraft' not in data:
        print("No aircraft data found")
        return []

    results = []
    for aircraft in data['aircraft']:
        if 'flight' in aircraft:
            flight = aircraft['flight']
            if any(term in flight for term in search_terms):
                results.append(flight)
    return results

def main():
    search_terms = ["EK85", "EK86"]
    
    while True:
        data = fetch_aircraft_data()
        if data:
            found_flights = search_flight(data, search_terms)
            if found_flights:
                print(f"Found flights: {found_flights}")
            else:
                print("No matching flights found")
        
        time.sleep(1)

if __name__ == "__main__":
    main()