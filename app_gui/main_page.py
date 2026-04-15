import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showerror, showwarning, showinfo
from pathlib import Path
import threading
import queue

from services.llm_analyzer import LLMAnalyzer


class StartPage(tk.Frame):
    """
   the initial start page where the user browses a pubmed file with annotations
   User selects the names for log file
   If the user continues with previous analysis session which has not completed
   the user can select a log file and continue the previous session
   user selects a path to save the results
    """
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.MODEL_NAME = 'deepseek-r1:8b'
        self.progress_queue = queue.Queue()
        self.stop_event = threading.Event()

        tk.Label(
            self,
            text="PubMed Annotation: LLM-powered analysis",
            font=("Arial", 18)
        ).pack(pady=20)

        tk.Label(self, text='Select your PubMed File').pack()

        ttk.Button(
            self,
            text="Browse .nbib file",
            command=self.browse_pubmed_file
        ).pack()

        tk.Label(
            self,
            textvariable=controller.selected_pubmed_file,
            wraplength=600
        ).pack(pady=10)

        # setting filename for results file
        tk.Label(self, text='Set the name of results file withou extention (.csv)').pack() # add the safe check for extention later
        self.result_file= tk.Entry(self, width=50)
        self.result_file.pack(pady=5)

        tk.Label(self, text=f"Your results and logs will be saved at data folder").pack()

        # setting the prompt for search among 
        tk.Label(self, text='Input your search prompt').pack()
        self.search_prompt = tk.Text(self)
        self.search_prompt.pack()

        model_label = tk.Label(self, text=f"{self.MODEL_NAME} is used for the analysis")
        model_label.pack()

        ttk.Button(
             self,
             text="Start",
             command=self.start_analysis
         ).pack(pady=15)
        

        self.progress_label = tk.Label(self, text = "Progress")
        self.progress_label.pack()

        ttk.Button(
                self,
                text="Stop",
                command=self._stop_analysis
                ).pack()


    def browse_pubmed_file(self):
        "browses predownloaded file"
        path = filedialog.askopenfilename(
            title="Select .csv file",
            filetypes=(("CSV files", "*.nbib"), ("All files", "*.*"))
        )

        if path:
            self.controller.selected_pubmed_file.set(path)


    def start_analysis(self):
        pubmed_file = self.controller.selected_pubmed_file.get().strip()
        if not pubmed_file:
            showerror("Missing file", "Select a PubMed .nbib file first.")
            return
        
        self.pubmed_path = Path(pubmed_file)
        if not self.pubmed_path.exists():
            showerror("Missing file", "The selected PubMed file does not exist.")
            return
        
        
        results_name_without_extention = self.result_file.get()
        result_name = results_name_without_extention
        print(f"res_name: {results_name_without_extention}")
        if not result_name:
            showerror("Missing result name", "Enter a valid name for the result file.")
            return
        
        self.user_prompt = self.search_prompt.get("1.0", "end").strip()
        if not self.user_prompt:
            showerror("Missing prompt", "Enter the search prompt for the analysis.")
            return
        
        base_dir = Path('data')
        self.results_filename = base_dir / f"{result_name}.csv"
        print(self.results_filename)
        
        self.log_filename = base_dir / f"{result_name}_log.txt"
        print(self.log_filename)

        self.analysis_thread = threading.Thread(
                target=self._run_analysis,
            )
        self.analysis_thread.start()

        self._update_progress() 

    def _run_analysis(self):
        analyzer = LLMAnalyzer(self.MODEL_NAME, 
                               self.pubmed_path, 
                               self.log_filename, 
                               self.results_filename, 
                               self.user_prompt, 
                               self.progress_queue,
                               self.stop_event)
        analyzer.process_pubmed_df()

    def _update_progress(self):
        try:
            while True:
                progress_stage = self.progress_queue.get_nowait()
                self.progress_label.config(text=f"Processed: {progress_stage}")
        except:
            pass
        self.after(1000, self._update_progress)

    def _stop_analysis(self):
        self.stop_event.set()
        self.progress_label.config(text="Stopping...")