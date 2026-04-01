import logging

SOURCE = "txt/source.txt"
try:
    with open(SOURCE, "r", encoding="utf-8") as RSS:
        RSS_URL = RSS.read().strip()
except FileNotFoundError:
    logging.warning(f"{SOURCE} not found!")
    logging.warning("You need a file called source.txt with a URL pointing towards an"
                    "XML file so the software knows where to get the information from!!")

COORD_SOURCE = "txt/coord_source.txt"

try:
    with open(COORD_SOURCE, "r", encoding="utf-8") as f:
        line = f.read().strip()
        if not line:
            raise ValueError("Coordinate file is empty")
        lat_str, lon_str = line.split(",")
        COORDINATES = (float(lat_str), float(lon_str))  # tuple of floats
except FileNotFoundError:
    logging.warning(f"{COORD_SOURCE} not found!")
    logging.warning("You need a file called coord_source.txt with coords in it so the radar has a location")
    COORDINATES = None
except ValueError as e:
    logging.warning(f"{COORD_SOURCE} is invalid: {e}")
    COORDINATES = None

logging.info(f"Coordinates: {COORDINATES}")
