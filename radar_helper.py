import os
import asyncio
import threading
import logging
from env_canada import ECRadar
from PIL import Image
import source_helper


async def fetch_radar(root_window=None, status_var=None):
    """Fetch the latest radar image and save it with a unique filename.

    Optional `root_window` and `status_var` are used to update UI status
    without blocking the main thread.
    """
    try:
        if status_var is not None and root_window is not None:
            root_window.after(0, lambda: status_var.set("Fetching radar image..."))

        radar = ECRadar(coordinates=source_helper.COORDINATES)
        latest_png = await radar.get_latest_frame()

        os.makedirs("images", exist_ok=True)
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

        if status_var is not None and root_window is not None:
            root_window.after(0, lambda: status_var.set("Radar image fetched successfully."))
            root_window.after(2000, lambda: status_var.set(""))


        return new_filename
    except Exception:
        logging.exception("Error in fetch_radar")
        raise


def open_radar(root_window=None, status_var=None, event=None):
    """Open the latest radar image without blocking the Tk mainloop.

    If `event` is a Tk event, this function will try to extract the
    top-level root from `event.widget` to optionally update a status
    variable inside the async fetch.
    """

    def _fetch_and_show():
        root_w = root_window
        status_v = status_var
        try:
            if event is not None and hasattr(event, "widget"):
                try:
                    root_w = event.widget.winfo_toplevel()
                except Exception:
                    root_w = None

            new_filename = asyncio.run(fetch_radar(root_window=root_w, status_var=status_v))
            if new_filename and os.path.exists(new_filename):
                img = Image.open(new_filename)
                img.show()
        except Exception:
            logging.exception("Failed to fetch or show radar image")

    threading.Thread(target=_fetch_and_show, daemon=True).start()
