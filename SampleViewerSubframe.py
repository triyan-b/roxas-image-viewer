from tkinter import *
from tkinter import ttk, messagebox, filedialog
from Application import Application
from RoxasImageViewerFrame import RoxasImageViewerFrame
import pandas as pd
import threading

class SampleViewerSubframe(Frame):
    def __init__(self, controller: Application, parent: RoxasImageViewerFrame):
        super().__init__()

        self.controller = controller
        self.parent = parent
        
        # State
        self.img_loader = self.parent.img_loader
        self.sample_dir = self.parent.sample_dir
        self.subsample_dir = self.parent.subsample_dir
        self.metadata_by_sample = self.parent.metadata_by_sample
        self.samples = self.parent.samples
        self.get_preview_sample = lambda sample: self.metadata_by_sample.get(sample).get('preview')
        
        ## Remove subsample tracking if being tracked
        self.parent.state.pop("curr_subsample", None)
        self.parent.state.pop("curr_subsample_index", None)
        
        self.curr_sample_i = self.parent.state.get("curr_sample_i", 0) # Tracked
        self.prev_sample, self.curr_sample, self.next_sample = None, None, None

        # General
        self.controller.title("Sample Viewer")
        self.controller.grid()
        self.focus_set()
        
        # Geometry
        self.w = int(0.95 * self.controller.winfo_screenwidth())
        self.h = int(0.9 * self.controller.winfo_screenheight())
        self.img_w = int(0.33*(self.w))
        self.img_max_h = int(0.7*(self.h))
        self.default_image = self.img_loader.default_image(self.img_w, self.img_w/2, (255, 255, 255, 0))
        self.x = 5
        self.y = 5
        self.grid_columnconfigure(tuple(range(3)), weight = 1)
        self.grid_rowconfigure(tuple(range(5)), weight = 1)
        self.grid(row=0, column=0, sticky='nsew')

        # Events
        self.bind("<Alt-Left>", lambda e: self.on_click_go_to_setup())
        self.bind("<Left>", lambda e: self.on_click_change_curr_sample(False) if (self.ui_prev_sample_button['state'] == NORMAL) else None)
        self.bind("<Right>", lambda e: self.on_click_change_curr_sample(True) if (self.ui_next_sample_button['state'] == NORMAL) else None)
        self.bind("<Return>", lambda e: self.on_click_view_subsamples() if (self.ui_view_subsamples_button['state'] == NORMAL) else None)
        self.controller.protocol("WM_DELETE_WINDOW", self.on_click_close_window)

        # UI Components
        self.ui_setup_button = Button(self, text=" ◀ Setup", command=self.on_click_go_to_setup)
        self.ui_setup_button.grid(row = 0, column = 0, sticky='nw', pady=10)
        
        ## Sample metadata
        self.ui_curr_sample_label = Label(self, font=("Segoe UI", 14, "bold"))
        self.ui_curr_sample_label.grid(row=1, column=1, sticky='s')
        self.ui_prev_sample_label = Label(self)
        self.ui_prev_sample_label.grid(row=1, column=0, sticky='s')
        self.ui_next_sample_label = Label(self)
        self.ui_next_sample_label.grid(row=1, column=2, sticky='s')

        ## Sample Images
        self.ui_prev_sample_img = Label(self)
        self.ui_prev_sample_img.grid(row=2, column=0)

        self.ui_curr_sample_img = Label(self)
        self.ui_curr_sample_img.grid(row=2, column=1)

        self.ui_next_sample_img = Label(self)
        self.ui_next_sample_img.grid(row=2, column=2)


        ## Controls
        self.sample_buttons_frame = Frame(self)
        self.sample_buttons_frame.grid_columnconfigure(tuple(range(3)), weight = 1)
        self.sample_buttons_frame.grid_rowconfigure(tuple(range(2)), weight = 1)
        self.sample_buttons_frame.grid(row=3, column=0, columnspan=3, sticky="s")

        self.ui_prev_sample_button = Button(self.sample_buttons_frame, text="    ◀    ", command=lambda: self.on_click_change_curr_sample(False), state=DISABLED)
        self.ui_prev_sample_button.grid(row=0, column=0, sticky="e")

        self.ui_next_sample_button = Button(self.sample_buttons_frame, text="    ▶    ", command=lambda: self.on_click_change_curr_sample(True), state=DISABLED)
        self.ui_next_sample_button.grid(row=0, column=2, sticky="w")

        self.ui_open_sample_in_viewer_button = Button(self.sample_buttons_frame, text="Open in viewer", command=lambda: self.parent.open_image_in_default_viewer(p.get("path")) if (p := self.get_preview_sample(self.curr_sample)) else None)
        self.ui_open_sample_in_viewer_button.grid(row=0, column=1, sticky="ew")

        self.ui_view_subsamples_button = Button(self.sample_buttons_frame, text="View subsamples", command=self.on_click_view_subsamples)
        self.ui_view_subsamples_button.grid(row=1, column=1, sticky='new')
        
        self.ui_view_evaluations_button = Button(self.sample_buttons_frame, text="View evaluations", command=self.on_click_view_evaluations)
        self.ui_view_evaluations_button.grid(row=2, column=1, sticky='new')

        self.ui_export_evaluations_button = Button(self.sample_buttons_frame, text="Export evaluations", command=self.on_click_export_evaluations)
        self.ui_export_evaluations_button.grid(row=3, column=1, sticky='new')


        self.ui_set_sample_dropdown_label = Label(self, text="Jump to sample:")
        self.ui_set_sample_dropdown_label.grid(row=4, column=1, sticky='se')

        self.ui_set_sample_dropdown = ttk.Combobox(self, state="readonly", values=[self.get_sample_label_text(s) for s in self.samples])
        self.ui_set_sample_dropdown.current(self.curr_sample_i)
        self.ui_set_sample_dropdown.bind("<<ComboboxSelected>>", lambda e: self.on_click_change_curr_sample(new_i = self.ui_set_sample_dropdown.current()))
        self.ui_set_sample_dropdown.grid(row=4, column=2, sticky='sew')

        ## Info
        self.ui_directories_text = Label(self, text="Sample preview directory: " + self.sample_dir.replace("/", " ▸ ").replace("\\", " ▸ ") + "\nSubsample directory: " + self.subsample_dir.replace("/", " ▸ ").replace("\\", " ▸ "), 
                                            wraplength=self.w, 
                                            justify='left')
        self.ui_directories_text.grid(row=4, column=0, columnspan=3, sticky='sw')

        ## Temporary elements
        self.ui_progressbar = ttk.Progressbar(self, mode='indeterminate', length=80)

        # Tasks
        self.on_click_change_curr_sample(new_i=self.curr_sample_i)

    def on_click_view_subsamples(self):
        from SubsampleViewerSubframe import SubsampleViewerSubframe
        self.save_tracked_state()
        self.parent.show_subframe(SubsampleViewerSubframe)
        
    
    def save_tracked_state(self):
        self.parent.state.update({
            "curr_sample_i": self.curr_sample_i,
        })

    def get_sample_image(self, sample):
        if sample is None:
            return self.default_image
        elif (preview := self.get_preview_sample(sample)) is not None:
            try:
                return self.img_loader.load_resized_landscape(preview.get("path"), self.img_w, self.img_max_h)
            except:
                pass
        return self.default_image
    
    def get_sample_label_text(self, sample):
        return "Site {} • Tree {} • Sample {}".format(*sample) if sample is not None else "No sample"
    
    def get_prev_curr_next_sample(self):
        curr_sample = self.samples[self.curr_sample_i]
        prev_sample = sample if (sample := (curr_sample[0], curr_sample[1], (curr_sample[2]) - 1)) in self.metadata_by_sample else None
        next_sample = sample if (sample := (curr_sample[0], curr_sample[1], (curr_sample[2]) + 1)) in self.metadata_by_sample else None
        return prev_sample, curr_sample, next_sample
    
    def on_click_view_evaluations(self):
        from EvaluationsTableSubframe import EvaluationsTableSubframe
        self.save_tracked_state()
        self.parent.show_subframe(EvaluationsTableSubframe)

    def on_click_export_evaluations(self):
        df = pd.DataFrame.from_dict(self.parent.state.get("evaluations"), orient='index').reset_index()
        if len(df) > 0:
            if not (path := filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], initialfile="XXX_feature.csv")):
                return True
            df = df.rename(columns={
                df.columns[0]: "Site",
                df.columns[1]: "Tree",
                df.columns[2]: "Sample",
                df.columns[3]: "Subsample",
                df.columns[4]: "Year"
            })
            
            try:
                df.to_csv(path, sep=self.controller.state.get("csv_delimiter"), index=False)
                self.parent.state["is_unsaved"] = False
                messagebox.showinfo("Export", "Export completed!")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Something went wrong during the export!\n\n{e}")
                return False
        else:
            messagebox.showerror("Error", "No evaluations to export!")
            return True
            

    def on_click_change_curr_sample(self, forward = None, new_i = None):
        self.ui_progressbar.grid(row=0, column=2, sticky='ne', pady=10, padx=2)
        self.ui_progressbar.start(15)
        self.ui_progressbar.focus_set()
        thrd = threading.Thread(target=self.change_curr_sample_task, args=(forward, new_i))
        thrd.start()

    def change_curr_sample_task(self, forward, new_i):
        self.curr_sample_i = new_i if new_i is not None else (min(self.curr_sample_i + 1, len(self.samples) - 1) if forward else max(self.curr_sample_i - 1, 0))
        self.prev_sample, self.curr_sample, self.next_sample = self.get_prev_curr_next_sample()
        
        prev_image = self.get_sample_image(self.prev_sample)
        curr_image = self.get_sample_image(self.curr_sample)
        next_image = self.get_sample_image(self.next_sample)
        self.ui_prev_sample_img.configure(image=prev_image)
        self.ui_curr_sample_img.configure(image=curr_image)
        self.ui_next_sample_img.configure(image=next_image)
        
        self.ui_prev_sample_button.configure(state=(NORMAL if self.curr_sample_i > 0 else DISABLED))
        self.ui_next_sample_button.configure(state=(NORMAL if self.curr_sample_i < len(self.samples) - 1 else DISABLED))
        self.ui_curr_sample_label.configure(text=self.get_sample_label_text(self.curr_sample))
        self.ui_prev_sample_label.configure(text=self.get_sample_label_text(self.prev_sample))
        self.ui_next_sample_label.configure(text=self.get_sample_label_text(self.next_sample))

        self.ui_set_sample_dropdown.current(self.curr_sample_i)

        self.ui_progressbar.stop()
        self.ui_progressbar.grid_forget()
        self.focus_set()

        # print(self.img_loader.load_resized_landscape.cache_info())
    
    def ask_to_save(self):
        if self.parent.state.get("is_unsaved"):
            do_save = messagebox.askyesnocancel("Save?", "Would you like to export current evaluations before exiting? Unsaved work will be lost!")
            # Don't continue if cancel pressed or saving failed
            if do_save is None or (do_save and not self.on_click_export_evaluations()):
                return False
        return True

    def on_click_go_to_setup(self):
        continue_to_next_screen = self.ask_to_save() 
        if not continue_to_next_screen:
            return
        from SetupFrame import SetupFrame
        self.controller.show_frame(SetupFrame)
    
    def on_click_close_window(self):
        continue_to_next_screen = self.ask_to_save()
        if not continue_to_next_screen:
            return
        self.controller.destroy()