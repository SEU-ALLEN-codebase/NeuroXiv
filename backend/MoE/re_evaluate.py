import os
import dashscope
import csv
from mistralai.client import MistralClient
from zhipuai import ZhipuAI
from nltk.tokenize import word_tokenize

import re
import json
import requests
import spacy
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import openai

# 加载T5模型和分词器
model_name = "t5-small"
semantic_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 加载spaCy模型
nlp = spacy.load('en_core_web_sm')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

# 设置API密钥
openai.api_key = ''
qwen_api_key = ""
dashscope.api_key = qwen_api_key
mistral_api_key = ""
zhipu_api_key = ''

# 初始化Qwen和Mistral客户端
mistral_client = MistralClient(api_key=mistral_api_key)
zhipu_client = ZhipuAI(api_key=zhipu_api_key)


def count_tokens(text):
    tokens = word_tokenize(text)
    return len(tokens)


def save_to_file(content, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(content)


def save_scores_to_csv(scores, model, time, type, filename):
    """
    Save the scores dictionary along with model, time, and type to a CSV file.

    Args:
    scores (dict): The dictionary containing scores to be saved.
    model (str): The model used.
    time (str): The time of evaluation.
    type (str): The type of summary or evaluation.
    filename (str): The name of the CSV file to save the scores.
    """
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)

        # If file doesn't exist or is empty, write the header
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writerow(
                ['Model', 'Time', 'Type', 'data_accuracy', 'logic_accuracy', 'new_conclusions', 'token_count',
                 "raw_token_count"])
        # Write the row of data
        writer.writerow([
            model,
            time,
            type,
            scores.get('data_accuracy'),
            scores.get('logic_accuracy'),
            scores.get('new_conclusions'),
            scores.get('token_count'),
            scores.get('raw_token_count'),
        ])


def extract_timestamp_from_filename(filename):
    pattern = r'(\d{8}_\d{6})'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    else:
        return None


def evaluate_summary(time, model, info_type, summary, origin, logs):
    accuracy_score, logic_accuracy, new_conclusions = check_data_accuracy(time, model, info_type, origin, summary, logs)
    token_count = count_tokens(summary)
    raw_token_count = count_tokens(origin)
    print("data_accuracy " + str(accuracy_score) + "\nlogic_accuracy: " + str(
        logic_accuracy) + "\nnew_conclusions:" + str(new_conclusions) + "\ntoken_count:" + str(
        token_count) + "\nraw_token_count:" + str(raw_token_count))
    scores = {
        "data_accuracy": accuracy_score,
        "logic_accuracy": logic_accuracy,
        "new_conclusions": new_conclusions,
        "token_count": token_count,
        "raw_token_count": raw_token_count
    }
    return scores


