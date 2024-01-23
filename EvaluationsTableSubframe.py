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
        self.eval_table_frame = Frame(self)
        self.eval_table_frame.grid(row=1, column=0, columnspan=3, sticky='n')

        self.evals_table_headers_text = Label(self.eval_table_frame, relief="solid")
        self.evals_table_headers_text.grid(row=0, column=0, sticky='sw')
        self.evals_table_rows_text = ScrolledText(self.eval_table_frame, font=("Consolas", 10), borderwidth=1, relief="solid", bg='SystemButtonFace')
        
        
        ### Compact/Expanded mode toggle
        self.compact_table_view = True
        self.table_view_toggle = Checkbutton(self.eval_table_frame, text="Grouped view", command=self.on_toggle_table_view)
        if self.compact_table_view:
            self.table_view_toggle.select()
        
        self.show_evaluations_table()
    
    def on_toggle_table_view(self):
        self.compact_table_view = not self.compact_table_view
        self.show_evaluations_table()

    def show_evaluations_table(self):
        headers, rows = self.get_evaluations_table()
        if headers:
            self.evals_table_headers_text.configure(text=headers, font=("Consolas", 10), borderwidth=1)
        else:
            self.evals_table_headers_text.configure(text='No evaluations in this session', font=("Segoe UI", 9), borderwidth=0)
        self.evals_table_headers_text.grid(row=0, column=0, sticky='sw')
        if rows:
            self.evals_table_rows_text.configure(width=len(headers), height=min(rows.count("\n") + 1, 50))
            self.evals_table_rows_text.delete('1.0', END)
            self.evals_table_rows_text.insert(END, rows)
            self.evals_table_rows_text.grid(row=1, column=0, sticky='nw')
            self.table_view_toggle.grid(row=2, column=0)
        else:
            self.evals_table_rows_text.grid_forget()
            self.table_view_toggle.grid_forget()
        
    
    def get_evaluations_table(self):
        df = pd.DataFrame.from_dict(self.evals, orient='index').reset_index()
        if len(df) > 0:
            df = df.rename(columns={
                df.columns[0]: "site",
                df.columns[1]: "tree",
                df.columns[2]: "sample",
                df.columns[3]: "subsample",
                df.columns[4]: "year"
            })
            if self.compact_table_view:
                df = df.drop("comment", axis=1)
                df = df.apply(lambda row: pd.Series(pd.concat([row.iloc[:5], pd.Series([row[row == value].index.tolist() for value in ["EW", "LW", "All"]])])), axis=1)
                df = df.rename(columns={df.columns[i]: name for i, name in enumerate(["EW", "LW", "All"], start = 5)})
            else:
                df.columns = [f"{col[:5].strip()}…" if len(col) > 5 else col for col in df.columns] 
            
            return tuple(df.to_string(index=False, justify="left").split("\n", 1))
        else:
            return '', ''