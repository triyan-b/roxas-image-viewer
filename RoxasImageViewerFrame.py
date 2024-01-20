from tkinter import *
from Application import Application
from ImageLoader import ImageLoader

class RoxasImageViewerFrame(Frame):
    def __init__(self, controller: Application):
        super().__init__()

        from SampleViewerSubframe import SampleViewerSubframe
        
        self.controller = controller

        # State
        self.state = {
            "evaluations": {('YAM', '8', 2, 1, '2021'): {'Category A': 'None', 'Category B': 'None', 'Category C': 'None', 'Category D': 'None', 'Category E': 'None', 'Category F': 'None', 'Category G': 'None'}, ('YAM', '8', 2, 1, '2022'): {'Category A': 'None', 'Category B': 'None', 'Category C': 'None', 'Category D': 'None', 'Category E': 'None', 'Category F': 'None', 'Category G': 'None'}, ('YAM', '8', 2, 1, '2023'): {'Category A': 'None', 'Category B': 'None', 'Category C': 'None', 'Category D': 'None', 'Category E': 'None', 'Category F': 'None', 'Category G': 'None'}}
        }
        self.img_loader = ImageLoader()
        self.sample_dir = self.controller.state.get("sample_dir")
        self.subsample_dir = self.controller.state.get("subsample_dir")
        self.metadata_by_sample = self.controller.state.get("metadata_by_sample")
        self.samples = self.controller.state.get("samples")
        
        # General

        
        # Geometry
        self.w = int(0.95 * self.controller.winfo_screenwidth())
        self.h = int(0.9 * self.controller.winfo_screenheight())
        self.x = 5
        self.y = 5
        self.controller.resizable(True, True)
        self.controller.geometry(f'{self.w}x{self.h}+{self.x}+{self.y}')

        # UI Components
        ## Entry point: Sample Viewer
        self.current_subframe = None
        self.show_subframe(SampleViewerSubframe)

    def show_subframe(self, subframe: Frame):
        if self.current_subframe is not None:
            self.current_subframe.grid_forget()
        new_subframe = subframe(self.controller, self)
        self.current_subframe = new_subframe