def extract_summaries_from_log(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define regex pattern for extracting blocks
    blocks_pattern = re.compile(r'(\[ORIGINAL TEXT\].*?)(?=\[ORIGINAL TEXT\]|\Z)', re.DOTALL)

    # Extract all blocks
    blocks = re.findall(blocks_pattern, content)

    all_data = []

    info_types = ['basic_info', 'morpho_info', 'proj_info']

    for i, block in enumerate(blocks):
        # Determine the info type based on the block index
        info_type = info_types[i % len(info_types)]

        # Extract original text
        original_text_match = re.search(r'\[ORIGINAL TEXT\]\n(.*?)(?=\[MODEL: Qwen\])', block, re.DOTALL)
        original_text = original_text_match.group(1).strip() if original_text_match else None

        # Initialize summaries dictionary
        summaries = {
            'Qwen': {'basic_info': '', 'morpho_info': '', 'proj_info': ''},
            'Mistral': {'basic_info': '', 'morpho_info': '', 'proj_info': ''},
            'Zhipu': {'basic_info': '', 'morpho_info': '', 'proj_info': ''},
            'GPT4o': {'basic_info': '', 'morpho_info': '', 'proj_info': ''},
            'MoE': {'basic_info': '', 'morpho_info': '', 'proj_info': ''}
        }

        # Extract and assign summaries for each model
        models = ['Qwen', 'Mistral', 'Zhipu', 'GPT4o', 'MoE']
        for model in models:
            model_pattern = re.compile(r'\[MODEL: {}\]\n(.*?)(?=\[MODEL: |\[ORIGINAL TEXT\]|\Z)'.format(model),
                                       re.DOTALL)
            model_summary_match = model_pattern.search(block)
            if model_summary_match:
                summaries_content = model_summary_match.group(1).strip()
                summaries_content = re.sub(r'\n\s*\n', '\n', summaries_content)  # Remove empty lines
                summaries[model][info_type] = summaries_content

        all_data.append((original_text, summaries, info_type))

    return all_data


def extract_numbers_with_context(text):
    """
    使用spaCy提取文本中的数字及其上下文
    """
    doc = nlp(text)
    numbers_with_context = []
    for token in doc:
        if token.like_num:
            start = max(0, token.i - 3)
            end = min(len(doc), token.i + 4)
            context = doc[start:end].text
            numbers_with_context.append((token.text, context))
    return numbers_with_context


def extract_sentences(text):
    """
    提取文本中的句子，去掉换行符和空行后再分割
    """
    # 去掉换行符和多余的空白
    text = re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\r', ' '))

    # 特殊处理 "vs."，避免在其处分割
    text = re.sub(r'\s+vs\.\s+', ' vs. ', text)

    # 正则表达式优化版：(?<!\d)\.(?!\d)(?=\s|$) 用于排除小数点，并且忽略 "vs."
    sentences = re.split(r'(?<!vs)(?<!\d)\.(?!\d)(?=\s|$)|(?<!\d)\?(?!\d)(?=\s|$)', text)

    # 去掉空字符串
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    return sentences


def check_data_calculation(origin, sentence):
    """
    使用LLM模型检查推理是否合理
    """
    evaluation_summary = ""

    prompt = f"Can the following calculated statement be inferred from the text? Return yes if it can, else return no." \
             f"Make sure to verify the numerical calculation is accurate.\n" \
             f"Text: {origin}\nStatement: {sentence} "

    url = "http://localhost:11434/api/chat"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "llama3.1",
        "messages": [{"role": "user", "content": prompt}],
        "options": {
            "num_ctx": 4096,  # Increase the input token limit
            "num_predict": 2048  # Increase the output token limit
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    try:
        for line in response.iter_lines():
            if line:
                decoded_line = json.loads(line.decode('utf-8'))
                if 'message' in decoded_line and 'content' in decoded_line['message']:
                    evaluation_summary += decoded_line['message']['content']
        if "yes" in evaluation_summary.lower():
            pass
        else:
            print(evaluation_summary)
        return "yes" in evaluation_summary.lower()
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.content)
        return False


def check_sentence_logic(origin, sentence):
    """
    使用LLM模型检查推理是否合理
    """
    evaluation_summary = ""

    prompt = f"Determine whether the provided sentence can be logically and numerically inferred from the given text. " \
             f"Return 'yes' if the inference is accurate and supported by the text, including correct numerical " \
             f"calculations; otherwise, return 'no'. Ensure careful examination of both sentence logic and numerical " \
             f"data.Make sure to verify the numerical calculation and the sentence logic are accurate.\n" \
             f"Text: {origin}\nStatement: {sentence} "

    url = "http://localhost:11434/api/chat"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "llama3.1",
        "messages": [{"role": "user", "content": prompt}],
        "options": {
            "num_ctx": 4096,  # Increase the input token limit
            "num_predict": 2048  # Increase the output token limit
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    try:
        for line in response.iter_lines():
            if line:
                decoded_line = json.loads(line.decode('utf-8'))
                if 'message' in decoded_line and 'content' in decoded_line['message']:
                    evaluation_summary += decoded_line['message']['content']
        if "yes" in evaluation_summary.lower():
            pass
        else:
            print(evaluation_summary)
        return "yes" in evaluation_summary.lower()
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.content)
        return False


def check_new_conclusions(origin, sentence):
    """
    使用LLM模型检查推理是否合理
    """
    evaluation_summary = ""

    prompt = f"Determine whether the provided sentence represents a new conclusion logically and numerically derived from the given text. " \
             f"Return 'yes' if the inference introduces new data or results based on the text, including correct numerical " \
             f"calculations; otherwise, return 'no'. Ensure careful examination of both sentence logic and numerical " \
             f"data. Make sure that the new conclusion is not just a rephrasing or restatement of the original text, but " \
             f"introduces new insights or results derived from the original content.\n" \
             f"Text: {origin}\nStatement: {sentence} "

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
    )
    evaluation_summary = response.choices[0].message.content
    return "yes" in evaluation_summary.lower()


