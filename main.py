import requests
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, scrolledtext

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
        return latlng["lat"], latlng["lng"], display_name
    else:
        messagebox.showerror("Error", f"Error in geocoding: {data['info']['messages']}")
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
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "=================================================\n")
        result_text.insert(tk.END, f"Directions from {from_loc} to {to_loc}\n")
        result_text.insert(tk.END, "=================================================\n")
        result_text.insert(tk.END, f"Distance: {data['route']['distance']} miles\n")
        result_text.insert(tk.END, f"Duration: {data['route']['formattedTime']}\n")
        result_text.insert(tk.END, "=================================================\n")
        for leg in data["route"]["legs"][0]["maneuvers"]:
            result_text.insert(tk.END, f"{leg['narrative']} ({leg['distance']:.1f} miles)\n")
        result_text.insert(tk.END, "=================================================\n")
    else:
        messagebox.showerror("Error", f"Error retrieving route: {data['info']['messages']}")

def on_get_directions():
    from_location = from_entry.get()
    to_location = to_entry.get()

    if not from_location or not to_location:
        messagebox.showwarning("Input Error", "Please enter both starting location and destination.")
        return

    lat1, lng1, from_name = geocode_location(from_location)
    lat2, lng2, to_name = geocode_location(to_location)

    if lat1 and lat2:
        get_directions(from_location, to_location)

# Create the main window
root = tk.Tk()
root.title("Route Finder")

# Input fields
tk.Label(root, text="Starting Location:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
from_entry = tk.Entry(root, width=40)
from_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Destination:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
to_entry = tk.Entry(root, width=40)
to_entry.grid(row=1, column=1, padx=10, pady=5)

# Get Directions button
get_directions_button = tk.Button(root, text="Get Directions", command=on_get_directions)
get_directions_button.grid(row=2, column=0, columnspan=2, pady=10)

# Result display
result_text = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD)
result_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Run the application
root.mainloop()