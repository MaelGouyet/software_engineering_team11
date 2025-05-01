import requests
import os
from dotenv import load_dotenv
import urllib.parse

#get the key from .env file
# Load environment variables from .env file
load_dotenv()
MAPQUEST_API_KEY = os.getenv("MAPQUEST_API_KEY")

GEOCODE_URL = "http://www.mapquestapi.com/geocoding/v1/address"
DIRECTIONS_URL = "http://www.mapquestapi.com/directions/v2/route"

def geocode_location(location):
    params = {
        "key": MAPQUEST_API_KEY,
        "location": location
    }
    response = requests.get(GEOCODE_URL, params=params)
    data = response.json()

    if response.status_code == 200 and data["info"]["statuscode"] == 0:
        latlng = data["results"][0]["locations"][0]["latLng"]
        display_name = data["results"][0]["locations"][0]["street"] + ", " + data["results"][0]["locations"][0]["adminArea5"] + ", " + data["results"][0]["locations"][0]["adminArea3"]
        print(f"Geocoding for {location}: {latlng}")
        return latlng["lat"], latlng["lng"], display_name
    else:
        print("Error in geocoding:", data["info"]["messages"])
        return None, None, location

def get_directions(from_loc, to_loc):
    params = {
        "key": MAPQUEST_API_KEY,
        "from": from_loc,
        "to": to_loc,
        "routeType": "fastest"
    }
    response = requests.get(DIRECTIONS_URL, params=params)
    data = response.json()

    if response.status_code == 200 and data["info"]["statuscode"] == 0:
        print("=================================================")
        print(f"Directions from {from_loc} to {to_loc}")
        print("=================================================")
        print(f"Distance: {data['route']['distance']} miles")
        print(f"Duration: {data['route']['formattedTime']}")
        print("=================================================")
        for leg in data["route"]["legs"][0]["maneuvers"]:
            print(f"{leg['narrative']} ({leg['distance']:.1f} miles)")
        print("=================================================")
    else:
        print("Error retrieving route:", data["info"]["messages"])

while True:
    from_location = input("Starting Location: ")
    if from_location.lower() in ["q", "quit"]:
        break

    to_location = input("Destination: ")
    if to_location.lower() in ["q", "quit"]:
        break

    lat1, lng1, from_name = geocode_location(from_location)
    lat2, lng2, to_name = geocode_location(to_location)

    if lat1 and lat2:
        get_directions(from_location, to_location)