def check_data_accuracy(time, model, info_type, origin, summary, logs):
    """
    检查总结的准确性，包括数字的匹配和可能的推理
    """
    numbers_origin = extract_numbers_with_context(origin)
    numbers_summary = extract_numbers_with_context(summary)

    matched_numbers = set()
    unmatched_numbers = set(numbers_summary)

    for num_s, context_s in numbers_summary:
        for num_o, context_o in numbers_origin:
            if num_s == num_o and context_s in context_o:
                matched_numbers.add((num_s, context_s))
                unmatched_numbers.discard((num_s, context_s))
                break

    summary_sentences = extract_sentences(summary)

    for num, context in unmatched_numbers:
        for sentence in summary_sentences:
            if num in sentence:
                if check_data_calculation(origin, sentence):
                    matched_numbers.add((num, context))
                else:
                    log_info = model + "_" + info_type + "_" + "data_accuracy_error:\n" + sentence + "\n"
                    log_info += "error number: " + str(num) + "\n\n"
                    save_to_file(log_info, logs)
                    print('calculation: ' + sentence)
    correct_sentence = 0
    for sentence in summary_sentences:
        if check_sentence_logic(origin, sentence):
            correct_sentence += 1
        else:
            log_info = model + "_" + info_type + "_" + "logic_accuracy_error:\n" + sentence + "\n\n"
            save_to_file(log_info, logs)
            print('logic: ' + sentence)
    new_conclusions = 0
    for sentence in summary_sentences:
        if check_new_conclusions(origin, sentence):
            n_c = model + "_" + info_type + "_" + "new conclusions" + str(new_conclusions) + ": \n" + sentence + "\n\n"
            save_to_file(n_c, logs)
            new_conclusions += 1
    data_accuracy = len(matched_numbers) / len(numbers_summary) if numbers_summary else 0
    logic_accuracy = correct_sentence / len(summary_sentences) if summary_sentences else 0
    return data_accuracy, logic_accuracy, new_conclusions


def pipeline():
    directory = r"D:\NeuroXiv\api\MoE\log_0726_batch\eva"
    csv_file = r"D:\NeuroXiv\api\MoE\log_0726_batch\eva\re_eva.csv"
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            log_file = os.path.join(directory, filename)
            # log_file = r"D:\NeuroXiv\api\MoE\log_0726_batch\test3\MoE_20240801_005200.txt"
            all_data = extract_summaries_from_log(log_file)
            results = []
            time = extract_timestamp_from_filename(log_file)
            log_name = "error_conclusions_" + time + ".txt"
            logs = "D:/NeuroXiv/api/MoE/error_and_conclusion/" + log_name
            file_name = "MoE_" + time + ".txt\n"
            save_to_file(file_name, logs)
            for i, (original_text, summaries, info_type) in enumerate(all_data):
                origintext = info_type + " origin text:\n" + original_text + '\n\n'
                save_to_file(origintext, logs)
                for model, summary_types in summaries.items():
                    summary = summary_types[info_type]
                    scores = evaluate_summary(time, model, info_type, summary, original_text, logs)
                    save_scores_to_csv(scores,model,time,info_type,csv_file)
                    # results.append([
                    #     model, time, info_type,
                    #     scores.get('data_accuracy'),
                    #     scores.get('logic_accuracy'),
                    #     scores.get('new_conclusions'),
                    #     scores.get('token_count'),
                    #     scores.get('raw_token_count'),
                    # ])
            print(results)


if __name__ == '__main__':
    pipeline()
