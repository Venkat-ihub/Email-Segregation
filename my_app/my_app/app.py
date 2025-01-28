# my_app/apps.py
from django.apps import AppConfig
from threading import Thread
from .management.commands.listen_for_emails import Command

class MyAppConfig(AppConfig):
    name = 'my_app'

    def ready(self):
        # Start the listener in a separate thread
        email_listener = Command()
        thread = Thread(target=email_listener.handle)
        thread.start()
