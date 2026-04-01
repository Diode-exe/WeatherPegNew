from notifypy import Notify

class NotificationHelper:
    """Helper class for sending notifications."""
    def __init__(self):
        self.notification = Notify()

    def send_notification(self, title: str, message: str) -> None:
        """
        Send a desktop notification.
        """
        self.notification.title = title
        self.notification.message = message
        self.notification.title = title
        self.notification.message = message
        self.notification.send()
