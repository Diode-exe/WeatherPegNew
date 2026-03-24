class Config:
    """Configuration management for WeatherPeg."""
    def __init__(self):
        self.show_warning = True
        self.show_buttons = True
        self.show_instruction = True
        self.do_tts = True
        self.show_link = True
        self.mode = True
        self.show_cmd = True
        self.show_display = True
        self.webserver = True
        self.port = 2046
        self.write_log = True
        self.show_scroller = True
        self.refresh_delay = 120000
        self.flash_delay = 600000
