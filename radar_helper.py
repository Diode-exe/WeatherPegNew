import os
import asyncio
import threading
import logging
from env_canada import ECRadar
from PIL import Image
import source_helper

async def fetch_radar():
    """Fetch the latest radar image and save it with a unique filename."""
    radar = ECRadar(coordinates=source_helper.COORDINATES)
    latest_png = await radar.get_latest_frame()

    filename = "images/radar_img.png"
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    # Find a unique filename
    while os.path.exists(new_filename):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1

    # Write the radar image
    with open(new_filename, "wb") as f:
        f.write(latest_png)

    return new_filename  # return the actual filename

def open_radar(event=None):
    """Open the latest radar image."""

    def _fetch_and_show():
        try:
            new_filename = asyncio.run(fetch_radar())
            img = Image.open(new_filename)
            img.show()
        except Exception:
            logging.exception("Failed to fetch or show radar image")

    threading.Thread(target=_fetch_and_show, daemon=True).start()
