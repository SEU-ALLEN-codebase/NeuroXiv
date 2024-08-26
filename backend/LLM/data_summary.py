import numpy as np
import openai
import json
import time
from http import HTTPStatus
import dashscope
from dataset_db import neurons, get_summary_info
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage as MistralChatMessage
from zhipuai import ZhipuAI
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

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

log_file = r"D:\NeuroXiv\api\LLM\log\data_summary_log.txt"


def save_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


def evaluate_summaries(reference, hypothesis):
    # Initialize ROUGE scorer
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    # Calculate ROUGE scores
    rouge_scores = scorer.score(reference, hypothesis)

    # Calculate BLEU score
    smoothing_function = SmoothingFunction().method1
    reference_tokens = [reference.split()]
    hypothesis_tokens = hypothesis.split()
    bleu_score = sentence_bleu(reference_tokens, hypothesis_tokens, smoothing_function=smoothing_function)

    return rouge_scores, bleu_score


# 生成数据的函数
def generate_data_with_models(prompt):
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': str(prompt)}]
    qwen_response = dashscope.Generation.call(model="qwen-max",
                                              messages=messages,
                                              result_format='message',  # set the result to be "message"  format.
                                              )

    print("qwen's summary: ")
    print(qwen_response.output.choices[0]['message']['content'])

    mistral_response = mistral_client.chat(
        model="mistral-large-latest",
        messages=[MistralChatMessage(role="user", content=prompt)]
    )
    print("mistral's summary: " + mistral_response.choices[0].message.content)

    zhipu_response = zhipu_client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    print("zhipu's summary: " + str(zhipu_response.choices[0].message.content))
    return qwen_response.output.choices[0]['message']['content'], mistral_response.choices[0].message.content, \
           zhipu_response.choices[0].message.content


# 生成prompt的函数
def generate_prompts(data):
    df_neurons, neuronlist, basic_info = neuron_class.summary_data(data)
    basic_info_prompt = f"Summarize the basic information in three sentences including the number of items, regions, " \
                        f"and sources: {basic_info}. Notice that 'SEU-ALLEN', 'ION' and 'MouseLight' are the names of data source "
    print('basic prompt')
    print(basic_info_prompt)
    morpho = neuron_class.calculate_morphology_info(neuronlist, df_neurons)
    morpho_info_prompt = f"Summarize the following data in three sentences, where the dictionary is structured from the top down as data source, cell type, and morphology feartures. Emphasize the differences in characteristics across the primary brain regions provided. Compare the numerical values to analyze the distinctions between the brain regions, noting any variations across different sources if applicable: {morpho} "
    proj = neuron_class.calculate_projection_info(df_neurons, neuronlist)
    proj_info_prompt = f"Summarize the following data in three sentences, where the dictionary is structured from the top down as data source, cell type, and neuron projection feartures. Emphasize the differences in characteristics across the primary brain regions provided. Compare the numerical values to analyze the distinctions between the brain regions, noting any variations across different sources if applicable.{proj}"
    prompts = {
        "basicInfo": basic_info_prompt,
        "morphologyFeatures": morpho_info_prompt,
        "projectionInfo": proj_info_prompt
    }
    origin_input = {
        "basicInfo": basic_info,
        "morphologyFeatures": morpho,
        "projectionInfo": proj
    }
    return prompts, origin_input


