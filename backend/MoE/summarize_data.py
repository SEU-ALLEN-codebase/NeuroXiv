import os
from datetime import datetime
import openai
import time
import dashscope
import csv

from dataset_db import neurons, get_summary_info
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage
from zhipuai import ZhipuAI
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk
from nltk.tokenize import word_tokenize
from extract_data import initalInput
import re
from evaluation import evaluate_data_accuracy as eva

neuron_class = neurons('/data')

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
                ['Model', 'Time', 'Type', 'data_accuracy', 'logic_accuracy', 'new_conclusions', 'token_count', "raw_token_count"])
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


def save_to_file(content, filename):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(content)


def extract_timestamp_from_filename(filename):
    """
    Extract the timestamp from the given filename.

    Args:
    filename (str): The filename containing the timestamp.

    Returns:
    str: The extracted timestamp.
    """
    # Define the regular expression pattern to match the timestamp
    pattern = r'(\d{8}_\d{6})'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    else:
        return None


def evaluate_summary(summary,origin):
    accuracy_score, logic_accuracy, new_conclusions = eva.check_data_accuracy(origin, summary)
    token_count = count_tokens(summary)
    raw_token_count = count_tokens(origin)
    print("data_accuracy " + str(accuracy_score) + "\nlogic_accuracy: " + str(
        logic_accuracy) + "\nnew_conclusions:" + str(new_conclusions) + "\ntoken_count:" + str(token_count) + "\nraw_token_count:" + str(raw_token_count))
    scores = {
        "data_accuracy": accuracy_score,
        "logic_accuracy": logic_accuracy,
        "new_conclusions": new_conclusions,
        "token_count": token_count,
        "raw_token_count": raw_token_count
    }
    return scores


def generate_data_with_models(prompt, model_name):
    # Define system and user messages
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': str(prompt)}]

    if model_name == "Qwen":
        response = dashscope.Generation.call(
            model="qwen-max",
            messages=messages,
            result_format='message'
        )
        summary = response.output.choices[0]['message']['content']
        print(f"{model_name}'s summary: ")
        print(summary)
    elif model_name == "Mistral":
        response = mistral_client.chat(
            model="mistral-large-latest",
            messages=[MistralChatMessage(role="user", content=prompt)]
        )
        summary = response.choices[0].message.content
        print(f"{model_name}'s summary: " + summary)
    elif model_name == "Zhipu":
        response = zhipu_client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        summary = response.choices[0].message.content
        print(f"{model_name}'s summary: " + summary)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    return summary


def openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content


# 生成prompt的函数
def generate_prompts_basicinfo(data):
    prompt = "As a professional data scientist, your task is to provide a concise summary of the provided text that " \
             "includes statistical data. Focus on enhancing readability and clarity while ensuring that all " \
             "significant numerical values are accurately represented. Prioritize and retain information with larger " \
             "values, as smaller statistics are less critical. Your summary present " \
             "the essential findings and key data points in a coherent paragraph, avoiding bullet points and ensuring " \
             "no important details are omitted. \n"
    prompt += f"original statistical data:\n{data}\n"
    return prompt


def generate_prompts_morpho(data):
    prompt = "You are a professional data scientist tasked with analyzing a set of neuronal morphology data. The " \
             "dataset includes multiple features with their respective means and standard deviations. Among these, " \
             "'Total Length' and 'Number of Bifurcations' are the most critical features, reflecting the extent and " \
             "complexity of neuronal projections, which are closely related to neuronal function. 'Max Path Distance' " \
             "indicates the range of neuronal projections, while 'Center Shift' reflects the spatial distribution " \
             "balance of neuronal morphology. Your goal is to provide a comparative summary that emphasizes the " \
             "importance of these features and maintains numerical accuracy. Avoid using bullet points and complete " \
             "the summary.\n "
    prompt += f"original neuronal morphology data:\n{data}\n"
    return prompt


def generate_prompts_proj(data):
    prompt = "You are a professional data scientist analyzing a set of neuronal projection data, specifically " \
             "focusing on projections. The axon projection describes how neurons transmit signals from their " \
             "originating brain region to target regions. In contrast, dendrite projections reflect how neurons " \
             "receive signals from various brain areas. The length of these projections indicates the volume of " \
             "transmission and reception, with greater lengths and proportions signifying stronger connectivity and " \
             "functional associations. Your task is to generate a comparative summary that highlights these key " \
             "points, improves readability, and ensures numerical accuracy. Avoid using bullet points and complete " \
             "the summary.\n "
    prompt += f"original neuronal projection data:\n{data}\n"
    return prompt


