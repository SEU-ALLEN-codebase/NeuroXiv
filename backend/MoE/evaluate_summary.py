import csv
import json
import os
import re

import requests


def summarize_text(origin_input):
    evaluation_summary = ""

    prompt = f"Evaluate the original input provided based on the following criteria, " \
             f"Provide a score for each criterion on " \
             f"a scale of 1 to 5, with 1 being the lowest and 5 being the highest. " \
             f"origin text: {origin_input}\n\n" \
             f"Additionally, explain the reasons for any score deductions and provide the reasoning process:\n\n" \
             f"1. Consistency: Is the narrative and structure in the summaries and conclusions consistent?\n" \
             f"   - Score: 1 (Poor consistency, confusing structure)\n" \
             f"   - Score: 2 (Some consistency, several inconsistencies)\n" \
             f"   - Score: 3 (Moderate consistency, minor inconsistencies)\n" \
             f"   - Score: 4 (High consistency, very few inconsistencies)\n" \
             f"   - Score: 5 (Excellent consistency, no inconsistencies)\n" \
             f"   - Explanation:\n\n" \
             f"2. Readability: Is the information presented clearly and concisely, making it easy to understand?\n" \
             f"   - Score: 1 (Poor readability, very difficult to understand)\n" \
             f"   - Score: 2 (Some readability, somewhat confusing)\n" \
             f"   - Score: 3 (Moderate readability, fairly clear)\n" \
             f"   - Score: 4 (High readability, very clear)\n" \
             f"   - Score: 5 (Excellent readability, extremely clear)\n" \
             f"   - Explanation:\n\n" \
             f"3. Conciseness: Are the summaries and conclusions brief and to the point?\n" \
             f"   - Score: 1 (Poor conciseness, excessively long)\n" \
             f"   - Score: 2 (Some conciseness, somewhat lengthy)\n" \
             f"   - Score: 3 (Moderate conciseness, fairly concise)\n" \
             f"   - Score: 4 (High conciseness, very concise)\n" \
             f"   - Score: 5 (Excellent conciseness, extremely concise)\n" \
             f"   - Explanation:\n\n" \
             "Finally, you must output the scores in a dictionary format in the following format: scores = {" \
             "'Consistency': None,'Readability': None,'Conciseness': None} "

    url = "http://localhost:11434/api/chat"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "llama3.1",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    try:
        for line in response.iter_lines():
            if line:
                decoded_line = json.loads(line.decode('utf-8'))
                if 'message' in decoded_line and 'content' in decoded_line['message']:
                    evaluation_summary += decoded_line['message']['content']
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.content)
        return "Error in summarizing text"

    scores = extract_scores(evaluation_summary)
    if scores is None:
        print("No scores found in the evaluation summary. Using default scores.")
        scores = {
            'Consistency': 0,
            'Readability': 0,
            'Conciseness': 0,
        }
    print("scores:")
    print(scores)
    return scores


def extract_scores(text):
    pattern = r"scores\s*=\s*\{([^}]*)\}"
    match = re.search(pattern, text)
    if match:
        scores_str = "{" + match.group(1) + "}"
        try:
            scores_dict = eval(scores_str)
            return scores_dict
        except Exception as e:
            print("Error evaluating scores string:", e)
            return None
    return None


def save_scores_to_csv(scores, inital_file, time, summary_type, filename):
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists or os.stat(filename).st_size == 0:
            writer.writerow(['Time', 'Type', 'Consistency', 'Readability', 'Conciseness'])

        writer.writerow([
            inital_file,
            time,
            summary_type,
            scores.get('Consistency'),
            scores.get('Readability'),
            scores.get('Conciseness')
        ])


def extract_timestamp_from_filename(filename):
    pattern = r'(\d{8}_\d{6})'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    return None


def extract_info(text):
    patterns = {
        'basic info': re.compile(r'basic info:\s*(.*?)\s*Qwen summary:', re.DOTALL),
        'morpho info': re.compile(r'morpho info:\s*(.*?)\s*Qwen summary:', re.DOTALL),
        'proj info': re.compile(r'proj info:\s*(.*?)\s*Qwen summary:', re.DOTALL)
    }

    extracted_info = {}
    for key, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            extracted_text = match.group(1).strip()
            extracted_info[key] = "\n".join([line for line in extracted_text.splitlines() if line.strip() != ''])
    return extracted_info


def process_files_in_folder(folder_path, csv_filename):
    extracted_data = {}

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                info = extract_info(text)
                extracted_data[filename] = info

                timestamp = extract_timestamp_from_filename(filename)

                for summary_type, summary_text in info.items():
                    print(summary_type + ": \n" + summary_text)
                    scores = summarize_text(summary_text)
                    save_scores_to_csv(scores, filename, timestamp, summary_type, csv_filename)

    return extracted_data


if __name__ == '__main__':
    folder_path = r'D:\NeuroXiv\api\MoE\log_0726_batch\test2'
    csv_file = r'D:\NeuroXiv\api\MoE\log_0726_batch\origin_input_evaluation.csv'
    all_extracted_info = process_files_in_folder(folder_path, csv_file)
