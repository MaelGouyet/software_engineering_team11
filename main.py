import requests
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk  # Install Pillow via pip: pip install pillow
from io import BytesIO
import urllib.parse
from colorTheme import white_theme, charcoal_theme, khaki_theme, light_blue_theme, pink_theme

# Load environment variables from .env file
load_dotenv()
MAPQUEST_API_KEY = os.getenv("MAPQUEST_API_KEY")

GEOCODE_URL = "https://www.mapquestapi.com/geocoding/v1/address"
DIRECTIONS_URL = "http://www.mapquestapi.com/directions/v2/route"
STATIC_MAP_URL = "https://www.mapquestapi.com/staticmap/v5/map"

def geocode_location(location):
    """
    Geocode a location to get latitude, longitude, and a formatted address.
    
    Args:
        location (str): The address or location name to be geocoded.
    
    Returns:
        tuple: Latitude, Longitude, and the formatted address (or original location if error occurs).
    """
    params = {
        "key": MAPQUEST_API_KEY,
        "location": location
    }
    response = requests.get(GEOCODE_URL, params=params)
    data = response.json()

    if response.status_code == 200 and data["info"]["statuscode"] == 0:
        # Extract latitude, longitude, and formatted address
        latlng = data["results"][0]["locations"][0]["latLng"]
        display_name = data["results"][0]["locations"][0]["street"] + ", " + data["results"][0]["locations"][0]["adminArea5"] + ", " + data["results"][0]["locations"][0]["adminArea3"]
        return latlng["lat"], latlng["lng"], display_name
    else:
        # Show error message if geocoding fails
        messagebox.showerror("Error", f"Error in geocoding: {data['info']['messages']}")
        return None, None, location

def get_static_map(from_loc, to_loc):
    """
    Fetch a static map image between two locations using MapQuest API.
    
    Args:
        from_loc (str): The starting location for the route.
        to_loc (str): The destination location for the route.
    
    Returns:
        PIL.Image: The static map image, or None if the request fails.
    """
    response = requests.get(
        STATIC_MAP_URL + "?start=" + urllib.parse.quote(from_loc) +
        "&end=" + urllib.parse.quote(to_loc) +
        "&size=800,600@2x&key=" + MAPQUEST_API_KEY
    )
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        # Show error message if map fails to load
        messagebox.showerror("Error", "Failed to load the map.")
        return None