# 分别生成数据并让GPT-4分析
def generate_combined_response(prompts, origin_input):
    # prompts, origin_input = generate_prompts(data)

    # Basic Info
    basic_info_qwen, basic_info_mistral, basic_info_zhipu = generate_data_with_models(prompts['basicInfo'])
    combined_basic_info_prompt = f"Analyze and combine the following responses from Qwen, Mistral  and GLM models to generate a comprehensive summary.\n\n"
    combined_basic_info_prompt += f"Qwen response for basic info:\n{basic_info_qwen}\n\n"
    combined_basic_info_prompt += f"Mistral response for basic info:\n{basic_info_mistral}\n\n"
    combined_basic_info_prompt += f"zhipu response for morphology features:\n{basic_info_zhipu}\n\n"
    # basic_info_summary = stream_openai_response(combined_basic_info_prompt, 'basicInfo')
    qwen_basicinfo_rouge_scores, qwen_basicinfo_bleu_score = evaluate_summaries(str(origin_input['basicInfo']),
                                                                                str(basic_info_qwen))
    mistral_basicinfo_rouge_scores, mistral_basicinfo_bleu_score = evaluate_summaries(str(origin_input['basicInfo']),
                                                                                      str(basic_info_mistral))
    zhipu_basicinfo_rouge_scores, zhipu_basicinfo_bleu_score = evaluate_summaries(str(origin_input['basicInfo']),
                                                                                  str(basic_info_zhipu))
    print("basic info task:\n\n" + 'qwen: ' + str(qwen_basicinfo_rouge_scores) + '|' + str(
        qwen_basicinfo_bleu_score) + '\n\n' + 'mistral: ' + str(mistral_basicinfo_rouge_scores) + '|' + str(
        mistral_basicinfo_bleu_score) + '\n\n' + 'zhipu: ' + str(zhipu_basicinfo_rouge_scores) + '|' + str(
        zhipu_basicinfo_bleu_score) + '\n\n')
    # basic_info_summary = 'GPT4 final summary\n\n' + str(basic_info_summary) + "\n\n"
    save_to_file(combined_basic_info_prompt, log_file)
    # save_to_file(basic_info_summary, log_file)

    # Morphology Features
    morpho_info_qwen, morpho_info_mistral, morpho_info_zhipu = generate_data_with_models(prompts['morphologyFeatures'])
    combined_morpho_info_prompt = f"Analyze and combine the following responses from Qwen, Mistral  and GLM models to generate a comprehensive summary.\n\n"
    combined_morpho_info_prompt += f"Qwen response for morphology features:\n{morpho_info_qwen}\n\n"
    combined_morpho_info_prompt += f"Mistral response for morphology features:\n{morpho_info_mistral}\n\n"
    combined_morpho_info_prompt += f"zhipu response for morphology features:\n{morpho_info_zhipu}\n\n"
    # morpho_info_summary = stream_openai_response(combined_morpho_info_prompt, 'morphologyFeatures')
    # morpho_info_summary = 'GPT4 final summary\n\n' + str(morpho_info_summary) + "\n\n"
    save_to_file(combined_morpho_info_prompt, log_file)

    # Projection Info
    proj_info_qwen, proj_info_mistral, proj_info_zhipu = generate_data_with_models(prompts['projectionInfo'])
    combined_proj_info_prompt = f"Analyze and combine the following responses from Qwen, Mistral  and GLM models to generate a comprehensive summary.\n\n"
    combined_proj_info_prompt += f"Qwen response for projection info:\n{proj_info_qwen}\n\n"
    combined_proj_info_prompt += f"Mistral response for projection info:\n{proj_info_mistral}\n\n"
    combined_proj_info_prompt += f"zhipu response for morphology features:\n{proj_info_zhipu}\n\n"
    # proj_info_summary = stream_openai_response(combined_proj_info_prompt, 'projectionInfo')
    # proj_info_summary = 'GPT4 final summary\n\n' + str(proj_info_summary) + "\n\n"
    save_to_file(combined_proj_info_prompt, log_file)


def stream_openai_response(prompt, data_type):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "You are an assistant that only returns the result for the current request without considering previous conversations."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=520,
        stream=True
    )

    for chunk in response:
        if 'choices' in chunk and len(chunk['choices']) > 0:
            text_chunk = chunk['choices'][0]['delta'].get('content', '')
            yield f'data: {json.dumps({"type": data_type, "content": text_chunk})}\n\n'
            time.sleep(0.1)  # Adjust the sleep time if needed
    return response


def generate_data_and_summarize(neuronlists, prompt, data_type):
    prompts, origin_input = generate_prompts(neuronlists)
    generate_combined_response(prompts, origin_input)
    qwen_response, mistral_response, zhipu_response = generate_data_with_models(prompt)
    combined_prompt = f"Analyze and combine the following responses from Qwen and Mistral models to generate a comprehensive summary.\n\n"
    combined_prompt += f"Qwen response for {data_type}:\n{qwen_response}\n\n"
    combined_prompt += f"Mistral response for {data_type}:\n{mistral_response}\n\n"
    combined_prompt += f"zhipu response for {data_type}:\n{zhipu_response}\n\n"

    for summary in stream_openai_response(combined_prompt, data_type):
        yield summary


