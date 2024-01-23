
from tkinter import *
import sys
import yaml

class Application(Tk):
    def __init__(self):
        super().__init__()

        # State
        self.state = {}
        args = sys.argv
        if len(args) > 1:
            self.state["prod"] = (args[1] == "prod")

        ## App settings
        app_settings = self.load_app_settings()
        self.state['accepted_image_formats'] = app_settings.get('ACCEPTED_IMAGE_FORMATS', ["jpg", "jpeg", "png"])
        self.state['csv_delimiter'] = app_settings.get('CSV_DELIMITER', ",")
        self.state['evaluation_criteria'] = app_settings.get('EVALUATION_CRITERIA', [])

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
            with open('./settings.yaml') as f:
                settings = yaml.safe_load(f)
            # print(settings)
            return settings
        except Exception as e:
            print(e)