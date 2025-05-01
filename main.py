import requests
import urllib.parse

# Graphhopper API URLs
route_url = "https://graphhopper.com/api/1/route?"
key = "your_api_key"  # Remplace avec ta vraie clé API

# Fonction de géocodage pour obtenir lat/lng à partir du lieu
def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")
        new_loc = f"{name}, {state}, {country}" if state and country else name
        print(f"Geocoding API URL for {new_loc} (Location Type: {value})\n{url}")
    else:
        lat = lng = "null"
        new_loc = location
        if json_status != 200:
            print("Geocode API status:", json_status, "\nError message:", json_data.get("message", "Unknown"))
    return json_status, lat, lng, new_loc

while True:
    # Sélection du mode de transport
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    profile = ["car", "bike", "foot"]
    vehicle = input("Enter a vehicle profile from the list above: ")
    if vehicle in ["quit", "q"]:
        break
    elif vehicle not in profile:
        print("No valid vehicle profile was entered. Using the car profile.")
        vehicle = "car"

    # Saisie des lieux de départ et destination
    loc1 = input("Starting Location: ")
    if loc1 in ["quit", "q"]:
        break
    orig = geocoding(loc1, key)

    loc2 = input("Destination: ")
    if loc2 in ["quit", "q"]:
        break
    dest = geocoding(loc2, key)

    print("=================================================")
    if orig[0] == 200 and dest[0] == 200:
        op = f"&point={orig[1]}%2C{orig[2]}"
        dp = f"&point={dest[1]}%2C{dest[2]}"
        # Construction de l'URL de routage
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp

        # Requête vers l'API de routage
        paths_data = requests.get(paths_url).json()
        paths_status = requests.get(paths_url).status_code
        print("Routing API Status:", paths_status, "\nRouting API URL:\n", paths_url)
        print("=================================================")
        print(f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
        print("=================================================")
        if paths_status == 200:
            km = paths_data["paths"][0]["distance"] / 1000
            miles = km / 1.61
            total_ms = paths_data["paths"][0]["time"]
            sec = int(total_ms / 1000 % 60)
            min = int(total_ms / 1000 / 60 % 60)
            hr = int(total_ms / 1000 / 60 / 60)
            print("Distance Traveled: {:.1f} miles / {:.1f} km".format(miles, km))
            print("Trip Duration: {:02d}:{:02d}:{:02d}".format(hr, min, sec))
            print("=================================================")

            # Affichage des étapes de la route
            for each in paths_data["paths"][0]["instructions"]:
                path = each["text"]
                distance = each["distance"]
                print("{} ( {:.1f} km / {:.1f} miles )".format(path, distance/1000, distance/1000/1.61))
            print("=================================================")
        else:
            print("Error message:", paths_data.get("message", "No route available"))
            print("*************************************************")