def get_directions(from_loc, to_loc):
    """
    Fetch directions between two locations using MapQuest API and display them.
    
    Args:
        from_loc (str): The starting location.
        to_loc (str): The destination location.
    """
    params = {
        "key": MAPQUEST_API_KEY,
        "from": from_loc,
        "to": to_loc,
        "routeType": transport_mode_var.get()
    }
    response = requests.get(DIRECTIONS_URL, params=params)
    data = response.json()

    if response.status_code == 200 and data["info"]["statuscode"] == 0:
        # Fetch and display the static map
        map_image = get_static_map(from_loc, to_loc)
        if map_image:
            # Scale the image to fit inside the map_label
            map_image = map_image.resize((map_label.winfo_width(), map_label.winfo_height()))
            map_image_tk = ImageTk.PhotoImage(map_image)
            map_label.config(image=map_image_tk)
            map_label.image = map_image_tk

        # Display textual directions in improved format
        result_text.delete(1.0, tk.END)
        
        # Header with origin and destination
        result_text.insert(tk.END, from_loc + "\n", "origin")
        result_text.insert(tk.END, "to ", "to_text")
        result_text.insert(tk.END, to_loc + "\n\n", "destination")
        
        # Time and distance summary
        total_minutes = int(data['route']['time'] / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            result_text.insert(tk.END, f"{hours} h {minutes} min\n", "time")
        else:
            result_text.insert(tk.END, f"{minutes} min\n", "time")
        
        result_text.insert(tk.END, f"{data['route']['distance']:.1f} mi\n\n", "distance")
        
        if 'fuelUsed' in data['route']:
            result_text.insert(tk.END, f"IRS reimbursement: ${data['route']['fuelUsed'] * 3.5:.2f}\n\n", "cost")
        
        arrow_color = "#FFFFFF" if is_dark_mode else "#000000"

        # Display each maneuver in the route
        for i, leg in enumerate(data["route"]["legs"][0]["maneuvers"]):
            direction = leg.get('directionName', '').lower()
            narrative = leg.get('narrative', '').lower()

             # Assign appropriate symbols for directions
            if "right" in narrative:
                symbol = "➤"
            elif "left" in narrative:
                symbol = "⬅"
            elif direction == "north":
                symbol = "⬆"
            elif direction == "northeast":
                symbol = "⬈"
            elif direction == "east":
                symbol = "➡"
            elif direction == "southeast":
                symbol = "⬊"
            elif direction == "south":
                symbol = "⬇"
            elif direction == "southwest":
                symbol = "⬋"
            elif direction == "west":
                symbol = "⬅"
            elif direction == "northwest":
                symbol = "⬉"
            elif "u-turn" in narrative:
                symbol = "↺"
            else:
                symbol = "➡"
            
            result_text.insert(tk.END, f"{symbol} ", "symbol")
            result_text.insert(tk.END, f"{leg['narrative']}\n", "instruction")
            
            if i < len(data["route"]["legs"][0]["maneuvers"]) - 1:
                result_text.insert(tk.END, f"Then {leg['distance']:.1f} mi\n\n", "distance_segment")

        # Styling the tags used in the result text
        result_text.tag_configure("origin", font=("Arial", 14, "bold"), foreground="#2E7D32")
        result_text.tag_configure("to_text", font=("Arial", 12))
        result_text.tag_configure("destination", font=("Arial", 14, "bold"))
        result_text.tag_configure("time", font=("Arial", 18, "bold"))
        result_text.tag_configure("distance", font=("Arial", 12))
        result_text.tag_configure("cost", font=("Arial", 12), foreground="#555555")
        result_text.tag_configure("symbol", font=("Arial", 28, "bold"), foreground=arrow_color)
        result_text.tag_configure("instruction", font=("Arial", 12))
        result_text.tag_configure("distance_segment", font=("Arial", 10), foreground="#666666")
        
    else:
        messagebox.showerror("Error", f"Error retrieving route: {data['info']['messages']}")

def on_get_directions():
    """
    Triggered when the 'Get Directions' button is clicked. Geocodes the locations and fetches directions.
    """
    from_location = from_entry.get()
    to_location = to_entry.get()

    if not from_location or not to_location:
        messagebox.showwarning("Input Error", "Please enter both starting location and destination.")
        return

    lat1, lng1, from_name = geocode_location(from_location)
    lat2, lng2, to_name = geocode_location(to_location)

    if lat1 and lat2:
        get_directions(from_location, to_location)

def apply_theme(theme):
    """
    Applies the selected theme to the application UI.
    
    Args:
        theme (dict): A dictionary containing the colors for the theme.
    """
    root.config(bg=theme["bg"])
    top_frame.config(bg=theme["bg"])
    main_frame.config(bg=theme["bg"])
    
    for widget in top_frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(bg=theme["bg"], fg=theme["fg"])
    
    from_entry.config(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])
    to_entry.config(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])

    get_directions_button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
    theme_selector.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
    find_gas_button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
    find_hotels_button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
    
    transport_mode_menu.config(bg=theme["button_bg"], fg=theme["button_fg"], highlightbackground=theme["button_bg"])
    
    map_label.config(bg=theme["bg"])

    result_text.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["text_fg"])
    gas_result_text.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["text_fg"])
    
    arrow_color = "#FFFFFF" if is_dark_mode else "#000000"
    result_text.tag_configure("symbol", font=("Arial", 28, "bold"), foreground=arrow_color)