if __name__ == '__main__':
    origin_input = "{'counts': [{'name': 'Total', 'num': 128}, {'name': 'SEU-ALLEN', 'num': 10}, {'name': 'ION', " \
                   "'num': 118}, {'name': 'MouseLight', 'num': 0}, {'name': 'basal dendrite', 'num': 102}, " \
                   "{'name': 'apical dendrite', 'num': 3}, {'name': 'axon', 'num': 128}, {'name': 'soma " \
                   "reconstructions', 'num': 0}, {'name': 'bouton reconstructions', 'num': 0}, {'name': 'CA1', " \
                   "'num': 73}, {'name': 'CA3', 'num': 27}, {'name': 'CA2', 'num': 5}, {'name': 'DG-sg', 'num': 4}, " \
                   "{'name': 'ProS', 'num': 3}, {'name': 'SUB', 'num': 3}, {'name': 'DG-po', 'num': 3}, " \
                   "{'name': 'TEa', 'num': 3}, {'name': 'AUDv', 'num': 2}, {'name': 'VISal', 'num': 2}, " \
                   "{'name': 'AUDpo', 'num': 1}, {'name': 'VISl', 'num': 1}, {'name': 'SSs4', 'num': 1}]}. Notice " \
                   "that 'SEU-ALLEN', 'ION' and 'MouseLight' are the names of data source "
    qwen_sumamry = "There are a total of 138 items across various categories. The data is sourced from three main providers: SEU-ALLEN with 10 items, ION with 128 items, and MouseLight with 0 items. These items include neuron parts like basal dendrites (110), apical dendrites (3), and axons (138), as well as regional classifications spanning 9 different brain regions with CA1 having the most at 81 items."
    mistral_summary = "The data consists of 138 items, which are sourced from three different providers: SEU-ALLEN (10 items), ION (128 items), and MouseLight, which currently has no items. These items are further categorized by region, with the majority coming from CA1 (81 items), CA3 (27 items), and the axon (138 items). Other regions represented include CA2, ProS, SUB, DG-sg, DG-po, TEa, AUDv, VISal, AUDpo, VISl, and SSs4, each contributing varying numbers of items."
    zhipu_summary = "There are a total of 138 items, with 10 from the SEU-ALLEN source, and 128 from the ION source. The MouseLight source has no items. These items are categorized into different regions, including basal dendrites (110), apical dendrites (3), axons (138), and various brain regions such as CA1 (81), CA3 (27), and others with smaller numbers."
    GPT4_final_summary = "The dataset comprises 138 items across various categories sourced from three providers: SEU-ALLEN (10 items), ION (128 items), and MouseLight (0 items). The items include neuron parts such as basal dendrites (110), apical dendrites (3), and axons (138). These items are distributed across nine different brain regions, with a significant concentration in the CA1 region (81 items), followed by CA3 (27 items). Other regions represented include CA2, ProS, SUB, DG-sg, DG-po, TEa, AUDv, VISal, AUDpo, VISl, and SSs4. No soma or bouton reconstructions were reported."
    GPT4_basicinfo_rouge_scores, GPT4_basicinfo_bleu_score = evaluate_summaries(str(origin_input),
                                                                                str(GPT4_final_summary))
    print("basic info task:\n\n" + 'GPT4: ' + str(GPT4_basicinfo_rouge_scores) + '|' + str(
        GPT4_basicinfo_bleu_score) + '\n\n')

