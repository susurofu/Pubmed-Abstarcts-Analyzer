# PubMed Annotations: Read Wiser with LLM

## What is this app?

PubMed Annotations: Search Wiser is a desktop application that helps researchers quickly filter and evaluate large numbers of PubMed abstracts using a local LLM (Large Language Model).
You provide a PubMed export file (.nbib) and a custom search prompt describing your research topic. The app uses Ollama to analyze each article’s title and abstract, then rates its relevance on a scale:

3 — Strong match

2 — Intermediate match

1 — Slight match

-1 — Mismatch


For every article, the app also saves a short explanation from the model. Results are saved as a .csv file, and the app supports resuming interrupted sessions.

## Requirements
- Python 3.8 or higher installed on your system
- Ollama installed and running
- Sufficient RAM (at least 16 GB recommended for the 8B model; more is better)

## Installation 
1. Download the application folder (or clone the repository).
2. Open a terminal / command prompt and navigate to the project folder.
3. Install the required dependencies:
~~~
pip install -r requirements.txt
~~~

## Running the Application
1. Make sure Ollama is running in the background.
2. Pull the required model (the app currently uses deepseek-r1:8b):
~~~
ollama pull deepseek-r1:8b
~~~

You can also run it once with ollama run deepseek-r1:8b to verify it works.

Navigate to the app folder in your terminal and start the app:
~~~
python abs_analyzer.py
~~~

## How to Use the App
1. Select your PubMed file
Click “Browse .nbib file” and choose your exported .nbib file from PubMed.
2. Set the results filename
Enter a name without the .csv extension (e.g. teenagers_diet_emotional_wellbeing).
All results and logs will be saved in the data/ folder.
3. Write your search prompt
Describe what you are looking for in detail. 

Example:

This article should be about how diet influences teenagers' emotional well-being. The article should focus on teenagers in Europe but also include or compare findings from Asia, Africa, and Latin America.

4. Click Start to begin analysis.
Progress is shown at the bottom. Processing time depends on your hardware and the number of articles.

## Important Features & Tips
1. Resuming a previous session
If you stop the analysis, you can continue later. Just use the exact same filename (without .csv) as before. The app will automatically skip already processed articles using the _log.txt file.
2. Stopping the analysis
Always click the Stop button first. The app will finish the current article and then stop the LLM thread safely.Only after pressing Stop should you close the window.If you close the window without pressing Stop, the background LLM process may continue running — in that case, stop the Python script in the terminal with Ctrl + C.
3. Customizing the system prompt
The file services/system_prompt.txt contains the instructions given to the LLM. You can edit this file to better suit your needs, but do not remove or modify:

The placeholder USER_PROMPT

The part that instructs the model to output JSON with relevance and explanation fields

4. Output
A .csv file is created/updated in the data/ folder with columns including:
PMID, ArticleTitle, Abstract, Date, Authors, Relevance (3/2/1/-1), and Explanation.

## Notes
1. Inference speed depends heavily on your hardware (CPU/GPU) and model size. The deepseek-r1:8b model is relatively fast but still takes time on large datasets.
2. This is the minimum working release. Further, I will refine the design and performance.
