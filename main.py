import requests
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk  # Install Pillow via pip: pip install pillow
from io import BytesIO
import urllib.parse
from colorTheme import light_theme, dark_theme

# Load environment variables from .env file
load_dotenv()
MAPQUEST_API_KEY = os.getenv("MAPQUEST_API_KEY")

GEOCODE_URL = "https://www.mapquestapi.com/geocoding/v1/address"
DIRECTIONS_URL = "http://www.mapquestapi.com/directions/v2/route"
STATIC_MAP_URL = "https://www.mapquestapi.com/staticmap/v5/map"

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

def get_static_map(from_loc, to_loc):
    response = requests.get(
        STATIC_MAP_URL + "?start=" + urllib.parse.quote(from_loc) +
        "&end=" + urllib.parse.quote(to_loc) +
        "&size=800,600@2x&key=" + MAPQUEST_API_KEY
    )
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        messagebox.showerror("Error", "Failed to load the map.")
        return None

def get_directions(from_loc, to_loc):
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

        # Display textual directions
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

def apply_theme(theme):
    root.config(bg=theme["bg"])
    top_frame.config(bg=theme["bg"])
    main_frame.config(bg=theme["bg"])
    
    # Labels
    for widget in top_frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(bg=theme["bg"], fg=theme["fg"])

    # Entries
    from_entry.config(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])
    to_entry.config(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])

    # Buttons
    get_directions_button.config(bg=theme["button_bg"], fg=theme["button_fg"])
    toggle_button.config(bg=theme["button_bg"], fg=theme["button_fg"])

    # OptionMenu (transport mode)
    transport_mode_menu.config(bg=theme["button_bg"], fg=theme["button_fg"])

    # Map label
    map_label.config(bg=theme["bg"])

    # Text area
    result_text.config(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["text_fg"])

def toggle_dark_mode():
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    theme = dark_theme if is_dark_mode else light_theme
    apply_theme(theme)

# Create the main window
root = tk.Tk()
root.title("Route Finder")

# Set dark_mode variable
is_dark_mode = False

# Set the window to full screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# Create frames for layout
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=10, pady=10)

# Dark mode button (moved to top left)
toggle_button = tk.Button(top_frame, text="Toggle Dark Mode", command=toggle_dark_mode)
toggle_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")

# Input fields (shifted down by one row)
tk.Label(top_frame, text="Starting Location:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
from_entry = tk.Entry(top_frame, width=40)
from_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(top_frame, text="Destination:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
to_entry = tk.Entry(top_frame, width=40)
to_entry.grid(row=1, column=3, padx=10, pady=5)

# Get Directions button (same row as input fields)
get_directions_button = tk.Button(top_frame, text="Get Directions", command=on_get_directions)
get_directions_button.grid(row=1, column=4, padx=10, pady=5)

# Transport mode selection (shifted to next row)
tk.Label(top_frame, text="Transport Mode:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
transport_mode_var = tk.StringVar()
transport_mode_var.set("fastest")  # default value
transport_mode_menu = tk.OptionMenu(top_frame, transport_mode_var, "fastest", "shortest", "pedestrian", "bicycle", "car")
transport_mode_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Map display (static map)
map_label = tk.Label(main_frame)
map_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Result display (textual directions)
result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
result_text.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Configure grid weights for resizing
main_frame.columnconfigure(0, weight=1)  # Map column
main_frame.columnconfigure(1, weight=1)  # Directions column
main_frame.rowconfigure(0, weight=1)     # Row containing both

# Apply light theme
apply_theme(light_theme)

# Run the application
root.mainloop()