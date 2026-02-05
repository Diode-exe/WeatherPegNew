import tkinter as tk
import html
import re
import requests
from requests.adapters import HTTPAdapter, Retry
import feedparser
import source_helper

PROG = "WeatherPeg"
class GUI:
    """Graphical User Interface setup."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(PROG)
        self.root.configure(bg="black")
        self.root.geometry("800x600")
        self.title_var = tk.StringVar(value="weather")
        title_label = tk.Label(self.root, textvariable=self.title_var, fg="lime", bg="black",
                            font=("VCR OSD Mono", 16, "bold"), justify="left",
                            padx=10, pady=10, wraplength=750)
        title_label.pack()

        self.current_warning_title_var = tk.StringVar(value="No warnings")
        self.current_warning_summary_var = tk.StringVar(value="No warnings in effect.")
        current_warning_title = tk.Label(
                self.root, textvariable=self.current_warning_title_var,
                fg="lime", bg="black",
                font=("VCR OSD Mono", 16, "bold"), justify="left",
                padx=10, pady=10, wraplength=750
        )
        current_warning_title.pack()

        current_warning_summary = tk.Label(
            self.root, textvariable=self.current_warning_summary_var,
            fg="lime", bg="black",
            font=("VCR OSD Mono", 16, "bold"), justify="left",
            padx=10, pady=10, wraplength=750
        )
        current_warning_summary.pack()


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
                    current_title = entry.title
                    current_link = entry.link

                    # Decode HTML entities and clean text
                    current_summary = html.unescape(entry.summary)
                    current_summary = re.sub(r'<[^>]+>', '', current_summary)

                    print("Current Conditions Updated:")
                    print("Entry title:", current_title)
                    print("Entry summary:", current_summary)
                    print("Entry link:", current_link)
                    print("-" * 50)
                    self.gui.title_var.set(current_title)
                    self.gui.current_warning_title_var.set(self.warning_title)
                    self.gui.current_warning_summary_var.set(self.warning_summary)

                    # link_var.set(current_link)
                    # if Config.get_config_bool("show_scroller"):
                    #     scrolling_summary.update_text(current_summary)
        except Exception as e:
            print(f"Error fetching weather data: {e}")

gui_class = GUI()
weather_fetcher = WeatherFetcher(gui_class)
weather_fetcher.get_weather()
gui_class.root.mainloop()