def generate_combined_response_basicinfo(prompt, origin_input, log_file, score_csv):
    # Helper function to generate summaries and scores
    def generate_summaries(models):
        summaries = {}
        for model in models:
            summaries[model] = generate_data_with_models(prompt, model)
        return summaries

    # Helper function to create combined prompts
    def create_combined_prompt(summaries, origin_input, log_file, score_csv):
        prompt = f"""As a neuroscientist and data analyst, your objective is to assess the precision of three summaries " \
                 "against an original text comprising statistical dataset insights. " \
                 f"original text:{origin_input}"  
                 "Your primary focus should be on " \
                 "the alignment of numerical data within the summaries with the source material, though the " \
                 "step-by-step reasoning need not be documented. Upon identifying the most accurate summary, " \
                 "utilize it along with pertinent details from the original text to craft a new summary. This revised " \
                 "summary must exhibit enhanced readability, brevity, and consistency, strictly confined to the scope " \
                 "of the original data presented. Just return the final summary without any reasoning process"""
        save_to_file(f"[ORIGINAL TEXT]\n{origin_input}\n\n", log_file)
        time = extract_timestamp_from_filename(log_file)
        for model, summary in summaries.items():
            scores = evaluate_summary(summary, origin_input)
            _summary = f"[MODEL: {model}]\n{summary}\n\n"
            save_to_file(_summary, log_file)
            save_scores_to_csv(scores, model, time, "basic info", score_csv)
            prompt += _summary
        return prompt

    models = ['Qwen', 'Mistral', 'Zhipu']

    model_summaries = generate_summaries(models)
    combined_basic_info_prompt = create_combined_prompt(model_summaries, origin_input, log_file, score_csv)
    final_summary = openai_response(combined_basic_info_prompt)
    final_score = evaluate_summary(final_summary, origin_input)
    # GPT direct summary and scoring for original input
    gpt_direct_basic_info_summary = openai_response(
        f"As a professional data scientist, your task is to provide a concise summary of the provided text {origin_input} that "
        "includes statistical data. Focus on enhancing readability and clarity while ensuring that all "
        "significant numerical values are accurately represented. Prioritize and retain information with larger "
        "values, as smaller statistics are less critical. Your summary should present "
        "the essential findings and key data points in a coherent paragraph, avoiding bullet points and ensuring "
        "no important details are omitted. \n"
    )
    direct_score = evaluate_summary(gpt_direct_basic_info_summary, origin_input)
    basic_info_summary_text = '[MODEL: MoE]\n' + str(final_summary) + "\n\n"
    gpt_direct_basic_info_summary_text = '[MODEL: GPT4o]\n' + str(gpt_direct_basic_info_summary) + "\n\n"

    time = extract_timestamp_from_filename(log_file)
    save_to_file(gpt_direct_basic_info_summary_text, log_file)
    save_scores_to_csv(direct_score, "Gpt4o_direct", time, "basic info", score_csv)

    save_to_file(basic_info_summary_text, log_file)
    save_scores_to_csv(final_score, "Gpt4o_combine", time, "basic info", score_csv)

    return final_summary


