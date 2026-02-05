SOURCE = "txt/source.txt"
try:
    with open(SOURCE, "r", encoding="utf-8") as RSS:
        RSS_URL = RSS.read().strip()
except FileNotFoundError:
    print(f"[WARN] {SOURCE} not found!")
    print("You need a file called source.txt with a URL pointing towards an XML file so the software knows")
    print("where to get the information from!!")
    input("Press Enter to continue...")

COORD_SOURCE = "txt/coord_source.txt"

try:
    with open(COORD_SOURCE, "r", encoding="utf-8") as f:
        line = f.read().strip()
        if not line:
            raise ValueError("Coordinate file is empty")
        lat_str, lon_str = line.split(",")
        COORDINATES = (float(lat_str), float(lon_str))  # tuple of floats
except FileNotFoundError:
    print(f"[WARN] {COORD_SOURCE} not found!")
    print("You need a file called coord_source.txt with coords in it so the radar has a location")
    input("Press Enter to continue...")
    COORDINATES = None
except ValueError as e:
    print(f"[WARN] {COORD_SOURCE} is invalid: {e}")
    input("Press Enter to continue...")
    COORDINATES = None

print("Coordinates:", COORDINATES)
