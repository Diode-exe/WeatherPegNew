import tkinter as tk

class CommandWindow:
    """Class to create and manage the command window"""
    def __init__(self, root_window, fullscreen_func=None, refresh_func=None):
        self.fullscreen_func = fullscreen_func
        self.refresh_func = refresh_func
        self.cmd_window = tk.Toplevel(root_window)
        self.cmd_window.title("WeatherPeg Commands")
        self.cmd_window.geometry("")

    def create_command_window(self):
        """Create the main command window with buttons"""
        if not self.cmd_window or not self.cmd_window.winfo_exists():
            print("Main window has been destroyed!")
            return None
        if self.fullscreen_func:
            fullscreen_button = tk.Button(
                self.cmd_window, text="Toggle Fullscreen (F11)",
                command=self.fullscreen_func,
                bg="blue", fg="white", font=("VCR OSD Mono", 12)
            )
            fullscreen_button.pack(pady=5)
        if self.refresh_func:
            refresh_button = tk.Button(
                self.cmd_window, text="Refresh Weather (F5)",
                command=self.refresh_func,
                bg="green", fg="yellow", font=("VCR OSD Mono", 12)
            )
            refresh_button.pack(pady=10)
