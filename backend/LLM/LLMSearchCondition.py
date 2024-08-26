import os
import re

import pandas as pd
import requests
import json


def predict_search_condition(querry):
    l_model = os.environ.get("MODEL", "llama3")
    context = pd.read_json('D:/NeuroXiv/api/LLM/SearchCondition/search_conditions.json')
    prompt = (
        "You are an AI retriever and your task is to understand the user's question and extract the corresponding "
        "search criteria based on the document provided to you. The format of the search criteria is as follows: {"
        "'celltype': ['FRP'], 'has_recon_axon': True, 'morpho_axon_relative center shift': [0, 0.997237091113382], "
        "'proj_axon_SSp-m_abs': [ 0, 97668.81152999999], 'brain_atlas': ['fMOST']}. \n\n "
        "If a condition with a range query is detected, but no specific value is detected, the corresponding default "
        "maximum and minimum values from the provided documentation should be used \n\n"
        "The following are some examples:\n\n"
        "1. user querry: find neurons from SEU_Allen in CCFv3 atlas"
        "   search condation: {'data_source': ['SEU-ALLEN'], 'brain_atlas': ['CCFv3']} \n\n"
        "2. user querry: find VPM neurons which project to CP "
        "search condation: {'celltype': ['VPM'], 'proj_axon_CP_abs': [0, 254574.4054], 'proj_den_CP_abs': [0, "
        "7243.805281999999], 'brain_atlas': ['fMOST']}\n\n "
        "3. user querry: find VPM neurons whose axon project to CP "
        "  search condation: {'celltype': ['VPM'], 'proj_axon_CP_abs': [0, 254574.4054], 'brain_atlas': ['fMOST']}\n\n"
        "4. user querry: find MOp neurons whose dendrite projection to MOs are more than 1000 "
        "search condation: {'celltype': ['MOp'], 'proj_den_MOs_abs': [1000, 20815.8311], 'brain_atlas': ['fMOST']}\n\n "
        "5. user querry: find VPM neurons whose axon projection to MOp are less than 1000 "
        "search condation: {'celltype': ['VPM'], 'proj_axon_MOp_abs': [0, 1000], 'brain_atlas': ['fMOST']}\n\n "
        "6. user querry: find CP neurons whose dendrite have more than 24 max branch order "
        "search condation: {'celltype': ['CP'],'morpho_den_max branch order': [0, 42], 'brain_atlas': ['fMOST']}\n\n "
        "6. user querry: MOs neurons which have axon total length more than 1000 um "
        "search condation: {'celltype': ['MOs'], 'morpho_axon_total length': [1000, 430315], 'brain_atlas': ['fMOST']}\n\n "

        f"User query: {querry}"
        f"context: {context}"
        "just return the search condition with nothing else! Pay Attention to this, i only need search condition in "
        "Json format!!!! "
    )

    url = "http://localhost:11434/api/chat"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": l_model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)

    complete_response = ""
    try:
        for line in response.iter_lines():
            if line:
                decoded_line = json.loads(line.decode('utf-8'))
                if 'message' in decoded_line and 'content' in decoded_line['message']:
                    complete_response += decoded_line['message']['content']
        pattern = r'\{([^}]+)\}'
        complete_response = re.search(pattern, complete_response).group(0)
        print(complete_response)
        return complete_response.strip()
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.content)
        raise


def predict_search_condition_llamacpp(query):
    l_model = "llama-3-8b"
    prompt = (
        "You are an AI retriever and your task is to understand the user's question and extract the corresponding "
        "search criteria based on the document provided to you. The format of the search criteria is as follows: {"
        "'celltype': ['FRP'], 'has_recon_axon': True, 'morpho_axon_relative center shift': [0, 0.997237091113382], "
        "'proj_axon_SSp-m_abs': [0, 97668.81152999999], 'brain_atlas': ['fMOST']}. \n\n"
        "If a condition with a range query is detected, but no specific value is detected, the corresponding default "
        "maximum and minimum values from the provided documentation should be used \n\n"
        "The following are some examples:\n\n"
        "1. user query: find neurons from SEU_Allen in CCFv3 atlas\n"
        "   search condition: {'data_source': ['SEU-ALLEN'], 'brain_atlas': ['CCFv3']} \n\n"
        "2. user query: find VPM neurons which project to CP\n"
        "   search condition: {'celltype': ['VPM'], 'proj_axon_CP_abs': [0, 254574.4054], 'proj_den_CP_abs': [0, 7243.805281999999], 'brain_atlas': ['fMOST']} \n\n"
        "3. user query: find VPM neurons whose axon project to CP\n"
        "   search condition: {'celltype': ['VPM'], 'proj_axon_CP_abs': [0, 254574.4054], 'brain_atlas': ['fMOST']} \n\n"
        "4. user query: find MOp neurons whose dendrite projection to MOs are more than 1000\n"
        "   search condition: {'celltype': ['MOp'], 'proj_den_MOs_abs': [1000, 20815.8311], 'brain_atlas': ['fMOST']} \n\n"
        "5. user query: find VPM neurons whose axon projection to MOp are less than 1000\n"
        "   search condition: {'celltype': ['VPM'], 'proj_axon_MOp_abs': [0, 1000], 'brain_atlas': ['fMOST']} \n\n"
        "6. user query: find CP neurons whose dendrite have more than 24 max branch order\n"
        "   search condition: {'celltype': ['CP'],'morpho_den_max branch order': [0, 42], 'brain_atlas': ['fMOST']} \n\n"
        "6. user query: MOs neurons which have axon total length more than 1000 um\n"
        "   search condition: {'celltype': ['MOs'], 'morpho_axon_total length': [1000, 430315], 'brain_atlas': ['fMOST']} \n\n"

        f"User query: {query}\n"
        "just return the search condition with nothing else! Pay Attention to this, I only need search condition in "
        "Json format!!!!"
    )

    url = "http://localhost:8083/v1/completions"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": l_model,
        "prompt": prompt,
        "max_tokens": 512
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    try:
        complete_response = response.json()
        print("Complete Response:", complete_response)  # Print the whole response for debugging

        # Adjust pattern and key access according to actual response
        content = complete_response.get('content', '')
        pattern = r'\{[^}]+\}'
        match = re.search(pattern, content)
        if match:
            complete_response = match.group(0)
            print(complete_response)
            return complete_response.strip()
        else:
            print("No valid JSON found in the response.")
            return None
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.content)

        raise


