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

openai.api_key = ''


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


def check_data_accuracy(origin, summary):
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
                    print('calculation: ' + sentence)
    correct_sentence = 0
    correct_sentence = len(summary_sentences)
    # for sentence in summary_sentences:
    #     if check_sentence_logic(origin, sentence):
    #         correct_sentence += 1
    #     else:
    #         print('logic: ' + sentence)
    new_conclusions = 0
    for sentence in summary_sentences:
        if check_new_conclusions(origin, sentence):
            new_conclusions += 1
    data_accuracy = len(matched_numbers) / len(numbers_summary) if numbers_summary else 0
    logic_accuracy = correct_sentence / len(summary_sentences) if summary_sentences else 0
    print(len(summary_sentences))
    return data_accuracy, logic_accuracy, new_conclusions


# # 示例文本
# origin_text = """The queried data comprises 150 neurons extracted from 3 datasets: ION (131 neurons), MouseLight (10
# neurons) and SEU-ALLEN (9 neurons). This selection encompasses neuron structures, including axons (150),
# basal dendrites (68), apical dendrites (4), and local dendrites (0). The queried data locates in left hemisphere (49)
# and right hemisphere (101). The queried data is distributed across 22 brain regions, detailed as follows:  CA1 (36
# neurons), DG (26 neurons), SUB (13 neurons), ProS (10 neurons), PL (9 neurons), ORBvl (8 neurons), ACAv (7 neurons),
# AId (7 neurons), MOs (7 neurons), CA3 (7 neurons), ACAd (4 neurons), ORBl (3 neurons), VPM (2 neurons),
# POST (2 neurons), ORBm (2 neurons), AIv (1 neurons), AUDp (1 neurons), RSPagl (1 neurons), TRN (1 neurons),
# MOp (1 neurons), PRE (1 neurons), and AON (1 neurons). Specifically, there are 50 neurons in cortical layers,
# including  L5 (25 neurons), L2/3 (16 neurons), L6a (6 neurons), and L1 (3 neurons). """
#
# summary_text = """The dataset comprises 150 neurons collected from three sources: ION (131), MouseLight (10),
# and SEU-ALLEN (9). These neurons include 150 axons, 68 basal dendrites, and 4 apical dendrites, with no local
# dendrites, and are distributed across 22 brain regions. The majority are located in the right hemisphere (101)
# compared to the left (49), with significant counts in regions such as CA1 (36 neurons) and DG (26 neurons).
# Additionally, 50 neurons reside in cortical layers, mainly in L5 (25) and L2/3 (16). """
#
# # 计算数据准确性
# accuracy_score, logic_accuracy, new_conclusions = check_data_accuracy(origin_text, summary_text)
# print("Data Accuracy Score:", accuracy_score)
# print("Logic Accuracy Score:", logic_accuracy)
# print("new conclusions:", new_conclusions)
