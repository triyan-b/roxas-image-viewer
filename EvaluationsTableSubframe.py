from tkinter import *
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from Application import Application
from RoxasImageViewerFrame import RoxasImageViewerFrame


class EvaluationsTableSubframe(Frame):
    def __init__(self, controller: Application, parent: RoxasImageViewerFrame):
        super().__init__()

        from SampleViewerSubframe import SampleViewerSubframe

        self.controller = controller
        self.parent = parent
        
        # State
        self.evals = self.parent.state.get("evaluations")

        # General
        self.controller.title("All Evaluations")
        self.controller.grid()
        self.focus_set()
        
        # Geometry
        self.w = int(0.95 * self.controller.winfo_screenwidth())
        self.h = int(0.9 * self.controller.winfo_screenheight())
        self.x = 5
        self.y = 5
        self.grid_columnconfigure(tuple(range(3)), weight = 1)
        self.grid(row=0, column=0, sticky='nsew')

        # Events
        self.bind("<Alt-Left>", lambda e: self.parent.show_subframe(SampleViewerSubframe))

        # UI Components
        self.ui_back_to_samples_button = Button(self, text=" ◀ Sample viewer", command=lambda: self.parent.show_subframe(SampleViewerSubframe))
        self.ui_back_to_samples_button.grid(row = 0, column = 0, sticky='nw', pady=10)

        ## Evaluations table
        headers, rows = self.get_evaluations_table()
        self.eval_table_frame = Frame(self)
        self.eval_table_frame.grid(row=1, column=0, columnspan=3, sticky='n')

        ### Table header
        self.evals_table_headers_text = Label(self.eval_table_frame, text=headers if headers else 'No evaluations in this session', font=("MS Gothic", 10) if headers else ("Segoe UI", 9), borderwidth=(1 if headers else 0), relief="solid")
        self.evals_table_headers_text.grid(row=0, column=0, sticky='sw')

        ### Table rows
        if rows:
            self.evals_table_rows_text = ScrolledText(self.eval_table_frame, width=len(headers), height=min(rows.count("\n") + 1, 20), font=("MS Gothic", 10), borderwidth=(1 if rows else 0), relief="solid", bg='SystemButtonFace')
            self.evals_table_rows_text.insert(END, rows)
            self.evals_table_rows_text.configure(state=DISABLED)
            self.evals_table_rows_text.grid(row=1, column=0, sticky='nw')
        
    
    def get_evaluations_table(self):
        df = pd.DataFrame.from_dict(self.evals, orient='index').reset_index()
        if len(df) > 0:
            df = df.rename(columns={
                df.columns[0]: "Site",
                df.columns[1]: "Tree",
                df.columns[2]: "Sample",
                df.columns[3]: "Subsample",
                df.columns[4]: "Year"
            })
            return tuple(str(df).split("\n", 1))
        else:
            return '', ''