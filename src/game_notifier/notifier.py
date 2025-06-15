"""
Handles notifications sent to users
"""

import requests


def send_ntfy(topic: str, message: str):
    """uses ntfy with a valid topic to send out a notification"""
    requests.post(topic, data=message.encode(encoding="utf-8"))
