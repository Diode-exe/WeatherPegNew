import webbrowser

class WebOpen:
    """Helper class to open the web browser to a specific URL."""
    def opener(self, port):
        """Open the web browser to the weather page."""
        webbrowser.open(f"http://localhost:{port}/weather")
