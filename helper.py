import os
import json
import sys
import io

from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance
from PyQt6.QtGui import QPixmap, QImage

FADE_SATURAION = 1.5
BORDER_SATURAION = 1

# Button sizes
button_width = 500
button_height = 100
button_radius = 24


RANKS = [
    "Iron",
    "Bronze",
    "Silver",
    "Gold",
    "Platinum",
    "Emerald",
    "Diamond",
    "Master",
    "Grandmaster",
    "Challenger",
]

RANKS_PATH_FADE = {
    "Unranked":     'images/fade/temp_rounded.png',
    "Iron":         'images/fade/iron.png',
    "Bronze":       'images/fade/bronze.png',
    "Silver":       'images/fade/silver.png',
    "Gold":         'images/fade/gold.png',
    "Platinum":     'images/fade/platinum.png',
    "Emerald":      'images/fade/emerald.png',
    "Diamond":      'images/fade/diamond.png',
    "Master":       'images/fade/master.png',
    "Grandmaster":  'images/fade/grandmaster.png',
    "Challenger":   'images/fade/challenger.png'
}

RANKS_PATH_BORDER = {
    "Unranked":     'images/border/temp_rounded.png', # fix this shit, diamond as default?
    "Iron":         'images/border/iron.png',
    "Bronze":       'images/border/bronze.png',
    "Silver":       'images/border/silver.png',
    "Gold":         'images/border/gold.png',
    "Platinum":     'images/border/platinum.png',
    "Emerald":      'images/border/emerald.png',
    "Diamond":      'images/border/diamond.png',
    "Master":       'images/border/master.png',
    "Grandmaster":  'images/border/grandmaster.png',
    "Challenger":   'images/border/challenger.png'
}

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
        json.dump(users, f)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for development and PyInstaller onefile mode."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def create_fade_image(image_path, size, radius):
    """Creates a rounded image with PIL and converts it to QPixmap."""
    if image_path == None:
        print(f'ERROR! create_fade_image image_path {image_path}')
        return
    
    if size[0] <= 0 or size[1] <= 0 or size == None:
        print(f'ERROR! create_fade_image size {size}')
        return

    if radius < 0 or radius == None:
        print(f'ERROR! create_fade_image radius {radius}')
        return

    abs_image_path = get_resource_path(image_path)
    img = Image.open(abs_image_path).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)

    # saturation
    color_enchancer = ImageEnhance.Color(img)
    img = color_enchancer.enhance(FADE_SATURAION)

    # Create rounded mask
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius, fill=255)

    # Apply rounded mask to image
    img.putalpha(mask)

    # Convert to QPixmap in-memory (avoid writing temporary files)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qimg = QImage.fromData(buf.getvalue())
    return QPixmap.fromImage(qimg)

def create_border_image(image_path):
    """Creates a rounded image with PIL and converts it to QPixmap."""
    if image_path == None:
        print(f'ERROR! create_border_image image_path {image_path}')
        return
    abs_image_path = get_resource_path(image_path)
    img = Image.open(abs_image_path).convert("RGBA")

    border_width = img.width
    border_height = img.height
    img = img.resize((round(border_width * 0.5), round(border_height * 0.5)), Image.Resampling.BICUBIC)

    color_enchancer = ImageEnhance.Color(img)
    img = color_enchancer.enhance(BORDER_SATURAION)

    # Convert to QPixmap in-memory (avoid writing temporary files)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qimg = QImage.fromData(buf.getvalue())
    return QPixmap.fromImage(qimg)

def create_circular_icon(image_path):
    """
    Takes image data (bytes or file path), creates a circular 50x50 image, and returns a QPixmap.
    """

    # Load image from bytes or file path
    if isinstance(image_path, bytes):
        img = Image.open(io.BytesIO(image_path)).convert("RGBA")
    else:
        img = Image.open(image_path).convert("RGBA")

    img_w = 45
    img_h = 45

    img = img.resize((img_w, img_h), Image.Resampling.BICUBIC)

    # Create circular mask
    mask = Image.new('L', (img_w, img_h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img_w, img_h), fill=255)
    img.putalpha(mask)

    # Convert to QPixmap
    data = io.BytesIO()
    img.save(data, format='PNG')
    qimg = QImage.fromData(data.getvalue())
    return QPixmap.fromImage(qimg)

def create_hot_streak(image_path):

    if image_path == None:
        print(f'ERROR! create_hot_streak image_path {image_path}')
        return
    abs_image_path = get_resource_path(image_path)
    img = Image.open(abs_image_path).convert("RGBA")

    img_w = 25
    img_h = 25

    img = img.resize((img_w, img_h), Image.Resampling.BICUBIC)

    # Convert to QPixmap
    data = io.BytesIO()
    img.save(data, format='PNG')
    qimg = QImage.fromData(data.getvalue())
    return QPixmap.fromImage(qimg)