if __name__ == "__main__":
    query = "find CP neurons whose dendrite have more than 24 max branch order"
    predict_search_condition_llamacpp(query)

# import os
# import re
# import json
# import pandas as pd
# import requests
#
#
# # 从JSON文件中加载默认值
# def load_default_values(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         data = json.load(file)
#     return data
#
#
# # 递归函数查找特定querry_name的默认值
# def find_default_values(node, querry_name):
#     if isinstance(node, dict):
#         if node.get('querry_name') == querry_name:
#             return node.get('default_min'), node.get('default_max')
#         for key in node:
#             result = find_default_values(node[key], querry_name)
#             if result:
#                 return result
#     elif isinstance(node, list):
#         for item in node:
#             result = find_default_values(item, querry_name)
#             if result:
#                 return result
#     return None, None
#
#
# def predict_search_condition(query):
#     l_model = os.environ.get("MODEL", "llama3")
#     context_path = 'D:/NeuroXiv/api/LLM/SearchCondition/search_conditions.json'
#     context = load_default_values(context_path)
#
#     prompt = (
#         "You are an AI retriever and your task is to understand the user's question and extract the corresponding "
#         "search criteria based on the document provided to you. The format of the search criteria is as follows: {"
#         "'celltype': ['FRP'], 'has_recon_axon': True, 'morpho_axon_relative center shift': [0, 0.997237091113382], "
#         "'proj_axon_SSp-m_abs': [ 0, 97668.81152999999], 'brain_atlas': ['fMOST']}. \n\n "
#         "If a condition with a range query is detected, but no specific value is detected, the corresponding default "
#         "maximum and minimum values from the provided documentation should be used \n\n"
#         "The following are some examples:\n\n"
#         "1. user query: find neurons from SEU_Allen in CCFv3 atlas\n"
#         "   search condition: {'data_source': ['SEU-ALLEN'], 'brain_atlas': ['CCFv3']} \n\n"
#         "2. user query: find VPM neurons which project to CP \n"
#         "   search condition: {'celltype': ['VPM'], 'proj_axon_CP_abs': [0, 254574.4054], 'proj_den_CP_abs': [0, 7243.805281999999], 'brain_atlas': ['fMOST']} \n\n"
#         "3. user query: find VPM neurons whose axon project to CP \n"
#         "   search condition: {'celltype': ['VPM'], 'proj_axon_CP_abs': [0, 254574.4054], 'brain_atlas': ['fMOST']} \n\n"
#         "4. user query: find MOp neurons whose dendrite projection to MOs are more than 1000 \n"
#         "   search condition: {'celltype': ['MOp'], 'proj_den_MOs_abs': [1000, 20815.8311], 'brain_atlas': ['fMOST']} \n\n"
#         "5. user query: find VPM neurons whose axon projection to MOp are less than 1000 \n"
#         "   search condition: {'celltype': ['VPM'], 'proj_axon_MOp_abs': [0, 1000], 'brain_atlas': ['fMOST']} \n\n"
#         "6. user query: find CP neurons whose dendrite have more than 24 max branch order \n"
#         "   search condition: {'celltype': ['CP'],'morpho_den_max branch order': [0, 42], 'brain_atlas': ['fMOST']} \n\n"
#         f"User query: {query}\n"
#         "Just return the search condition in JSON format! Pay attention to this, I only need the search condition in JSON format!\n"
#     )
#
#     url = "http://localhost:11434/api/chat"
#     headers = {'Content-Type': 'application/json'}
#     data = {
#         "model": l_model,
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }
#     response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
#
#     complete_response = ""
#     try:
#         for line in response.iter_lines():
#             if line:
#                 decoded_line = json.loads(line.decode('utf-8'))
#                 if 'message' in decoded_line and 'content' in decoded_line['message']:
#                     complete_response += decoded_line['message']['content']
#         pattern = r'\{[^}]+\}'
#         match = re.search(pattern, complete_response)
#         if match:
#             search_condition = json.loads(match.group(0))
#             # 检查并补全缺少的范围查询值
#             for key in search_condition.keys():
#                 if isinstance(search_condition[key], list) and len(search_condition[key]) == 0:
#                     default_min, default_max = find_default_values(context, key)
#                     if default_min is not None and default_max is not None:
#                         search_condition[key] = [default_min, default_max]
#             print(json.dumps(search_condition))
#             return search_condition
#         else:
#             print("No search condition found in the response.")
#             return {}
#     except json.JSONDecodeError as e:
#         print("Error decoding JSON response:", e)
#         print("Response content:", response.content)
#         raise
#
#
# if __name__ == "__main__":
#     query = "find MOp neurons whose axon projection to MOs more than 3000 and lower than 5000"
#     predict_search_condition(query)
