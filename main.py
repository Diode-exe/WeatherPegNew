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

PROG = "WeatherPeg"
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

        self.summary_var = tk.StringVar(value="Loading weather data...")
        self.summary_label = tk.Label(self.root, textvariable=self.summary_var, fg="lime", bg="black",
                    font=("VCR OSD Mono", 16, "bold"), justify="left",
                    padx=10, pady=10, wraplength=750)
        self.summary_label.pack()

        self.current_warning_title_var = tk.StringVar(value="No warnings")
        self.current_warning_summary_var = tk.StringVar(value="No warnings in effect.")
        self.current_warning_title = tk.Label(
                self.root, textvariable=self.current_warning_title_var,
                fg="lime", bg="black",
                font=("VCR OSD Mono", 16, "bold"), justify="left",
                padx=10, pady=10, wraplength=750
        )
        self.current_warning_title.pack()

        self.current_warning_summary = tk.Label(
            self.root, textvariable=self.current_warning_summary_var,
            fg="lime", bg="black",
            font=("VCR OSD Mono", 16, "bold"), justify="left",
            padx=10, pady=10, wraplength=750
        )

        self.timestamp_var = tk.StringVar()
        self.timestamp_label = tk.Label(
            self.root, textvariable=self.timestamp_var,
            fg="yellow", bg="black",
            font=("Courier", 10)
        )
        self.timestamp_label.pack(side=tk.BOTTOM, pady=10)

        self.current_warning_summary.pack()
        self.root.bind("<F6>", self.open_command_window)
        self.command_window = None
        self.current_title = None
        self.current_summary = None
        self.current_link = None
        # start the recurring timestamp updates
        self.update_timestamp()

    def open_command_window(self, event=None):
        """Open the command window"""
        if self.command_window is None or not self.command_window.cmd_window.winfo_exists():
            self.command_window = command_window.CommandWindow(self.root,
            fullscreen_func=ScreenState(self).toggle_fullscreen,
            refresh_func=WeatherFetcher(self).get_weather)
            self.command_window.create_command_window()

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
        self.root.bind("<F11>", self.toggle_fullscreen)

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        current_fullscreen = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current_fullscreen)

class Networking:
    """Networking utilities with retry logic."""
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

    _HTTP_SESSION = _create_http_session(self=None)

    def http_get(self, url, **kwargs):
        """Perform an HTTP GET request with retries and timeout."""
        timeout = kwargs.pop("timeout", 10)
        return self._HTTP_SESSION.get(url, timeout=timeout, **kwargs)

class WeatherFetcher:
    """Fetch and process weather data from RSS feed."""
    def __init__(self, gui):
        self.gui = gui
        self.networking = Networking()
        self.warning_title = "No warnings"
        self.warning_summary = "No warnings in effect."
        self.current_title = "none"
        self.current_summary = "none"
        self.current_link = "none"

    def get_weather(self):
        """Fetch and process weather data from RSS feed."""
        try:
            response = self.networking.http_get(url=source_helper.RSS_URL)
            # print(f"DEBUG: HTTP {getattr(response, 'status_code', '<no-status>')} {getattr(response, 'url', '<no-url>')}")
            # try:
            #     snippet = response.content[:200].decode('utf-8', errors='replace')
            # except Exception:
            #     snippet = repr(response.content[:200])
            # print("DEBUG: response content snippet:\n", snippet)

            feed = feedparser.parse(response.content)
            # print(f"DEBUG: parsed feed, entries={len(feed.entries)}")
            # print("DEBUG: entry categories:", [getattr(e, 'category', None) for e in feed.entries])

            for entry in feed.entries:
                if entry.category == "Warnings and Watches":
                    if not entry.summary == "No watches or warnings in effect.":
                        self.warning_summary = entry.summary
                    if entry.summary == "No watches or warnings in effect.":
                        self.warning_summary = "No watches or warnings in effect."
                    self.warning_title = entry.title

            for entry in feed.entries:
                if entry.category == "Current Conditions":
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

                    # link_var.set(current_link)
                    # if Config.get_config_bool("show_scroller"):
                    #     scrolling_summary.update_text(current_summary)
        except Exception as e:
            print(f"Error fetching weather data: {e}")

    def logger(self):
        """Log current weather data to a file if enabled in config."""
        if Config.get_config_bool(self, key="write_log"):
            filename = "txt/history.txt"
            logged_time = self.gui.timestamp_var.get()
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            if os.path.exists(filename):
                logging.info(f"Found {filename}")
            else:
                logging.info(f"Could not find {filename}, but created it")
            with open(filename, "a", encoding="utf-8") as f:
                f.write(f"{self.current_title}\n")
                f.write(f"Summary: {self.current_summary}\n")
                f.write(f"Coords/Link: {self.current_link}\n")
                f.write(f"Current warning: {self.warning_summary}\n")
                f.write(f"Logged time: {logged_time}\n")
                f.write("-" * 50 + "\n")
            logging.info(f"Logged current weather to {filename}")
        else:
            logging.info("Not writing to log")

gui_class = GUI()
fullscreen_manager = ScreenState(gui_class)
weather_fetcher = WeatherFetcher(gui_class)
weather_fetcher.get_weather()
gui_class.root.mainloop()