# v1.0
# def parse_redis_data(data):
#     parsed_data = {}
#     for k, v in data.items():
#         key_parts = k.decode('utf-8').split(':')
#         current_level = parsed_data
#         for part in key_parts[:-1]:
#             if part not in current_level:
#                 current_level[part] = {}
#             current_level = current_level[part]
#
#         final_key = key_parts[-1]
#         if ',' in v.decode('utf-8'):  # If the value contains commas, it might be a list
#             current_level[final_key] = v.decode('utf-8').split(',')
#         else:
#             current_level[final_key] = int(v.decode('utf-8')) if v.decode('utf-8').isdigit() else v.decode('utf-8')
#
#     return parsed_data
#
#
# def analyze_data(data):
#     basic_info = data.get('basic_info', {}).get('counts', [])
#     morpho_info = data.get('morpho_info', [])
#     proj_info = data.get('proj_info', [])
#
#     # 检查 basic_info 是否为列表
#     if not isinstance(basic_info, list):
#         raise ValueError("basic_info.counts should be a list")
#
#     # 统计数据
#     total_neurons = next((item['num'] for item in basic_info if item['name'] == 'Total'), 0)
#     sources = list(set(item['name'] for item in basic_info if item['name'] != 'Total'))
#
#     # 验证每个项目是否包含 'region' 键
#     all_regions = []
#     for proj in proj_info:
#         for item in proj.get('info', []):
#             if 'region' not in item:
#                 raise KeyError(f"Missing 'region' key in proj_info item: {item}")
#             all_regions.append(item['region'])
#     regions = list(set(all_regions))
#
#     # 形态特征分布
#     morpho_summaries = []
#     for morpho in morpho_info:
#         morpho_type = morpho['type']
#         metrics = morpho['info']
#         summary = f"{morpho_type.capitalize()} features:\n"
#         for metric in metrics:
#             mean = metric['mean']
#             std = metric['std']
#             max_value = mean + std
#             min_value = mean - std
#             summary += f"  - {metric['metric']}: Avg = {mean}, StdDev = {std}, Max = {max_value}, Min = {min_value}\n"
#         morpho_summaries.append(summary)
#
#     # 投射脑区分布
#     projection_summary = "Projection regions:\n"
#     for proj in proj_info:
#         proj_type = proj['type']
#         regions_info = proj['info']
#         region_summary = f"{proj_type.capitalize()} projections:\n"
#         for region in regions_info:
#             abs_value = region['abs']
#             relative_value = region['relative']
#             region_name = region['region']
#             region_summary += f"  - {region_name}: Abs = {abs_value}, Relative = {relative_value}\n"
#         projection_summary += region_summary
#
#     # 综合总结
#     basicInfo_summary = f"Basic Information:\n  - Total Neurons: {total_neurons}\n  - Regions: {', '.join(regions)}\n  " \
#                         f"- Sources: {', '.join(sources)}\n"
#     morphFea_summary = "\nMorphology Features:\n" + "\n".join(morpho_summaries)
#     projinfo_summary = "\nProjection Info:\n" + projection_summary
#
#     return {
#         "basicInfo": basicInfo_summary,
#         "morphologyFeatures": morphFea_summary,
#         "projectionInfo": projinfo_summary
#     }
#
#
# def generate_prompts(data):
#     df_neurons, neuronlist, basic_info = neuron_class.summary_data(data)
#     basic_info_prompt = f"Summarize the basic information in three sentences including the number of items, regions, and sources: {basic_info}"
#     morpho = neuron_class.calculate_morphology_info(neuronlist, df_neurons)
#     morpho_info_prompt = f"Summarize the following data in three sentences, where the dictionary is structured from the top down as data source, cell type, and morphology feartures. Emphasize the differences in characteristics across the primary brain regions provided. Compare the numerical values to analyze the distinctions between the brain regions, noting any variations across different sources if applicable: {morpho} "
#     proj = neuron_class.calculate_projection_info(df_neurons, neuronlist)
#     proj_info_prompt = f"Summarize the following data in three sentences, where the dictionary is structured from the top down as data source, cell type, and neuron projection feartures. Emphasize the differences in characteristics across the primary brain regions provided. Compare the numerical values to analyze the distinctions between the brain regions, noting any variations across different sources if applicable.{proj}"
#     return {
#         "basicInfo": basic_info_prompt,
#         "morphologyFeatures": morpho_info_prompt,
#         "projectionInfo": proj_info_prompt
#     }
#
#
# def stream_openai_response(prompt, data_type):
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system",
#              "content": "You are an assistant that only returns the result for the current request without considering previous conversations."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=520,
#         stream=True
#     )
#
#     for chunk in response:
#         if 'choices' in chunk and len(chunk['choices']) > 0:
#             text_chunk = chunk['choices'][0]['delta'].get('content', '')
#             yield f'data: {json.dumps({"type": data_type, "content": text_chunk})}\n\n'
#             time.sleep(0.1)  # Adjust the sleep time if needed
