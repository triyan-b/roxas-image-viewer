from tkinter import *
from tkinter import ttk
from Application import Application
from RoxasImageViewerFrame import RoxasImageViewerFrame
import threading

class SubsampleViewerSubframe(Frame):
    def __init__(self, controller: Application, parent: RoxasImageViewerFrame):
        super().__init__()

        from SampleViewerSubframe import SampleViewerSubframe

        self.controller = controller
        self.parent = parent
        
        # State
        self.img_loader = self.parent.img_loader
        self.sample_dir = self.parent.sample_dir
        self.subsample_dir = self.parent.subsample_dir
        self.metadata_by_sample = self.parent.metadata_by_sample
        self.curr_sample_i = self.parent.state.get("curr_sample_i")
        self.curr_sample = self.parent.samples[self.curr_sample_i]

        self.get_annotated_twin_subsamples = lambda: self.metadata_by_sample[self.curr_sample]['subsamples_annotated_twin']
        self.get_annotated_subsamples = lambda: self.metadata_by_sample[self.curr_sample]['subsamples_annotated']
        self.get_default_subsamples = lambda: self.metadata_by_sample[self.curr_sample]['subsamples_default']

        self.subsample_ids = sorted(list(
            set(self.get_annotated_twin_subsamples().keys())
            .union(set(self.get_annotated_subsamples().keys())
            .union(set(self.get_default_subsamples().keys())))
        ))
        self.curr_subsample_index = None # Tracked
        self.prev_subsample, self.curr_subsample, self.next_subsample = None, None, None # Curr is Tracked

        # General
        self.controller.title("Subsample Viewer")
        self.controller.grid()
        self.focus_set()
        
        # Geometry
        self.w = int(0.95 * self.controller.winfo_screenwidth())
        self.h = int(0.9 * self.controller.winfo_screenheight())
        self.img_h = int(0.8*(self.h))
        self.img_max_w = int(0.33*(self.w))
        self.default_image = self.img_loader.default_image(int(0.1*(self.w)), self.img_h, (255, 255, 255, 0), text="No Image")
        self.x = 5
        self.y = 5
        self.grid_columnconfigure(tuple(range(3)), weight = 1)
        self.grid_rowconfigure(tuple(range(5)), weight = 1)
        self.grid(row=0, column=0, sticky='nsew')

        # Events
        self.bind("<Alt-Left>", lambda e: self.parent.show_subframe(SampleViewerSubframe))
        self.bind("<Alt-i>", lambda e: self.parent.open_image_in_default_viewer(self.curr_subsample.get("path")) if self.curr_subsample else None)
        self.bind("<Alt-I>", lambda e: self.parent.open_image_in_default_viewer(self.curr_subsample.get("path")) if self.curr_subsample else None)
        self.bind("<Left>", lambda e: self.on_click_change_curr_subsample(False) if (self.ui_prev_subsample_button['state'] == NORMAL) else None)
        self.bind("<Right>", lambda e: self.on_click_change_curr_subsample(True) if (self.ui_next_subsample_button['state'] == NORMAL) else None)
        self.bind("<Return>", lambda e: self.on_click_evaluate_subsample() if (self.ui_evaluate_subsample_button['state'] == NORMAL) else None)


        # UI Components
        self.ui_back_to_samples_button = Button(self, text=" ◀ Sample viewer", command=lambda: self.parent.show_subframe(SampleViewerSubframe))
        self.ui_back_to_samples_button.grid(row = 0, column = 0, sticky='nw', pady=10)

        self.ui_curr_sample_label = Label(self, text="Site {} • Tree {} • Sample {}".format(*self.curr_sample), font=("Segoe UI", 14, "bold"), justify='center')
        self.ui_curr_sample_label.grid(row=0, column=1, sticky='new', pady=10)

        ## Subsample metadata
        self.ui_curr_subsample_label = Label(self, font=("Segoe UI", 12, "bold"))
        self.ui_curr_subsample_label.grid(row=1, column=1, sticky='s')
        self.ui_prev_subsample_label = Label(self)
        self.ui_prev_subsample_label.grid(row=1, column=0, sticky='s')
        self.ui_next_subsample_label = Label(self)
        self.ui_next_subsample_label.grid(row=1, column=2, sticky='s')

        ## Subsample Images
        self.ui_prev_subsample_img = Label(self)
        self.ui_prev_subsample_img.grid(row=2, column=0)

        self.ui_curr_subsample_img = Label(self)
        self.ui_curr_subsample_img.grid(row=2, column=1)

        self.ui_next_subsample_img = Label(self)
        self.ui_next_subsample_img.grid(row=2, column=2)

        ## Controls
        self.subsample_buttons_frame = Frame(self)
        self.subsample_buttons_frame.grid_columnconfigure(tuple(range(3)), weight = 1)
        self.subsample_buttons_frame.grid_rowconfigure(tuple(range(2)), weight = 1)
        self.subsample_buttons_frame.grid(row=3, column=0, columnspan=3, sticky="s")
        self.ui_prev_subsample_button = Button(self.subsample_buttons_frame, text=" ◀ ", command=lambda: self.on_click_change_curr_subsample(False), state=DISABLED)
        self.ui_prev_subsample_button.grid(row=0, column=0, sticky="e")
        self.ui_next_subsample_button = Button(self.subsample_buttons_frame, text=" ▶ ", command=lambda: self.on_click_change_curr_subsample(True), state=DISABLED)
        self.ui_next_subsample_button.grid(row=0, column=2, sticky="w")
        self.ui_open_subsample_in_viewer_button = Button(self.subsample_buttons_frame, text="Open in viewer", command=lambda: self.parent.open_image_in_default_viewer(self.curr_subsample.get("path")) if self.curr_subsample else None)
        self.ui_open_subsample_in_viewer_button.grid(row=0, column=1, sticky='ew')
        self.ui_evaluate_subsample_button = Button(self.subsample_buttons_frame, text="Evaluate subsample", command=self.on_click_evaluate_subsample, state=DISABLED)
        self.ui_evaluate_subsample_button.grid(row=1, column=1, sticky='new')

        ## Info
        self.ui_directories_text = Label(self, text="Sample preview directory: " + self.sample_dir.replace("/", " ▸ ").replace("\\", " ▸ ") + "\nSubsample directory: " + self.subsample_dir.replace("/", " ▸ ").replace("\\", " ▸ "), 
                                            wraplength=self.w, 
                                            justify='left')
        self.ui_directories_text.grid(row=4, column=0, columnspan=3, sticky='sw')

        ## Temporary elements
        self.ui_progressbar = ttk.Progressbar(self, mode='indeterminate', length=80)

        # Tasks
        self.on_click_change_curr_subsample()
    
    def on_click_evaluate_subsample(self):
        from SubsampleEvaluationSubframe import SubsampleEvaluationSubframe
        self.save_tracked_state()
        self.parent.show_subframe(SubsampleEvaluationSubframe)
    
    def save_tracked_state(self):
        self.parent.state.update({
            "curr_subsample_index": self.curr_subsample_index,
            "curr_subsample": self.curr_subsample,
        })
    
    def get_subsample_by_priority(self, subsample_id):
        return self.get_annotated_twin_subsamples().get(subsample_id) \
            or self.get_annotated_subsamples().get(subsample_id) \
            or self.get_default_subsamples().get(subsample_id)

    def get_prev_curr_next_subsample(self):
        if self.curr_subsample_index is None:
            return None, None, None
        curr_subsample_id = self.subsample_ids[self.curr_subsample_index]
        prev_subsample_id = self.subsample_ids[i] if (i := self.curr_subsample_index - 1) in range(len(self.subsample_ids)) else None
        next_subsample_id = self.subsample_ids[i] if (i := self.curr_subsample_index + 1) in range(len(self.subsample_ids)) else None
        
        curr_subsample = self.get_subsample_by_priority(curr_subsample_id)
        prev_subsample = self.get_subsample_by_priority(prev_subsample_id)
        next_subsample = self.get_subsample_by_priority(next_subsample_id)
        
        return prev_subsample, curr_subsample, next_subsample

    def get_subsample_image(self, subsample):
        try:
            return self.img_loader.load_resized(subsample.get("path"), self.img_h, self.img_max_w) if subsample else self.default_image
        except:
            return self.default_image

    def get_subsample_label_text(self, subsample):
        return f"Subsample {subsample.get('subsample')} • {subsample.get('file')}" if subsample is not None else "No subsample"

    def on_click_change_curr_subsample(self, forward=None):
        self.ui_progressbar.grid(row=0, column=2, sticky='ne', pady=10, padx=2)
        self.ui_progressbar.start(15)
        self.ui_progressbar.focus_set()
        thrd = threading.Thread(target=self.change_curr_subsample_task, args=(forward,))
        thrd.start()
    
    def change_curr_subsample_task(self, forward):
        if forward is not None:
            self.curr_subsample_index = (min(self.curr_subsample_index + 1, len(self.subsample_ids) - 1) if forward else max(self.curr_subsample_index - 1, 0)) if len(self.subsample_ids) > 0 else None
        else:
            self.curr_subsample_index = self.parent.state.get("curr_subsample_index", 0 if len(self.subsample_ids) > 0 else None)
        self.prev_subsample, self.curr_subsample, self.next_subsample = self.get_prev_curr_next_subsample()

        prev_image = self.get_subsample_image(self.prev_subsample)
        curr_image = self.get_subsample_image(self.curr_subsample)
        next_image = self.get_subsample_image(self.next_subsample)
        self.ui_prev_subsample_img.configure(image=prev_image)
        self.ui_curr_subsample_img.configure(image=curr_image)
        self.ui_next_subsample_img.configure(image=next_image)

        self.ui_prev_subsample_button.configure(state=(NORMAL if self.prev_subsample else DISABLED))
        self.ui_next_subsample_button.configure(state=(NORMAL if self.next_subsample else DISABLED))
        self.ui_curr_subsample_label.configure(text=self.get_subsample_label_text(self.curr_subsample))
        self.ui_prev_subsample_label.configure(text=self.get_subsample_label_text(self.prev_subsample))
        self.ui_next_subsample_label.configure(text=self.get_subsample_label_text(self.next_subsample))

        self.ui_evaluate_subsample_button.configure(state=(NORMAL if self.curr_subsample else DISABLED))

        self.ui_progressbar.stop()
        self.ui_progressbar.grid_forget()
        self.focus_set()