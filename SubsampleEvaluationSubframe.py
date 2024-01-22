from tkinter import *
from tkinter import messagebox
from Application import Application
from RoxasImageViewerFrame import RoxasImageViewerFrame
import pandas as pd
import re

class SubsampleEvaluationSubframe(Frame):
    def __init__(self, controller: Application, parent: RoxasImageViewerFrame):
        super().__init__()

        from SubsampleViewerSubframe import SubsampleViewerSubframe

        self.controller = controller
        self.parent = parent

        # State
        self.img_loader = self.parent.img_loader
        self.sample_dir = self.parent.sample_dir
        self.subsample_dir = self.parent.subsample_dir
        self.metadata_by_sample = self.parent.metadata_by_sample
        self.curr_sample_i = self.parent.state.get("curr_sample_i")
        self.curr_sample = self.parent.samples[self.curr_sample_i]
        self.curr_subsample = self.parent.state.get("curr_subsample")

        self.eval_criteria_keys = ["X-dating", "Compression wood", "Orientation", "Artefacts", "Crack(s)", "Out of focus", "Frost ring?", "Decay", "Filled cells", "Compressed cells", "Overlapping cells", "Broken cells", "Tyloses", "Paraffin", "Others"]
        self.eval_criteria_values = ["None", "EW", "LW", "All"]
        self.eval_criteria = {key: StringVar() for key in self.eval_criteria_keys}
        self.eval_criteria_count = len(list(self.eval_criteria.keys()))

        # General
        self.controller.title("Evaluate Subample")
        self.controller.grid()
        self.focus_set()

        # Geometry
        self.w = int(0.95 * self.controller.winfo_screenwidth())
        self.h = int(0.9 * self.controller.winfo_screenheight())
        self.img_h = int(0.8*(self.h))
        self.img_max_w = int(0.33*(self.w))
        self.default_image = self.img_loader.default_image(self.img_max_w, self.img_h, (255, 255, 255, 0))
        self.x = 5
        self.y = 5
        self.grid_columnconfigure(tuple(range(3)), weight = 1)
        self.grid_rowconfigure(tuple(range(5)), weight = 1)
        self.grid(row=0, column=0, sticky='nsew')

        # Events
        self.bind("<Alt-Left>", lambda e: self.parent.show_subframe(SubsampleViewerSubframe))
        self.bind("<Button-1>", lambda e: self.on_click_focus_set(e))

        # UI components
        self.ui_back_to_subsamples_button = Button(self, text=" ◀ Subample viewer", command=lambda: self.parent.show_subframe(SubsampleViewerSubframe))
        self.ui_back_to_subsamples_button.grid(row = 0, column = 0, sticky='nw', pady=10)

        ## Subsample
        self.ui_curr_subsample_label = Label(self, text=self.get_subsample_label_text(), font=("Segoe UI", 14, "bold"), justify='center')
        self.ui_curr_subsample_label.grid(row=0, column=1, sticky='new', pady=10)

        self.ui_curr_subsample_filename_label = Label(self, text=f"{self.curr_subsample.get('file')}", font=("Segoe UI", 12, "bold"))
        self.ui_curr_subsample_filename_label.grid(row=1, column=0, sticky='s')

        self.ui_curr_subsample_img = Label(self, image=self.get_subsample_image(self.curr_subsample))
        self.ui_curr_subsample_img.grid(row=2, column=0)

        ## Controls
        self.subsample_buttons_frame = Frame(self)
        self.subsample_buttons_frame.grid_columnconfigure(tuple(range(3)), weight = 1)
        self.subsample_buttons_frame.grid_rowconfigure(tuple(range(2)), weight = 1)
        self.subsample_buttons_frame.grid(row=3, column=0, sticky="n")
        self.ui_open_subsample_in_viewer_button = Button(self.subsample_buttons_frame, text="Open in viewer", command=lambda: self.parent.open_image_in_default_viewer(self.curr_subsample.get("path")))
        self.ui_open_subsample_in_viewer_button.grid(row=0, column=1, sticky='ew')

        ## Evaluation grid
        self.eval_frame = Frame(self)
        self.eval_frame.grid_columnconfigure(tuple(range(len(self.eval_criteria_values) + 1)), weight = 1)
        self.eval_frame.grid_rowconfigure(tuple(range(self.eval_criteria_count + 1)), weight = 1)
        self.eval_frame.grid(row=2, column=1, sticky='n')

        ### Top row 
        self.eval_year_label = Label(self.eval_frame, text="Year", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky='w')
        self.eval_year_input = Entry(self.eval_frame, justify='center')
        self.eval_year_input.grid(row=0, column=1, columnspan=1, sticky='ew')
        self.inc_dec_frame = Frame(self.eval_frame)
        self.inc_dec_frame.grid(row=0, column=2, sticky='w')
        self.eval_dec_year_button = Button(self.inc_dec_frame, text="−", command=lambda: self.on_click_change_year(False))
        self.eval_dec_year_button.grid(row=0, column=0, sticky='w')
        self.eval_inc_year_button = Button(self.inc_dec_frame, text="+", command=lambda: self.on_click_change_year(True))
        self.eval_inc_year_button.grid(row=0, column=1, sticky='w')
        self.eval_delete_button = Button(self.eval_frame, text="Delete", command=lambda: self.on_click_crud_evaluation(False))
        self.eval_delete_button.grid(row=0, column=len(self.eval_criteria_values) - 1, sticky='ew')
        self.eval_save_button = Button(self.eval_frame, text="Save", command=lambda: self.on_click_crud_evaluation(True))
        self.eval_save_button.grid(row=0, column=len(self.eval_criteria_values), sticky='ew')
        
        ### Radio button grid
        for i, category in enumerate(self.eval_criteria):
            Label(self.eval_frame, text=category, font=("Segoe UI", 9, "bold")).grid(row=i+1, column=0, sticky='w')
            for j, value in enumerate(self.eval_criteria_values):
                rb = Radiobutton(self.eval_frame, text=value, variable=self.eval_criteria[category], value=value)
                rb.select() if j == 0 else rb.deselect() # Default value is first in values list
                rb.grid(row=i+1, column=j+1, padx=8, pady=5, sticky='ew')

        ## Current subsample evaluations table
        self.subsample_evals = None
        self.evals_table_headers_text = Label(self.eval_frame, font=("MS Gothic", 10), justify='left', borderwidth=1, relief="solid")
        self.evals_table_rows_text = Label(self.eval_frame, font=("MS Gothic", 10), justify='left', borderwidth=1, relief="solid")
        
        ### Compact/Expanded mode toggle
        self.compact_table_view = True
        self.table_view_toggle = Checkbutton(self.eval_frame, text="Compact view", command=self.on_toggle_table_view)
        if self.compact_table_view:
            self.table_view_toggle.select()

        self.show_evaluations_table()
    
    def on_toggle_table_view(self):
        self.compact_table_view = not self.compact_table_view
        self.show_evaluations_table()

    def show_evaluations_table(self):
        self.subsample_evals = self.get_subsample_evaluations()
        headers, rows = self.get_subsample_evaluations_table()
        if not headers:
            self.evals_table_headers_text.grid_forget()
            self.evals_table_rows_text.grid_forget()
            self.table_view_toggle.grid_forget()
        else:        
            self.evals_table_headers_text.configure(text=headers)
            self.evals_table_headers_text.grid(row=self.eval_criteria_count + 1, column=0, columnspan=len(self.eval_criteria_values) + 1)
            self.evals_table_rows_text.configure(text=rows)
            self.evals_table_rows_text.grid(row=self.eval_criteria_count + 2, column=0, columnspan=len(self.eval_criteria_values) + 1)
            self.table_view_toggle.grid(row=self.eval_criteria_count + 3, column=0, columnspan=len(self.eval_criteria_values) + 1)

    def on_click_crud_evaluation(self, save=True):
        year = self.eval_year_input.get()
        if len(year) == 0:
            messagebox.showerror("Error", 'Please enter a value for "Year"')
            return
        pk = (*self.curr_sample, self.curr_subsample.get("subsample"), year)
        if save:
            self.parent.state.get("evaluations")[pk] = {category: "" if (v := value.get()) == "None" else v for category, value in self.eval_criteria.items()}
        else:
            self.parent.state.get("evaluations").pop(pk, None)
        self.parent.state["is_unsaved"] = (True and bool(self.parent.state.get("evaluations")))
        self.show_evaluations_table()
        self.focus_set()
        print(self.parent.state)

    def get_subsample_evaluations_table(self):
        df = pd.DataFrame.from_dict(self.subsample_evals, orient='index').reset_index()
        if len(df) > 0:
            df = df.drop(df.columns[[0, 1, 2, 3]], axis = 1).rename(columns={df.columns[4]: "year"})
            if self.compact_table_view:
                df = df.apply(lambda row: pd.Series(pd.concat([row.iloc[:1], pd.Series([row[row == value].index.tolist() for value in self.eval_criteria_values[1:]])])), axis=1)
                df = df.rename(columns={df.columns[i]: name for i, name in enumerate(self.eval_criteria_values[1:], start = 1)})  
            return tuple(df.to_string(index=False).split("\n", 1))
        else:
            return '', ''

    def get_subsample_evaluations(self):
        return {key: val for key, val in self.parent.state.get("evaluations").items() if key[:-1] == (*self.curr_sample, self.curr_subsample.get("subsample"))}

    def get_subsample_label_text(self):
        return "Site {} • Tree {} • Sample {} • Subsample {}".format(*self.curr_sample, self.curr_subsample.get('subsample'))

    def get_subsample_image(self, subsample):
        try:
            return self.img_loader.load_resized(subsample.get("path"), self.img_h, self.img_max_w) if subsample else self.default_image
        except:
            return self.default_image
    
    def on_click_change_year(self, increase=True):
        year = self.eval_year_input.get() 
        if re.match(r'^-?[0-9]+$', year):
            self.eval_year_input.delete(0, END)
            self.eval_year_input.insert(0, str(int(year) + (1 if increase else -1)))

    def on_click_focus_set(self, event):
        x, y = self.controller.winfo_pointerxy()
        widget = self.controller.winfo_containing(x, y)
        if widget.winfo_name().find("input") < 0:
            self.focus_set()
