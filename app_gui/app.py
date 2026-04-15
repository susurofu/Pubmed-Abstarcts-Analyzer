import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showerror, showwarning, showinfo

from app_gui.main_page import StartPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PubMed Annotations: Search Wiser")

        #addjusts to occupy 80% of user's screen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        window_w = int(screen_w * 0.8)
        window_h = int(screen_h * 0.8)
        x = (screen_w - window_w) // 2
        y = (screen_h - window_h) // 2
        self.geometry(f"{window_w}x{window_h}+{x}+{y}")

        self.selected_pubmed_file = tk.StringVar(value="") # saves the file with pubmed annotations
        self.annotation_dataset_file = tk.StringVar(value="") # the file with annotations
        self.log_file = tk.StringVar(value="") # log file to continue work after the program finished
        #self.download_status = tk.StringVar(value="") 

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for Page in [StartPage]:
            frame = Page(container, self)
            self.frames[Page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()