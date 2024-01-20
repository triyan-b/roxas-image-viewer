from textwrap import dedent
from tkinter import *
from tkinter import  ttk
from Application import Application
from DendroImageManager import DendroImageManager
import time
import threading
import traceback


class DendroImageMetadataLoaderFrame(Frame):
    def __init__(self, controller: Application):
        super().__init__()
        
        self.controller = controller
        
        # State
        self.sample_dir = self.controller.state.get("sample_dir")
        self.subsample_dir = self.controller.state.get("subsample_dir")
        self.accepted_image_formats = self.controller.state.get("acceptedImageFormats")
        
        # General
        self.controller.title("Loading")
        self.controller.grid()
        self.focus_set()
        
        # Geometry
        self.w = int(0.4 * self.controller.winfo_screenwidth())
        self.h = int(0.2 * self.controller.winfo_screenheight())
        self.x = (self.controller.winfo_screenwidth() // 2) - (self.w // 2)
        self.y = (self.controller.winfo_screenheight() // 2) - (self.h // 2)
        self.controller.resizable(False, False)
        self.controller.geometry(f'{self.w}x{self.h}+{self.x}+{self.y}')

        self.grid_columnconfigure(tuple(range(1)), weight = 1)
        self.grid_rowconfigure(tuple(range(2)), weight = 1)
        self.grid(row=0, column=0, sticky='nsew')

        # UI components
        self.ui_loading_text = Label(self, text="Analyzing directories...")
        self.ui_loading_text.grid(row=0, column=0, sticky='nesw')

        self.ui_progressbar = ttk.Progressbar(mode='indeterminate', length=200)
        self.ui_progressbar.grid(row=1, column=0, sticky='nesw', padx=2, pady=2)

        # Tasks
        self.ui_progressbar.start(20)
        thrd = threading.Thread(target=self.load_directories_worker)
        thrd.start()
        self.schedule_check(thrd, 300)

    def load_directories_worker(self):
        try:
            metadata_by_sample = DendroImageManager.get_metadata_by_sample(self.sample_dir, self.subsample_dir, self.accepted_image_formats) 
            self.controller.state['metadata_by_sample'] = metadata_by_sample
            samples = list(metadata_by_sample.keys())
            if len(samples) == 0:
                self.loading_status = 'FAILED'
                self.loading_status_message = dedent("""
                    No samples found in chosen directories. Please ensure correct file formats and naming scheme:
                    [site]_[species?]_[tree]_[sample]_[subsample?]_[other attributes]"""
                )
                return 
            self.controller.state['samples'] = samples
            # print(metadata_by_sample)
            # time.sleep(3)
        except Exception as e:
            self.loading_status = 'FAILED'
            self.loading_status_message = traceback.format_exc(limit=2)
            print(self.loading_status_message)
            return            
        
        self.loading_status = 'SUCCESS'
    
    def schedule_check(self, thrd, delay_ms):
        self.controller.after(delay_ms, self.check_worker_done, thrd)

    def check_worker_done(self, thrd):
        # If the thread has finished, load next screen
        if not thrd.is_alive():
            from RoxasImageViewerFrame import RoxasImageViewerFrame
            from SetupFrame import SetupFrame
            self.ui_progressbar.grid_forget()
            
            if self.loading_status == 'SUCCESS':
                self.ui_loading_text.configure(text="Done. Opening Image Viewer.")
                self.controller.show_frame(RoxasImageViewerFrame)
            elif self.loading_status == 'FAILED':
                self.controller.title("Error")
                self.ui_loading_text.configure(text=f"An error occured while loading:\n{self.loading_status_message}", 
                                               justify='left',
                                               wraplength=self.ui_loading_text.winfo_width())
                self.ui_loading_text.grid(sticky="w")
                self.ui_setup_button = Button(self, text="Back to setup", command=lambda: self.controller.show_frame(SetupFrame))
                self.ui_setup_button.grid(row = 1, column = 0, sticky='ews', padx=2, pady=2)
        else:
            # Otherwise check again later
            self.schedule_check(thrd, 100)