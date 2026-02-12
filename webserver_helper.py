import threading
import os
import datetime
import logging
import signal
from flask import Flask, url_for, request, render_template
from flask_socketio import SocketIO
from config import Config

TEMPLATE_FOLDER = "templates"
STATIC_FOLDER = "static"

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

socketio = SocketIO(app, async_mode="threading")

class WebServerHelper:
    """Helper class to manage the Flask web server and its routes."""

    def __init__(self, current_title, current_summary, warning_title, warning_summary, port=2046):
        self.current_title = current_title
        self.current_summary = current_summary
        self.warning_title = warning_title
        self.warning_summary = warning_summary
        self.port = port
        app.add_url_rule("/weather", view_func=self.webweather)
        app.add_url_rule("/shutdown", view_func=self.shutdown, methods=["GET", "POST"])

    def webweather(self, timestamp_var=None):
        """Flask route to display weather information."""
        logging.info("Flask route accessed!")
        css_url = url_for('static', filename='styles.css')
        try:
            last_updated_value = timestamp_var.get()
        except Exception:
            last_updated_value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return render_template(
            "weather.html",
            css_url=css_url,
            current_title=self.current_title,
            current_summary=self.current_summary,
            warning_title=self.warning_title,
            warning_summary=self.warning_summary,
            last_updated=last_updated_value
        )

    def shutdown(self):
        """Flask route to shut down the server. Only accessible from localhost."""
        if request.remote_addr != "127.0.0.1":
            return "Forbidden", 403

        # Schedule shutdown after response is sent
        threading.Timer(1.0, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()

        return "Server is shutting down..."

    def start_webserver(self):
        """Start the Flask web server in a separate thread."""
        if Config.get_config_bool(self, key="webserver"):
            def run_server():
                app.run(host="0.0.0.0", port=self.port, debug=False, use_reloader=False)
            threading.Thread(target=run_server, daemon=True).start()
        else:
            logging.info("Not starting webserver")