def generate_combined_response_morphoinfo(prompt, origin_input, log_file, score_csv):
    # Helper function to generate summaries and scores
    def generate_summaries(models):
        summaries = {}
        for model in models:
            summaries[model] = generate_data_with_models(prompt, model)
        return summaries

    # Helper function to create combined prompts
    def create_combined_prompt(summaries, origin_input, log_file, score_csv):
        prompt = f"""As a professional neuroscientist and data analyst, your objective is to meticulously assess the " \
                 "precision of three summaries provided against an original text detailing statistical measures—mean " \
                 "and standard deviations—of neuronal morphology data. " \
                 "original text:{origin_input}" \
                 "The core features under examination are 'Total " \
                 "Length', 'Number of Bifurcations', 'Max Path Distance', and 'Center Shift', which hold significant " \
                 "implications for understanding neuronal function, complexity, reach, and spatial arrangement. Your " \
                 "task involves the following steps: 1. **Thorough Comparison:** Carefully compare the numerical " \
                 "values presented in the summaries with those stated in the original text for 'Total Length', " \
                 "'Number of Bifurcations', 'Max Path Distance', and 'Center Shift'. 2. **Accuracy Verification:** " \
                 "Validate that the summaries accurately represent the descriptive statistics from the source " \
                 "material, ensuring no misinterpretation or misrepresentation of the data. 3. **Logical " \
                 "Assessment:** Confirm that any comparisons made within the summaries are logically sound, " \
                 "well-supported by the data, and correctly interpret the differences or similarities in the neuronal " \
                 "morphology features. You will receive: - The original text outlining the statistical descriptions " \
                 "of neuronal morphology data. - Three separate texts, each attempting to provide a comparative " \
                 "summary based on the original data. While conducting this evaluation, maintain a rigorous " \
                 "analytical mindset, although there is no need to explicitly document your step-by-step reasoning " \
                 "process. Focus on delivering a conclusion regarding the accuracy and validity of each summary's " \
                 "content concerning the initial dataset. Finally, you should craft an enhanced summary that is more accurate, " \
                 "readable, concise, and consistent, strictly limiting the content to the comparison outlined in the summaries. Just return the final summary without any reasoning process"""
        prompt += f"original text:\n{origin_input}\n"
        save_to_file(f"[ORIGINAL TEXT]\n{origin_input}\n\n", log_file)
        time = extract_timestamp_from_filename(log_file)
        for model, summary in summaries.items():
            scores = evaluate_summary(summary, origin_input)
            _summary = f"[MODEL: {model}]\n{summary}\n\n"
            save_to_file(_summary, log_file)
            save_scores_to_csv(scores, model, time, "morpho info", score_csv)
            prompt += _summary
        return prompt

    models = ['Qwen', 'Mistral', 'Zhipu']

    model_summaries = generate_summaries(models)
    combined_basic_info_prompt = create_combined_prompt(model_summaries, origin_input, log_file, score_csv)
    final_summary = openai_response(combined_basic_info_prompt)
    final_score = evaluate_summary(final_summary, origin_input)
    # GPT direct summary and scoring for original input
    gpt_direct_basic_info_summary = openai_response(
        f"You are a professional data scientist tasked with analyzing a set of neuronal morphology data {origin_input}. The dataset "
        f"includes multiple features with their respective means and standard deviations. Among these, 'Total Length' "
        f"and 'Number of Bifurcations' are the most critical features, reflecting the extent and complexity of "
        f"neuronal projections, which are closely related to neuronal function. 'Max Path Distance' indicates the "
        f"range of neuronal projections, while 'Center Shift' reflects the spatial distribution balance of neuronal "
        f"morphology. Your goal is to provide a comparative summary that emphasizes the importance of these features "
        f"and maintains numerical accuracy. Avoid using bullet points and complete the summary.\n "
    )
    direct_score = evaluate_summary(gpt_direct_basic_info_summary, origin_input)
    basic_info_summary_text = '[MODEL: MoE]\n' + str(final_summary) + "\n\n"
    gpt_direct_basic_info_summary_text = '[MODEL: GPT4o]\n' + str(gpt_direct_basic_info_summary) + "\n\n"

    time = extract_timestamp_from_filename(log_file)
    save_to_file(gpt_direct_basic_info_summary_text, log_file)
    save_scores_to_csv(direct_score, "Gpt4o_direct", time, "morpho info", score_csv)

    save_to_file(basic_info_summary_text, log_file)
    save_scores_to_csv(final_score, "Gpt4o_combine", time, "morpho info", score_csv)

    return final_summary


