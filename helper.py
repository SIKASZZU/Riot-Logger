import os
import json
import sys

from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance
from PyQt6.QtGui import QPixmap


# Available ranks -> riot confirmed
RANKS = {
    "Iron":         'images/iron.png',
    "Bronze":       'images/bronze.png',
    "Silver":       'images/silver.png',
    "Gold":         'images/gold.png',
    "Platinum":     'images/platinum.png',
    "Emerald":      'images/emerald.png',
    "Diamond":      'images/diamond.png',
    "Master":       'images/master.png',
    "Grandmaster":  'images/grandmaster.png',
    "Challenger":   'images/challenger.png'}

# Regions user can choose from -> riot confirmed
REGIONS = [
    'Region',
    'BR1',
    'EUN1',
    'EUW1',
    'JP1',
    'KR',
    'LA1',
    'LA2',
    'ME1',
    'NA1',
    'OC1',
    'RU',
    'SG2',
    'TR1',
    'TW2',
    'VN2',
]


# Get path to Documents/riot_logger/users_data.json
def get_data_path():
    documents = Path.home() / "Documents"
    data_folder = documents / "Riot Logger"
    data_folder.mkdir(exist_ok=True)
    return data_folder / "users_data.json"

FILE_PATH = get_data_path()

def load_data():
    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)

    # Kui datat ei ole ss return empty list 
    except (FileNotFoundError, json.JSONDecodeError):
        print('Did not find any data')
        return []
    
def save_data(users):
    with open(FILE_PATH, "w") as f:
        json.dump(users, f, indent=4)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for development and PyInstaller onefile mode."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def create_rounded_image(image_path, size, radius):
    """Creates a rounded image with PIL and converts it to QPixmap."""
    abs_image_path = get_resource_path(image_path)
    img = Image.open(abs_image_path).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)

    # saturation
    color_enchancer = ImageEnhance.Color(img)
    img = color_enchancer.enhance(1.5)

    # Create rounded mask
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius, fill=255)

    # Apply rounded mask to image
    img.putalpha(mask)

    # Convert to QPixmap
    img.save(get_resource_path("images/temp_rounded.png"))  # Temporary save for conversion
    return QPixmap(get_resource_path("images/temp_rounded.png"))
