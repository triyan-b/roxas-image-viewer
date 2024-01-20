
from tkinter import *
import json

class Application(Tk):
    def __init__(self):
        super().__init__()

        # State
        self.state = {}

        ## App settings
        app_settings = self.load_app_settings()
        self.state['acceptedImageFormats'] = app_settings.get('acceptedImageFormats', ["jpg", "jpeg", "png"])
        self.state['csvDelimiter'] = app_settings.get('csvDelimiter', ",")

        # Default geometry        
        self.grid()
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Entry point
        from SetupFrame import SetupFrame # Delayed import
        self.show_frame(SetupFrame)
        self.iconbitmap("./icon.ico")
    
    def show_frame(self, frame: type):
        frame(controller = self).tkraise()

    def load_app_settings(self) -> dict:
        try:
            with open('./settings.json') as f:
                settings = json.load(f)
            # print(settings)
            return settings
        except Exception as e:
            print(e)