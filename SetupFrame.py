from tkinter import *
from tkinter import filedialog
from Application import Application
import webbrowser
from urllib.parse import quote
import uuid

class SetupFrame(Frame):
    def __init__(self, controller: Application):
        super().__init__()

        self.controller = controller
        
        # State
        self.sample_preview_dir = self.controller.state.get("sample_dir")
        self.subsample_dir = self.controller.state.get("subsample_dir")
        if not self.controller.state.get("prod"):
            self.sample_preview_dir = "N:/dendro/Dendrosciences_All/PatrickFonti_CALDERA_2019_PF/Box1-30/Box01/0_JPG"
            self.subsample_dir = "N:/dendro/Dendrosciences_All/PatrickFonti_CALDERA_2019_PF/Box1-30/Box01/ROXAS/4_Roxas_final"
            self.sample_preview_dir = "C:/Users/bhardwaj/Desktop/Triyan/git/roxas-image-viewer/images"
            self.subsample_dir = "C:/Users/bhardwaj/Desktop/Triyan/git/roxas-image-viewer/images"
            pass

        # General
        self.controller.title("Setup")
        self.controller.grid()
        self.controller.protocol("WM_DELETE_WINDOW", self.controller.destroy)
        self.focus_set()

        
        # Geometry
        self.w = int(0.4 * self.controller.winfo_screenwidth())
        self.h = int(0.2 * self.controller.winfo_screenheight())
        self.x = (self.controller.winfo_screenwidth() // 2) - (self.w // 2)
        self.y = (self.controller.winfo_screenheight() // 2) - (self.h // 2)
        self.controller.resizable(False, False)
        self.controller.geometry(f'{self.w}x{self.h}+{self.x}+{self.y}')

        self.grid_columnconfigure(tuple(range(3)), weight = 1)
        self.grid_rowconfigure(tuple(range(3)), weight = 1)
        self.grid(row=0, column=0, sticky='nsew')

        # Events
        self.bind("<Return>", lambda e: self.on_click_continue() if (self.ui_continue_button['state'] == NORMAL) else None)

        # UI components
        
        self.ui_sample_preview_dir_text = Label(self, text="Sample preview directory:\n"+f"{self.sample_preview_dir}", wraplength=int(0.75*self.w), justify='left')
        self.ui_sample_preview_dir_text.grid(row=0, column=0, columnspan=2, sticky='w')

        self.ui_subsample_dir_text = Label(self, text="Subsample directory:\n"+f"{self.subsample_dir}", wraplength=int(0.75*self.w), justify='left')
        self.ui_subsample_dir_text.grid(row=1, column=0, columnspan=2, sticky='w')

        self.ui_select_sample_preview_dir_button = Button(self, text="Select sample directory", command=self.on_click_select_sample_preview_dir)
        self.ui_select_sample_preview_dir_button.grid(row=0, column=2, sticky='e', padx=2)
        
        self.ui_select_subsample_dir_button = Button(self, text="Select subsample directory", command=self.on_click_select_subsample_dir)
        self.ui_select_subsample_dir_button.grid(row=1, column=2, sticky='e', padx=2)
        
        self.bottom_frame = Frame(self)
        self.bottom_frame.grid(row=2, column=0, columnspan=3, sticky='sew')
        self.bottom_frame.grid_columnconfigure(0, weight = 1)
        self.bottom_frame.grid_columnconfigure(1, weight = 7)

        self.ui_report_bug_button = Button(self.bottom_frame, text="Report a bug 🐞", command=self.on_click_report_bug)
        self.ui_report_bug_button.grid(row=0, column=0, sticky='sew', padx=2, pady=2)
        self.ui_continue_button = Button(self.bottom_frame, text="Continue", command=self.on_click_continue, state=(NORMAL if self.is_setup_complete() else DISABLED))
        self.ui_continue_button.grid(row=0, column=1, sticky='sew', padx=2, pady=2)

    
    def on_click_select_sample_preview_dir(self):
        self.sample_preview_dir = directory if (directory := self.ask_directory()) else self.sample_preview_dir
        self.update_ui()

    def on_click_select_subsample_dir(self):
        self.subsample_dir = directory if (directory := self.ask_directory()) else self.subsample_dir
        self.update_ui()

    def on_click_continue(self):
        from DendroImageMetadataLoaderFrame import DendroImageMetadataLoaderFrame
        self.controller.state.update({
            "sample_dir": self.sample_preview_dir,
            "subsample_dir": self.subsample_dir
        })
        self.controller.show_frame(DendroImageMetadataLoaderFrame)
    
    def ask_directory(self) -> str:
        return directory if (directory := filedialog.askdirectory()) else None

    def update_ui(self):
        self.ui_sample_preview_dir_text.configure(text="Sample preview directory:\n"+f"{self.sample_preview_dir}")
        self.ui_subsample_dir_text.configure(text="Subsample directory:\n"+f"{self.subsample_dir}")
        self.ui_continue_button.configure(state=('normal' if self.is_setup_complete() else 'disabled'))

    def is_setup_complete(self) -> bool:
        return self.sample_preview_dir is not None and self.subsample_dir is not None

    def on_click_report_bug(self):
        to = "triyanb@gmail.com"
        subject = f"Bug in Roxas Image Viewer (#{uuid.uuid4().hex[:6].upper()})"
        url = f"mailto:?to={to}&subject={quote(subject)}"
        webbrowser.open(url, new=2)