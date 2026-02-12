import tkinter as tk

import radar_helper
from browser_helper import WebOpen

class CommandWindow:
    """Class to create and manage the command window"""
    def __init__(self, root_window, fullscreen_func=None, refresh_func=None, status_var=None, gui=None):
        self.fullscreen_func = fullscreen_func
        self.refresh_func = refresh_func
        self.status_var = status_var
        self.gui = gui
        self.cmd_window = tk.Toplevel(root_window)
        self.cmd_window.title("WeatherPeg Commands")
        self.cmd_window.geometry("")
        self.cmd_window.bind("<F2>", lambda event=None: radar_helper.open_radar(root_window=self.cmd_window, status_var=self.gui.status_var, event=event))
        self.cmd_window.bind("<F4>", lambda event=None: WebOpen.opener(self, port=2046))
        self.cmd_window.bind("<F5>", lambda event=None: self.refresh_func())
        self.cmd_window.bind("<F6>", self.create_command_window)
        self.cmd_window.bind("<F11>", self.fullscreen_func)

    def create_command_window(self, event=None):
        """Create the main command window with buttons"""
        if not self.cmd_window or not self.cmd_window.winfo_exists():
            print("Main window has been destroyed!")
            return None

        radar_button = tk.Button(
            self.cmd_window, text="Open radar (F2)",
            command=lambda event=None: radar_helper.open_radar(root_window=self.cmd_window, status_var=self.gui.status_var, event=event),
            bg="blue", fg="white", font=("VCR OSD Mono", 12)
        )

        webserver_button = tk.Button(
            self.cmd_window, text="Open webserver (F4)",
            command=lambda: WebOpen.opener(self, port=2046),
            bg="blue", fg="white", font=("VCR OSD Mono", 12)
        )
        webserver_button.pack(pady=5)

        if self.refresh_func:
            refresh_button = tk.Button(
                self.cmd_window, text="Refresh Weather (F5)",
                command=self.refresh_func,
                bg="green", fg="yellow", font=("VCR OSD Mono", 12)
            )
            refresh_button.pack(pady=10)

        open_command_window_button = tk.Button(
            self.cmd_window, text="Open Command Window (F6)",
            command=self.create_command_window,
            bg="green", fg="yellow", font=("VCR OSD Mono", 12)
        )
        open_command_window_button.pack(pady=10)

        radar_button.pack(pady=5)
        if self.fullscreen_func:
            fullscreen_button = tk.Button(
                self.cmd_window, text="Toggle Fullscreen (F11)",
                command=self.fullscreen_func,
                bg="blue", fg="white", font=("VCR OSD Mono", 12)
            )
            fullscreen_button.pack(pady=5)
