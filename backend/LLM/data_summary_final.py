import json
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
import re

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
    elif model_name == "Zhipu":
        response = zhipu_client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        summary = response.choices[0].message.content
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


def generate_prompts(data):
    origin_basic, origin_fea_den, origin_fea_axon, origin_proj_den, origin_proj_axon = neuron_class.inital_data_summary(
        data)
    morpho = origin_fea_axon + origin_fea_den
    proj = origin_proj_den + origin_proj_axon

    basic_info_prompt = generate_prompts_basicinfo(origin_basic)

    morpho_info_prompt = generate_prompts_morpho(morpho)

    proj_info_prompt = generate_prompts_proj(proj)

    prompts = {
        "basicInfo": basic_info_prompt,
        "morphologyFeatures": morpho_info_prompt,
        "projectionInfo": proj_info_prompt
    }
    origin_input = {
        "basicInfo": origin_basic,
        "morphologyFeatures": morpho,
        "projectionInfo": proj
    }
    return prompts, origin_input


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


def generate_combined_response_basicinfo(prompt, origin_input):
    # Helper function to generate summaries and scores
    def generate_summaries(models):
        summaries = {}
        for model in models:
            summaries[model] = generate_data_with_models(prompt, model)
        return summaries

    # Helper function to create combined prompts
    def create_combined_prompt(summaries, origin_input):
        prompt = f"""As a neuroscientist and data analyst, your objective is to assess the precision of three summaries " \
                 "against an original text comprising statistical dataset insights. " \
                 f"original text:{origin_input}" "Your primary focus should be on the alignment of numerical 
                 data within the summaries with the source material, though the step-by-step reasoning need not 
                 be documented. Upon identifying the most accurate summary, utilize it along with pertinent 
                 details from the original text to craft a new summary. This revised summary must exhibit 
                 enhanced readability, brevity, and consistency, strictly confined to the scope of the original 
                 data presented. Please present the final summary as a continuous paragraph without any use of 
                 bullet points, numbered lists, or other similar formatting.Just return the final summary without any 
                 reasoning process """

        for model, summary in summaries.items():
            _summary = f"[MODEL: {model}]\n{summary}\n\n"
            prompt += _summary
        return prompt

    models = ['Qwen', 'Mistral', 'Zhipu']

    model_summaries = generate_summaries(models)
    combined_basic_info_prompt = create_combined_prompt(model_summaries, origin_input)
    final_summary = openai_response(combined_basic_info_prompt)
    return final_summary


def generate_combined_response_morphoinfo(prompt, origin_input):
    # Helper function to generate summaries and scores
    def generate_summaries(models):
        summaries = {}
        for model in models:
            summaries[model] = generate_data_with_models(prompt, model)
        return summaries

    # Helper function to create combined prompts
    def create_combined_prompt(summaries, origin_input):
        prompt = f"""As a professional neuroscientist and data analyst, your objective is to meticulously assess the " \
                 "precision of three summaries provided against an original text detailing statistical measures—mean " \
                 "and standard deviations—of neuronal morphology data. " \
                 "original text:{origin_input}. " \
                 "The core features under examination are 'Total Length', 
                 'Number of Bifurcations', 'Max Path Distance', and 'Center Shift', which hold significant " \ 
                 "implications for understanding neuronal function, complexity, reach, and spatial arrangement. Your 
                 task involves the following steps: 1. **Thorough Comparison:** Carefully compare the numerical 
                 values presented in the summaries with those stated in the original text for 'Total Length', 
                 'Number of Bifurcations', 'Max Path Distance', and 'Center Shift'. 2. **Accuracy 
                 Verification:** Validate that the summaries accurately represent the descriptive statistics 
                 from the source material, ensuring no misinterpretation or misrepresentation of the data. 3. 
                 **Logical Assessment:** Confirm that any comparisons made within the summaries are logically 
                 sound, well-supported by the data, and correctly interpret the differences or similarities in 
                 the neuronal morphology features. You will receive: - The original text outlining the 
                 statistical descriptions of neuronal morphology data. - Three separate texts, each attempting 
                 to provide a comparative summary based on the original data. While conducting this evaluation, 
                 maintain a rigorous analytical mindset, although there is no need to explicitly document your 
                 step-by-step reasoning "process. Focus on delivering a conclusion regarding the accuracy and 
                 validity of each summary's content concerning the initial dataset. Finally, you should craft an 
                 enhanced summary that is more accurate, readable, concise, and consistent, strictly limiting 
                 the content to the comparison outlined in the summaries. Please present the final summary as a 
                 continuous paragraph without any use of bullet points, numbered lists, or other similar 
                 formatting.Just return the final summary without any reasoning process """
        prompt += f"original text:\n{origin_input}\n"
        for model, summary in summaries.items():
            _summary = f"[MODEL: {model}]\n{summary}\n\n"
            prompt += _summary
        return prompt

    models = ['Qwen', 'Mistral', 'Zhipu']

    model_summaries = generate_summaries(models)
    combined_basic_info_prompt = create_combined_prompt(model_summaries, origin_input)
    final_summary = openai_response(combined_basic_info_prompt)
    return final_summary


