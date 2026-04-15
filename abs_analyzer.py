####################################
# this applications works with pubmed annotation docs
# and using local llm prepares the review which articles 
# fit the research topic by prompt
####################################

import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showerror, showwarning, showinfo
from pathlib import Path

from app_gui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()