def generate_combined_response_projinfo(prompt, origin_input, log_file, score_csv):
    # Helper function to generate summaries and scores
    def generate_summaries(models):
        summaries = {}
        for model in models:
            summaries[model] = generate_data_with_models(prompt, model)
        return summaries

    # Helper function to create combined prompts
    def create_combined_prompt(summaries, origin_input, log_file, score_csv):
        prompt = f"""As a neuroscientist and data analyst, your objective is to assess the precision of three summaries " \
                 "provided against an original text detailing neuronal projection characteristics. " \
                 "original text:{origin_input}" \
                 "This analysis involves confirming numerical congruity and validating the logical consistency of comparative " \
                 "statements within the summaries concerning axon and dendrite projections, which illustrate signal " \
                 "transmission and reception in the brain, respectively. Emphasize the significance of projection " \
                 "lengths as indicators of connectivity strength. Your final deliverable should be a refined, " \
                 "coherent, and succinct comparative summary that encapsulates the essence of the original content " \
                 "without requiring a step-by-step explanation of your evaluation process. **Given Material:** - " \
                 "**Original Text:** Outlining axon and dendrite projection attributes with respect to signal " \
                 "transmission and reception, emphasizing projection length's correlation with connectivity strength. " \
                 "- **Comparative Summaries:** Three texts summarizing the above, including numerical data and " \
                 "comparative analyses. **Your Task:** 1. **Accuracy Verification:** Ensure each summary accurately " \
                 "represents the numerical data and comparative aspects present in the original text concerning " \
                 "projection lengths and their implications on brain connectivity, although there is no need to " \
                 "explicitly document your step-by-step reasoning process 2. **Consolidated Summary " \
                 "Creation:** Produce a new, enhanced summary that is: - **Readable:** Clear and easily " \
                 "understandable. - **Concise:** Free from redundancy while preserving key information. - " \
                 "**Consistent:** Maintains coherence across all comparative points and factual data. Just return the final summary without any reasoning process"""
        prompt += f"original text:\n{origin_input}\n"
        save_to_file(f"[ORIGINAL TEXT]\n{origin_input}\n\n", log_file)
        time = extract_timestamp_from_filename(log_file)
        for model, summary in summaries.items():
            scores = evaluate_summary(summary, origin_input)
            _summary = f"[MODEL: {model}]\n{summary}\n\n"
            save_to_file(_summary, log_file)
            save_scores_to_csv(scores, model, time, "proj info", score_csv)
            prompt += _summary
        return prompt

    models = ['Qwen', 'Mistral', 'Zhipu']

    model_summaries = generate_summaries(models)
    combined_basic_info_prompt = create_combined_prompt(model_summaries, origin_input, log_file, score_csv)
    final_summary = openai_response(combined_basic_info_prompt)
    final_score = evaluate_summary(final_summary, origin_input)
    # GPT direct summary and scoring for original input
    gpt_direct_basic_info_summary = openai_response(
        f"You are a professional data scientist analyzing a set of neuronal projection data {origin_input}, specifically focusing on "
        f"projections. The axon projection describes how neurons transmit signals from their originating brain region "
        f"to target regions. In contrast, dendrite projections reflect how neurons receive signals from various brain "
        f"areas. The length of these projections indicates the volume of transmission and reception, with greater "
        f"lengths and proportions signifying stronger connectivity and functional associations. Your task is to "
        f"generate a comparative summary that highlights these key points, improves readability, and ensures "
        f"numerical accuracy. Avoid using bullet points and complete the summary.\n "
    )
    direct_score = evaluate_summary(gpt_direct_basic_info_summary, origin_input)
    basic_info_summary_text = '[MODEL: MoE]\n' + str(final_summary) + "\n\n"
    gpt_direct_basic_info_summary_text = '[MODEL: GPT4o]\n' + str(gpt_direct_basic_info_summary) + "\n\n"

    time = extract_timestamp_from_filename(log_file)
    save_to_file(gpt_direct_basic_info_summary_text, log_file)
    save_scores_to_csv(direct_score, "Gpt4o_direct", time, "proj info", score_csv)

    save_to_file(basic_info_summary_text, log_file)
    save_scores_to_csv(final_score, "Gpt4o_combine", time, "proj info", score_csv)

    return final_summary


def pipeline():
    num_iterations = 50
    save_path = "./log_0726_batch/test4/"
    os.makedirs(save_path, exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    # score_csv = save_path + 'MoE_scores_' + str(current_time) + ".csv"
    score_csv = save_path + "MoE_scores_20240804_000000.csv"
    for _ in range(num_iterations):
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = save_path + 'MoE_' + str(current_time) + ".txt"
        origin_basic, origin_fea_den, origin_fea_axon, origin_proj_den, origin_proj_axon = initalInput()
        morpho = origin_fea_axon + origin_fea_den
        proj = origin_proj_den + origin_proj_axon

        basic_prompts = generate_prompts_basicinfo(origin_basic)
        generate_combined_response_basicinfo(basic_prompts, origin_basic, log_file, score_csv)
        time.sleep(5)

        morpho_prompts = generate_prompts_morpho(morpho)
        generate_combined_response_morphoinfo(morpho_prompts, morpho, log_file, score_csv)
        time.sleep(5)

        proj_prompts = generate_prompts_proj(proj)
        generate_combined_response_projinfo(proj_prompts, proj, log_file, score_csv)
        time.sleep(5)


if __name__ == '__main__':
    pipeline()