def generate_combined_response_projinfo(prompt, origin_input):
    # Helper function to generate summaries and scores
    def generate_summaries(models):
        summaries = {}
        for model in models:
            summaries[model] = generate_data_with_models(prompt, model)
        return summaries

    # Helper function to create combined prompts
    def create_combined_prompt(summaries, origin_input):
        prompt = f"""As a neuroscientist and data analyst, your objective is to assess the precision of three summaries " \
                 "provided against an original text detailing neuronal projection characteristics. " \
                 "original text:{origin_input}. This analysis involves confirming numerical congruity and 
                 validating the logical consistency of comparative statements within the summaries concerning 
                 axon and dendrite projections, which illustrate signal transmission and reception in the brain, 
                 respectively. Emphasize the significance of projection lengths as indicators of connectivity 
                 strength. Your final deliverable should be a refined, coherent, and succinct comparative 
                 summary that encapsulates the essence of the original content without requiring a step-by-step 
                 explanation of your evaluation process. **Given Material:** - **Original Text:** Outlining axon 
                 and dendrite projection attributes with respect to signal transmission and reception, 
                 emphasizing projection length's correlation with connectivity strength. - **Comparative 
                 Summaries:** Three texts summarizing the above, including numerical data and comparative 
                 analyses. **Your Task:** 1. **Accuracy Verification:** Ensure each summary accurately " \ 
                 "represents the numerical data and comparative aspects present in the original text concerning " \ 
                 "projection lengths and their implications on brain connectivity, although there is no need to " \ 
                 "explicitly document your step-by-step reasoning process 2. **Consolidated Summary Creation:** 
                 Produce a new, enhanced summary that is: - **Readable:** Clear and easily understandable. - 
                 **Concise:** Free from redundancy while preserving key information. - **Consistent:** Maintains 
                 coherence across all comparative points and factual data. Please present the final summary as a 
                 continuous paragraph without any use of bullet points, numbered lists, "or other similar formatting. 
                 Just return the final summary without any reasoning process """
        prompt += f"original text:\n{origin_input}\n"
        for model, summary in summaries.items():
            _summary = f"[MODEL: {model}]\n{summary}\n\n"
            prompt += _summary
        return prompt

    models = ['Qwen', 'Mistral', 'Zhipu']

    model_summaries = generate_summaries(models)
    combined_basic_info_prompt = create_combined_prompt(model_summaries, origin_input)
    final_summary = openai_response(combined_basic_info_prompt)
    return final_summary


def generate_MoE_Summary_stream(prompt, origin_input, data_type):
    if data_type == 'basicInfo':
        response = generate_combined_response_basicinfo(prompt, origin_input)
    elif data_type == 'morphologyFeatures':
        response = generate_combined_response_morphoinfo(prompt, origin_input)
    else:
        response = generate_combined_response_projinfo(prompt, origin_input)

    yield f'data: {json.dumps({"type": data_type, "content": response})}\n\n'