def find_nearby_gas_stations(lat, lng):
    """
    Finds nearby gas stations using the MapQuest API and displays the results.

    Parameters:
    lat (float): Latitude of the current location.
    lng (float): Longitude of the current location.

    This function sends a request to the MapQuest API to search for gas stations
    within a 10km radius of the specified location, and then displays the results
    in a text widget.
    """
    url = 'https://www.mapquestapi.com/search/v4/place'
    params = {
        'location': f'{lng},{lat}',
        'q': 'station-service',
        'sort': 'distance',
        'feedback': 'false',
        'circle': f'{lng},{lat},10000',
        'key': MAPQUEST_API_KEY,
        'pageSize': 10
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        if results:
            gas_result_text.delete(1.0, tk.END)
            gas_result_text.insert(tk.END, "Nearby Gas Stations:\n\n", "header")
            for place in results:
                name = place.get('name', 'Unknown')
                coords = place.get('place', {}).get('geometry', {}).get('coordinates', [])
                address = place.get('displayString', 'No address')
                distance = place.get('distance', 0)
                gas_result_text.insert(tk.END, f"- {name}\n", "poi_name")
                gas_result_text.insert(tk.END, f"  Distance: {distance:.2f} km\n\n", "poi_distance")
        else:
            gas_result_text.delete(1.0, tk.END)
            gas_result_text.insert(tk.END, "No gas stations found nearby.\n", "error")
    else:
        messagebox.showerror("Error", f"Failed to retrieve gas stations: {response.status_code}")

def on_find_gas_stations():
    """
    Handles the event when the user requests to find nearby gas stations.

    This function retrieves the destination entered by the user, geocodes the location,
    and calls the `find_nearby_gas_stations` function if the geocoding is successful.
    """
    to_location = to_entry.get()

    if not to_location:
        messagebox.showwarning("Input Error", "Please enter a destination.")
        return

    lat, lng, location_name = geocode_location(to_location)

    if lat and lng:
        find_nearby_gas_stations(lat, lng)

def find_nearby_hotels(lat, lng):
    """
    Finds nearby hotels using the MapQuest API and displays the results.

    Parameters:
    lat (float): Latitude of the current location.
    lng (float): Longitude of the current location.

    This function sends a request to the MapQuest API to search for hotels
    within a 10km radius of the specified location, and then displays the results
    in a text widget.
    """
    url = 'https://www.mapquestapi.com/search/v4/place'
    params = {
        'location': f'{lng},{lat}',
        'q': 'hotel',
        'sort': 'distance',
        'feedback': 'false',
        'circle': f'{lng},{lat},10000',
        'key': MAPQUEST_API_KEY,
        'pageSize': 10
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        if results:
            gas_result_text.delete(1.0, tk.END)
            gas_result_text.insert(tk.END, "Nearby Hotels:\n\n", "header")
            for place in results:
                name = place.get('name', 'Unknown')
                coords = place.get('place', {}).get('geometry', {}).get('coordinates', [])
                address = place.get('displayString', 'No address')
                distance = place.get('distance', 0)
                gas_result_text.insert(tk.END, f"- {name}\n", "poi_name")
                gas_result_text.insert(tk.END, f"  Address: {address}\n", "poi_address")
        else:
            gas_result_text.delete(1.0, tk.END)
            gas_result_text.insert(tk.END, "No hotels found nearby.\n", "error")
    else:
        messagebox.showerror("Error", f"Failed to retrieve hotels: {response.status_code}")

def on_find_hotels():
    """
    Handles the event when the user requests to find nearby hotels.

    This function retrieves the destination entered by the user, geocodes the location,
    and calls the `find_nearby_hotels` function if the geocoding is successful.
    """
    to_location = to_entry.get()

    if not to_location:
        messagebox.showwarning("Input Error", "Please enter a destination.")
        return

    lat, lng, location_name = geocode_location(to_location)

    if lat and lng:
        find_nearby_hotels(lat, lng)

root = tk.Tk()
root.title("Route Finder")

is_dark_mode = False
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=10, pady=10)

tk.Label(top_frame, text="Starting Location:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
from_entry = tk.Entry(top_frame, width=40)
from_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(top_frame, text="Destination:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
to_entry = tk.Entry(top_frame, width=40)
to_entry.grid(row=1, column=3, padx=10, pady=5)

get_directions_button = tk.Button(top_frame, text="Get Directions", command=on_get_directions)
get_directions_button.grid(row=1, column=4, padx=10, pady=5)

tk.Label(top_frame, text="Transport Mode:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
transport_mode_var = tk.StringVar()
transport_mode_var.set("fastest")
transport_mode_menu = tk.OptionMenu(top_frame, transport_mode_var, "fastest", "shortest", "pedestrian", "bicycle", "car")
transport_mode_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

find_gas_button = tk.Button(top_frame, text="Find Gas Stations", command=on_find_gas_stations)
find_gas_button.grid(row=2, column=2, padx=10, pady=5)

find_hotels_button = tk.Button(top_frame, text="Find Hotels", command=on_find_hotels)
find_hotels_button.grid(row=2, column=3, padx=10, pady=5)

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

map_label = tk.Label(main_frame)
map_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Directions Result Frame
result_frame = tk.Frame(main_frame, bd=1, relief=tk.SOLID, bg="#FFFFFF", highlightbackground="#D0D0D0", highlightthickness=1)
result_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

canvas = tk.Canvas(result_frame, bd=0, highlightthickness=0, bg="#FFFFFF")
canvas.pack(fill=tk.BOTH, expand=True)

result_text = scrolledtext.ScrolledText(canvas, wrap=tk.WORD, font=("Arial", 11), bd=0, padx=15, pady=15, highlightthickness=0)
result_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

# Nearby Gas Stations Result Frame
gas_result_frame = tk.Frame(main_frame, bd=1, relief=tk.SOLID, bg="#FFFFFF", highlightbackground="#D0D0D0", highlightthickness=1)
gas_result_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

gas_canvas = tk.Canvas(gas_result_frame, bd=0, highlightthickness=0, bg="#FFFFFF")
gas_canvas.pack(fill=tk.BOTH, expand=True)

gas_result_text = scrolledtext.ScrolledText(gas_canvas, wrap=tk.WORD, font=("Arial", 11), bd=0, padx=15, pady=15, highlightthickness=0)
gas_result_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

# Theme Selector
theme_var = tk.StringVar(value="light")
theme_selector = tk.OptionMenu(top_frame, theme_var, "white", "charcoal", "khaki", "light blue", "pink",
    command=lambda theme: apply_theme({
        "white": white_theme,
        "charcoal": charcoal_theme,
        "khaki": khaki_theme,
        "light blue": light_blue_theme,
        "pink": pink_theme
    }.get(theme, white_theme)))

theme_selector.grid(row=0, column=0, padx=10, pady=5, sticky="w")

apply_theme(white_theme)
root.mainloop()
