############################
#helper functions#
############################

import re
import json

import pandas as pd


def parse_pubmed_file(file_path):
    records = []
    current_record = {}
    current_field = None

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            if not line:
                if current_record:
                    records.append(current_record)
                    current_record = {}
                continue

            if line[:4].strip():  # e.g. "TI  -"
                tag = line[:4].strip()
                value = line[6:].strip()

                if tag in current_record:
                    if isinstance(current_record[tag], list):
                        current_record[tag].append(value)
                    else:
                        current_record[tag] = [current_record[tag], value]
                else:
                    current_record[tag] = value

                current_field = tag

            else:
                if current_field:
                    current_record[current_field] += " " + line.strip()

    if current_record:
        records.append(current_record)

    cleaned = []
    for r in records:
        cleaned.append({
            "pmid": r.get("PMID"),
            "title": r.get("TI"),
            "abstract": r.get("AB"),
            "date": r.get("DP"),
            "authors": "; ".join(r["AU"]) if isinstance(r.get("AU"), list) else r.get("AU"),
            "LID": r.get("LID")
        })

    return pd.DataFrame(cleaned)




def parse_json(input_text:str):
    "parses json object or array from LLM output"
    match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', input_text)
    if not match:
        return None    
    try:
        return json.loads(match.group(0))
    except Exception:
        return None



