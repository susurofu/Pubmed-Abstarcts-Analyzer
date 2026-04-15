from pathlib import Path
import json
import re
import csv

import pandas as pd
import ollama
from tqdm import tqdm

from services.helpers import parse_pubmed_file, parse_json

class LLMAnalyzer:
    """
    implements the analysis

    model_name: the selected LLM model for use
    pubmed_file: path to Pubmed file
    log_file: path in pathlib.Path() to txt log file
    results_file: path in pathlib.Path() to results files (.csv)
    user_prompt: prompt for user
    """

    def __init__(self, model_name, pubmed_file, log_file, results_file, user_prompt, download_status_queue, stop_event):
        self.model_name = model_name
        self.pubmed_file = pubmed_file
        self.log_file = log_file
        self.results_file = results_file
        self.user_prompt = user_prompt
        self.download_status_queue = download_status_queue # the queque in which the initial step is storaged
        self.stop_event = stop_event

        # gets base system prompt from txt. User can modify this sustem prompt 
        with open('services/system_prompt.txt', encoding='utf-8') as f:
             self.system_prompt = f.read()


    def _process_annotation(self, article_title, anno_text):
        """
        runs local llm for one annotation.
        """

        full_prompt = self.system_prompt.replace('USER_PROMPT', self.user_prompt)
        full_prompt = f"{full_prompt}\nHere is article title: {article_title}.\nHere is the abstract: {anno_text}"

        resp = ollama.chat(
            model=self.model_name,
            keep_alive=300,
            messages=[{
                "role": "user",
                "content": full_prompt
            }]
        )

        json_data = parse_json(resp["message"]["content"])
        #print(resp["message"]["content"])
        return json_data
    
    def process_pubmed_df(self):

        pubmed_df = parse_pubmed_file(Path(self.pubmed_file))

        log_file_path = Path(self.log_file)
        if log_file_path.exists():
            with open(log_file_path,'r',encoding='utf-8') as f:
                processed_annos = f.read().split('\n')
            # here add the check for corrupted log file

        else:
            with open(log_file_path,'w',encoding='utf-8') as f:
                f.write('')
            processed_annos = []

        results_file_path = Path(self.results_file)
        if not results_file_path.exists():
            with open(results_file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["PMID", "ArticleTitle", "Abstract", "Date", "Authors", "LID", "Relevance", "Explanation"]) # check pubmed metadata


        number_of_annos = len(pubmed_df)
        processed_annos_number = 0
        self.download_status_queue.put(f"Processed {processed_annos_number} / {number_of_annos}") # initial status

        for i, anno_idx in tqdm(enumerate(pubmed_df['pmid'])): 
            if self.stop_event.is_set():
                self.download_status_queue.put("Stopped")
                break
            if str(anno_idx) in processed_annos:
                processed_annos_number += 1
                self.download_status_queue.put(f"Processed {processed_annos_number} / {number_of_annos}")
                continue

            res_json = self._process_annotation(pubmed_df.iloc[i]['title'], pubmed_df.iloc[i]['abstract'])
            res_df = pd.DataFrame(res_json)

            if res_df is None or res_df.empty:
                # still mark as processed
                with open(log_file_path, "a", encoding="utf-8") as f:
                    f.write(str(anno_idx) + "\n")

                processed_annos_number += 1
                self.download_status_queue.put(f"Processed {processed_annos_number} / {number_of_annos}")
                continue

            # appends new res to .csv
            with open(results_file_path, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                        pubmed_df['pmid'].iloc[i],
                        pubmed_df['title'].iloc[i],
                        pubmed_df['abstract'].iloc[i],
                        pubmed_df['date'].iloc[i],
                        pubmed_df['authors'].iloc[i],
                        pubmed_df['LID'].iloc[i],
                        res_df["relevance"][0],
                        res_df['explanation'][0]
                ])

            # logging
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write(str(anno_idx) + "\n")

            processed_annos_number += 1
            self.download_status_queue.put(f"Processed {processed_annos_number} / {number_of_annos}") # put the progress to the queue for UI