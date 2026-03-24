import tkinter as tk
import logging
import html
import os
import re
import datetime
import requests
from requests.adapters import HTTPAdapter, Retry
import feedparser
import source_helper
import command_window
from config import Config
from scrolling_text_widget import ScrollingTextWidget
import radar_helper
from webserver_helper import WebServerHelper
from browser_helper import WebOpen
import webserver_helper as _ws

PROG = "WeatherPeg"
DESIGNED_BY = "Designed by Diode-exe"

config_class = Config()

class GUI:
    """Graphical User Interface setup."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(PROG)
        self.root.configure(bg="black")
        self.root.geometry("800x600")
        self.title_var = tk.StringVar(value="Loading weather data...")
        self.title_label = tk.Label(self.root, textvariable=self.title_var, fg="lime", bg="black",
                            font=("VCR OSD Mono", 16, "bold"), justify="left",
                            padx=10, pady=10, wraplength=750)
        self.title_label.pack()

        web_open = WebOpen()

        self.port = config_class.port
        if self.port is None:
            logging.warning("Port not configured properly. Defaulting to 2046.")
            self.port = 2046

        # optional scrolling summary (placed under title)
        self.scrolling_summary = None
        try:
            if config_class.show_scroller:
                self.scrolling_summary = ScrollingTextWidget(self.root, "Loading weather data...", width=80, speed=150)
        except Exception:
            self.scrolling_summary = None

        self.summary_var = tk.StringVar(value="Loading weather data...")
        # self.summary_label = tk.Label(self.root, textvariable=self.summary_var, fg="lime", bg="black",
        #             font=("VCR OSD Mono", 16, "bold"), justify="left",
        #             padx=10, pady=10, wraplength=750)
        # self.summary_label.pack()

        self.link_var = tk.StringVar(value="")
        if config_class.show_link:
            logging.info("Showing link")
            self.link_label = tk.Label(
                self.root, textvariable=self.link_var,
                fg="cyan", bg="black",
                font=("VCR OSD Mono", 10), justify="left",
                padx=10, pady=10
            )
            self.link_label.pack()
        else:
            logging.info("Not showing link")

        self.current_warning_title_var = tk.StringVar(value="No warnings")
        self.current_warning_summary_var = tk.StringVar(value="No warnings in effect.")
        self.current_warning_title_label = tk.Label(
                self.root, textvariable=self.current_warning_title_var,
                fg="lime", bg="black",
                font=("VCR OSD Mono", 16, "bold"), justify="left",
                padx=10, pady=10, wraplength=750
        )
        self.current_warning_title_label.pack()

        self.current_warning_summary = tk.Label(
            self.root, textvariable=self.current_warning_summary_var,
            fg="lime", bg="black",
            font=("VCR OSD Mono", 16, "bold"), justify="left",
            padx=10, pady=10, wraplength=750
        )
        self.current_warning_summary.pack()

        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(
            self.root, textvariable=self.status_var,
            fg="lime", bg="black",
            font=("Courier", 10)
        )
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        self.designed_by_label = tk.Label(
            self.root, text=DESIGNED_BY,
            fg="cyan", bg="black",
            font=("Courier", 10), justify="left"
        )
        self.designed_by_label.pack(side=tk.BOTTOM, pady=10, padx=10)

        self.timestamp_var = tk.StringVar()
        self.timestamp_label = tk.Label(
            self.root, textvariable=self.timestamp_var,
            fg="lime", bg="black",
            font=("Courier", 10)
        )
        self.timestamp_label.pack(side=tk.BOTTOM, pady=10)

        self.root.bind("<F4>", lambda event=None: web_open.opener(port=self.port))
        self.root.bind("<F6>", self.open_command_window)
        self.command_window = None
        self.current_title = None
        self.current_summary = None
        self.current_link = None
        self.fullscreen_manager = ScreenState(self)
        self.weather_fetcher = WeatherFetcher(self, networking, self.fullscreen_manager)
        self.update_timestamp()

    def open_command_window(self, event=None):
        """Open the command window"""
        if self.command_window is None or not self.command_window.cmd_window.winfo_exists():
            self.command_window = command_window.CommandWindow(
                self.root,
                fullscreen_func=self.fullscreen_manager.toggle_fullscreen,
                refresh_func=self.weather_fetcher.get_weather,
                status_var=self.status_var,
                gui=self
            )
            self.command_window.create_command_window()
            self.command_window.cmd_window.lift()

    def update_timestamp(self):
        """Update the timestamp every second."""
        self.timestamp_var.set(f"Current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.root.after(1000, self.update_timestamp)  # Update every second

class ScreenState():
    """Manage screen state such as fullscreen toggling."""
    def __init__(self, gui):
        self.gui = gui
        self.root = gui.root
        self.fullscreen = False
        self.root.bind("<F2>", lambda event=None: radar_helper.open_radar(root_window=self.root, status_var=self.gui.status_var, event=event))
        self.root.bind("<F11>", self.toggle_fullscreen)

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        current_fullscreen = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current_fullscreen)

    def display_flash_off(self):
        """Make the screen flash off."""
        self.gui.title_label.config(fg="black", bg="black")
        self.gui.current_warning_title_label.config(fg="black", bg="black")
        self.gui.current_warning_summary.config(fg="black", bg="black")
        self.gui.status_label.config(fg="black", bg="black")
        self.gui.timestamp_label.config(fg="black", bg="black")
        self.gui.designed_by_label.config(fg="black", bg="black")
        if getattr(self.gui, 'scrolling_summary', None):
            ScrollingTextWidget.flash_black(self.gui.scrolling_summary)
        self.gui.root.update()
        self.gui.root.after(250, self.display_flash_on)

    def display_flash_on(self):
        """Make the screen flash on."""
        self.gui.title_label.config(fg="lime", bg="black")
        self.gui.current_warning_title_label.config(fg="lime", bg="black")
        self.gui.current_warning_summary.config(fg="lime", bg="black")
        self.gui.status_label.config(fg="lime", bg="black")
        self.gui.timestamp_label.config(fg="lime", bg="black")
        self.gui.designed_by_label.config(fg="cyan", bg="black")
        self.gui.root.update()

class Networking:
    """Networking utilities with retry logic."""
    def __init__(self):
        self._http_session = self._create_http_session()
        self.result = None

    def _create_http_session(self):
        session = requests.Session()
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def http_get(self, url, **kwargs):
        """Perform an HTTP GET request with retries and timeout."""
        timeout = kwargs.pop("timeout", 10)
        return self._http_session.get(url, timeout=timeout, **kwargs)

class WeatherFetcher:
    """Fetch and process weather data from RSS feed."""
    def __init__(self, gui, networking_ref, screen_state_ref):
        self.gui = gui
        self.networking = networking_ref
        self.warning_title = "No warnings"
        self.warning_summary = "No warnings in effect."
        self.current_title = "none"
        self.current_summary = "none"
        self.current_link = "none"
        self.scrolling_summary = None
        self.screen_state = screen_state_ref
        self.gui.root.bind("<F5>", lambda event=None: self.get_weather())
        self.did_not_exist = False

    def get_weather(self):
        """Fetch and process weather data from RSS feed."""
        try:
            response = self.networking.http_get(url=source_helper.RSS_URL)

            feed = feedparser.parse(response.content)

            for entry in feed.entries:

                if entry.category == "Warnings and Watches":
                    if not entry.summary == "No watches or warnings in effect.":
                        self.warning_summary = entry.summary
                    if entry.summary == "No watches or warnings in effect.":
                        self.warning_summary = "No watches or warnings in effect."
                    self.warning_title = entry.title

                if entry.category == "Current Conditions":
                    try:
                        self.current_title = entry.title
                        self.current_link = entry.link

                        # Decode HTML entities and clean text
                        self.current_summary = html.unescape(entry.summary)
                        self.current_summary = re.sub(r'<[^>]+>', '', self.current_summary)

                        print("Current Conditions Updated:")
                        print("Entry title:", self.current_title)
                        print("Entry summary:", self.current_summary)
                        print("Entry link:", self.current_link)
                        print("-" * 50)
                        self.gui.title_var.set(self.current_title)
                        self.gui.summary_var.set(self.current_summary)
                        self.gui.current_warning_title_var.set(self.warning_title)
                        self.gui.current_warning_summary_var.set(self.warning_summary)
                        self.gui.link_var.set(self.current_link)

                        try:
                            if hasattr(_ws, "socketio") and _ws.socketio:
                                _ws.socketio.emit("weather_updated")
                                logging.debug("Emitted SocketIO weather_updated event")
                        except Exception:
                            logging.debug("Could not emit SocketIO update (webserver may not be running)")

                    except AttributeError as e:
                        logging.warning(f"Missing expected feed entry attribute: {e}")
                    except Exception as e:
                        logging.warning(f"Error processing feed entry: {e}")
                        continue

                    self.logger()

                    # update scrolling summary widget if present
                    if getattr(self.gui, 'scrolling_summary', None):
                        try:
                            self.gui.scrolling_summary.update_text(self.current_summary)
                            self.gui.scrolling_summary.flash_black()
                        except Exception as e:
                            logging.warning(f"Error updating scrolling summary: {e}")
        except Exception as e:
            logging.warning(f"Error fetching weather data: {e}")
        self.screen_state.display_flash_off()
        self.gui.root.after(120000, self.get_weather)  # Refresh every 2 minutes

    def logger(self):
        """Log current weather data to a file if enabled in config."""
        if config_class.write_log:
            filename = "txt/history.txt"
            logged_time = self.gui.timestamp_var.get()
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            if os.path.exists(filename):
                logging.info(f"Found {filename}")
            else:
                self.did_not_exist = True
            with open(filename, "a", encoding="utf-8") as f:
                f.write(f"{self.current_title}\n")
                f.write(f"Summary: {self.current_summary}\n")
                f.write(f"Coords/Link: {self.current_link}\n")
                f.write(f"Current warning: {self.warning_summary}\n")
                f.write(f"Logged time: {logged_time}\n")
                f.write("-" * 50 + "\n")
            if self.did_not_exist:
                logging.info(f"Could not find {filename}, but created it")
            logging.info(f"Logged current weather to {filename}")
            self.dlhistory()
        else:
            logging.info("Not writing to log")

    def dlhistory(self):
        """Download the RSS feed history to an XML file"""
        url = source_helper.RSS_URL
        filename = "history/weatherpegsource.xml"

        # If file exists, append a number
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename

        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        while os.path.exists(new_filename):
            new_filename = f"{base}_{counter}{ext}"
            counter += 1

        response = self.networking.http_get(url, stream=True)
        with open(new_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
            logging.info(f"Download complete! Saved as {new_filename}")

networking = Networking()

gui_class = GUI()
# Open the command window on startup
gui_class.open_command_window()
gui_class.weather_fetcher.get_weather()
webserver_helper = WebServerHelper(
    current_title=gui_class.weather_fetcher.current_title,
    current_summary=gui_class.weather_fetcher.current_summary,
    warning_title=gui_class.weather_fetcher.warning_title,
    warning_summary=gui_class.weather_fetcher.warning_summary
)
webserver_helper.start_webserver()
gui_class.root.mainloop()
